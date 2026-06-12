require('dotenv').config({ path: require('path').join(__dirname, '../../.env') });

const REQUIRED = [
  'SERPER_API_KEY',
  'GOOGLE_SHEETS_ID',
  'GOOGLE_SERVICE_ACCOUNT_EMAIL',
  'GOOGLE_PRIVATE_KEY',
];
// Optional — tool degrades gracefully without Places API (no ratings/reviews from Google)
// const OPTIONAL = ['GOOGLE_PLACES_API_KEY'];

function validateEnv() {
  const missing = REQUIRED.filter((key) => !process.env[key]);
  if (missing.length > 0) {
    console.error(`[LeadForge] Missing required env vars: ${missing.join(', ')}`);
    console.error('[LeadForge] Copy .env.example to .env and fill in all values.');
    process.exit(1);
  }
}

module.exports = {
  validateEnv,
  serperApiKey: process.env.SERPER_API_KEY,
  googlePlacesApiKey: process.env.GOOGLE_PLACES_API_KEY,
  googleSheetsId: process.env.GOOGLE_SHEETS_ID,
  googleServiceAccountEmail: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
  googlePrivateKey: (process.env.GOOGLE_PRIVATE_KEY || '').replace(/\\n/g, '\n'),
  port: parseInt(process.env.PORT || '3000', 10),
  concurrencyLimit: parseInt(process.env.CONCURRENCY_LIMIT || '5', 10),
  requestDelayMs: parseInt(process.env.REQUEST_DELAY_MS || '1200', 10),
};
