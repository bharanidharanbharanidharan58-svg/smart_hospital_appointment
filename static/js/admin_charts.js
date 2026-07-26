/* Admin Analytics Chart.js Visualizations */

document.addEventListener('DOMContentLoaded', () => {
    const revenueCanvas = document.getElementById('revenueChart');
    const deptCanvas = document.getElementById('deptChart');
    const statusCanvas = document.getElementById('statusChart');

    if (!revenueCanvas || !deptCanvas) return;

    fetchAdminAnalytics();

    async function fetchAdminAnalytics() {
        try {
            const res = await fetch('/api/admin/analytics');
            const data = await res.json();

            // 1. Revenue Chart
            new Chart(revenueCanvas, {
                type: 'bar',
                data: {
                    labels: data.revenue_by_hospital.labels,
                    datasets: [{
                        label: 'Total Revenue (₹)',
                        data: data.revenue_by_hospital.data,
                        backgroundColor: 'rgba(37, 99, 235, 0.75)',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'Hospital Branch Revenue (₹)' }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // 2. Department Distribution Chart
            new Chart(deptCanvas, {
                type: 'doughnut',
                data: {
                    labels: data.department_distribution.labels,
                    datasets: [{
                        data: data.department_distribution.data,
                        backgroundColor: [
                            '#2563eb', '#06b6d4', '#10b981', '#f59e0b',
                            '#ef4444', '#8b5cf6', '#ec4899', '#64748b'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: 'Department Patient Consultation Share' }
                    }
                }
            });

            // 3. Status Chart (if present)
            if (statusCanvas && data.status_breakdown) {
                new Chart(statusCanvas, {
                    type: 'pie',
                    data: {
                        labels: data.status_breakdown.labels,
                        datasets: [{
                            data: data.status_breakdown.data,
                            backgroundColor: ['#10b981', '#3b82f6', '#ef4444', '#f59e0b']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
        } catch (e) {
            console.error('Error initializing admin analytics charts:', e);
        }
    }
});
