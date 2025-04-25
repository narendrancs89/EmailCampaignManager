document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh the page every 5 seconds if the job is running or paused
    const jobStatus = document.getElementById('job-status').dataset.status;
    if (jobStatus === 'running' || jobStatus === 'paused') {
        setInterval(function() {
            refreshJobData();
        }, 5000);
    }
    
    // Refresh logs button
    document.getElementById('refresh-logs').addEventListener('click', function() {
        refreshLogs();
    });
    
    // Initialize charts if we have data
    initCharts();
});

// Function to refresh job data via AJAX
function refreshJobData() {
    const jobId = document.getElementById('job-container').dataset.jobId;
    
    fetch(`/job/${jobId}/data`)
        .then(response => response.json())
        .then(data => {
            // Update job status
            document.getElementById('job-status').textContent = data.status;
            document.getElementById('job-status').dataset.status = data.status;
            
            // Update progress bar
            const progress = data.total_emails > 0 ? (data.sent_emails / data.total_emails) * 100 : 0;
            document.getElementById('progress-bar').style.width = `${progress}%`;
            document.getElementById('progress-bar').textContent = `${progress.toFixed(1)}%`;
            
            // Update statistics
            document.getElementById('sent-count').textContent = data.sent_emails;
            document.getElementById('failed-count').textContent = data.failed_emails;
            document.getElementById('remaining-count').textContent = data.total_emails - (data.sent_emails + data.failed_emails);
            
            // Update timing data
            if (data.started_at) {
                document.getElementById('started-at').textContent = new Date(data.started_at).toLocaleTimeString();
            }
            document.getElementById('send-rate').textContent = `${data.avg_sending_rate.toFixed(2)} emails/sec`;
            
            // Update the control buttons based on job status
            updateControlButtons(data.status);
            
            // Refresh logs while we're at it
            refreshLogs();
            
            // Update charts if needed
            updateCharts(data);
        })
        .catch(error => console.error('Error refreshing job data:', error));
}

// Function to refresh just the logs
function refreshLogs() {
    const jobId = document.getElementById('job-container').dataset.jobId;
    
    fetch(`/job/${jobId}/logs`)
        .then(response => response.json())
        .then(data => {
            const logsContainer = document.getElementById('logs-container');
            let logsHtml = '';
            
            if (data.logs.length === 0) {
                logsHtml = '<tr><td colspan="3" class="text-center">No logs available yet</td></tr>';
            } else {
                data.logs.forEach(log => {
                    const rowClass = log.level === 'error' ? 'table-danger' : 
                                    log.level === 'warning' ? 'table-warning' : '';
                    const badgeClass = log.level === 'info' ? 'bg-info' : 
                                      log.level === 'warning' ? 'bg-warning' : 'bg-danger';
                    
                    logsHtml += `
                        <tr class="${rowClass}">
                            <td>${log.timestamp}</td>
                            <td><span class="badge ${badgeClass}">${log.level.toUpperCase()}</span></td>
                            <td>${log.message}</td>
                        </tr>
                    `;
                });
            }
            
            logsContainer.innerHTML = logsHtml;
        })
        .catch(error => console.error('Error fetching logs:', error));
}

// Function to update control buttons based on job status
function updateControlButtons(status) {
    const controlContainer = document.getElementById('job-controls');
    const jobId = document.getElementById('job-container').dataset.jobId;
    
    let controlsHtml = '';
    
    if (status === 'scheduled') {
        controlsHtml = `
            <a href="/job/${jobId}/control/start" class="btn btn-primary btn-sm">
                <i class="fas fa-play me-1"></i> Start Now
            </a>
            <a href="/job/${jobId}/control/cancel" class="btn btn-danger btn-sm">
                <i class="fas fa-times me-1"></i> Cancel
            </a>
        `;
    } else if (status === 'running') {
        controlsHtml = `
            <a href="/job/${jobId}/control/pause" class="btn btn-warning btn-sm">
                <i class="fas fa-pause me-1"></i> Pause
            </a>
            <a href="/job/${jobId}/control/stop" class="btn btn-danger btn-sm">
                <i class="fas fa-stop me-1"></i> Stop
            </a>
        `;
    } else if (status === 'paused') {
        controlsHtml = `
            <a href="/job/${jobId}/control/resume" class="btn btn-primary btn-sm">
                <i class="fas fa-play me-1"></i> Resume
            </a>
            <a href="/job/${jobId}/control/stop" class="btn btn-danger btn-sm">
                <i class="fas fa-stop me-1"></i> Stop
            </a>
        `;
    }
    
    controlContainer.innerHTML = controlsHtml;
}

// Function to initialize charts
function initCharts() {
    const opensChartEl = document.getElementById('opens-chart');
    const clicksChartEl = document.getElementById('clicks-chart');
    const sendingChartEl = document.getElementById('sending-chart');
    
    if (!opensChartEl || !clicksChartEl || !sendingChartEl) return;
    
    // Get initial data from the page
    const jobData = JSON.parse(document.getElementById('job-data').textContent);
    
    // Create charts with initial data
    window.opensChart = new Chart(opensChartEl, {
        type: 'line',
        data: {
            labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
            datasets: [{
                label: 'Opens',
                data: [0, 0, 0, 0, jobData.opened_emails || 0],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    window.clicksChart = new Chart(clicksChartEl, {
        type: 'line',
        data: {
            labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
            datasets: [{
                label: 'Clicks',
                data: [0, 0, 0, 0, jobData.clicked_emails || 0],
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    window.sendingChart = new Chart(sendingChartEl, {
        type: 'line',
        data: {
            labels: ['Start'],
            datasets: [{
                label: 'Sending Rate',
                data: [0],
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Emails per second'
                    }
                }
            }
        }
    });
}

// Function to update charts with new data
function updateCharts(data) {
    if (!window.opensChart || !window.clicksChart || !window.sendingChart) return;
    
    // Update open chart data
    window.opensChart.data.datasets[0].data[4] = data.opened_emails || 0;
    window.opensChart.update();
    
    // Update click chart data
    window.clicksChart.data.datasets[0].data[4] = data.clicked_emails || 0;
    window.clicksChart.update();
    
    // Update sending rate chart
    if (data.avg_sending_rate > 0) {
        const now = new Date().toLocaleTimeString();
        window.sendingChart.data.labels.push(now);
        window.sendingChart.data.datasets[0].data.push(data.avg_sending_rate);
        
        // Keep only the last 10 data points to avoid overcrowding
        if (window.sendingChart.data.labels.length > 10) {
            window.sendingChart.data.labels.shift();
            window.sendingChart.data.datasets[0].data.shift();
        }
        
        window.sendingChart.update();
    }
}