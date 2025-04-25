document.addEventListener('DOMContentLoaded', function() {
    // Initialize date range pickers for analytics
    const dateRangePickers = document.querySelectorAll('.date-range-picker');
    if (dateRangePickers.length > 0) {
        dateRangePickers.forEach(picker => {
            flatpickr(picker, {
                dateFormat: "Y-m-d",
                maxDate: "today"
            });
        });
    }
    
    // Handle date filter form submission
    const dateFilterForm = document.getElementById('date-filter-form');
    if (dateFilterForm) {
        dateFilterForm.addEventListener('submit', function(e) {
            const fromDate = document.getElementById('from_date').value;
            const toDate = document.getElementById('to_date').value;
            
            if (!fromDate || !toDate) {
                e.preventDefault();
                alert('Please select both from and to dates.');
                return false;
            }
            
            if (new Date(fromDate) > new Date(toDate)) {
                e.preventDefault();
                alert('From date cannot be after to date.');
                return false;
            }
        });
    }
    
    // Check if the job status chart element exists
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
    
    // Check if engagement metrics chart exists
    const engagementChart = document.getElementById('engagementChart');
    if (engagementChart) {
        const ctx = engagementChart.getContext('2d');
        
        // Get the rates from the data attributes
        const rates = {
            openRate: parseFloat(engagementChart.dataset.openRate || 0),
            clickRate: parseFloat(engagementChart.dataset.clickRate || 0),
            clickToOpenRate: parseFloat(engagementChart.dataset.clickToOpenRate || 0),
            bounceRate: parseFloat(engagementChart.dataset.bounceRate || 0)
        };
        
        // Create the chart
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Open Rate', 'Click Rate', 'Click-to-Open Rate', 'Bounce Rate'],
                datasets: [{
                    label: 'Current Period',
                    data: [
                        rates.openRate,
                        rates.clickRate,
                        rates.clickToOpenRate,
                        rates.bounceRate
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Engagement Metrics (%)'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Check if time series chart exists
    const timeSeriesChart = document.getElementById('timeSeriesChart');
    if (timeSeriesChart) {
        const ctx = timeSeriesChart.getContext('2d');
        
        // Get the time series data from the data attribute
        let timeSeriesData;
        try {
            timeSeriesData = JSON.parse(timeSeriesChart.dataset.timeseriesData || '[]');
        } catch (e) {
            console.error('Error parsing time series data:', e);
            timeSeriesData = [];
        }
        
        // Prepare data for chart
        const dates = timeSeriesData.map(item => item.date);
        const sentData = timeSeriesData.map(item => item.sent);
        const openedData = timeSeriesData.map(item => item.opened);
        const clickedData = timeSeriesData.map(item => item.clicked);
        
        // Create the chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'Sent',
                        data: sentData,
                        backgroundColor: 'rgba(46, 204, 113, 0.2)',
                        borderColor: 'rgb(46, 204, 113)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Opened',
                        data: openedData,
                        backgroundColor: 'rgba(243, 156, 18, 0.2)',
                        borderColor: 'rgb(243, 156, 18)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Clicked',
                        data: clickedData,
                        backgroundColor: 'rgba(155, 89, 182, 0.2)',
                        borderColor: 'rgb(155, 89, 182)',
                        tension: 0.1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            tooltipFormat: 'MMM d, yyyy'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Email Performance Over Time'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }
    
    // Check if segment performance chart exists
    const segmentPerformanceChart = document.getElementById('segmentPerformanceChart');
    if (segmentPerformanceChart) {
        const ctx = segmentPerformanceChart.getContext('2d');
        
        // Get the segment data from the data attribute
        let segmentData;
        try {
            segmentData = JSON.parse(segmentPerformanceChart.dataset.segmentData || '[]');
        } catch (e) {
            console.error('Error parsing segment data:', e);
            segmentData = [];
        }
        
        // Prepare data for chart
        const segmentNames = segmentData.map(item => item.segment_name);
        const openRates = segmentData.map(item => item.open_rate);
        const clickRates = segmentData.map(item => item.click_rate);
        
        // Create the chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: segmentNames,
                datasets: [
                    {
                        label: 'Open Rate (%)',
                        data: openRates,
                        backgroundColor: 'rgba(243, 156, 18, 0.7)',
                        borderColor: 'rgb(243, 156, 18)',
                        borderWidth: 1
                    },
                    {
                        label: 'Click Rate (%)',
                        data: clickRates,
                        backgroundColor: 'rgba(155, 89, 182, 0.7)',
                        borderColor: 'rgb(155, 89, 182)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Segment'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Rate (%)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Segment Performance Comparison'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Check if template performance chart exists
    const templatePerformanceChart = document.getElementById('templatePerformanceChart');
    if (templatePerformanceChart) {
        const ctx = templatePerformanceChart.getContext('2d');
        
        // Get the template data from the data attribute
        let templateData;
        try {
            templateData = JSON.parse(templatePerformanceChart.dataset.templateData || '[]');
        } catch (e) {
            console.error('Error parsing template data:', e);
            templateData = [];
        }
        
        // Prepare data for chart (limit to top 5 templates)
        const topTemplates = templateData.slice(0, 5);
        const templateNames = topTemplates.map(item => item.template_name);
        const clickRates = topTemplates.map(item => item.click_rate);
        
        // Create the chart
        new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: templateNames,
                datasets: [{
                    label: 'Click Rate (%)',
                    data: clickRates,
                    backgroundColor: [
                        'rgba(155, 89, 182, 0.7)',
                        'rgba(142, 68, 173, 0.7)',
                        'rgba(127, 61, 156, 0.7)',
                        'rgba(116, 55, 139, 0.7)',
                        'rgba(102, 51, 153, 0.7)'
                    ],
                    borderColor: [
                        'rgb(155, 89, 182)',
                        'rgb(142, 68, 173)',
                        'rgb(127, 61, 156)',
                        'rgb(116, 55, 139)',
                        'rgb(102, 51, 153)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Click Rate (%)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Template'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Performing Templates (Click Rate)'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Initialize datetime pickers for job scheduling
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
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
