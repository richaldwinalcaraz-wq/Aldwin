const { google } = require('googleapis');
const crypto = require('crypto');
const logger = require('../utils/logger');
const config = require('../config/env');

const TABS = {
  MED_SPAS: 'Med Spas',
  ROOFING: 'Roofing Companies',
  AESTHETIC_CLINICS: 'Aesthetic Clinics',
  DENTAL_CLINICS: 'Dental Clinics',
  REALTORS: 'Realtors',
  LAW_FIRMS: 'Law Firms',
  INSURANCE: 'Insurance Agencies',
  GYMS: 'Gyms',
  CAR_DEALERSHIPS: 'Car Dealerships',
  HVAC: 'HVAC Companies',
  TRAVEL: 'Travel Agencies',
  HOT: 'Hot Leads',
  WARM: 'Warm Leads',
  COLD: 'Cold Leads',
};

const NICHE_TAB_MAP = {
  // Med Spas
  'med spa': TABS.MED_SPAS,
  'med spas': TABS.MED_SPAS,
  'medspa': TABS.MED_SPAS,
  // Roofing
  'roofing': TABS.ROOFING,
  'roofing companies': TABS.ROOFING,
  'roofing company': TABS.ROOFING,
  'roofer': TABS.ROOFING,
  // Aesthetic Clinics
  'aesthetic clinic': TABS.AESTHETIC_CLINICS,
  'aesthetic clinics': TABS.AESTHETIC_CLINICS,
  'aesthetics': TABS.AESTHETIC_CLINICS,
  // Dental Clinics
  'dental clinic': TABS.DENTAL_CLINICS,
  'dental clinics': TABS.DENTAL_CLINICS,
  'dentist': TABS.DENTAL_CLINICS,
  'dental': TABS.DENTAL_CLINICS,
  // Realtors
  'realtor': TABS.REALTORS,
  'realtors': TABS.REALTORS,
  'real estate': TABS.REALTORS,
  'real estate agent': TABS.REALTORS,
  // Law Firms
  'law firm': TABS.LAW_FIRMS,
  'law firms': TABS.LAW_FIRMS,
  'attorney': TABS.LAW_FIRMS,
  'lawyer': TABS.LAW_FIRMS,
  // Insurance
  'insurance agency': TABS.INSURANCE,
  'insurance agencies': TABS.INSURANCE,
  'insurance': TABS.INSURANCE,
  // Gyms
  'gym': TABS.GYMS,
  'gyms': TABS.GYMS,
  'fitness center': TABS.GYMS,
  'fitness': TABS.GYMS,
  // Car Dealerships
  'car dealership': TABS.CAR_DEALERSHIPS,
  'car dealerships': TABS.CAR_DEALERSHIPS,
  'auto dealership': TABS.CAR_DEALERSHIPS,
  'car dealer': TABS.CAR_DEALERSHIPS,
  // HVAC
  'hvac': TABS.HVAC,
  'hvac company': TABS.HVAC,
  'hvac companies': TABS.HVAC,
  'heating and cooling': TABS.HVAC,
  // Travel Agencies
  'travel agency': TABS.TRAVEL,
  'travel agencies': TABS.TRAVEL,
  'travel agent': TABS.TRAVEL,
  'travel': TABS.TRAVEL,
};

const CLASSIFICATION_TAB_MAP = {
  Hot: TABS.HOT,
  Warm: TABS.WARM,
  Cold: TABS.COLD,
};

const HEADERS = [
  'Business Name', 'Niche', 'Location', 'Website', 'Email',
  'Phone Number', 'Google Reviews', 'Google Rating', 'Lead Score',
  'Classification', 'Company Size', 'AI Opportunity Score',
  'Website Quality', 'Detected Gaps', 'Social Links',
  'Google Maps URL', 'Notes', 'Outreach Status', 'Date Scraped', 'Dedup Hash',
];

const HOT_GREEN = { red: 0.565, green: 0.933, blue: 0.565 };
const WARM_YELLOW = { red: 1.0, green: 0.949, blue: 0.612 };
const COLD_BLUE = { red: 0.729, green: 0.855, blue: 0.984 };

let _sheets = null;

function getAuth() {
  return new google.auth.JWT(
    config.googleServiceAccountEmail,
    null,
    config.googlePrivateKey,
    ['https://www.googleapis.com/auth/spreadsheets']
  );
}

async function getSheetsClient() {
  if (_sheets) return _sheets;
  const auth = getAuth();
  _sheets = google.sheets({ version: 'v4', auth });
  return _sheets;
}

function deduplicationHash(lead) {
  const name = (lead.businessName || '').toLowerCase().trim();
  const domain = extractDomain(lead.website || '');
  const phone = (lead.phone || '').replace(/\D/g, '');
  return crypto.createHash('sha256').update(`${name}|${domain}|${phone}`).digest('hex').slice(0, 16);
}

function extractDomain(url) {
  try {
    const u = new URL(url.startsWith('http') ? url : `https://${url}`);
    return u.hostname.replace('www.', '');
  } catch {
    return url.toLowerCase().trim();
  }
}

async function getOrCreateSheet(sheets, title) {
  const meta = await sheets.spreadsheets.get({ spreadsheetId: config.googleSheetsId });
  const existing = meta.data.sheets.find((s) => s.properties.title === title);
  if (existing) return existing.properties.sheetId;

  const res = await sheets.spreadsheets.batchUpdate({
    spreadsheetId: config.googleSheetsId,
    requestBody: {
      requests: [{ addSheet: { properties: { title } } }],
    },
  });
  const newSheetId = res.data.replies[0].addSheet.properties.sheetId;
  await addHeaderRow(sheets, title);
  logger.info(`Created sheet tab: ${title}`);
  return newSheetId;
}

