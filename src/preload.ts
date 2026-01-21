import { contextBridge, ipcRenderer } from 'electron';
contextBridge.exposeInMainWorld('win', {
minimize: () => ipcRenderer.send('win:minimize'),
close: () => ipcRenderer.send('win:close'),
});
contextBridge.exposeInMainWorld('gitlab', {
openProjectWeb: () => ipcRenderer.invoke('gitlab:openProjectWeb'),
});