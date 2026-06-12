const express = require('express');
const router = express.Router();
const config = require('../config/env');

router.get('/health', (req, res) => {
  const checks = {
    serper: !!config.serperApiKey,
    googlePlaces: !!config.googlePlacesApiKey,
    googleSheets: !!config.googleSheetsId && !!config.googleServiceAccountEmail && !!config.googlePrivateKey,
  };

  const allReady = Object.values(checks).every(Boolean);

  res.json({
    status: allReady ? 'ready' : 'missing_config',
    version: '1.0.0',
    checks,
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
