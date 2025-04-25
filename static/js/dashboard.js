document.addEventListener('DOMContentLoaded', function() {
    // Check if the chart element exists
    const jobStatusChart = document.getElementById('jobStatusChart');
    if (jobStatusChart) {
        const ctx = jobStatusChart.getContext('2d');
        
        // Get the status counts from the data attributes
        const statusCounts = {
            scheduled: parseInt(jobStatusChart.dataset.scheduled || 0),
            running: parseInt(jobStatusChart.dataset.running || 0),
            completed: parseInt(jobStatusChart.dataset.completed || 0),
            failed: parseInt(jobStatusChart.dataset.failed || 0),
            cancelled: parseInt(jobStatusChart.dataset.cancelled || 0)
        };
        
        // Create the chart
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Scheduled', 'Running', 'Completed', 'Failed', 'Cancelled'],
                datasets: [{
                    data: [
                        statusCounts.scheduled,
                        statusCounts.running,
                        statusCounts.completed,
                        statusCounts.failed,
                        statusCounts.cancelled
                    ],
                    backgroundColor: [
                        '#3498db',  // Blue for scheduled
                        '#f39c12',  // Orange for running
                        '#2ecc71',  // Green for completed
                        '#e74c3c',  // Red for failed
                        '#95a5a6'   // Gray for cancelled
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Email Job Status'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Check if email stats chart exists
    const emailStatsChart = document.getElementById('emailStatsChart');
    if (emailStatsChart) {
        const ctx = emailStatsChart.getContext('2d');
        
        // Get the stats from the data attributes
        const emailStats = {
            total: parseInt(emailStatsChart.dataset.total || 0),
            sent: parseInt(emailStatsChart.dataset.sent || 0),
            failed: parseInt(emailStatsChart.dataset.failed || 0),
            opened: parseInt(emailStatsChart.dataset.opened || 0),
            clicked: parseInt(emailStatsChart.dataset.clicked || 0)
        };
        
        // Create the chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total', 'Sent', 'Failed', 'Opened', 'Clicked'],
                datasets: [{
                    label: 'Email Statistics',
                    data: [
                        emailStats.total,
                        emailStats.sent,
                        emailStats.failed,
                        emailStats.opened,
                        emailStats.clicked
                    ],
                    backgroundColor: [
                        '#3498db',  // Blue for total
                        '#2ecc71',  // Green for sent
                        '#e74c3c',  // Red for failed
                        '#f39c12',  // Orange for opened
                        '#9b59b6'   // Purple for clicked
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Email Campaign Statistics'
                    }
                }
            }
        });
    }
    
    // Initialize datetime pickers
    const datetimePickers = document.querySelectorAll('.datetime-picker');
    if (datetimePickers.length > 0) {
        datetimePickers.forEach(picker => {
            flatpickr(picker, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                time_24hr: true,
                minDate: "today"
            });
        });
    }
    
    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }
    
    // Add confirmation for job cancellation
    const cancelButtons = document.querySelectorAll('.cancel-confirm');
    if (cancelButtons.length > 0) {
        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to cancel this job? This action cannot be undone.')) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }
});
