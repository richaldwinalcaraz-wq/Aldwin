const { hasChatWidget, hasBookingSystem, getCmsName } = require('../utils/techDetector');

/**
 * Detect AI automation opportunity gaps in a business.
 * Returns array of gap strings + an opportunity score (0–100).
 */
function detectOpportunities(lead) {
  const gaps = [];
  const tech = lead.techStack || {};

  // No website at all
  if (!lead.website || !lead.websiteReachable) {
    gaps.push('No website');
  }

  // No booking system
  if (lead.websiteReachable && !hasBookingSystem(tech)) {
    gaps.push('No online booking');
  }

  // No chat widget
  if (lead.websiteReachable && !hasChatWidget(tech)) {
    gaps.push('No chatbot / live chat');
  }

  // No contact form
  if (lead.websiteReachable && !lead.hasContactForm) {
    gaps.push('No contact form');
  }

  // Website not HTTPS
  if (lead.website && !lead.hasHttps) {
    gaps.push('No HTTPS');
  }

  // Mobile unfriendly
  if (lead.websiteReachable && !lead.hasMobileViewport) {
    gaps.push('Not mobile optimized');
  }

  // Slow website
  if (lead.websiteLoadTime && lead.websiteLoadTime > 4000) {
    gaps.push('Slow website (>4s load)');
  }

  // Using cheap/bad-SEO CMS
  const cms = getCmsName(tech);
  if (['wix', 'weebly', 'godaddy'].includes(cms)) {
    gaps.push(`Low-SEO CMS (${cms})`);
  }

  // No social media presence
  const socialCount = (lead.socialLinks || []).length;
  if (socialCount === 0) {
    gaps.push('No social media');
  }

  // Weak review count
  if ((lead.reviewCount || 0) < 10) {
    gaps.push('Fewer than 10 reviews (needs reputation management)');
  }

  // No email found (hard to contact = opportunity to setup CRM)
  if (!lead.email) {
    gaps.push('No public email (CRM/lead capture gap)');
  }

  const aiOpportunityScore = calculateOpportunityScore(gaps);

  return { gaps, aiOpportunityScore };
}

function calculateOpportunityScore(gaps) {
  const weights = {
    'No website': 30,
    'No online booking': 20,
    'No chatbot / live chat': 15,
    'No contact form': 10,
    'No HTTPS': 8,
    'Not mobile optimized': 10,
    'Slow website (>4s load)': 8,
    'No social media': 8,
    'Fewer than 10 reviews (needs reputation management)': 5,
    'No public email (CRM/lead capture gap)': 8,
  };

  let score = gaps.reduce((sum, gap) => {
    // Partial match for dynamic labels like "Low-SEO CMS (wix)"
    const key = Object.keys(weights).find((k) => gap.startsWith(k.split('(')[0].trim()));
    return sum + (key ? weights[key] : 5);
  }, 0);

  return Math.min(score, 100);
}

module.exports = { detectOpportunities };
