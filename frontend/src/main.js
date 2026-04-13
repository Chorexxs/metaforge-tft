const { app, BrowserWindow, globalShortcut, ipcMain } = require("electron");
const path = require("path");

let mainWindow = null;
let isVisible = true;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 600,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.loadFile(path.join(__dirname, "index.html"));

  mainWindow.on("blur", () => {
    if (!mainWindow.webContents.isDevToolsOpened()) {
    }
  });

  console.log("[TFT HUD] Window created");
}

function toggleVisibility() {
  isVisible = !isVisible;
  if (isVisible) {
    mainWindow.show();
  } else {
    mainWindow.hide();
  }
  console.log(`[TFT HUD] Visibility: ${isVisible}`);
}

function toggleMiniMode() {
  if (mainWindow.getSize()[0] === 200) {
    mainWindow.setSize(400, 600);
  } else {
    mainWindow.setSize(200, 200);
  }
  console.log("[TFT HUD] Mini mode toggled");
}

app.whenReady().then(() => {
  createWindow();

  globalShortcut.register("Alt+H", toggleVisibility);
  globalShortcut.register("Alt+M", toggleMiniMode);

  console.log("[TFT HUD] Global shortcuts registered");
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

ipcMain.handle("get-settings", () => {
  return {
    apiUrl: "http://127.0.0.1:8000",
  };
});

ipcMain.handle("hide-window", () => {
  mainWindow.hide();
});
