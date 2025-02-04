// Sidebar Toggle
document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('active');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (window.innerWidth < 992) {
        if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
            sidebar.classList.remove('active');
        }
    }
});

// Responsive table initialization
document.querySelectorAll('.table-responsive').forEach(el => {
    new ResizeObserver(updateTableHeader).observe(el);
});

function updateTableHeader() {
    document.querySelectorAll('.table-responsive').forEach(el => {
        let header = el.querySelector('thead');
        let body = el.querySelector('tbody');
        if(el.offsetWidth < el.scrollWidth) {
            header.style.paddingRight = '17px';
            body.style.paddingRight = '17px';
        } else {
            header.style.paddingRight = '0';
            body.style.paddingRight = '0';
        }
    });
}