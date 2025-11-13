// Company Listings Page JavaScript

(function() {
    'use strict';

    let propertyToDelete = null;

    document.addEventListener('DOMContentLoaded', function() {
        initializeFilters();
        initializeSearch();
        initializeSort();
        initializeDeleteButtons();
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
                            // Assuming cards are already in newest order from backend
                            return 0;
                        case 'oldest':
                            // Reverse order
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
        // Remove currency symbol and commas, then convert to number
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

    // Delete Functionality
    function initializeDeleteButtons() {
        const deleteButtons = document.querySelectorAll('.action-btn.delete');
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
        const confirmDeleteBtn = document.getElementById('confirmDelete');

        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                propertyToDelete = {
                    id: this.dataset.id,
                    type: this.dataset.type,
                    element: this.closest('.property-card')
                };
                deleteModal.show();
            });
        });

        confirmDeleteBtn.addEventListener('click', function() {
            if (propertyToDelete) {
                deleteProperty(propertyToDelete);
                deleteModal.hide();
            }
        });
    }

    // Delete Property Function
    function deleteProperty(property) {
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');

        // Determine the correct URL based on property type
        const deleteUrl = property.type === 'sale' 
            ? `/company/delete-sale-property/${property.id}/`
            : `/company/delete-rent-property/${property.id}/`;

        // Send delete request
        fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Animate card removal
                property.element.style.transition = 'all 0.3s ease';
                property.element.style.opacity = '0';
                property.element.style.transform = 'translateY(-20px)';
                
                setTimeout(() => {
                    property.element.remove();
                    updateSectionVisibility();
                    updateStats();
                    showNotification('Property deleted successfully', 'success');
                }, 300);
            } else {
                showNotification('Failed to delete property', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred while deleting the property', 'error');
        });

        propertyToDelete = null;
    }

    // Update statistics after deletion
    function updateStats() {
        const saleCards = document.querySelectorAll('.property-card[data-category="sale"]').length;
        const rentCards = document.querySelectorAll('.property-card[data-category="rent"]').length;
        
        // Update stat cards
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards[0]) statCards[0].querySelector('h3').textContent = saleCards;
        if (statCards[1]) statCards[1].querySelector('h3').textContent = rentCards;
        if (statCards[2]) statCards[2].querySelector('h3').textContent = saleCards + rentCards;

        // Update tab counts
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            const target = tab.dataset.target;
            const count = tab.querySelector('.tab-count');
            
            if (target === 'all') {
                count.textContent = saleCards + rentCards;
            } else if (target === 'sale') {
                count.textContent = saleCards;
            } else if (target === 'rent') {
                count.textContent = rentCards;
            }
        });

        // Update section counts
        document.querySelectorAll('.property-count').forEach((element, index) => {
            element.textContent = index === 0 ? `${saleCards} listings` : `${rentCards} listings`;
        });
    }

    // Show notification
    function showNotification(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill';
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertClass} alert-dismissible fade show`;
        alert.innerHTML = `
            <i class="bi bi-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of page or in a messages container
        const container = document.querySelector('.messages-container') || document.body;
        container.insertBefore(alert, container.firstChild);

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