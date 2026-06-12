const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  saveFile: (opts) => ipcRenderer.invoke('save-file', opts),
  isElectron: true,
});
