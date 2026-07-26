/* Doctor Queue Status & Patient Action Handlers */

function filterDoctorQueue(statusFilter) {
    const rows = document.querySelectorAll('.queue-table-row');
    rows.forEach(row => {
        const rowStatus = row.dataset.status;
        if (statusFilter === 'all' || rowStatus === statusFilter) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('queue-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('.queue-table-row');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});
