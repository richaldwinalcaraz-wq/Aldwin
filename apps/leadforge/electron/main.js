const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const ipcMain = electron.ipcMain;
const dialog = electron.dialog;
const shell = electron.shell;

const path = require('path');
const fs = require('fs');
const { fork } = require('child_process');

let mainWindow = null;
let serverProcess = null;
const SERVER_PORT = 3000;

function startExpressServer() {
  return new Promise((resolve, reject) => {
    const envPath = app.isPackaged
      ? path.join(process.resourcesPath, '.env')
      : path.join(__dirname, '../.env');

    serverProcess = fork(path.join(__dirname, '../src/server.js'), [], {
      env: {
        ...process.env,
        DOTENV_PATH: envPath,
        PORT: String(SERVER_PORT),
        ELECTRON_APP: '1',
      },
      silent: true,
    });

    serverProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log('[Server]', msg.trim());
      if (msg.includes('LeadForge running')) resolve();
    });

    serverProcess.stderr.on('data', (data) => console.error('[Server ERR]', data.toString().trim()));
    serverProcess.on('error', reject);

    // Timeout fallback — assume ready after 5s
    setTimeout(resolve, 5000);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 960,
    minHeight: 600,
    title: 'LeadForge AI Scraper',
    backgroundColor: '#0d0f14',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    autoHideMenuBar: true,
    show: false,
  });

  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.loadURL(`http://localhost:${SERVER_PORT}`);
  mainWindow.on('closed', () => { mainWindow = null; });
}

app.whenReady().then(async () => {
  try {
    await startExpressServer();
  } catch (err) {
    console.error('Server startup error:', err.message);
  }
  createWindow();
});

app.on('window-all-closed', () => {
  if (serverProcess) serverProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

ipcMain.handle('open-external', (_, url) => shell.openExternal(url));

ipcMain.handle('save-file', async (_, { content, defaultName, filters }) => {
  const { canceled, filePath } = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: filters || [{ name: 'All Files', extensions: ['*'] }],
  });
  if (!canceled && filePath) {
    fs.writeFileSync(filePath, content);
    return { success: true, filePath };
  }
  return { success: false };
});
