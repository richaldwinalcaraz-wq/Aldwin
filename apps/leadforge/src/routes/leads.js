const express = require('express');
const router = express.Router();
const { stringify } = require('csv-stringify/sync');
const { getLeads, getStats, clearLeads } = require('../services/leadStore');
const logger = require('../utils/logger');

router.get('/leads', (req, res) => {
  const { niche, classification, minScore } = req.query;
  const leads = getLeads({ niche, classification, minScore });
  res.json({ count: leads.length, leads });
});

router.get('/leads/stats', (req, res) => {
  res.json(getStats());
});

router.delete('/leads', (req, res) => {
  clearLeads();
  res.json({ success: true, message: 'Lead store cleared' });
});

router.get('/export', (req, res) => {
  const { format = 'json', niche, classification } = req.query;
  const leads = getLeads({ niche, classification });

  if (format === 'csv') {
    try {
      const headers = [
        'businessName', 'niche', 'location', 'website', 'email', 'phone',
        'reviewCount', 'rating', 'leadScore', 'classification', 'companySize',
        'aiOpportunityScore', 'websiteQuality', 'detectedGaps', 'socialLinks',
        'mapsUrl', 'outreachStatus', 'dateScraped',
      ];
      const rows = leads.map((l) =>
        headers.map((h) => {
          const v = l[h];
          return Array.isArray(v) ? v.join('; ') : (v ?? '');
        })
      );
      const csv = stringify([headers, ...rows]);
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', 'attachment; filename="leadforge_export.csv"');
      return res.send(csv);
    } catch (err) {
      logger.error(`[API] CSV export failed: ${err.message}`);
      return res.status(500).json({ error: 'CSV export failed' });
    }
  }

  res.json({ count: leads.length, leads });
});

module.exports = router;
