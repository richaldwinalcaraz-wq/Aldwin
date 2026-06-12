/**
 * Detect website tech stack, CMS, booking tools, and chat widgets
 * from raw HTML + URL signals.
 */

const DETECTORS = {
  // CMS / Builders
  wordpress: [/wp-content\//, /wp-includes\//, /\/xmlrpc\.php/],
  wix: [/wix\.com/, /wixsite\.com/, /_wix_/],
  squarespace: [/squarespace\.com/, /static1\.squarespace/, /squarespace-cdn/],
  webflow: [/webflow\.com/, /\.webflow\.io/],
  shopify: [/shopify\.com/, /cdn\.shopify/, /Shopify\.theme/],
  weebly: [/weebly\.com/, /editmysite\.com/],
  godaddy: [/godaddy\.com/, /secureserver\.net/],

  // Booking systems
  calendly: [/calendly\.com/, /assets\.calendly/],
  acuity: [/acuityscheduling\.com/, /squareup\.com\/appointments/],
  vagaro: [/vagaro\.com/],
  booksy: [/booksy\.com/],
  mindbody: [/mindbodyonline\.com/, /mindbody\.io/],
  jane: [/jane\.app/],
  boulevard: [/boulevard\.io/, /joinblvd\.com/],

  // Chat widgets
  tidio: [/tidiochat\.com/, /tidio\.co/],
  intercom: [/intercom\.io/, /widget\.intercom\.io/],
  drift: [/drift\.com/, /js\.driftt\.com/],
  hubspot_chat: [/hubspot\.com\/messenger/, /js\.hs-scripts/],
  zendesk: [/zopim\.com/, /zendesk\.com\/embeddable/],
  freshchat: [/freshchat\.com/, /wchat\.freshchat/],
  tawk: [/tawk\.to/],
  crisp: [/crisp\.chat/],

  // Analytics / presence signals
  google_analytics: [/google-analytics\.com\/analytics\.js/, /gtag\/js/],
  facebook_pixel: [/connect\.facebook\.net\/.*\/fbevents/],
  hotjar: [/hotjar\.com/],
};

function detectTech(html, url) {
  const detected = {};
  const combined = `${html} ${url}`.toLowerCase();

  for (const [tech, patterns] of Object.entries(DETECTORS)) {
    detected[tech] = patterns.some((p) => p.test(combined));
  }

  return detected;
}

function hasChatWidget(techStack) {
  const chatTools = ['tidio', 'intercom', 'drift', 'hubspot_chat', 'zendesk', 'freshchat', 'tawk', 'crisp'];
  return chatTools.some((t) => techStack[t]);
}

function hasBookingSystem(techStack) {
  const bookingTools = ['calendly', 'acuity', 'vagaro', 'booksy', 'mindbody', 'jane', 'boulevard'];
  return bookingTools.some((t) => techStack[t]);
}

function getCmsName(techStack) {
  const cmsList = ['wordpress', 'wix', 'squarespace', 'webflow', 'shopify', 'weebly', 'godaddy'];
  for (const cms of cmsList) {
    if (techStack[cms]) return cms;
  }
  return 'custom';
}

module.exports = { detectTech, hasChatWidget, hasBookingSystem, getCmsName };
