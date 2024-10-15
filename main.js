const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let flaskProcess;
let detectionProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
    });

    // Load the Flask app in Electron
    mainWindow.loadURL('http://127.0.0.1:5000');

    mainWindow.on('closed', function () {
        mainWindow = null;
        if (flaskProcess) flaskProcess.kill();  // Stop Flask server
        if (detectionProcess) detectionProcess.kill();  // Stop detection script
    });
}

// Start the Flask server
function startFlaskServer() {
    flaskProcess = spawn('python', ['app.py']);
    flaskProcess.stdout.on('data', (data) => console.log(`Flask: ${data}`));
    flaskProcess.stderr.on('data', (data) => console.error(`Flask Error: ${data}`));
}

// Let the user choose a folder and run the detection script
function selectFolderAndStartDetection() {
    dialog.showOpenDialog({
        properties: ['openDirectory']
    }).then(result => {
        if (!result.canceled) {
            const folderPath = result.filePaths[0];

            // Start detection.py with the selected folder
            detectionProcess = spawn('python', ['detection.py', folderPath]);

            detectionProcess.stdout.on('data', (data) => console.log(`Detection: ${data}`));
            detectionProcess.stderr.on('data', (data) => console.error(`Detection Error: ${data}`));
        }
    }).catch(err => console.error(err));
}

app.whenReady().then(() => {
    startFlaskServer();  // Start the Flask server
    createWindow();  // Create the Electron window

    // Allow the user to select a folder after the window is ready
    selectFolderAndStartDetection();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});
