const axios = require('axios');
const logger = require('../utils/logger');
const config = require('../config/env');

const PLACES_TEXT_SEARCH = 'https://maps.googleapis.com/maps/api/place/textsearch/json';
const PLACES_DETAILS = 'https://maps.googleapis.com/maps/api/place/details/json';

const DETAIL_FIELDS = [
  'name', 'formatted_address', 'formatted_phone_number',
  'website', 'rating', 'user_ratings_total',
  'url', 'business_status', 'types', 'opening_hours',
].join(',');

async function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

/**
 * Search businesses via Google Places Text Search API.
 * Returns enriched lead data for each result.
 */
async function searchPlaces(niche, location, limit = 20) {
  const query = `${niche} in ${location}`;
  const results = [];

  try {
    logger.info(`[Places] Text search: "${query}"`);
    let nextPageToken = null;

    do {
      const params = {
        query,
        key: config.googlePlacesApiKey,
        ...(nextPageToken ? { pagetoken: nextPageToken } : {}),
      };

      const res = await axios.get(PLACES_TEXT_SEARCH, { params, timeout: 10000 });

      if (res.data.status === 'REQUEST_DENIED') {
        logger.error(`[Places] API key rejected: ${res.data.error_message}`);
        break;
      }

      for (const place of res.data.results || []) {
        if (results.length >= limit) break;
        const detail = await getPlaceDetail(place.place_id);
        if (detail) results.push(detail);
        await delay(config.requestDelayMs);
      }

      nextPageToken = res.data.next_page_token || null;
      if (nextPageToken) await delay(2000); // Google requires delay before using next page token

    } while (nextPageToken && results.length < limit);

  } catch (err) {
    logger.error(`[Places] Search failed: ${err.message}`);
  }

  logger.info(`[Places] Got ${results.length} places for "${query}"`);
  return results;
}

async function getPlaceDetail(placeId) {
  try {
    const res = await axios.get(PLACES_DETAILS, {
      params: { place_id: placeId, fields: DETAIL_FIELDS, key: config.googlePlacesApiKey },
      timeout: 10000,
    });

    if (res.data.status !== 'OK') return null;
    const p = res.data.result;

    // Skip permanently closed businesses
    if (p.business_status === 'CLOSED_PERMANENTLY') {
      logger.info(`[Places] Skipped permanently closed: ${p.name}`);
      return null;
    }

    return {
      businessName: p.name || '',
      address: p.formatted_address || '',
      phone: p.formatted_phone_number || '',
      website: p.website || '',
      rating: p.rating || null,
      reviewCount: p.user_ratings_total || 0,
      mapsUrl: p.url || `https://www.google.com/maps/place/?q=place_id:${placeId}`,
      businessStatus: p.business_status || '',
      placeId,
      source: 'google_places',
    };
  } catch (err) {
    logger.warn(`[Places] Detail fetch failed for ${placeId}: ${err.message}`);
    return null;
  }
}

/**
 * Lookup a single business by name + location.
 * Used to enrich businesses found via Serper.
 */
async function lookupBusiness(businessName, location) {
  try {
    const res = await axios.get(PLACES_TEXT_SEARCH, {
      params: {
        query: `${businessName} ${location}`,
        key: config.googlePlacesApiKey,
      },
      timeout: 10000,
    });

    if (res.data.status !== 'OK' || !res.data.results?.length) return null;
    const placeId = res.data.results[0].place_id;
    await delay(config.requestDelayMs);
    return getPlaceDetail(placeId);
  } catch (err) {
    logger.warn(`[Places] Lookup failed for "${businessName}": ${err.message}`);
    return null;
  }
}

module.exports = { searchPlaces, lookupBusiness };
