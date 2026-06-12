/**
 * Heuristic lead scoring engine.
 * Score = review signal + rating signal + website quality + social presence + opportunity gaps.
 * Range: 0–100. Higher = more valuable lead for AI services.
 */

function scoreReviews(reviewCount) {
  if (reviewCount >= 100) return 25;
  if (reviewCount >= 50) return 18;
  if (reviewCount >= 10) return 10;
  return 3;
}

function scoreRating(rating) {
  if (!rating) return 0;
  if (rating >= 4.5) return 20;
  if (rating >= 4.0) return 15;
  if (rating >= 3.0) return 8;
  return 2;
}

function scoreWebsite(lead) {
  if (!lead.website || !lead.websiteReachable) return 0;
  if (lead.hasHttps && lead.websiteLoadTime && lead.websiteLoadTime < 2000) return 20;
  if (lead.hasHttps) return 12;
  return 5;
}

function scoreSocial(socialLinks) {
  const count = (socialLinks || []).length;
  if (count >= 3) return 15;
  if (count >= 1) return 8;
  return 0;
}

/**
 * Opportunity gaps boost the score — more gaps = more AI services to sell.
 */
function scoreOpportunityGaps(gaps) {
  const gapWeights = {
    'No online booking': 10,
    'No chatbot / live chat': 8,
    'No contact form': 6,
    'Not mobile optimized': 5,
    'No HTTPS': 4,
    'Slow website': 5,
    'Low-SEO CMS': 5,
    'No public email': 8,
    'No social media': 4,
    'Fewer than 10 reviews': 3,
  };

  return (gaps || []).reduce((sum, gap) => {
    const key = Object.keys(gapWeights).find((k) => gap.toLowerCase().includes(k.toLowerCase()));
    return sum + (key ? gapWeights[key] : 2);
  }, 0);
}

function classify(score) {
  if (score >= 75) return 'Hot';
  if (score >= 45) return 'Warm';
  return 'Cold';
}

function getWebsiteQuality(lead) {
  if (!lead.website || !lead.websiteReachable) return 'None';
  if (lead.hasHttps && lead.hasMobileViewport && lead.websiteLoadTime < 2000) return 'Good';
  if (lead.hasHttps || lead.hasMobileViewport) return 'Fair';
  return 'Poor';
}

/**
 * Score a single lead. Returns lead with score, classification, and quality fields.
 */
function scoreLead(lead) {
  const reviewScore = scoreReviews(lead.reviewCount || 0);
  const ratingScore = scoreRating(lead.rating);
  const websiteScore = scoreWebsite(lead);
  const socialScore = scoreSocial(lead.socialLinks);
  const gapScore = scoreOpportunityGaps(lead.detectedGaps || []);

  // Cap base score at 80, then gaps can push to 100
  const baseScore = reviewScore + ratingScore + websiteScore + socialScore;
  const totalScore = Math.min(baseScore + gapScore, 100);

  return {
    ...lead,
    leadScore: totalScore,
    classification: classify(totalScore),
    websiteQuality: getWebsiteQuality(lead),
    dateScraped: lead.dateScraped || new Date().toISOString().split('T')[0],
  };
}

module.exports = { scoreLead };
