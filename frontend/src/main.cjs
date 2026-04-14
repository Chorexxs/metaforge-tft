const {
  app,
  BrowserWindow,
  globalShortcut,
  ipcMain,
  screen,
} = require("electron");
const path = require("path");

let mainWindow = null;
let isVisible = true;
let isMiniMode = false;

function createWindow() {
  const { width: screenWidth, height: screenHeight } =
    screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    width: 340,
    height: 520,
    x: screenWidth - 360,
    y: screenHeight - 600,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  if (process.env.NODE_ENV === "development") {
    mainWindow.loadURL("http://localhost:5173");
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }

  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  console.log("[TFT HUD] Window created");
}

function toggleVisibility() {
  isVisible = !isVisible;
  if (mainWindow) {
    if (isVisible) {
      mainWindow.show();
    } else {
      mainWindow.hide();
    }
  }
  mainWindow?.webContents.send("visibility-changed", isVisible);
  console.log(`[TFT HUD] Visibility: ${isVisible}`);
}

function toggleMiniMode() {
  isMiniMode = !isMiniMode;
  if (mainWindow) {
    if (isMiniMode) {
      mainWindow.setSize(260, 180);
    } else {
      mainWindow.setSize(340, 520);
    }
  }
  mainWindow?.webContents.send("mini-mode-changed", isMiniMode);
  console.log(`[TFT HUD] Mini mode: ${isMiniMode}`);
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

ipcMain.handle("hide-window", () => {
  if (mainWindow) {
    mainWindow.hide();
  }
});

ipcMain.handle("get-settings", () => {
  return {
    apiUrl: "http://127.0.0.1:8000",
  };
});
