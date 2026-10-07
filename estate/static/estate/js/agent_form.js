// Agent Profile Form JavaScript - Handles Dynamic Formsets

(function() {
    'use strict';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeFormsets();
    });

    function initializeFormsets() {
        // Experience Formset
        setupFormset({
            containerId: 'experience-container',
            templateId: 'exp-template',
            addButtonId: 'add-experience',
            managementId: 'exp-management',
            formsetType: 'experience'
        });

        // Social Links Formset
        setupFormset({
            containerId: 'social-container',
            templateId: 'soc-template',
            addButtonId: 'add-social',
            managementId: 'soc-management',
            formsetType: 'social'
        });
    }

    function setupFormset(config) {
        const container = document.getElementById(config.containerId);
        const template = document.getElementById(config.templateId);
        const addButton = document.getElementById(config.addButtonId);
        const managementDiv = document.getElementById(config.managementId);

        if (!container || !template || !addButton || !managementDiv) {
            console.error('Required elements not found for formset:', config.formsetType);
            return;
        }

        const prefix = template.dataset.prefix;

        // Add new form
        addButton.addEventListener('click', function(e) {
            e.preventDefault();
            addForm(container, template, managementDiv, prefix, config.formsetType);
        });

        // Setup existing remove buttons
        setupRemoveButtons(container, managementDiv, prefix, config.formsetType);
    }

    function addForm(container, template, managementDiv, prefix, formsetType) {
        // Get current form count
        const totalFormsInput = managementDiv.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
        if (!totalFormsInput) {
            console.error('TOTAL_FORMS input not found');
            return;
        }

        const formIdx = parseInt(totalFormsInput.value);

        // Create template HTML from the first form structure
        const firstForm = container.querySelector('.formset-item');
        if (!firstForm) {
            console.error('No existing form to clone from');
            return;
        }

        // Clone the first form
        const newForm = firstForm.cloneNode(true);
        
        // Clear all input values
        const inputs = newForm.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else if (input.type !== 'hidden') {
                input.value = '';
            }
        });

        // Update form index
        newForm.dataset.formIndex = formIdx;

        // Update form number display
        const formNumber = newForm.querySelector('.form-number');
        if (formNumber) {
            formNumber.textContent = formIdx + 1;
        }

        // Update all name and id attributes
        updateFormIndexes(newForm, prefix, formIdx);

        // Add remove button if it doesn't exist
        let removeBtn = newForm.querySelector('.btn-remove-form');
        if (!removeBtn) {
            const header = newForm.querySelector('.formset-header');
            if (header) {
                removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn-remove-form';
                removeBtn.dataset.formset = formsetType;
                removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
                header.appendChild(removeBtn);
            }
        }

        // Setup remove button handler
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                removeForm(newForm, managementDiv, prefix, formsetType);
            });
        }

        // Append to container
        container.appendChild(newForm);

        // Update total forms count
        totalFormsInput.value = formIdx + 1;

        // Scroll to new form
        newForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Add animation
        newForm.style.opacity = '0';
        newForm.style.transform = 'translateY(20px)';
        setTimeout(() => {
            newForm.style.transition = 'all 0.3s ease';
            newForm.style.opacity = '1';
            newForm.style.transform = 'translateY(0)';
        }, 10);
    }

    function updateFormIndexes(formElement, prefix, newIndex) {
        // Update all input, select, and textarea elements
        const fields = formElement.querySelectorAll('input, select, textarea, label');
        
        fields.forEach(field => {
            // Update name attribute
            if (field.name) {
                field.name = field.name.replace(
                    new RegExp(`${prefix}-(\\d+)-`),
                    `${prefix}-${newIndex}-`
                );
            }

            // Update id attribute
            if (field.id) {
                field.id = field.id.replace(
                    new RegExp(`id_${prefix}-(\\d+)-`),
                    `id_${prefix}-${newIndex}-`
                );
            }

            // Update for attribute (for labels)
            if (field.htmlFor) {
                field.htmlFor = field.htmlFor.replace(
                    new RegExp(`id_${prefix}-(\\d+)-`),
                    `id_${prefix}-${newIndex}-`
                );
            }
        });
    }

    function setupRemoveButtons(container, managementDiv, prefix, formsetType) {
        const removeButtons = container.querySelectorAll('.btn-remove-form');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const formItem = button.closest('.formset-item');
                removeForm(formItem, managementDiv, prefix, formsetType);
            });
        });
    }

    function removeForm(formElement, managementDiv, prefix, formsetType) {
        const container = formElement.parentElement;
        
        // Check if this is an existing form (has DELETE checkbox)
        const deleteCheckbox = formElement.querySelector(`input[name*="-DELETE"]`);
        
        if (deleteCheckbox) {
            // Mark for deletion instead of removing
            deleteCheckbox.checked = true;
            formElement.style.display = 'none';
        } else {
            // Remove the form element with animation
            formElement.style.transition = 'all 0.3s ease';
            formElement.style.opacity = '0';
            formElement.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                formElement.remove();
                
                // Update form numbers
                updateFormNumbers(container);
                
                // Update TOTAL_FORMS count
                const totalFormsInput = managementDiv.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
                if (totalFormsInput) {
                    const visibleForms = container.querySelectorAll('.formset-item:not([style*="display: none"])');
                    totalFormsInput.value = visibleForms.length;
                    
                    // Reindex all forms
                    reindexForms(container, prefix);
                }
            }, 300);
        }
    }

    function updateFormNumbers(container) {
        const forms = container.querySelectorAll('.formset-item:not([style*="display: none"])');
        forms.forEach((form, index) => {
            const formNumber = form.querySelector('.form-number');
            if (formNumber) {
                formNumber.textContent = index + 1;
            }
            form.dataset.formIndex = index;
        });
    }

    function reindexForms(container, prefix) {
        const forms = container.querySelectorAll('.formset-item:not([style*="display: none"])');
        forms.forEach((form, index) => {
            updateFormIndexes(form, prefix, index);
        });
    }

    // Form validation helper
    function validateForm() {
        const form = document.getElementById('agent-profile-form');
        if (!form) return true;

        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    }

    // Add form submission handler
    const form = document.getElementById('agent-profile-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Remove animation styles before submission
            const formItems = form.querySelectorAll('.formset-item');
            formItems.forEach(item => {
                item.style.transition = '';
                item.style.opacity = '';
                item.style.transform = '';
            });
        });
    }

})();