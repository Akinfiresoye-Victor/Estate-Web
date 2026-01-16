// Agent Registration Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Multi-step form navigation
    const formSteps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.step');
    let currentStep = 1;

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
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            } else {
                field.style.borderColor = '#e5e7eb';
            }
        });

        if (!isValid && firstInvalidField) {
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidField.focus();
            alert('Please fill in all required fields before proceeding.');
        }

        return isValid;
    }

    // Universal Agent Toggle
    const universalAgentCheckbox = document.getElementById('id_universal_agent');
    const universalAgentFields = document.getElementById('universalAgentFields');
    const agencyCheckbox = document.getElementById('id_agency');
    const agencyNameField = document.getElementById('agencyNameField');

    if (universalAgentCheckbox) {
        universalAgentCheckbox.addEventListener('change', function() {
            if (this.checked) {
                universalAgentFields.style.display = 'grid';
            } else {
                universalAgentFields.style.display = 'none';
                // Reset universal agent fields
                if (agencyCheckbox) agencyCheckbox.checked = false;
                if (agencyNameField) agencyNameField.style.display = 'none';
            }
        });
    }

    if (agencyCheckbox) {
        agencyCheckbox.addEventListener('change', function() {
            if (this.checked) {
                agencyNameField.style.display = 'block';
            } else {
                agencyNameField.style.display = 'none';
            }
        });
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
            const totalForms = document.querySelector('input[name="experiences-TOTAL_FORMS"]');
            const formCount = experienceForms.querySelectorAll('.experience-item').length;
            
            // Clone the first experience form
            const newForm = experienceForms.querySelector('.experience-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.exp-number').textContent = formCount + 1;
            
            // Clear input values
            newForm.querySelectorAll('input').forEach(input => {
                if (input.type !== 'hidden') {
                    input.value = '';
                }
                // Update input names and ids
                input.name = input.name.replace(/experiences-\d+/, `experiences-${formCount}`);
                input.id = input.id.replace(/id_experiences-\d+/, `id_experiences-${formCount}`);
            });
            
            // Add remove button if not present
            if (!newForm.querySelector('.btn-remove-exp')) {
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn-remove-exp';
                removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
                newForm.querySelector('.experience-header').appendChild(removeBtn);
                
                // Add remove functionality
                removeBtn.addEventListener('click', function() {
                    newForm.remove();
                    updateFormNumbers('.experience-item', '.exp-number');
                    updateTotalForms('experiences-TOTAL_FORMS');
                });
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
            
            // Clear input values
            newForm.querySelectorAll('input, select').forEach(input => {
                if (input.type !== 'hidden') {
                    input.value = '';
                }
                // Update input names and ids
                input.name = input.name.replace(/social-\d+/, `social-${formCount}`);
                input.id = input.id.replace(/id_social-\d+/, `id_social-${formCount}`);
            });
            
            // Add remove button if not present
            if (!newForm.querySelector('.btn-remove-social')) {
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn-remove-social';
                removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
                newForm.querySelector('.social-header').appendChild(removeBtn);
                
                // Add remove functionality
                removeBtn.addEventListener('click', function() {
                    newForm.remove();
                    updateFormNumbers('.social-item', '.social-number');
                    updateTotalForms('social-TOTAL_FORMS');
                });
            }
            
            socialForms.appendChild(newForm);
            totalForms.value = formCount + 1;
        });
    }

    // Remove experience functionality for initial forms
    document.querySelectorAll('.btn-remove-exp').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.experience-item').remove();
            updateFormNumbers('.experience-item', '.exp-number');
            updateTotalForms('experiences-TOTAL_FORMS');
        });
    });

    // Remove social functionality for initial forms
    document.querySelectorAll('.btn-remove-social').forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.social-item').remove();
            updateFormNumbers('.social-item', '.social-number');
            updateTotalForms('social-TOTAL_FORMS');
        });
    });

    function updateFormNumbers(itemSelector, numberSelector) {
        document.querySelectorAll(itemSelector).forEach((item, index) => {
            item.querySelector(numberSelector).textContent = index + 1;
        });
    }

    function updateTotalForms(formName) {
        const totalForms = document.querySelector(`input[name="${formName}"]`);
        if (totalForms) {
            const prefix = formName.replace('-TOTAL_FORMS', '');
            const itemCount = document.querySelectorAll(`[name^="${prefix}-"]`).length / 
                             document.querySelectorAll(`input[name^="${prefix}-0-"]`).length;
            totalForms.value = Math.floor(itemCount);
        }
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
            
            // Optional: Log form data for debugging
            console.log('Form is submitting...');
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
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

    // Initialize: Check if universal agent is already checked (for form errors)
    if (universalAgentCheckbox && universalAgentCheckbox.checked) {
        universalAgentFields.style.display = 'grid';
    }

    if (agencyCheckbox && agencyCheckbox.checked) {
        agencyNameField.style.display = 'block';
    }

});
// Add this to your agent_form.js file or in a <script> tag at the bottom of the template

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== Multi-Step Form Navigation ==========
    let currentStep = 1;
    const totalSteps = 3;
    
    // Navigation functions
    function showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show current step
        const currentStepElement = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
        
        // Update progress indicators
        document.querySelectorAll('.step').forEach((step, index) => {
            if (index < stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        currentStep = stepNumber;
    }
    
    // Next button handlers
    document.querySelectorAll('.btn-next').forEach(button => {
        button.addEventListener('click', function() {
            // Basic validation for current step
            const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            const requiredFields = currentStepElement.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (isValid && currentStep < totalSteps) {
                showStep(currentStep + 1);
                window.scrollTo(0, 0);
            } else if (!isValid) {
                alert('Please fill in all required fields before proceeding.');
            }
        });
    });
    
    // Previous button handlers
    document.querySelectorAll('.btn-prev').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep > 1) {
                showStep(currentStep - 1);
                window.scrollTo(0, 0);
            }
        });
    });
    
    // ========== Universal Agent Toggle ==========
    const universalCheckbox = document.querySelector('input[name="universal_agent"]');
    const universalFields = document.getElementById('universalAgentFields');
    
    if (universalCheckbox && universalFields) {
        universalCheckbox.addEventListener('change', function() {
            universalFields.style.display = this.checked ? 'contents' : 'none';
        });
    }
    
    // Agency checkbox toggle
    const agencyCheckbox = document.getElementById('id_agency');
    const agencyNameField = document.getElementById('agencyNameField');
    
    if (agencyCheckbox && agencyNameField) {
        agencyCheckbox.addEventListener('change', function() {
            agencyNameField.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // ========== File Upload Display ==========
    document.querySelectorAll('.file-input').forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const fileNameDisplay = this.parentElement.querySelector('.file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });
    
    // ========== Dynamic Formset Management ==========
    
    // Experience Formset
    const addExperienceBtn = document.getElementById('addExperience');
    if (addExperienceBtn) {
        addExperienceBtn.addEventListener('click', function() {
            const experienceForms = document.querySelector('.experience-forms');
            const totalForms = document.querySelector('input[name="exp-TOTAL_FORMS"]');
            const formNum = parseInt(totalForms.value);
            
            // Clone the first experience item
            const newForm = document.querySelector('.experience-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.exp-number').textContent = formNum + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`exp-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `exp-${formNum}-`);
            
            // Clear values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-exp');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
            }
            
            // Add to DOM
            experienceForms.appendChild(newForm);
            
            // Update total forms count
            totalForms.value = formNum + 1;
            
            // Attach delete handler to new form
            attachDeleteHandler(newForm.querySelector('.btn-remove-exp'));
        });
    }
    
    // Social Links Formset
    const addSocialBtn = document.getElementById('addSocial');
    if (addSocialBtn) {
        addSocialBtn.addEventListener('click', function() {
            const socialForms = document.querySelector('.social-forms');
            const totalForms = document.querySelector('input[name="social-TOTAL_FORMS"]');
            const formNum = parseInt(totalForms.value);
            
            // Clone the first social item
            const newForm = document.querySelector('.social-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.social-number').textContent = formNum + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`social-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `social-${formNum}-`);
            
            // Clear values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-social');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
            }
            
            // Add to DOM
            socialForms.appendChild(newForm);
            
            // Update total forms count
            totalForms.value = formNum + 1;
            
            // Attach delete handler to new form
            attachDeleteHandler(newForm.querySelector('.btn-remove-social'));
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
                totalForms.value = parseInt(totalForms.value) - 1;
            }
        });
    }
    
    // Attach delete handlers to existing forms
    document.querySelectorAll('.btn-remove-exp, .btn-remove-social').forEach(button => {
        attachDeleteHandler(button);
    });
    
    // ========== Form Submission ==========
    const agentForm = document.getElementById('agentForm');
    if (agentForm) {
        agentForm.addEventListener('submit', function(e) {
            // Show loading state
            const submitBtn = document.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Submitting...';
            }
        });
    }
    
    // Auto-dismiss messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
