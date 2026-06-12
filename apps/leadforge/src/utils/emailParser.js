const EMAIL_REGEX = /[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}/g;

function extractEmails(text) {
  if (!text) return [];
  const matches = text.match(EMAIL_REGEX) || [];
  // Deduplicate, lowercase
  return [...new Set(matches.map((e) => e.toLowerCase()))];
}

module.exports = { extractEmails };
