// Bare minimum Electron test - no npm electron package conflict
// Access built-in via process internal
try {
  // Try to access Electron internals directly
  const binding = process.binding('electron');
  console.log('binding works:', typeof binding);
} catch(e) {
  console.log('binding failed:', e.message);
}

// Try alternate require paths
const paths = [
  'electron/main',
  'electron/common',
];
for (const p of paths) {
  try {
    const m = require(p);
    console.log(p, '->', typeof m, Object.keys(m||{}).slice(0,5));
  } catch(e) {
    console.log(p, '-> FAIL:', e.message.slice(0,60));
  }
}

// Check if app is global
console.log('global.app:', typeof global.app);
console.log('process.type:', process.type);
console.log('process.versions.electron:', process.versions.electron);
