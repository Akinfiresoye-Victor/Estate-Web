// Company Listings Page JavaScript

(function() {
    'use strict';

    let deleteUrl = null;

    document.addEventListener('DOMContentLoaded', function() {
        initializeFilters();
        initializeSearch();
        initializeSort();
    });

    // Filter Tabs Functionality
    function initializeFilters() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const propertySections = document.querySelectorAll('.listings-section');

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const target = this.dataset.target;

                // Update active tab
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Show/hide sections
                if (target === 'all') {
                    propertySections.forEach(section => {
                        section.style.display = 'block';
                    });
                } else {
                    propertySections.forEach(section => {
                        if (section.dataset.category === target) {
                            section.style.display = 'block';
                        } else {
                            section.style.display = 'none';
                        }
                    });
                }
            });
        });
    }

    // Search Functionality
    function initializeSearch() {
        const searchInput = document.getElementById('searchInput');
        
        if (!searchInput) return;

        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const propertyCards = document.querySelectorAll('.property-card');

            propertyCards.forEach(card => {
                const title = card.querySelector('.property-title').textContent.toLowerCase();
                const location = card.querySelector('.property-location span').textContent.toLowerCase();

                if (title.includes(searchTerm) || location.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            // Update section visibility
            updateSectionVisibility();
        });
    }

    // Sort Functionality
    function initializeSort() {
        const sortSelect = document.getElementById('sortSelect');
        
        if (!sortSelect) return;

        sortSelect.addEventListener('change', function() {
            const sortType = this.value;
            const sections = document.querySelectorAll('.listings-section');

            sections.forEach(section => {
                const grid = section.querySelector('.properties-grid');
                const cards = Array.from(grid.querySelectorAll('.property-card'));

                cards.sort((a, b) => {
                    switch(sortType) {
                        case 'newest':
                            return 0;
                        case 'oldest':
                            return 1;
                        case 'price-high':
                            return getPriceValue(b) - getPriceValue(a);
                        case 'price-low':
                            return getPriceValue(a) - getPriceValue(b);
                        default:
                            return 0;
                    }
                });

                // Re-append sorted cards
                cards.forEach(card => grid.appendChild(card));
            });
        });
    }

    // Helper function to get price value from card
    function getPriceValue(card) {
        const priceText = card.querySelector('.price-amount').textContent;
        return parseFloat(priceText.replace(/[₦,]/g, ''));
    }

    // Update section visibility based on visible cards
    function updateSectionVisibility() {
        const sections = document.querySelectorAll('.listings-section');

        sections.forEach(section => {
            const visibleCards = section.querySelectorAll('.property-card[style="display: block"], .property-card:not([style*="display: none"])');
            
            if (visibleCards.length === 0) {
                section.style.display = 'none';
            } else {
                section.style.display = 'block';
            }
        });
    }

    // Delete Modal Functions
    window.showDeleteModal = function(url) {
        deleteUrl = url;
        const modal = document.getElementById('deleteModal');
        if (modal) {
            modal.classList.add('active');
        }
    };

    window.closeDeleteModal = function() {
        const modal = document.getElementById('deleteModal');
        if (modal) {
            modal.classList.remove('active');
        }
        deleteUrl = null;
    };

    // Confirm Delete
    window.confirmDelete = function() {
        if (!deleteUrl) return;

        const CSRF = getCookie('csrftoken');

        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': CSRF,
            },
            credentials: 'same-origin',
        })
        .then(response => {
            // If response is ok (status 200-299), consider it successful
            if (response.ok) {
                closeDeleteModal();
                showNotification('Property deleted successfully', 'success');
                // Reload page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Try to get error message from response
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to delete property');
                }).catch(() => {
                    throw new Error('Failed to delete property');
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            closeDeleteModal();
            showNotification(error.message || 'An error occurred while deleting the property', 'error');
        });
    };

    // Close modal when clicking outside
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('deleteModal');
        if (e.target === modal) {
            closeDeleteModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeDeleteModal();
        }
    });

    // Show notification
    function showNotification(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show`;
        alert.style.position = 'fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="bi bi-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }

    // Get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

})();