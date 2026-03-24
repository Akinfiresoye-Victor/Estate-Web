// ============================================
// COMPANY SETTINGS PAGE JAVASCRIPT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initializeSettingsNavigation();
    initializeLogoUpload();
    initializeCharacterCounter();
    initializePasswordValidation();
    initializeToggleSwitches();
    initializeDangerZoneActions();
    initializeFormValidation();
    initializeAutoSave();
    initializeMobileScroll();
});

// ============================================
// SETTINGS NAVIGATION
// ============================================
function initializeSettingsNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.settings-section');

    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetSection = this.getAttribute('data-section');

            // Remove active class from all nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked nav item
            this.classList.add('active');

            // Hide all sections
            sections.forEach(section => section.classList.remove('active'));

            // Show target section
            const activeSection = document.getElementById(targetSection);
            if (activeSection) {
                activeSection.classList.add('active');
                
                // Smooth scroll to top of content on mobile
                if (window.innerWidth <= 992) {
                    activeSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
}

// ============================================
// LOGO UPLOAD PREVIEW
// ============================================
function initializeLogoUpload() {
    const logoInput = document.getElementById('logoInput');
    const logoPreview = document.getElementById('logoPreview');
    const uploadLogoBtn = document.querySelector('.btn-upload-logo');
    const removeLogoBtn = document.querySelector('.btn-remove-logo');

    if (uploadLogoBtn && logoInput) {
        uploadLogoBtn.addEventListener('click', function() {
            logoInput.click();
        });
    }

    if (logoInput && logoPreview) {
        logoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    logoPreview.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (removeLogoBtn && logoPreview) {
        removeLogoBtn.addEventListener('click', function() {
            // Reset to default logo
            logoPreview.src = '/static/estate/images/logo.png';
            if (logoInput) {
                logoInput.value = '';
            }
        });
    }
}

// ============================================
// CHARACTER COUNTER
// ============================================
function initializeCharacterCounter() {
    const companyBio = document.getElementById('companyBio');
    const charCount = document.querySelector('.char-count');

    if (companyBio && charCount) {
        companyBio.addEventListener('input', function() {
            const currentLength = this.value.length;
            const maxLength = 500;
            charCount.textContent = `${currentLength} / ${maxLength} characters`;
            
            // Change color when approaching limit
            if (currentLength > maxLength * 0.9) {
                charCount.style.color = '#dc3545';
            } else if (currentLength > maxLength * 0.7) {
                charCount.style.color = '#ffc107';
            } else {
                charCount.style.color = '#6c757d';
            }
        });
    }
}

// ============================================
// PASSWORD VALIDATION
// ============================================
function initializePasswordValidation() {
    const newPassword = document.getElementById('newPassword');
    const requirements = document.querySelectorAll('.requirement');

    if (newPassword && requirements.length > 0) {
        newPassword.addEventListener('input', function() {
            const password = this.value;
            
            // Check each requirement
            const checks = {
                length: password.length >= 8,
                uppercase: /[A-Z]/.test(password),
                lowercase: /[a-z]/.test(password),
                number: /[0-9]/.test(password)
            };
            
            // Update UI for each requirement
            requirements.forEach(req => {
                const type = req.getAttribute('data-requirement');
                const icon = req.querySelector('i');
                
                if (checks[type]) {
                    req.classList.add('valid');
                    icon.classList.remove('bi-x-circle');
                    icon.classList.add('bi-check-circle');
                } else {
                    req.classList.remove('valid');
                    icon.classList.remove('bi-check-circle');
                    icon.classList.add('bi-x-circle');
                }
            });
        });
    }

    // Password Confirmation Validation
    const confirmPassword = document.getElementById('confirmPassword');

    if (newPassword && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            if (this.value && this.value !== newPassword.value) {
                this.style.borderColor = '#dc3545';
            } else {
                this.style.borderColor = '';
            }
        });
    }
}

// ============================================
// SAVE ALL CHANGES BUTTON
// ============================================
const saveAllBtn = document.querySelector('.btn-save-all');

if (saveAllBtn) {
    saveAllBtn.addEventListener('click', function() {
        // Get active section
        const activeSection = document.querySelector('.settings-section.active');
        
        if (activeSection) {
            const saveBtn = activeSection.querySelector('.btn-save');
            if (saveBtn) {
                saveBtn.click();
            } else {
                // If no save button in section, show general success
                alert('All changes saved successfully!');
            }
        }
    });
}

// ============================================
// TOGGLE SWITCHES
// ============================================
function initializeToggleSwitches() {
    const toggleSwitches = document.querySelectorAll('.toggle-switch input[type="checkbox"]');

    toggleSwitches.forEach(toggle => {
        toggle.addEventListener('change', function() {
            console.log('Toggle changed:', this.checked);
            // Add your toggle change logic here
        });
    });
}

