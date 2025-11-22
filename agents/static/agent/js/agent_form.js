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