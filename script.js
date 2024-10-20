document.addEventListener('DOMContentLoaded', function () {
  const logContainer = document.getElementById('logContainer');
  const refreshButton = document.getElementById('refreshLogs');
  const searchInput = document.getElementById('search');
  const totalLogs = document.getElementById('totalLogs');
  const lastLogTime = document.getElementById('lastLogTime');

  function fetchLogs() {
      fetch('http://127.0.0.1:5000/logs')
          .then(response => response.json())
          .then(data => {
              logContainer.innerHTML = ''; // Clear previous logs
              totalLogs.textContent = data.logs.length;

              if (data.logs.length > 0) {
                  lastLogTime.textContent = data.logs[data.logs.length - 1].timestamp;
              } else {
                  lastLogTime.textContent = '-';
              }

              data.logs.reverse().forEach(log => {
                  const logEntry = document.createElement('div');
                  logEntry.classList.add('log-entry');
                  logEntry.textContent = `[${log.timestamp}] ${log.file} - ${log.action}`;
                  logContainer.appendChild(logEntry);
              });
          })
          .catch(error => console.error('Error fetching logs:', error));
  }

  searchInput.addEventListener('input', function () {
      const searchTerm = this.value.toLowerCase();
      const logEntries = logContainer.getElementsByClassName('log-entry');

      Array.from(logEntries).forEach(entry => {
          const isVisible = entry.textContent.toLowerCase().includes(searchTerm);
          entry.style.display = isVisible ? '' : 'none';
      });
  });

  refreshButton.addEventListener('click', fetchLogs);

  setInterval(fetchLogs, 10000); // Fetch logs every 10 seconds

  fetchLogs(); // Initial fetch
});
