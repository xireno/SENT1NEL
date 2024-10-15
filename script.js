const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', function() {

  // Function to fetch logs from the server
  function fetchLogs() {
    fetch('http://localhost:5000/get_logs')
      .then(response => response.json())
      .then(data => {
        const logContainer = document.getElementById('logContainer');
        logContainer.innerHTML = '';  // Clear previous logs

        // Display each log message
        data.forEach(logMessage => {
          const logEntry = document.createElement('div');
          logEntry.classList.add('log-entry');
          logEntry.textContent = logMessage;
          logContainer.appendChild(logEntry);
        });
      })
      .catch(err => console.error('Error fetching logs:', err));
  }

  // Periodically fetch logs every 2 seconds
  setInterval(fetchLogs, 2000);
});
