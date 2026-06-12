const crypto = require('crypto');

function extractDomain(url) {
  try {
    const u = new URL(url.startsWith('http') ? url : `https://${url}`);
    return u.hostname.replace('www.', '').toLowerCase();
  } catch {
    return (url || '').toLowerCase().trim();
  }
}

function buildHash(businessName, website, phone) {
  const name = (businessName || '').toLowerCase().trim();
  const domain = extractDomain(website || '');
  const digits = (phone || '').replace(/\D/g, '');
  return crypto.createHash('sha256').update(`${name}|${domain}|${digits}`).digest('hex').slice(0, 16);
}

function deduplicateLeads(leads) {
  const seen = new Set();
  return leads.filter((lead) => {
    const hash = buildHash(lead.businessName, lead.website, lead.phone);
    if (seen.has(hash)) return false;
    seen.add(hash);
    lead._hash = hash;
    return true;
  });
}

module.exports = { buildHash, deduplicateLeads, extractDomain };