// ============================================
// DANGER ZONE ACTIONS
// ============================================
function initializeDangerZoneActions() {
    const deactivateBtn = document.querySelector('.btn-danger-action:not(.critical)');
    
    // Deactivate account logic
    if (deactivateBtn) {
        deactivateBtn.addEventListener('click', function() {
            const confirmed = confirm('Are you sure you want to deactivate your account? You can reactivate it anytime by logging back in.');
            
            if (confirmed) {
                console.log('Deactivating account...');
                // Add deactivation logic here
                alert('Account deactivated successfully');
            }
        });
    }

    // Initialize delete account modal
    initializeDeleteModal();
}

// ============================================
// DELETE ACCOUNT MODAL
// ============================================
function initializeDeleteModal() {
    const deleteBtn = document.getElementById('deleteAccountBtn');
    const modal = document.getElementById('deleteModal');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelDeleteBtn');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const confirmInput = document.getElementById('deleteConfirmInput');
    const errorMessage = document.getElementById('deleteInputError');

    if (!deleteBtn || !modal) return;

    // Open modal
    deleteBtn.addEventListener('click', function() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        // Reset input
        confirmInput.value = '';
        confirmBtn.disabled = true;
        errorMessage.classList.remove('show');
        confirmInput.classList.remove('error');
    });

    // Close modal function
    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        confirmInput.value = '';
        confirmBtn.disabled = true;
        errorMessage.classList.remove('show');
        confirmInput.classList.remove('error');
    }

    // Close modal on X button
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }

    // Close modal on Cancel button
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // Close modal on overlay click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Validate input
    if (confirmInput) {
        confirmInput.addEventListener('input', function() {
            const value = this.value.trim();
            
            if (value === 'DELETE') {
                confirmBtn.disabled = false;
                errorMessage.classList.remove('show');
                this.classList.remove('error');
            } else {
                confirmBtn.disabled = true;
                if (value.length > 0) {
                    errorMessage.classList.add('show');
                    this.classList.add('error');
                } else {
                    errorMessage.classList.remove('show');
                    this.classList.remove('error');
                }
            }
        });

        // Handle Enter key in input
        confirmInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim() === 'DELETE') {
                confirmBtn.click();
            }
        });
    }

    // Confirm delete button
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (confirmInput.value.trim() === 'DELETE') {
                // Get the company UUID from data attribute
                const companyUuid = this.getAttribute('data-company-uuid');
                
                if (!companyUuid) {
                    console.error('Company UUID not found');
                    alert('Error: Company ID not found. Please refresh the page and try again.');
                    return;
                }
                
                // Create form and submit
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/company/delete/company`;
                
                // Try to get CSRF token from various sources
                let csrfToken = null;
                
                // Method 1: Get from cookie
                const cookieValue = document.cookie
                    .split('; ')
                    .find(row => row.startsWith('csrftoken='))
                    ?.split('=')[1];
                
                if (cookieValue) {
                    csrfToken = cookieValue;
                }
                
                // Method 2: Get from existing form on page
                if (!csrfToken) {
                    const existingToken = document.querySelector('[name=csrfmiddlewaretoken]');
                    if (existingToken) {
                        csrfToken = existingToken.value;
                    }
                }
                
                // Method 3: Get from meta tag (if you add one)
                if (!csrfToken) {
                    const metaToken = document.querySelector('meta[name="csrf-token"]');
                    if (metaToken) {
                        csrfToken = metaToken.getAttribute('content');
                    }
                }
                
                if (!csrfToken) {
                    console.error('CSRF token not found');
                    alert('Error: Security token not found. Please refresh the page and try again.');
                    return;
                }
                
                // Add CSRF token to form
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
                
                // Add to body and submit
                document.body.appendChild(form);
                form.submit();
            }
        });
    }
}

// ============================================
// FORM VALIDATION
// ============================================
function initializeFormValidation() {
    const emailInput = document.getElementById('emailAddress');
    const phoneInput = document.getElementById('phoneNumber');

    // Email validation
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (this.value && !validateEmail(this.value)) {
                this.style.borderColor = '#dc3545';
                // You could show an error message here
            } else {
                this.style.borderColor = '';
            }
        });
    }

    // Phone validation
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            if (this.value && !validatePhone(this.value)) {
                this.style.borderColor = '#dc3545';
                // You could show an error message here
            } else {
                this.style.borderColor = '';
            }
        });
    }
}

// Validation helper functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\+?[0-9]{10,14}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// ============================================
// AUTO-SAVE INDICATOR (OPTIONAL)
// ============================================
function initializeAutoSave() {
    let saveTimeout;
    const formInputs = document.querySelectorAll('.form-control');

    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Clear existing timeout
            clearTimeout(saveTimeout);
            
            // Show "unsaved changes" indicator
            // You could add a visual indicator here
            
            // Set new timeout for auto-save
            saveTimeout = setTimeout(() => {
                console.log('Auto-saving...');
                // Add auto-save logic here
            }, 2000); // Auto-save after 2 seconds of inactivity
        });
    });
}

// ============================================
// SMOOTH SCROLL FOR MOBILE
// ============================================
function initializeMobileScroll() {
    const navItems = document.querySelectorAll('.nav-item');
    
    if (window.innerWidth <= 768) {
        navItems.forEach(item => {
            item.addEventListener('click', function() {
                // Scroll to top of content area on mobile
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        });
    }
}