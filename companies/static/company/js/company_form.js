// Company Profile Form JavaScript - Handles Dynamic Social Links Formset

(function() {
    'use strict';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeSocialLinksFormset();
        initializeFileUploads();
        initializeAlertDismissal();
    });

    function initializeSocialLinksFormset() {
        const container = document.getElementById('socialLinksContainer');
        const addButton = document.querySelector('.btn-add-social');
        
        if (!container || !addButton) {
            console.error('Social links container or add button not found');
            return;
        }

        // Get the prefix from the first form
        const firstForm = container.querySelector('.social-link-item');
        if (!firstForm) {
            console.error('No existing social link form found');
            return;
        }

        // Add new social link
        addButton.addEventListener('click', function(e) {
            e.preventDefault();
            addSocialLinkForm();
        });

        // Setup existing remove buttons
        setupRemoveButtons();
    }

    function addSocialLinkForm() {
        const container = document.getElementById('socialLinksContainer');
        const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
        
        if (!totalFormsInput) {
            console.error('TOTAL_FORMS input not found');
            return;
        }

        const formIdx = parseInt(totalFormsInput.value);
        const prefix = totalFormsInput.name.replace('-TOTAL_FORMS', '');
        
        // Get the first form to clone
        const firstForm = container.querySelector('.social-link-item');
        if (!firstForm) {
            console.error('No form to clone');
            return;
        }

        // Clone the form
        const newForm = firstForm.cloneNode(true);
        
        // Clear all input values
        const inputs = newForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else if (!input.name.includes('TOTAL_FORMS') && 
                       !input.name.includes('INITIAL_FORMS') && 
                       !input.name.includes('MAX_NUM_FORMS') &&
                       !input.name.includes('MIN_NUM_FORMS')) {
                input.value = '';
            }
        });

        // Update all name and id attributes
        updateFormIndexes(newForm, prefix, formIdx);

        // Make sure remove button exists and is visible
        let removeBtn = newForm.querySelector('.btn-remove-social');
        if (removeBtn) {
            removeBtn.style.display = 'flex';
            // Remove old event listener by cloning
            const newRemoveBtn = removeBtn.cloneNode(true);
            removeBtn.parentNode.replaceChild(newRemoveBtn, removeBtn);
            removeBtn = newRemoveBtn;
        }

        // Setup remove button handler
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                removeSocialLinkForm(newForm);
            });
        }

        // Append to container (before management form)
        const managementForm = container.querySelector('input[name$="-TOTAL_FORMS"]').parentElement;
        if (managementForm && managementForm.parentElement === container) {
            container.insertBefore(newForm, managementForm);
        } else {
            container.appendChild(newForm);
        }

        // Update total forms count
        totalFormsInput.value = formIdx + 1;

        // Scroll to new form with smooth animation
        setTimeout(() => {
            newForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);

        // Add entrance animation
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

    function setupRemoveButtons() {
        const removeButtons = document.querySelectorAll('.btn-remove-social');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const formItem = button.closest('.social-link-item');
                removeSocialLinkForm(formItem);
            });
        });
    }

    function removeSocialLinkForm(formElement) {
        const container = document.getElementById('socialLinksContainer');
        const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
        
        // Check if this is an existing form (has DELETE checkbox)
        const deleteCheckbox = formElement.querySelector('input[name$="-DELETE"]');
        
        if (deleteCheckbox) {
            // Mark for deletion instead of removing
            deleteCheckbox.checked = true;
            formElement.style.display = 'none';
        } else {
            // Remove the form element with animation
            formElement.style.transition = 'all 0.3s ease';
            formElement.style.opacity = '0';
            formElement.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                formElement.remove();
                
                // Update TOTAL_FORMS count
                if (totalFormsInput) {
                    const visibleForms = container.querySelectorAll('.social-link-item:not([style*="display: none"])');
                    totalFormsInput.value = visibleForms.length;
                    
                    // Reindex all forms
                    reindexForms(container);
                }
            }, 300);
        }
    }

    function reindexForms(container) {
        const prefix = document.querySelector('input[name$="-TOTAL_FORMS"]').name.replace('-TOTAL_FORMS', '');
        const forms = container.querySelectorAll('.social-link-item:not([style*="display: none"])');
        
        forms.forEach((form, index) => {
            updateFormIndexes(form, prefix, index);
        });
    }

    // File upload previews
    function initializeFileUploads() {
        // Company logo upload
        const logoInput = document.querySelector('input[name="company_logo"]');
        if (logoInput) {
            logoInput.addEventListener('change', function(e) {
                handleFilePreview(e, 'logoPreview', true);
            });
        }

        // Legal certificate upload
        const certInput = document.querySelector('input[name="legal_certificate"]');
        if (certInput) {
            certInput.addEventListener('change', function(e) {
                handleFilePreview(e, 'certPreview', false);
            });
        }
    }

    function handleFilePreview(event, previewId, isImage) {
        const file = event.target.files[0];
        const preview = document.getElementById(previewId);
        const fileLabel = event.target.nextElementSibling;
        const fileText = fileLabel ? fileLabel.querySelector('.file-text') : null;
        
        if (!file) return;
        
        // Update file name
        if (fileText) {
            fileText.textContent = file.name;
        }
        
        // Show preview
        if (preview) {
            if (isImage && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            } else {
                preview.innerHTML = `
                    <div class="file-info">
                        <i class="bi bi-file-earmark-check"></i> 
                        ${file.name}
                    </div>
                `;
            }
        }
    }

    // Auto-dismiss alerts - ONLY dismiss message/notification alerts, NOT file info
    function initializeAlertDismissal() {
        // Wait a bit to ensure DOM is fully loaded
        setTimeout(function() {
            // Only target alerts that are NOT inside .current-file-info
            // AND are either dismissible or Django messages
            const allAlerts = document.querySelectorAll('.alert');
            
            allAlerts.forEach(function(alert) {
                // Skip if this alert is inside current-file-info
                
                
                // Skip if alert has data-permanent attribute
                if (alert.hasAttribute('data-permanent')) {
                    return;
                }
                
                // Only dismiss if it's a message alert or has dismissible class
                const isMessage = alert.closest('.messages') || 
                                 alert.classList.contains('alert-dismissible');
                
                if (isMessage) {
                    setTimeout(function() {
                        alert.classList.remove('show');
                        setTimeout(function() {
                            alert.remove();
                        }, 300);
                    }, 5000);
                }
            });
        }, 100); // Small delay to ensure everything is loaded
    }

})();