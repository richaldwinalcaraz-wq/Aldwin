// Minimal Electron test
const e = require('electron');
console.log('electron type:', typeof e);
console.log('process.type:', process.type);
console.log('process.versions.electron:', process.versions.electron);

if (typeof e === 'string') {
  console.log('ERROR: require(electron) returned path string, not module');
  console.log('This means the npm electron package is shadowing the built-in');
  process.exit(1);
}

const { app } = e;
app.whenReady().then(() => {
  console.log('SUCCESS: Electron app ready');
  app.quit();
});
