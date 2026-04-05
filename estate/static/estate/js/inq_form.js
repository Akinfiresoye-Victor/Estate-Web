// Inquiry Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Get form and elements
    const form = document.getElementById('inquiryForm');
    const submitBtn = form?.querySelector('.btn-submit');
    
    // Set minimum date for schedule tour to today
    const scheduleTourInput = document.getElementById('id_schedule_tour');
    if (scheduleTourInput) {
        const today = new Date().toISOString().split('T')[0];
        scheduleTourInput.setAttribute('min', today);
    }

    // Phone number formatting
    const phoneInput = document.querySelector('input[name="phone_no"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Remove all non-numeric characters except + at the start
            let value = e.target.value.replace(/[^\d+]/g, '');
            
            // Ensure + is only at the beginning
            if (value.indexOf('+') > 0) {
                value = value.replace(/\+/g, '');
            }
            
            e.target.value = value;
        });

        // Add validation on blur
        phoneInput.addEventListener('blur', function(e) {
            const value = e.target.value.trim();
            if (value && !value.match(/^\+?[\d\s-]{10,}$/)) {
                showFieldError(phoneInput, 'Please enter a valid phone number');
            } else {
                clearFieldError(phoneInput);
            }
        });
    }

    // Email validation
    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) {
        emailInput.addEventListener('blur', function(e) {
            const value = e.target.value.trim();
            if (value && !value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                showFieldError(emailInput, 'Please enter a valid email address');
            } else {
                clearFieldError(emailInput);
            }
        });
    }

    // Character counter for inquiry message
    const messageTextarea = document.querySelector('textarea[name="inquiry_message"]');
    if (messageTextarea) {
        const maxLength = 500;
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.cssText = 'text-align: right; font-size: 0.875rem; color: var(--text-light); margin-top: 0.5rem;';
        messageTextarea.parentElement.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - messageTextarea.value.length;
            counter.textContent = `${messageTextarea.value.length} / ${maxLength} characters`;
            
            if (remaining < 50) {
                counter.style.color = 'var(--warning-color)';
            } else if (remaining < 0) {
                counter.style.color = 'var(--danger-color)';
            } else {
                counter.style.color = 'var(--text-light)';
            }
        }

        messageTextarea.addEventListener('input', updateCounter);
        messageTextarea.setAttribute('maxlength', maxLength);
        updateCounter();
    }

    // Form validation on submit
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');

            // Clear all previous errors
            document.querySelectorAll('.invalid-feedback').forEach(el => {
                if (!el.classList.contains('d-block')) {
                    el.remove();
                }
            });

            // Validate required fields
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }
            });

            // Additional validation for phone
            if (phoneInput && phoneInput.value.trim()) {
                if (!phoneInput.value.match(/^\+?[\d\s-]{10,}$/)) {
                    showFieldError(phoneInput, 'Please enter a valid phone number (minimum 10 digits)');
                    isValid = false;
                }
            }

            // Additional validation for email if provided
            if (emailInput && emailInput.value.trim()) {
                if (!emailInput.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                    showFieldError(emailInput, 'Please enter a valid email address');
                    isValid = false;
                }
            }

            // If form is not valid, prevent submission
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.invalid-feedback');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                // Show error notification
                showNotification('Please fix the errors before submitting', 'error');
                return false;
            }

            // Show loading state on submit button
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Sending...';
            }
        });
    }

    // Helper function to show field error
    function showFieldError(field, message) {
        clearFieldError(field);
        
        field.classList.add('is-invalid');
        field.style.borderColor = 'var(--danger-color)';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        
        field.parentElement.appendChild(errorDiv);
    }

    // Helper function to clear field error
    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        field.style.borderColor = '';
        
        const existingError = field.parentElement.querySelector('.invalid-feedback');
        if (existingError && !existingError.classList.contains('d-block')) {
            existingError.remove();
        }
    }

    // Helper function to show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.style.cssText = 'position: fixed; top: 100px; right: 2rem; z-index: 10000; min-width: 300px; animation: slideInRight 0.5s ease;';
        
        const icon = type === 'error' ? 'exclamation-triangle-fill' : 
                     type === 'success' ? 'check-circle-fill' : 'info-circle-fill';
        
        notification.innerHTML = `
            <i class="bi bi-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Real-time field validation feedback
    const allInputs = form?.querySelectorAll('input, textarea, select');
    allInputs?.forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                if (this.value.trim()) {
                    clearFieldError(this);
                }
            }
        });
    });

    // Contact type change handler
    const contactTypeSelect = document.querySelector('select[name="contact_type"]');
    if (contactTypeSelect) {
        contactTypeSelect.addEventListener('change', function() {
            const phoneGroup = phoneInput?.closest('.form-group');
            const emailGroup = emailInput?.closest('.form-group');
            
            // Highlight the selected contact method field
            if (this.value === 'Whatsapp' || this.value === 'Phone') {
                phoneGroup?.classList.add('highlight-field');
                emailGroup?.classList.remove('highlight-field');
            } else if (this.value === 'Email') {
                emailGroup?.classList.add('highlight-field');
                phoneGroup?.classList.remove('highlight-field');
            }
            
            // Add highlight effect
            setTimeout(() => {
                document.querySelectorAll('.highlight-field').forEach(el => {
                    el.classList.remove('highlight-field');
                });
            }, 2000);
        });
    }

    // Add CSS for highlight effect
    const style = document.createElement('style');
    style.textContent = `
        .highlight-field {
            animation: highlightPulse 1s ease;
        }
        
        @keyframes highlightPulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.02);
            }
        }
        
        .highlight-field .form-control {
            border-color: var(--secondary-color) !important;
            box-shadow: 0 0 0 4px rgba(193, 155, 118, 0.2) !important;
        }
    `;
    document.head.appendChild(style);

    // Prevent multiple form submissions
    let isSubmitting = false;
    form?.addEventListener('submit', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            return false;
        }
        isSubmitting = true;
    });

    // Auto-save draft to localStorage (optional feature)
    const draftKey = 'inquiry_form_draft';
    
    // Load draft if exists
    function loadDraft() {
        const draft = localStorage.getItem(draftKey);
        if (draft) {
            try {
                const draftData = JSON.parse(draft);
                Object.keys(draftData).forEach(key => {
                    const field = form?.querySelector(`[name="${key}"]`);
                    if (field && !field.value) {
                        field.value = draftData[key];
                    }
                });
                
                showNotification('Draft restored', 'info');
            } catch (e) {
            }
        }
    }
    
    // Save draft on input
    function saveDraft() {
        const formData = {};
        const inputs = form?.querySelectorAll('input, textarea, select');
        inputs?.forEach(input => {
            if (input.name && input.value) {
                formData[input.name] = input.value;
            }
        });
        
        localStorage.setItem(draftKey, JSON.stringify(formData));
    }
    
    // Load draft on page load
    loadDraft();
    
    // Save draft every 30 seconds
    let draftInterval;
    if (form) {
        draftInterval = setInterval(saveDraft, 30000);
    }
    
    // Clear draft on successful submission
    form?.addEventListener('submit', function(e) {
        if (!e.defaultPrevented) {
            localStorage.removeItem(draftKey);
            clearInterval(draftInterval);
        }
    });

    // Accessibility improvements
    // Add aria-labels to form controls
    allInputs?.forEach(input => {
        const label = input.closest('.form-group')?.querySelector('label');
        if (label && !input.getAttribute('aria-label')) {
            input.setAttribute('aria-label', label.textContent.trim());
        }
    });


});