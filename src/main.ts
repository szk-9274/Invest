import { app, BrowserWindow, ipcMain, shell } from 'electron';
import { join } from 'path';

let mainWindow: BrowserWindow | null = null;

// USE_DEV_SERVER=true のときは Vite の dev サーバを使用。
// start:prod では USE_DEV_SERVER=false を付与してビルド済みを読み込みます。
const useDevServer = process.env.USE_DEV_SERVER === 'true';

function createWindow(): void {
const devServerURL = 'http://127.0.0.1:5173';
const indexHtml = join(__dirname, '..', 'renderer-dist', 'index.html');
const iconPath = join(__dirname, '..', 'build', 'icon.ico');

mainWindow = new BrowserWindow({
width: 450,
height: 665,
frame: false,
resizable: false,
alwaysOnTop: false,
skipTaskbar: false,
show: false,
backgroundColor: '#0f1b28',
title: 'Toolbox',
icon: iconPath,
webPreferences: {
preload: join(__dirname, 'preload.js'),
contextIsolation: true,
nodeIntegration: false,
// sandbox: true, // 必要なら有効化
},
});

if (useDevServer) {
// 開発時: dev サーバをロード。失敗時はビルド済みにフォールバック。
mainWindow
.loadURL(devServerURL)
.catch(() => {
mainWindow?.loadFile(indexHtml);
});


mainWindow.webContents.on('did-fail-load', () => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.loadFile(indexHtml).catch(() => {});
  }
});

// 開発中のみ DevTools を自動で開く
mainWindow.webContents.on('did-finish-load', () => {
  mainWindow?.webContents.openDevTools({ mode: 'detach' });
});
} else {
// 本番相当: ビルド済みの静的ファイルをロード
mainWindow.loadFile(indexHtml);
}

mainWindow.once('ready-to-show', () => {
mainWindow?.center();
mainWindow?.show();
mainWindow?.focus();
});

mainWindow.on('closed', () => {
mainWindow = null;
});
}

// タイトルバー操作
ipcMain.on('win:minimize', () => {
mainWindow?.minimize();
});
ipcMain.on('win:close', () => {
mainWindow?.close();
});

ipcMain.handle('gitlab:openProjectWeb', async () => {
const url = 'http://z0003103917.dnjp.globaldenso:50080/tsukasa.suzuki.j4g';
await shell.openExternal(url);
return true;
});

// シングルトンロック
const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
app.quit();
} else {
// Windows で通知などに使われる AppUserModelID を設定（electron-builder の appId と合わせる）
if (process.platform === 'win32') {
const appId = useDevServer
? 'jp.co.example.demoelectron.dev' // ← 開発用の別ID
: 'jp.co.example.demoelectron'; // ← パッケージと一致
app.setAppUserModelId(appId);
}

app.whenReady().then(createWindow);

app.on('second-instance', () => {
if (mainWindow) {
if (mainWindow.isMinimized()) mainWindow.restore();
mainWindow.show();
mainWindow.focus();
}
});

// macOS でも挙動を安定させたい場合の再作成（Windowsのみなら不要）
app.on('activate', () => {
if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('window-all-closed', () => {
app.quit();
});
}