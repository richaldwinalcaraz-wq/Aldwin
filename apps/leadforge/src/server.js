// Standalone server entry point
// Run directly: node src/server.js
// Compiled .exe: double-click → starts server + opens browser

const dotenvPath = process.env.DOTENV_PATH;
if (dotenvPath) {
  require('dotenv').config({ path: dotenvPath });
} else {
  require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
}

process.env.ELECTRON_APP = '1';

const { validateEnv } = require('./config/env');
validateEnv();

const { startServer } = require('./index');
const { exec } = require('child_process');
const port = parseInt(process.env.PORT) || 3000;

startServer(port).then(() => {
  const url = `http://localhost:${port}`;
  console.log(`\nLeadForge AI Scraper running at ${url}`);
  console.log('Press Ctrl+C to stop.\n');

  // Auto-open browser
  const cmd = process.platform === 'win32'
    ? `start "" "${url}"`
    : process.platform === 'darwin'
    ? `open "${url}"`
    : `xdg-open "${url}"`;

  exec(cmd, (err) => {
    if (err) console.log(`Open manually: ${url}`);
  });
}).catch((err) => {
  console.error('Failed to start server:', err.message);
  process.exit(1);
});
