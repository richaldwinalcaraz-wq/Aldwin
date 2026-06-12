// Skip env validation in Electron (already loaded via dotenv in electron/main.js)
if (!process.env.ELECTRON_APP) {
  const { validateEnv } = require('./config/env');
  validateEnv();
}

const express = require('express');
const path = require('path');
const logger = require('./utils/logger');
const config = require('./config/env');

const healthRoute = require('./routes/health');
const scrapeRoute = require('./routes/scrape');
const leadsRoute = require('./routes/leads');

const isCLI = require.main === module && process.argv[2] === 'scrape';

async function startServer(port) {
  const app = express();
  app.use(express.json());
  app.use(express.static(path.join(__dirname, '../public')));

  app.use('/api', healthRoute);
  app.use('/api', scrapeRoute);
  app.use('/api', leadsRoute);

  app.get('/', (req, res) => res.sendFile(path.join(__dirname, '../public/index.html')));

  const listenPort = port || config.port;
  return new Promise((resolve, reject) => {
    const server = app.listen(listenPort, () => {
      logger.info(`LeadForge running at http://localhost:${listenPort}`);
      resolve(server);
    });
    server.on('error', reject);
  });
}

async function runCLI() {
  const { validateEnv } = require('./config/env');
  validateEnv();

  const yargs = require('yargs/yargs');
  const { hideBin } = require('yargs/helpers');
  const { runScrape } = require('./scrapers');
  const { ensureAllTabs } = require('./services/sheets');

  const argv = yargs(hideBin(process.argv))
    .command('scrape', 'Scrape leads', (y) => {
      y.option('niche', { alias: 'n', type: 'string', demandOption: true })
        .option('location', { alias: 'l', type: 'string', demandOption: true })
        .option('limit', { alias: 'lim', type: 'number', default: 20 });
    })
    .help().argv;

  if (argv._[0] === 'scrape') {
    try {
      await ensureAllTabs();
      const results = await runScrape({ niche: argv.niche, location: argv.location, limit: argv.limit });
      console.log('\n=== LeadForge Results ===');
      console.log(`Niche:      ${argv.niche}`);
      console.log(`Location:   ${argv.location}`);
      console.log(`Found:      ${results.total}`);
      console.log(`New:        ${results.inserted}`);
      console.log(`Duplicates: ${results.skipped}`);
      console.log(`Hot:        ${results.hot}`);
      console.log(`Warm:       ${results.warm}`);
      console.log(`Cold:       ${results.cold}`);
      console.log('=========================\n');
    } catch (err) {
      logger.error('Scrape failed', { error: err.message });
      process.exit(1);
    }
  }
}

if (isCLI) {
  runCLI();
} else if (require.main === module) {
  startServer();
}

module.exports = { startServer };
