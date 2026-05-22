// SecureScan Operations Room Chart.js Renderer
document.addEventListener('DOMContentLoaded', () => {
    // 1. Severity Distribution Doughnut Chart
    const severityCanvas = document.getElementById('severityDoughnutChart');
    if (severityCanvas) {
        const counts = JSON.parse(severityCanvas.dataset.counts || '{}');
        
        new Chart(severityCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Medium', 'High', 'Critical'],
                datasets: [{
                    data: [counts.Low || 0, counts.Medium || 0, counts.High || 0, counts.Critical || 0],
                    backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
                    borderColor: '#ffffff',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#475569',
                            font: { family: 'Outfit', size: 12 },
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleColor: '#ffffff',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Trend Metrics Charts (Risk Score history trends)
    const trendsCanvas = document.getElementById('scanTrendsLineChart');
    if (trendsCanvas) {
        // Fetch history data via API
        fetch('/api/history')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success' && data.scans.length > 0) {
                    const scans = data.scans.slice(-10); // take last 10 scans
                    const labels = scans.map(s => s.target);
                    const riskScores = scans.map(s => s.risk_score);
                    const portsCount = scans.map(s => s.ports_count);

                    new Chart(trendsCanvas, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [
                                {
                                    label: 'Risk Threat Rating',
                                    data: riskScores,
                                    borderColor: '#2563eb',
                                    backgroundColor: 'rgba(37, 99, 235, 0.05)',
                                    fill: true,
                                    tension: 0.35,
                                    borderWidth: 3,
                                    pointBackgroundColor: '#2563eb',
                                    pointBorderColor: '#ffffff',
                                    pointBorderWidth: 2,
                                    pointRadius: 5
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    backgroundColor: '#0f172a',
                                    titleColor: '#ffffff',
                                    bodyColor: '#e2e8f0',
                                    borderColor: 'rgba(255, 255, 255, 0.1)',
                                    borderWidth: 1
                                }
                            },
                            scales: {
                                x: {
                                    grid: {
                                        color: 'rgba(15, 23, 42, 0.05)'
                                    },
                                    ticks: {
                                        color: '#475569',
                                        font: { family: 'Inter', size: 10 }
                                    }
                                },
                                y: {
                                    grid: {
                                        color: 'rgba(15, 23, 42, 0.05)'
                                    },
                                    ticks: {
                                        color: '#475569',
                                        font: { family: 'Inter', size: 10 }
                                    },
                                    min: 0,
                                    max: 100
                                }
                            }
                        }
                    });
                } else {
                    // Show a standard placeholder if empty
                    trendsCanvas.closest('.cyber-card').innerHTML += '<div class="text-center py-5 text-muted">No completed scan history found.</div>';
                }
            })
            .catch(err => console.error("Error drawing charts: ", err));
    }
});
