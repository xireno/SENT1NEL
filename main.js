const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let flaskProcess;

// Function to start Flask server
function startFlaskServer() {
    flaskProcess = spawn('python', ['app.py']);
    flaskProcess.stdout.on('data', (data) => {
        console.log(`Flask: ${data}`);
    });
    flaskProcess.stderr.on('data', (data) => {
        console.error(`Flask Error: ${data}`);
    });
    return flaskProcess;
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,  // For backward compatibility
        },
    });

    // Load the Flask index page
    mainWindow.loadURL('http://127.0.0.1:5000');

    mainWindow.on('closed', function () {
        mainWindow = null;
        flaskProcess.kill();  // Kill Flask when Electron is closed
    });
}

app.whenReady().then(() => {
    flaskProcess = startFlaskServer();
    createWindow();

    // Handler for selecting folder
    ipcMain.handle('select-folder', async () => {
        const result = await dialog.showOpenDialog(mainWindow, {
            properties: ['openDirectory']
        });
        if (!result.canceled) {
            return result.filePaths[0];  // Return selected folder path
        }
        return null;  // If no folder is selected
    });

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});
