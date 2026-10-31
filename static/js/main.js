document.addEventListener('DOMContentLoaded', function () {
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('ai-threat-theme');
    const preferredTheme = savedTheme || 'dark';
    document.body.setAttribute('data-theme', preferredTheme);

    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = preferredTheme === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
        }

        themeToggle.addEventListener('click', function () {
            const currentTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', currentTheme);
            localStorage.setItem('ai-threat-theme', currentTheme);
            if (icon) {
                icon.className = currentTheme === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
            }

            if (window.dashboardData && window.dashboardCharts) {
                window.dashboardCharts.forEach(function (chart) {
                    if (chart) {
                        chart.options.plugins.legend.labels.color = document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a';
                        chart.options.scales && chart.options.scales.x && chart.options.scales.x.ticks && (chart.options.scales.x.ticks.color = document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a');
                        chart.options.scales && chart.options.scales.y && chart.options.scales.y.ticks && (chart.options.scales.y.ticks.color = document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a');
                        chart.options.scales && chart.options.scales.x && chart.options.scales.x.grid && (chart.options.scales.x.grid.color = document.body.getAttribute('data-theme') === 'dark' ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)');
                        chart.options.scales && chart.options.scales.y && chart.options.scales.y.grid && (chart.options.scales.y.grid.color = document.body.getAttribute('data-theme') === 'dark' ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)');
                        chart.update();
                    }
                });
            }
        });
    }

    if (typeof window.dashboardData === 'undefined' || !window.dashboardData) {
        return;
    }

    const chartRegistry = {};
    window.dashboardCharts = [];

    function createOrReplaceChart(chartId, config) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            return;
        }

        if (chartRegistry[chartId]) {
            chartRegistry[chartId].destroy();
            chartRegistry[chartId] = null;
        }

        const chart = new Chart(canvas, config);
        chartRegistry[chartId] = chart;
        window.dashboardCharts.push(chart);
    }

    const trafficConfig = {
        type: 'doughnut',
        data: {
            labels: window.dashboardData.labels,
            datasets: [{
                data: window.dashboardData.values,
                backgroundColor: ['#22D3EE', '#3B82F6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300
            },
            plugins: {
                legend: {
                    labels: { color: document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a' }
                }
            }
        }
    };

    const historyLabels = window.dashboardData.history.map(function (item) {
        const timestamp = item.timestamp || '';
        if (!timestamp) {
            return '—';
        }
        const dt = new Date(timestamp);
        if (Number.isNaN(dt.getTime())) {
            return timestamp.slice(11, 16);
        }
        return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });
    const historyValues = window.dashboardData.history.map(item => item.label === 'Attack Traffic' ? 1 : 0);

    const historyConfig = {
        type: 'line',
        data: {
            labels: historyLabels,
            datasets: [{
                label: 'Attack score',
                data: historyValues,
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 300
            },
            scales: {
                x: {
                    ticks: { color: document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a' },
                    grid: { color: document.body.getAttribute('data-theme') === 'dark' ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)' }
                },
                y: {
                    ticks: { color: document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a' },
                    grid: { color: document.body.getAttribute('data-theme') === 'dark' ? 'rgba(148, 163, 184, 0.12)' : 'rgba(15, 23, 42, 0.08)' }
                }
            },
            plugins: {
                legend: { labels: { color: document.body.getAttribute('data-theme') === 'dark' ? '#edf6ff' : '#0f172a' } }
            }
        }
    };

    createOrReplaceChart('trafficChart', trafficConfig);
    createOrReplaceChart('historyChart', historyConfig);
});