async function addHeaderRow(sheets, title) {
  await sheets.spreadsheets.values.update({
    spreadsheetId: config.googleSheetsId,
    range: `'${title}'!A1`,
    valueInputOption: 'RAW',
    requestBody: { values: [HEADERS] },
  });
}

async function ensureAllTabs() {
  const sheets = await getSheetsClient();
  for (const tabName of Object.values(TABS)) {
    await getOrCreateSheet(sheets, tabName);
  }
  logger.info('All Google Sheets tabs ready');
}

async function getExistingHashes(sheets, tabName) {
  try {
    const res = await sheets.spreadsheets.values.get({
      spreadsheetId: config.googleSheetsId,
      range: `'${tabName}'!T2:T`,
    });
    return new Set((res.data.values || []).flat().filter(Boolean));
  } catch {
    return new Set();
  }
}

function leadToRow(lead) {
  return [
    lead.businessName || '',
    lead.niche || '',
    lead.location || '',
    lead.website || '',
    lead.email || '',
    lead.phone || '',
    lead.reviewCount ?? '',
    lead.rating ?? '',
    lead.leadScore ?? '',
    lead.classification || '',
    lead.companySize || '',
    lead.aiOpportunityScore ?? '',
    lead.websiteQuality || '',
    Array.isArray(lead.detectedGaps) ? lead.detectedGaps.join(', ') : (lead.detectedGaps || ''),
    Array.isArray(lead.socialLinks) ? lead.socialLinks.join(', ') : (lead.socialLinks || ''),
    lead.mapsUrl || '',
    lead.notes || '',
    lead.outreachStatus || 'Not Contacted',
    lead.dateScraped || new Date().toISOString().split('T')[0],
    lead._hash || deduplicationHash(lead),
  ];
}

async function insertLeads(leads) {
  if (!leads || leads.length === 0) return { inserted: 0, skipped: 0 };

  const sheets = await getSheetsClient();
  // Track at unique LEAD level (not tab level) for accurate reporting
  const insertedHashes = new Set();
  const skippedHashes = new Set();

  // Group leads by niche tab + classification tab
  const groups = {};
  for (const lead of leads) {
    lead._hash = deduplicationHash(lead);
    const nicheTab = NICHE_TAB_MAP[(lead.niche || '').toLowerCase()] || TABS.MED_SPAS;
    const classTab = CLASSIFICATION_TAB_MAP[lead.classification] || TABS.COLD;
    if (!groups[nicheTab]) groups[nicheTab] = [];
    if (!groups[classTab]) groups[classTab] = [];
    groups[nicheTab].push(lead);
    if (nicheTab !== classTab) groups[classTab].push(lead);
  }

  for (const [tabName, tabLeads] of Object.entries(groups)) {
    await getOrCreateSheet(sheets, tabName);
    const existingHashes = await getExistingHashes(sheets, tabName);

    const newLeads = tabLeads.filter((l) => !existingHashes.has(l._hash));
    const skipped = tabLeads.length - newLeads.length;

    // Track at lead level (use Set to avoid double-counting across tabs)
    tabLeads.filter((l) => existingHashes.has(l._hash)).forEach((l) => skippedHashes.add(l._hash));
    newLeads.forEach((l) => insertedHashes.add(l._hash));

    if (newLeads.length === 0) {
      logger.info(`[${tabName}] All ${skipped} leads already exist — skipped`);
      continue;
    }

    const rows = newLeads.map(leadToRow);
    // Batch in chunks of 100
    for (let i = 0; i < rows.length; i += 100) {
      const chunk = rows.slice(i, i + 100);
      await sheets.spreadsheets.values.append({
        spreadsheetId: config.googleSheetsId,
        range: `'${tabName}'!A1`,
        valueInputOption: 'RAW',
        insertDataOption: 'INSERT_ROWS',
        requestBody: { values: chunk },
      });
    }

    logger.info(`[${tabName}] Inserted ${newLeads.length} leads, skipped ${skipped} duplicates`);
    await applyConditionalFormatting(sheets, tabName);
  }

  return { inserted: insertedHashes.size, skipped: skippedHashes.size };
}

async function applyConditionalFormatting(sheets, tabName) {
  try {
    const meta = await sheets.spreadsheets.get({ spreadsheetId: config.googleSheetsId });
    const sheet = meta.data.sheets.find((s) => s.properties.title === tabName);
    if (!sheet) return;
    const sheetId = sheet.properties.sheetId;
    const classColIndex = HEADERS.indexOf('Classification'); // column J = index 9

    await sheets.spreadsheets.batchUpdate({
      spreadsheetId: config.googleSheetsId,
      requestBody: {
        requests: [
          makeConditionalRule(sheetId, classColIndex, 'Hot', HOT_GREEN),
          makeConditionalRule(sheetId, classColIndex, 'Warm', WARM_YELLOW),
          makeConditionalRule(sheetId, classColIndex, 'Cold', COLD_BLUE),
        ],
      },
    });
  } catch (err) {
    logger.warn(`Conditional formatting skipped for ${tabName}: ${err.message}`);
  }
}

function makeConditionalRule(sheetId, colIndex, value, color) {
  return {
    addConditionalFormatRule: {
      rule: {
        ranges: [{ sheetId, startRowIndex: 1, startColumnIndex: 0, endColumnIndex: HEADERS.length }],
        booleanRule: {
          condition: {
            type: 'TEXT_EQ',
            values: [{ userEnteredValue: value }],
          },
          format: {
            backgroundColor: color,
          },
        },
      },
      index: 0,
    },
  };
}

module.exports = {
  ensureAllTabs,
  insertLeads,
  deduplicationHash,
  TABS,
  NICHE_TAB_MAP,
};
