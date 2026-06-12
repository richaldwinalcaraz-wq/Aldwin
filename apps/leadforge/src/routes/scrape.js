const express = require('express');
const router = express.Router();
const { runScrape } = require('../scrapers');
const { ensureAllTabs } = require('../services/sheets');
const progress = require('../services/progressEmitter');
const logger = require('../utils/logger');

const ALL_NICHES = [
  'med spa',
  'roofing',
  'aesthetic clinic',
  'dental clinic',
  'realtor',
  'law firm',
  'insurance agency',
  'gym',
  'car dealership',
  'hvac',
  'travel agency',
];

function sseSetup(res) {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.flushHeaders();
  return (data) => res.write(`data: ${JSON.stringify(data)}\n\n`);
}

// Single niche SSE stream
router.get('/scrape/stream', async (req, res) => {
  const { niche, location, limit = 20 } = req.query;

  if (!niche || !location) {
    res.status(400).json({ error: 'niche and location are required' });
    return;
  }

  const send = sseSetup(res);
  const onEvent = (event) => send(event);
  progress.on('event', onEvent);
  req.on('close', () => progress.off('event', onEvent));

  try {
    await ensureAllTabs();
    await runScrape({ niche, location, limit: Math.min(parseInt(limit) || 20, 100) });
  } catch (err) {
    logger.error(`[API] Scrape stream error: ${err.message}`);
    send({ type: 'error', message: err.message });
  }

  progress.off('event', onEvent);
  res.end();
});

// All niches SSE stream — scrapes every niche sequentially
router.get('/scrape/all/stream', async (req, res) => {
  const { location, limit = 20 } = req.query;

  if (!location) {
    res.status(400).json({ error: 'location is required' });
    return;
  }

  const send = sseSetup(res);
  const onEvent = (event) => send(event);
  progress.on('event', onEvent);
  req.on('close', () => progress.off('event', onEvent));

  const perNicheLimit = Math.min(parseInt(limit) || 20, 100);
  const totals = { total: 0, inserted: 0, skipped: 0, hot: 0, warm: 0, cold: 0 };

  try {
    await ensureAllTabs();

    for (let i = 0; i < ALL_NICHES.length; i++) {
      const niche = ALL_NICHES[i];
      send({
        type: 'niche_start',
        niche,
        nicheIndex: i + 1,
        nicheTotal: ALL_NICHES.length,
        message: `[${i + 1}/${ALL_NICHES.length}] Scraping ${niche}...`,
      });

      try {
        const result = await runScrape({ niche, location, limit: perNicheLimit });
        totals.total    += result.total;
        totals.inserted += result.inserted;
        totals.skipped  += result.skipped;
        totals.hot      += result.hot;
        totals.warm     += result.warm;
        totals.cold     += result.cold;

        send({
          type: 'niche_done',
          niche,
          nicheIndex: i + 1,
          nicheTotal: ALL_NICHES.length,
          result,
          totals,
        });
      } catch (err) {
        logger.error(`[API] Scrape all — ${niche} failed: ${err.message}`);
        send({ type: 'niche_error', niche, message: err.message });
      }
    }

    send({ type: 'all_done', totals });

  } catch (err) {
    logger.error(`[API] Scrape all error: ${err.message}`);
    send({ type: 'error', message: err.message });
  }

  progress.off('event', onEvent);
  res.end();
});

// Non-streaming POST
router.post('/scrape', async (req, res) => {
  const { niche, location, limit = 20 } = req.body;

  if (!niche || !location) {
    return res.status(400).json({ error: 'niche and location are required' });
  }

  try {
    await ensureAllTabs();
    const results = await runScrape({ niche, location, limit: Math.min(parseInt(limit) || 20, 100) });
    res.json({ success: true, ...results });
  } catch (err) {
    logger.error(`[API] Scrape error: ${err.message}`);
    res.status(500).json({ error: 'Scrape failed', details: err.message });
  }
});

module.exports = router;
