// admin_panel/static/admin_panel/js/admin.js

document.addEventListener('DOMContentLoaded', () => {
    // Sidebar Toggle for Mobile
    const hamburger = document.getElementById('adm-hamburger-btn');
    const sidebar = document.getElementById('adm-sidebar');
    if (hamburger && sidebar) {
        hamburger.addEventListener('click', () => {
            sidebar.classList.toggle('adm-open');
        });
    }

    // Type-to-confirm modals handling
    const confirmForms = document.querySelectorAll('.adm-confirm-form');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const expected = form.getAttribute('data-expected');
            const input = form.querySelector('.adm-confirm-input');
            if (input && input.value !== expected) {
                e.preventDefault();
                alert(`Confirmation failed. Please type "${expected}" exactly to proceed.`);
            }
        });
    });
});
