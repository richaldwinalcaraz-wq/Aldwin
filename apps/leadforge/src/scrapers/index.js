const pLimit = require('p-limit');
const { searchBusinesses } = require('./serper');
const { lookupBusiness } = require('./googlePlaces');
const { scrapeWebsite } = require('./website');
const { mergeLeads, estimateCompanySize } = require('../services/enricher');
const { detectOpportunities } = require('../services/opportunityDetector');
const { scoreLead } = require('../services/scorer');
const { insertLeads } = require('../services/sheets');
const { addLead } = require('../services/leadStore');
const { deduplicateLeads } = require('../utils/deduplication');
const progress = require('../services/progressEmitter');
const logger = require('../utils/logger');
const config = require('../config/env');

function emit(type, data) {
  progress.emit('event', { type, ...data });
}

async function runScrape({ niche, location, limit = 20 }) {
  logger.info(`[Scrape] Starting: niche="${niche}" location="${location}" limit=${limit}`);
  emit('status', { message: `Starting scrape: ${niche} in ${location}` });

  // Step 1: Search
  emit('status', { message: `Searching for ${niche} businesses in ${location}...` });
  const serperResults = await searchBusinesses(niche, location, limit);
  emit('status', { message: `Found ${serperResults.length} businesses from search` });

  if (serperResults.length === 0) {
    emit('error', { message: 'No results from search. Check Serper API key and quota.' });
    return { total: 0, inserted: 0, skipped: 0, hot: 0, warm: 0, cold: 0, leads: [] };
  }

  // Step 2: Enrich each business
  const limiter = pLimit(config.concurrencyLimit);
  let processed = 0;

  const enriched = await Promise.all(
    serperResults.map((serperResult) =>
      limiter(async () => {
        const result = await enrichBusiness(serperResult, niche, location);
        processed++;
        emit('progress', {
          current: processed,
          total: serperResults.length,
          business: result.businessName || serperResult.businessName,
          rating: result.rating,
          reviewCount: result.reviewCount,
          email: result.email ? true : false,
        });
        return result;
      })
    )
  );

  // Step 3: Score and classify
  emit('status', { message: 'Scoring and classifying leads...' });
  const scored = enriched.map((lead) => {
    const { gaps, aiOpportunityScore } = detectOpportunities(lead);
    return scoreLead({
      ...lead,
      detectedGaps: gaps,
      aiOpportunityScore,
      niche: normalizeNiche(niche),
      location,
      companySize: estimateCompanySize(lead),
    });
  });

  // Step 4: Deduplicate
  const unique = deduplicateLeads(scored);
  emit('status', { message: `${unique.length} unique leads after deduplication` });

  // Step 5: Store in memory + push to Sheets
  unique.forEach((lead) => addLead(lead));

  emit('status', { message: 'Saving to Google Sheets...' });
  const { inserted, skipped } = await insertLeads(unique);

  const hot = unique.filter((l) => l.classification === 'Hot').length;
  const warm = unique.filter((l) => l.classification === 'Warm').length;
  const cold = unique.filter((l) => l.classification === 'Cold').length;

  const summary = { total: unique.length, inserted, skipped, hot, warm, cold };
  emit('done', { ...summary, leads: unique });

  return { ...summary, leads: unique };
}

async function enrichBusiness(serperResult, niche, location) {
  const { businessName, website } = serperResult;
  const [placesData, websiteData] = await Promise.all([
    lookupBusiness(businessName, location).catch(() => null),
    website ? scrapeWebsite(website).catch(() => ({})) : Promise.resolve({}),
  ]);
  const merged = mergeLeads(serperResult, placesData, null, websiteData);
  logger.info(`[Enrich] ${merged.businessName || businessName} — rating:${merged.rating} reviews:${merged.reviewCount} email:${merged.email ? 'found' : 'none'}`);
  return merged;
}

function normalizeNiche(niche) {
  const n = niche.toLowerCase();
  if (n.includes('med spa') || n.includes('medspa')) return 'Med Spa';
  if (n.includes('roof')) return 'Roofing';
  if (n.includes('aesthetic')) return 'Aesthetic Clinic';
  if (n.includes('dental') || n.includes('dentist')) return 'Dental Clinic';
  if (n.includes('realtor') || n.includes('real estate')) return 'Realtor';
  if (n.includes('law') || n.includes('attorney') || n.includes('lawyer')) return 'Law Firm';
  if (n.includes('insurance')) return 'Insurance Agency';
  if (n.includes('gym') || n.includes('fitness')) return 'Gym';
  if (n.includes('car') || n.includes('auto') || n.includes('dealer')) return 'Car Dealership';
  if (n.includes('hvac') || n.includes('heating') || n.includes('cooling')) return 'HVAC Company';
  if (n.includes('travel')) return 'Travel Agency';
  return niche;
}

module.exports = { runScrape };
