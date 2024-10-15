document.addEventListener('DOMContentLoaded', function() {
    // Simulated Data
    const events = [
        { time: '12:05', event: 'Login Attempt', severity: 'Medium', source: '192.168.1.101' },
        { time: '12:10', event: 'Suspicious Traffic', severity: 'High', source: '10.0.0.2' },
        { time: '12:15', event: 'Malware Detected', severity: 'Critical', source: '8.8.8.8' },
        { time: '12:20', event: 'File Modification', severity: 'Low', source: '172.16.254.3' }
    ];
  
    // Fetch event data and update the dashboard
    function fetchEventData() {
      fetch('/api/events')
        .then(response => response.json())
        .then(data => {
          const events = data.events;
          const threats = data.threats;
  
          // Clear previous logs
          const eventLogsTable = document.getElementById('eventLogs');
          eventLogsTable.innerHTML = '';
  
          // Populate Event Logs
          events.forEach(event => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${event.time}</td>
              <td>${event.event}</td>
              <td>${event.severity}</td>
              <td>${event.source}</td>
            `;
            eventLogsTable.appendChild(row);
          });
  
          // Populate Summary Data
          document.getElementById('totalEvents').textContent = events.length;
          document.getElementById('criticalAlerts').textContent = events.filter(e => e.severity === 'Critical').length;
  
          // Fetch data again after 5 seconds
          setTimeout(fetchEventData, 5000);
        })
        .catch(error => console.error('Error fetching event data:', error));
    }
  
    // Initial data fetch
    fetchEventData();
  
    // Simulated Threat Alerts and Event Severity Distribution Chart
    const threats = [
      'Critical Alert: Malware detected from IP 8.8.8.8',
      'High Alert: Suspicious traffic from IP 10.0.0.2',
    ];
  
    // Populate Event Logs
    const eventLogsTable = document.getElementById('eventLogs');
    events.forEach(event => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${event.time}</td>
        <td>${event.event}</td>
        <td>${event.severity}</td>
        <td>${event.source}</td>
      `;
      eventLogsTable.appendChild(row);
    });
  
    // Populate Threat Alerts
    const threatAlertsList = document.getElementById('threatAlerts');
    threats.forEach(threat => {
      const li = document.createElement('li');
      li.textContent = threat;
      threatAlertsList.appendChild(li);
    });
  
    // Populate Summary Data
    document.getElementById('totalEvents').textContent = events.length;
    document.getElementById('threatsDetected').textContent = threats.length;
    document.getElementById('criticalAlerts').textContent = events.filter(e => e.severity === 'Critical').length;
    document.getElementById('highRiskIPs').textContent = events.filter(e => e.severity === 'High').length;
  
    // Event Severity Distribution Chart
    const ctx = document.getElementById('eventSeverityChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Low', 'Medium', 'High', 'Critical'],
        datasets: [{
          label: 'Event Severity',
          data: [
            events.filter(e => e.severity === 'Low').length,
            events.filter(e => e.severity === 'Medium').length,
            events.filter(e => e.severity === 'High').length,
            events.filter(e => e.severity === 'Critical').length,
          ],
          backgroundColor: ['#4caf50', '#ffeb3b', '#ff9800', '#f44336']
        }]
      },
      options: {
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  
    // Handling folder selection for "Monitoring"
    const { dialog } = require('electron').remote;
  
    const openFolderBtn = document.getElementById('openFolderBtn');
    if (openFolderBtn) {
      openFolderBtn.addEventListener('click', () => {
        dialog.showOpenDialog({ properties: ['openDirectory'] }).then(result => {
          if (!result.canceled) {
            console.log('Selected folder: ', result.filePaths[0]);
            // You can now handle the folder path, e.g., start monitoring the folder
          }
        }).catch(err => {
          console.log('Error selecting folder: ', err);
        });
      });
    }
  });
  