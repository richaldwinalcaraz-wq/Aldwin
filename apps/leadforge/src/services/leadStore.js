// In-memory lead store — persists for the lifetime of the server process.
// Source of truth is Google Sheets; this enables fast API queries without re-fetching Sheets.

const leads = [];
const seenHashes = new Set();

function addLead(lead) {
  if (!lead._hash || seenHashes.has(lead._hash)) return false;
  seenHashes.add(lead._hash);
  leads.push(lead);
  return true;
}

function getLeads({ niche, classification, minScore } = {}) {
  let result = [...leads];
  if (niche) result = result.filter((l) => (l.niche || '').toLowerCase().includes(niche.toLowerCase()));
  if (classification) result = result.filter((l) => (l.classification || '').toLowerCase() === classification.toLowerCase());
  if (minScore != null) result = result.filter((l) => (l.leadScore || 0) >= Number(minScore));
  return result;
}

function getStats() {
  return {
    total: leads.length,
    hot: leads.filter((l) => l.classification === 'Hot').length,
    warm: leads.filter((l) => l.classification === 'Warm').length,
    cold: leads.filter((l) => l.classification === 'Cold').length,
    byNiche: leads.reduce((acc, l) => {
      const n = l.niche || 'Unknown';
      acc[n] = (acc[n] || 0) + 1;
      return acc;
    }, {}),
  };
}

function clearLeads() {
  leads.length = 0;
  seenHashes.clear();
}

module.exports = { addLead, getLeads, getStats, clearLeads };
