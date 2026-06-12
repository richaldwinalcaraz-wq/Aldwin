const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

// __dirname = .../frontend/electron/
const BACKEND_DIR  = path.join(__dirname, '../../backend');
const FRONTEND_DIR = path.join(__dirname, '..');
const ICON         = path.join(FRONTEND_DIR, 'public/riverbend-logo.png');

const processes = [];
let win;

function spawnServer(label, cwd) {
  const proc = spawn('npm', ['run', 'dev'], {
    cwd,
    shell: true,
    stdio: 'inherit',
  });
  proc.on('error', (e) => console.error(`[${label}] error:`, e.message));
  processes.push(proc);
}

function waitForServer(url, timeoutMs = 45000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;
    function attempt() {
      http.get(url, () => resolve()).on('error', () => {
        if (Date.now() > deadline) return reject(new Error('Timeout: ' + url));
        setTimeout(attempt, 800);
      });
    }
    attempt();
  });
}

function createWindow() {
  win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 680,
    title: 'Reimbursement Report Sender',
    icon: ICON,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  win.loadURL('http://localhost:3000');

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function killAll() {
  processes.forEach((p) => { try { p.kill(); } catch (_) {} });
}

app.whenReady().then(async () => {
  spawnServer('backend', BACKEND_DIR);
  spawnServer('frontend', FRONTEND_DIR);

  try {
    await waitForServer('http://localhost:3000');
    createWindow();
  } catch (e) {
    console.error('Server failed to start:', e.message);
    killAll();
    app.quit();
  }
});

app.on('window-all-closed', () => { killAll(); app.quit(); });
app.on('before-quit', killAll);
