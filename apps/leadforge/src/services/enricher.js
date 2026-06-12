/**
 * Merges data from Google Places, Yelp, and website scrapers.
 * Priority: Google Places > Yelp > Website
 */

function mergeLeads(serperResult, placesData, yelpData, websiteData) {
  const merged = { ...serperResult };

  // Business name: prefer Places > Yelp > Serper
  merged.businessName = placesData?.businessName || yelpData?.businessName || serperResult?.businessName || '';

  // Address: Places > Yelp
  merged.address = placesData?.address || yelpData?.address || '';

  // Phone: Places > Website > Yelp
  merged.phone = placesData?.phone || websiteData?.phone || yelpData?.phone || '';

  // Website: Places > Yelp > Serper
  merged.website = placesData?.website || yelpData?.website || serperResult?.website || '';

  // Ratings: Places is authoritative; supplement with Yelp
  merged.rating = placesData?.rating || yelpData?.rating || null;
  merged.reviewCount = placesData?.reviewCount || yelpData?.reviewCount || 0;

  // Maps URL: always from Places
  merged.mapsUrl = placesData?.mapsUrl || '';

  // Email: website is primary source
  merged.email = websiteData?.email || '';

  // Social links: from website
  merged.socialLinks = websiteData?.socialLinks || [];

  // Tech + website signals
  merged.websiteReachable = websiteData?.websiteReachable || false;
  merged.websiteLoadTime = websiteData?.websiteLoadTime || null;
  merged.hasHttps = websiteData?.hasHttps || merged.website?.startsWith('https') || false;
  merged.hasMobileViewport = websiteData?.hasMobileViewport || false;
  merged.hasContactForm = websiteData?.hasContactForm || false;
  merged.techStack = websiteData?.techStack || {};

  // Yelp URL as additional reference
  merged.yelpUrl = yelpData?.yelpUrl || '';

  // Source tracking
  merged.sources = [
    serperResult ? 'serper' : null,
    placesData ? 'google_places' : null,
    yelpData ? 'yelp' : null,
    websiteData?.websiteReachable ? 'website' : null,
  ].filter(Boolean);

  return merged;
}

/**
 * Estimate company size from review count + website signals.
 */
function estimateCompanySize(lead) {
  const reviews = lead.reviewCount || 0;
  if (reviews > 500) return 'Large';
  if (reviews > 100) return 'Medium';
  if (reviews > 20) return 'Small';
  return 'Solo/Micro';
}

module.exports = { mergeLeads, estimateCompanySize };
