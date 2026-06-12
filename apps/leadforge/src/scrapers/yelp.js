const axios = require('axios');
const cheerio = require('cheerio');
const logger = require('../utils/logger');
const config = require('../config/env');

// Rotate user agents to reduce blocking
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
];

function getRandomUA() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

const YELP_NICHE_MAP = {
  // Med Spas
  'med spa': 'medspas',
  'medspa': 'medspas',
  'medical spa': 'medspas',
  // Roofing
  'roofing': 'roofing',
  'roofing company': 'roofing',
  // Aesthetic Clinics
  'aesthetic clinic': 'skincare',
  'aesthetic clinics': 'skincare',
  'aesthetics': 'skincare',
  // Dental
  'dental clinic': 'dentists',
  'dental clinics': 'dentists',
  'dentist': 'dentists',
  'dental': 'dentists',
  // Realtors
  'realtor': 'realestate',
  'realtors': 'realestate',
  'real estate': 'realestate',
  'real estate agent': 'realestate',
  // Law Firms
  'law firm': 'lawyers',
  'law firms': 'lawyers',
  'attorney': 'lawyers',
  'lawyer': 'lawyers',
  // Insurance
  'insurance agency': 'insuranceagents',
  'insurance agencies': 'insuranceagents',
  'insurance': 'insuranceagents',
  // Gyms
  'gym': 'gyms',
  'gyms': 'gyms',
  'fitness center': 'gyms',
  'fitness': 'gyms',
  // Car Dealerships
  'car dealership': 'usedcar',
  'car dealerships': 'usedcar',
  'auto dealership': 'usedcar',
  'car dealer': 'usedcar',
  // HVAC
  'hvac': 'hvac',
  'hvac company': 'hvac',
  'hvac companies': 'hvac',
  'heating and cooling': 'hvac',
  // Travel
  'travel agency': 'travelagents',
  'travel agencies': 'travelagents',
  'travel agent': 'travelagents',
  'travel': 'travelagents',
};

/**
 * Scrape Yelp search results for a niche + location.
 * Returns array of partial lead objects.
 */
async function scrapeYelp(niche, location, limit = 20) {
  const category = YELP_NICHE_MAP[niche.toLowerCase()] || niche.toLowerCase().replace(/\s+/g, '');
  const locationEncoded = encodeURIComponent(location);
  const results = [];

  let start = 0;
  while (results.length < limit) {
    const url = `https://www.yelp.com/search?find_desc=${category}&find_loc=${locationEncoded}&start=${start}`;
    try {
      logger.info(`[Yelp] Scraping: ${url}`);
      const res = await axios.get(url, {
        headers: {
          'User-Agent': getRandomUA(),
          'Accept': 'text/html,application/xhtml+xml',
          'Accept-Language': 'en-US,en;q=0.9',
        },
        timeout: 15000,
      });

      const $ = cheerio.load(res.data);
      const listings = parseYelpResults($);

      if (listings.length === 0) break;
      results.push(...listings);
      start += 10;

      await new Promise((r) => setTimeout(r, config.requestDelayMs + Math.random() * 500));
    } catch (err) {
      logger.warn(`[Yelp] Failed to scrape (may be blocked): ${err.message}`);
      break;
    }
  }

  logger.info(`[Yelp] Found ${results.length} listings for "${niche}" in "${location}"`);
  return results.slice(0, limit);
}

function parseYelpResults($) {
  const results = [];

  // Yelp uses data embedded in JSON script tags + HTML fallback
  $('script[type="application/ld+json"]').each((_, el) => {
    try {
      const data = JSON.parse($(el).html());
      if (Array.isArray(data)) {
        data.forEach((item) => {
          if (item['@type'] === 'LocalBusiness' && item.name) {
            results.push(parseJsonLd(item));
          }
        });
      } else if (data['@type'] === 'LocalBusiness' && data.name) {
        results.push(parseJsonLd(data));
      }
    } catch {}
  });

  // Fallback: scrape HTML list items if JSON LD not found
  if (results.length === 0) {
    $('[data-testid="serp-ia-card"], .businessName__09f24__HG_pC, h3 a[href*="/biz/"]').each((_, el) => {
      const name = $(el).text().trim();
      const href = $(el).attr('href');
      if (name && href) {
        results.push({
          businessName: name,
          yelpUrl: href.startsWith('http') ? href : `https://www.yelp.com${href}`,
          source: 'yelp',
        });
      }
    });
  }

  return results;
}

function parseJsonLd(item) {
  return {
    businessName: item.name || '',
    address: formatAddress(item.address),
    phone: item.telephone || '',
    website: item.url || '',
    rating: item.aggregateRating?.ratingValue || null,
    reviewCount: item.aggregateRating?.reviewCount || 0,
    yelpUrl: item['@id'] || '',
    source: 'yelp',
  };
}

function formatAddress(addr) {
  if (!addr) return '';
  if (typeof addr === 'string') return addr;
  const parts = [addr.streetAddress, addr.addressLocality, addr.addressRegion, addr.postalCode];
  return parts.filter(Boolean).join(', ');
}

module.exports = { scrapeYelp };
