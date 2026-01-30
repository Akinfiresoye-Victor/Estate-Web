// Agent Registration Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Multi-step form navigation
    const formSteps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.step');
    let currentStep = 1;
    const totalSteps = 3;

    // Next button functionality
    document.querySelectorAll('.btn-next').forEach(button => {
        button.addEventListener('click', function() {
            if (validateCurrentStep()) {
                if (currentStep < formSteps.length) {
                    currentStep++;
                    updateFormStep();
                }
            }
        });
    });

    // Previous button functionality
    document.querySelectorAll('.btn-prev').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep > 1) {
                currentStep--;
                updateFormStep();
            }
        });
    });

    function updateFormStep() {
        // Update form steps visibility
        formSteps.forEach((step, index) => {
            if (index + 1 === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Update progress steps
        progressSteps.forEach((step, index) => {
            if (index + 1 <= currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function validateCurrentStep() {
        const currentFormStep = document.querySelector(`.form-step[data-step="${currentStep}"]`);
        const requiredFields = currentFormStep.querySelectorAll('input[required], textarea[required], select[required]');
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(field => {
            // Skip hidden fields
            if (field.offsetParent === null) {
                return;
            }
            
            if (!field.value || field.value.trim() === '') {
                field.style.borderColor = '#ef4444';
                field.classList.add('error');
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            } else {
                field.style.borderColor = '#e5e7eb';
                field.classList.remove('error');
            }
        });

        if (!isValid && firstInvalidField) {
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidField.focus();
            alert('Please fill in all required fields before proceeding.');
        }

        return isValid;
    }

    // Agency Toggle
    const agencyCheckbox = document.getElementById('id_agency');
    const agencyNameField = document.getElementById('agencyNameField');

    if (agencyCheckbox && agencyNameField) {
        agencyCheckbox.addEventListener('change', function() {
            if (this.checked) {
                agencyNameField.style.display = 'block';
            } else {
                agencyNameField.style.display = 'none';
            }
        });
        
        // Initialize: Check if agency is already checked (for form errors)
        if (agencyCheckbox.checked) {
            agencyNameField.style.display = 'block';
        }
    }

    // File Upload Display
    const fileInputs = document.querySelectorAll('.file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const fileNameDisplay = this.parentElement.querySelector('.file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });

    // Dynamic Experience Forms
    const addExperienceBtn = document.getElementById('addExperience');
    if (addExperienceBtn) {
        addExperienceBtn.addEventListener('click', function() {
            const experienceForms = document.querySelector('.experience-forms');
            const totalForms = document.querySelector('input[name="exp-TOTAL_FORMS"]');
            const formCount = experienceForms.querySelectorAll('.experience-item').length;
            
            // Clone the first experience form
            const newForm = experienceForms.querySelector('.experience-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.exp-number').textContent = formCount + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`exp-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `exp-${formCount}-`);
            
            // Clear input values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-exp');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
                // Attach delete handler to new form
                attachDeleteHandler(deleteBtn);
            }
            
            experienceForms.appendChild(newForm);
            totalForms.value = formCount + 1;
        });
    }

    // Dynamic Social Links Forms
    const addSocialBtn = document.getElementById('addSocial');
    if (addSocialBtn) {
        addSocialBtn.addEventListener('click', function() {
            const socialForms = document.querySelector('.social-forms');
            const totalForms = document.querySelector('input[name="social-TOTAL_FORMS"]');
            const formCount = socialForms.querySelectorAll('.social-item').length;
            
            // Clone the first social form
            const newForm = socialForms.querySelector('.social-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.social-number').textContent = formCount + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`social-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `social-${formCount}-`);
            
            // Clear input values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-social');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
                // Attach delete handler to new form
                attachDeleteHandler(deleteBtn);
            }
            
            socialForms.appendChild(newForm);
            totalForms.value = formCount + 1;
        });
    }

    // Delete form functionality
    function attachDeleteHandler(button) {
        if (!button) return;
        
        button.addEventListener('click', function() {
            const formItem = this.closest('.experience-item, .social-item');
            const deleteInput = formItem.querySelector('input[name$="-DELETE"]');
            
            if (deleteInput) {
                // Mark for deletion if it's an existing record
                deleteInput.value = 'on';
                formItem.style.display = 'none';
            } else {
                // Just remove from DOM if it's a new form
                formItem.remove();
                
                // Update form count
                const prefix = formItem.classList.contains('experience-item') ? 'exp' : 'social';
                const totalForms = document.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
                if (totalForms) {
                    totalForms.value = parseInt(totalForms.value) - 1;
                }
            }
            
            // Update form numbers
            updateFormNumbers();
        });
    }

    // Attach delete handlers to existing forms
    document.querySelectorAll('.btn-remove-exp, .btn-remove-social').forEach(button => {
        attachDeleteHandler(button);
    });

    function updateFormNumbers() {
        // Update experience form numbers
        document.querySelectorAll('.experience-item').forEach((item, index) => {
            const numberElement = item.querySelector('.exp-number');
            if (numberElement) {
                numberElement.textContent = index + 1;
            }
        });
        
        // Update social form numbers
        document.querySelectorAll('.social-item').forEach((item, index) => {
            const numberElement = item.querySelector('.social-number');
            if (numberElement) {
                numberElement.textContent = index + 1;
            }
        });
    }

    // Form submission with loading state
    const form = document.getElementById('agentForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Don't prevent default, let the form submit naturally
            const submitBtn = form.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
            }
        });
    }

    // Add smooth animations
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.01)';
            this.parentElement.style.transition = 'transform 0.3s ease';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Auto-dismiss messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(alert => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
    
    // ========== Character Count Limiter for Bio/Work Summary ==========
    const bioTextarea = document.querySelector('textarea[name="bio"]');

    if (bioTextarea) {
        // Create counter display
        const counterDiv = document.createElement('div');
        counterDiv.className = 'char-counter';
        counterDiv.style.cssText = `
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: #6c757d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;

        const charCountSpan = document.createElement('span');
        charCountSpan.className = 'char-count-text';

        const progressBar = document.createElement('div');
        progressBar.style.cssText = `
            flex-grow: 1;
            height: 4px;
            background: #e9ecef;
            border-radius: 2px;
            margin: 0 1rem;
            overflow: hidden;
        `;

        const progressFill = document.createElement('div');
        progressFill.className = 'char-progress-fill';
        progressFill.style.cssText = `
            height: 100%;
            background: #28a745;
            width: 0%;
            transition: all 0.3s ease;
        `;

        progressBar.appendChild(progressFill);
        counterDiv.appendChild(charCountSpan);
        counterDiv.appendChild(progressBar);

        bioTextarea.parentElement.appendChild(counterDiv);

        // Function to count characters
        function countChars(text) {
            return text.length;
        }

        // Function to update counter
        function updateCharCount() {
            const text = bioTextarea.value;
            const charCount = countChars(text);
            const maxChars = 1024;
            const percentage = (charCount / maxChars) * 100;

            // Update text
            charCountSpan.textContent = `${charCount} / ${maxChars} characters`;

            // Update progress bar
            progressFill.style.width = `${Math.min(percentage, 100)}%`;

            // Change color based on character count
            if (charCount > maxChars) {
                charCountSpan.style.color = '#dc3545';
                progressFill.style.background = '#dc3545';
                bioTextarea.classList.add('error');
            } else if (charCount > maxChars * 0.9) {
                charCountSpan.style.color = '#ffc107';
                progressFill.style.background = '#ffc107';
                bioTextarea.classList.remove('error');
            } else {
                charCountSpan.style.color = '#28a745';
                progressFill.style.background = '#28a745';
                bioTextarea.classList.remove('error');
            }

            // Truncate if over limit
            if (charCount > maxChars) {
                bioTextarea.value = text.slice(0, maxChars);
                // Show warning message
                showCharLimitWarning();
            }
        }

        // Function to show warning
        function showCharLimitWarning() {
            // Check if warning already exists
            if (document.querySelector('.char-limit-warning')) return;

            const warning = document.createElement('div');
            warning.className = 'char-limit-warning';
            warning.style.cssText = `
                background: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
                padding: 0.75rem 1rem;
                border-radius: 6px;
                margin-top: 0.5rem;
                display: flex;
                align-items: center;
                animation: slideDown 0.3s ease;
            `;
            warning.innerHTML = `
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <span>You've reached the 1024-character limit. Additional characters will be automatically removed.</span>
            `;

            bioTextarea.parentElement.appendChild(warning);

            // Remove warning after 3 seconds
            setTimeout(() => {
                warning.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => warning.remove(), 300);
            }, 3000);
        }

        // Add keydown listener to prevent typing when at limit
        bioTextarea.addEventListener('keydown', function(e) {
            const currentLen = this.value.length;
            const selectionLen = this.selectionEnd - this.selectionStart;

            // Allow backspace, delete, arrow keys, etc.
            const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab'];
            if (allowedKeys.includes(e.key) || e.ctrlKey || e.metaKey) return;

            // If there's no selection and we're already at or beyond limit, block input
            if (currentLen - selectionLen >= 1024) {
                e.preventDefault();
                showCharLimitWarning();
            }
        });

        // Update on input
        bioTextarea.addEventListener('input', updateCharCount);

        // Update on paste
        bioTextarea.addEventListener('paste', function() {
            setTimeout(updateCharCount, 0);
        });

        // Initial count
        updateCharCount();
    }
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideUp {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-10px);
            }
        }
    `;
    document.head.appendChild(style);
});