const axios = require('axios');
const cheerio = require('cheerio');
const { extractEmails } = require('../utils/emailParser');
const { detectTech } = require('../utils/techDetector');
const logger = require('../utils/logger');

const CONTACT_PATH_HINTS = ['/contact', '/contact-us', '/about', '/about-us', '/reach-us', '/get-in-touch'];

const SOCIAL_PATTERNS = {
  facebook: /facebook\.com\/[a-zA-Z0-9._-]+/i,
  instagram: /instagram\.com\/[a-zA-Z0-9._-]+/i,
  twitter: /(?:twitter|x)\.com\/[a-zA-Z0-9._-]+/i,
  linkedin: /linkedin\.com\/(?:company|in)\/[a-zA-Z0-9._-]+/i,
  youtube: /youtube\.com\/@?[a-zA-Z0-9._-]+/i,
  tiktok: /tiktok\.com\/@[a-zA-Z0-9._-]+/i,
};

/**
 * Scrape a business website for contact info, social links, and tech signals.
 */
async function scrapeWebsite(websiteUrl) {
  if (!websiteUrl) return {};

  const baseUrl = normalizeUrl(websiteUrl);
  const result = {
    email: '',
    phone: '',
    socialLinks: [],
    techStack: {},
    websiteReachable: false,
    websiteLoadTime: null,
    hasHttps: baseUrl.startsWith('https'),
    hasMobileViewport: false,
    hasContactForm: false,
    source: 'website',
  };

  try {
    const start = Date.now();
    const html = await fetchPage(baseUrl);
    result.websiteLoadTime = Date.now() - start;
    result.websiteReachable = true;

    const $ = cheerio.load(html);
    extractContactInfo($, html, result);
    extractSocialLinks($, html, result);
    result.hasMobileViewport = hasMobileViewport($);
    result.hasContactForm = hasContactForm($);
    result.techStack = detectTech(html, baseUrl);

    // Try contact page if no email found
    if (!result.email) {
      for (const path of CONTACT_PATH_HINTS) {
        try {
          const contactHtml = await fetchPage(`${baseUrl}${path}`);
          const $c = cheerio.load(contactHtml);
          const emails = extractEmails(contactHtml);
          if (emails.length > 0) {
            result.email = emails[0];
            break;
          }
          extractContactInfo($c, contactHtml, result);
          if (result.email) break;
        } catch {}
      }
    }

  } catch (err) {
    logger.warn(`[Website] Failed to scrape ${baseUrl}: ${err.message}`);
  }

  return result;
}

async function fetchPage(url) {
  const res = await axios.get(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept': 'text/html',
    },
    timeout: 8000,
    maxRedirects: 3,
  });
  return res.data;
}

function extractContactInfo($, html, result) {
  // Emails
  const emails = extractEmails(html);
  // Filter out common false positives
  const validEmails = emails.filter((e) => !e.match(/example\.|@sentry|@w3\.|noreply@|no-reply@/i));
  if (validEmails.length > 0 && !result.email) result.email = validEmails[0];

  // Phone: look for tel: links first, then regex
  const telLink = $('a[href^="tel:"]').first().attr('href');
  if (telLink && !result.phone) {
    result.phone = telLink.replace('tel:', '').trim();
  }
  if (!result.phone) {
    const phoneMatch = html.match(/\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/);
    if (phoneMatch) result.phone = phoneMatch[0];
  }
}

function extractSocialLinks($, html, result) {
  const found = new Set();
  $('a[href]').each((_, el) => {
    const href = $(el).attr('href') || '';
    for (const [platform, pattern] of Object.entries(SOCIAL_PATTERNS)) {
      if (pattern.test(href)) {
        const match = href.match(pattern);
        if (match) found.add(`${platform}:https://www.${match[0]}`);
      }
    }
  });
  result.socialLinks = Array.from(found);
}

function hasMobileViewport($) {
  const viewport = $('meta[name="viewport"]').attr('content') || '';
  return viewport.includes('width=device-width');
}

function hasContactForm($) {
  return $('form').length > 0 && (
    $('input[type="email"]').length > 0 ||
    $('input[name*="email"]').length > 0 ||
    $('textarea').length > 0
  );
}

function normalizeUrl(url) {
  if (!url) return '';
  if (!url.startsWith('http')) return `https://${url}`;
  return url.replace(/\/$/, '');
}

module.exports = { scrapeWebsite };