// Add this to your agent_form.js file or in a <script> tag at the bottom of the template

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== Multi-Step Form Navigation ==========
    let currentStep = 1;
    const totalSteps = 3;
    
    // Navigation functions
    function showStep(stepNumber) {
        // Hide all steps
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show current step
        const currentStepElement = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
        
        // Update progress indicators
        document.querySelectorAll('.step').forEach((step, index) => {
            if (index < stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        currentStep = stepNumber;
    }
    
    // Next button handlers
    document.querySelectorAll('.btn-next').forEach(button => {
        button.addEventListener('click', function() {
            // Basic validation for current step
            const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            const requiredFields = currentStepElement.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (isValid && currentStep < totalSteps) {
                showStep(currentStep + 1);
                window.scrollTo(0, 0);
            } else if (!isValid) {
                alert('Please fill in all required fields before proceeding.');
            }
        });
    });
    
    // Previous button handlers
    document.querySelectorAll('.btn-prev').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep > 1) {
                showStep(currentStep - 1);
                window.scrollTo(0, 0);
            }
        });
    });
    
    // ========== Universal Agent Toggle ==========
    const universalCheckbox = document.querySelector('input[name="universal_agent"]');
    const universalFields = document.getElementById('universalAgentFields');
    
    if (universalCheckbox && universalFields) {
        universalCheckbox.addEventListener('change', function() {
            universalFields.style.display = this.checked ? 'contents' : 'none';
        });
    }
    
    // Agency checkbox toggle
    const agencyCheckbox = document.getElementById('id_agency');
    const agencyNameField = document.getElementById('agencyNameField');
    
    if (agencyCheckbox && agencyNameField) {
        agencyCheckbox.addEventListener('change', function() {
            agencyNameField.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // ========== File Upload Display ==========
    document.querySelectorAll('.file-input').forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file chosen';
            const fileNameDisplay = this.parentElement.querySelector('.file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });
    
    // ========== Dynamic Formset Management ==========
    
    // Experience Formset
    const addExperienceBtn = document.getElementById('addExperience');
    if (addExperienceBtn) {
        addExperienceBtn.addEventListener('click', function() {
            const experienceForms = document.querySelector('.experience-forms');
            const totalForms = document.querySelector('input[name="exp-TOTAL_FORMS"]');
            const formNum = parseInt(totalForms.value);
            
            // Clone the first experience item
            const newForm = document.querySelector('.experience-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.exp-number').textContent = formNum + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`exp-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `exp-${formNum}-`);
            
            // Clear values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-exp');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
            }
            
            // Add to DOM
            experienceForms.appendChild(newForm);
            
            // Update total forms count
            totalForms.value = formNum + 1;
            
            // Attach delete handler to new form
            attachDeleteHandler(newForm.querySelector('.btn-remove-exp'));
        });
    }
    
    // Social Links Formset
    const addSocialBtn = document.getElementById('addSocial');
    if (addSocialBtn) {
        addSocialBtn.addEventListener('click', function() {
            const socialForms = document.querySelector('.social-forms');
            const totalForms = document.querySelector('input[name="social-TOTAL_FORMS"]');
            const formNum = parseInt(totalForms.value);
            
            // Clone the first social item
            const newForm = document.querySelector('.social-item').cloneNode(true);
            
            // Update form number
            newForm.querySelector('.social-number').textContent = formNum + 1;
            
            // Update form field names and IDs
            const formRegex = new RegExp(`social-(\\d+)-`, 'g');
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `social-${formNum}-`);
            
            // Clear values
            newForm.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.type !== 'hidden') {
                    field.value = '';
                }
            });
            
            // Show delete button
            const deleteBtn = newForm.querySelector('.btn-remove-social');
            if (deleteBtn) {
                deleteBtn.style.display = 'block';
            }
            
            // Add to DOM
            socialForms.appendChild(newForm);
            
            // Update total forms count
            totalForms.value = formNum + 1;
            
            // Attach delete handler to new form
            attachDeleteHandler(newForm.querySelector('.btn-remove-social'));
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
                totalForms.value = parseInt(totalForms.value) - 1;
            }
        });
    }
    
    // Attach delete handlers to existing forms
    document.querySelectorAll('.btn-remove-exp, .btn-remove-social').forEach(button => {
        attachDeleteHandler(button);
    });
    
    // ========== Form Submission ==========
    const agentForm = document.getElementById('agentForm');
    if (agentForm) {
        agentForm.addEventListener('submit', function(e) {
            // Show loading state
            const submitBtn = document.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Submitting...';
            }
        });
    }
    
    // Auto-dismiss messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // ========== Word Count Limiter for Bio/Work Summary ==========
    const bioTextarea = document.querySelector('textarea[name="bio"]');
    
    if (bioTextarea) {
        // Create word counter display
        const counterDiv = document.createElement('div');
        counterDiv.className = 'word-counter';
        counterDiv.style.cssText = `
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: #6c757d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        `;
        
        const wordCountSpan = document.createElement('span');
        wordCountSpan.className = 'word-count-text';
        
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
        progressFill.className = 'word-progress-fill';
        progressFill.style.cssText = `
            height: 100%;
            background: #28a745;
            width: 0%;
            transition: all 0.3s ease;
        `;
        
        progressBar.appendChild(progressFill);
        counterDiv.appendChild(wordCountSpan);
        counterDiv.appendChild(progressBar);
        
        bioTextarea.parentElement.appendChild(counterDiv);
        
        // Function to count words
        function countWords(text) {
            const trimmed = text.trim();
            if (trimmed === '') return 0;
            return trimmed.split(/\s+/).length;
        }
        
        // Function to update counter
        function updateWordCount() {
            const text = bioTextarea.value;
            const wordCount = countWords(text);
            const maxWords = 250;
            const percentage = (wordCount / maxWords) * 100;
            
            // Update text
            wordCountSpan.textContent = `${wordCount} / ${maxWords} words`;
            
            // Update progress bar
            progressFill.style.width = `${Math.min(percentage, 100)}%`;
            
            // Change color based on word count
            if (wordCount > maxWords) {
                wordCountSpan.style.color = '#dc3545';
                progressFill.style.background = '#dc3545';
                bioTextarea.classList.add('error');
            } else if (wordCount > maxWords * 0.9) {
                wordCountSpan.style.color = '#ffc107';
                progressFill.style.background = '#ffc107';
                bioTextarea.classList.remove('error');
            } else {
                wordCountSpan.style.color = '#28a745';
                progressFill.style.background = '#28a745';
                bioTextarea.classList.remove('error');
            }
            
            // Prevent typing if over limit
            if (wordCount > maxWords) {
                // Get words array
                const words = text.trim().split(/\s+/);
                // Keep only first 250 words
                const limitedWords = words.slice(0, maxWords);
                // Set textarea value to limited words
                bioTextarea.value = limitedWords.join(' ');
                
                // Show warning message
                showWordLimitWarning();
            }
        }
        
        // Function to show warning
        function showWordLimitWarning() {
            // Check if warning already exists
            if (document.querySelector('.word-limit-warning')) return;
            
            const warning = document.createElement('div');
            warning.className = 'word-limit-warning';
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
                <span>You've reached the 250-word limit. Additional words will be automatically removed.</span>
            `;
            
            bioTextarea.parentElement.appendChild(warning);
            
            // Remove warning after 3 seconds
            setTimeout(() => {
                warning.style.animation = 'slideUp 0.3s ease';
                setTimeout(() => warning.remove(), 300);
            }, 3000);
        }
        
        // Add keydown listener to show warning on attempt
        bioTextarea.addEventListener('keydown', function(e) {
            const wordCount = countWords(this.value);
            
            // Allow backspace, delete, arrow keys, etc.
            const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab'];
            
            if (wordCount >= 250 && !allowedKeys.includes(e.key) && e.key !== ' ' && !e.ctrlKey && !e.metaKey) {
                // Check if adding this would create a new word
                const cursorPos = this.selectionStart;
                const textBefore = this.value.substring(0, cursorPos);
                const textAfter = this.value.substring(cursorPos);
                
                // If last character before cursor is a space or we're at the start, we're starting a new word
                if (textBefore === '' || textBefore.slice(-1) === ' ') {
                    e.preventDefault();
                    showWordLimitWarning();
                }
            }
        });
        
        // Update on input
        bioTextarea.addEventListener('input', updateWordCount);
        
        // Update on paste
        bioTextarea.addEventListener('paste', function() {
            setTimeout(updateWordCount, 0);
        });
        
        // Initial count
        updateWordCount();
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