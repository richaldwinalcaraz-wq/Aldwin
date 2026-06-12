const axios = require('axios');
const logger = require('../utils/logger');
const config = require('../config/env');

const SERPER_URL = 'https://google.serper.dev/search';

// Cache search results to disk to preserve Serper quota
const fs = require('fs');
const path = require('path');
const CACHE_DIR = path.join(__dirname, '../../.tmp/serper_cache');

function getCacheKey(niche, location) {
  return Buffer.from(`${niche}|${location}`).toString('base64').replace(/[/+=]/g, '_');
}

function readCache(key) {
  try {
    const file = path.join(CACHE_DIR, `${key}.json`);
    if (fs.existsSync(file)) {
      const data = JSON.parse(fs.readFileSync(file, 'utf8'));
      // Cache valid for 24 hours
      if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
        return data.results;
      }
    }
  } catch {}
  return null;
}

function writeCache(key, results) {
  try {
    if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR, { recursive: true });
    fs.writeFileSync(
      path.join(CACHE_DIR, `${key}.json`),
      JSON.stringify({ timestamp: Date.now(), results })
    );
  } catch {}
}

/**
 * Search for businesses using Serper.dev Google search API.
 * Returns array of { businessName, website, snippet } objects.
 */
async function searchBusinesses(niche, location, limit = 20) {
  const cacheKey = getCacheKey(niche, location);
  const cached = readCache(cacheKey);
  if (cached) {
    logger.info(`[Serper] Cache hit for "${niche}" in "${location}"`);
    return cached.slice(0, limit);
  }

  const results = [];
  const queries = buildQueries(niche, location);

  for (const query of queries) {
    if (results.length >= limit) break;
    try {
      logger.info(`[Serper] Searching: "${query}"`);
      // Request enough results per query to fill the limit (Serper max: 100)
      const numPerQuery = Math.min(Math.ceil(limit * 1.5 / queries.length), 100);
      const res = await axios.post(
        SERPER_URL,
        { q: query, num: numPerQuery, gl: 'us' },
        {
          headers: {
            'X-API-KEY': config.serperApiKey,
            'Content-Type': 'application/json',
          },
          timeout: 10000,
        }
      );

      const organic = res.data.organic || [];
      for (const item of organic) {
        if (results.length >= limit * 2) break; // fetch extra for dedup
        // Filter out directories, Yelp listings, Google My Business — we scrape those separately
        if (isBusinessWebsite(item.link)) {
          results.push({
            businessName: cleanBusinessName(item.title, niche),
            website: normalizeUrl(item.link),
            snippet: item.snippet || '',
          });
        }
      }

      // Also check knowledgeGraph and localResults
      if (res.data.knowledgeGraph?.title) {
        results.unshift({
          businessName: res.data.knowledgeGraph.title,
          website: res.data.knowledgeGraph.website || '',
          snippet: res.data.knowledgeGraph.description || '',
        });
      }

    } catch (err) {
      logger.error(`[Serper] Search failed for "${query}": ${err.message}`);
    }
  }

  // Deduplicate by website domain
  const seen = new Set();
  const unique = results.filter((r) => {
    const domain = extractDomain(r.website);
    if (!domain || seen.has(domain)) return false;
    seen.add(domain);
    return true;
  });

  writeCache(cacheKey, unique);
  logger.info(`[Serper] Found ${unique.length} unique businesses for "${niche}" in "${location}"`);
  return unique.slice(0, limit);
}

function buildQueries(niche, location) {
  const nicheTerms = getNicheTerms(niche);
  return nicheTerms.map((term) => `${term} in ${location}`);
}

function getNicheTerms(niche) {
  const n = niche.toLowerCase();
  if (n.includes('med spa') || n.includes('medspa')) return ['med spa', 'medical spa', 'medspa'];
  if (n.includes('roof')) return ['roofing company', 'roofing contractor', 'roof repair'];
  if (n.includes('aesthetic')) return ['aesthetic clinic', 'aesthetics clinic', 'cosmetic clinic'];
  if (n.includes('dental') || n.includes('dentist')) return ['dental clinic', 'dentist', 'dental office'];
  if (n.includes('realtor') || n.includes('real estate')) return ['realtor', 'real estate agent', 'real estate agency'];
  if (n.includes('law') || n.includes('attorney') || n.includes('lawyer')) return ['law firm', 'attorney office', 'legal services'];
  if (n.includes('insurance')) return ['insurance agency', 'insurance agent', 'insurance company'];
  if (n.includes('gym') || n.includes('fitness')) return ['gym', 'fitness center', 'health club'];
  if (n.includes('car') || n.includes('auto') || n.includes('dealer')) return ['car dealership', 'auto dealership', 'car dealer'];
  if (n.includes('hvac') || n.includes('heating') || n.includes('cooling')) return ['HVAC company', 'HVAC contractor', 'heating and cooling'];
  if (n.includes('travel')) return ['travel agency', 'travel agent', 'travel company'];
  return [niche];
}

function isBusinessWebsite(url) {
  if (!url) return false;
  const blocked = ['yelp.com', 'google.com', 'facebook.com', 'instagram.com',
    'linkedin.com', 'yellowpages.com', 'bbb.org', 'angi.com',
    'thumbtack.com', 'houzz.com', 'bark.com', 'angieslist.com'];
  return !blocked.some((b) => url.includes(b));
}

function cleanBusinessName(title, niche) {
  // Remove " - Yelp", " | Google Maps", etc.
  return title.replace(/\s*[-|–]\s*(yelp|google|maps|facebook|instagram|linkedin|yellowpages).*/i, '').trim();
}

function normalizeUrl(url) {
  try {
    const u = new URL(url);
    return `${u.protocol}//${u.hostname}`;
  } catch {
    return url;
  }
}

function extractDomain(url) {
  try {
    const u = new URL(url.startsWith('http') ? url : `https://${url}`);
    return u.hostname.replace('www.', '');
  } catch {
    return url;
  }
}

module.exports = { searchBusinesses };
