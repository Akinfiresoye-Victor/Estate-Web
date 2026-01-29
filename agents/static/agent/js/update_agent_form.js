// ===================================
// COMPANY PROFILE UPDATE JS
// ===================================

document.addEventListener('DOMContentLoaded', function() {
  
  // ===================================
  // AUTO-DISMISS ALERTS
  // ===================================
  
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.classList.remove('show');
      setTimeout(function() {
        alert.remove();
      }, 500);
    }, 5000);
  });

  // ===================================
  // FILE INPUT DISPLAY
  // ===================================
  
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

  // ===================================
  // EXPERIENCE MANAGEMENT
  // ===================================
  
  const experienceSection = document.getElementById('experienceSection');
  const addExperienceBtn = document.getElementById('addExperience');
  
  if (experienceSection && addExperienceBtn) {
    const experienceFormsContainer = experienceSection.querySelector('.experience-forms');
    
    // Get total forms count
    let totalExpForms = parseInt(document.querySelector('[name$="-TOTAL_FORMS"]').value) || 0;
    
    // Add new experience
    addExperienceBtn.addEventListener('click', function() {
      const firstForm = experienceFormsContainer.querySelector('.experience-item');
      if (!firstForm) return;
      
      const formCount = experienceFormsContainer.querySelectorAll('.experience-item').length;
      const newForm = firstForm.cloneNode(true);
      
      // Update form index in all inputs
      newForm.innerHTML = newForm.innerHTML.replace(/form-\d+-/g, `form-${formCount}-`);
      newForm.querySelector('.exp-number').textContent = formCount + 1;
      
      // Clear all input values
      newForm.querySelectorAll('input, select, textarea').forEach(input => {
        if (input.type === 'checkbox') {
          input.checked = false;
        } else {
          input.value = '';
        }
      });
      
      // Ensure remove button exists
      if (!newForm.querySelector('.btn-remove-exp')) {
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove-exp';
        removeBtn.innerHTML = '<i class="bi bi-trash"></i> Remove';
        newForm.querySelector('.experience-header').appendChild(removeBtn);
      }
      
      experienceFormsContainer.appendChild(newForm);
      
      // Update total forms count
      totalExpForms++;
      document.querySelector('[name$="-TOTAL_FORMS"]').value = totalExpForms;
      
      updateExperienceNumbers();
    });
    
    // Remove experience
    experienceSection.addEventListener('click', function(e) {
      if (e.target.closest('.btn-remove-exp')) {
        const experienceItem = e.target.closest('.experience-item');
        const deleteCheckbox = experienceItem.querySelector('[name$="-DELETE"]');
        
        if (deleteCheckbox) {
          // Mark for deletion if existing record
          deleteCheckbox.checked = true;
          experienceItem.style.display = 'none';
        } else {
          // Remove from DOM if new record
          experienceItem.remove();
          totalExpForms--;
          document.querySelector('[name$="-TOTAL_FORMS"]').value = totalExpForms;
        }
        
        updateExperienceNumbers();
      }
    });
    
    // Update experience numbers
    function updateExperienceNumbers() {
      const visibleItems = experienceFormsContainer.querySelectorAll('.experience-item:not([style*="display: none"])');
      visibleItems.forEach((item, index) => {
        item.querySelector('.exp-number').textContent = index + 1;
      });
    }
  }

  // ===================================
  // SOCIAL LINKS MANAGEMENT
  // ===================================
  
  const socialSection = document.getElementById('socialSection');
  const addSocialBtn = document.getElementById('addSocial');
  
  if (socialSection && addSocialBtn) {
    const socialFormsContainer = socialSection.querySelector('.social-forms');
    
    // Get total forms count
    const totalFormsInput = socialSection.querySelector('[name$="-TOTAL_FORMS"]');
    let totalSocialForms = parseInt(totalFormsInput.value) || 0;
    
    // Add new social link
    addSocialBtn.addEventListener('click', function() {
      const firstForm = socialFormsContainer.querySelector('.social-item');
      if (!firstForm) return;
      
      const formCount = socialFormsContainer.querySelectorAll('.social-item').length;
      const newForm = firstForm.cloneNode(true);
      
      // Update form index in all inputs
      const formPrefix = totalFormsInput.name.split('-TOTAL_FORMS')[0];
      newForm.innerHTML = newForm.innerHTML.replace(
        new RegExp(formPrefix + '-\\d+-', 'g'), 
        formPrefix + '-' + formCount + '-'
      );
      newForm.querySelector('.social-number').textContent = formCount + 1;
      
      // Clear all input values
      newForm.querySelectorAll('input, select, textarea').forEach(input => {
        if (input.type === 'checkbox') {
          input.checked = false;
        } else {
          input.value = '';
        }
      });
      
      // Ensure remove button exists
      if (!newForm.querySelector('.btn-remove-social')) {
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove-social';
        removeBtn.innerHTML = '<i class="bi bi-trash"></i> Remove';
        newForm.querySelector('.social-header').appendChild(removeBtn);
      }
      
      socialFormsContainer.appendChild(newForm);
      
      // Update total forms count
      totalSocialForms++;
      totalFormsInput.value = totalSocialForms;
      
      updateSocialNumbers();
    });
    
    // Remove social link
    socialSection.addEventListener('click', function(e) {
      if (e.target.closest('.btn-remove-social')) {
        const socialItem = e.target.closest('.social-item');
        const deleteCheckbox = socialItem.querySelector('[name$="-DELETE"]');
        
        if (deleteCheckbox) {
          // Mark for deletion if existing record
          deleteCheckbox.checked = true;
          socialItem.style.display = 'none';
        } else {
          // Remove from DOM if new record
          socialItem.remove();
          totalSocialForms--;
          totalFormsInput.value = totalSocialForms;
        }
        
        updateSocialNumbers();
      }
    });
    
    // Update social link numbers
    function updateSocialNumbers() {
      const visibleItems = socialFormsContainer.querySelectorAll('.social-item:not([style*="display: none"])');
      visibleItems.forEach((item, index) => {
        item.querySelector('.social-number').textContent = index + 1;
      });
    }
  }

  // ===================================
  // FORM VALIDATION
  // ===================================
  
  const form = document.getElementById('companyUpdateForm');
  if (form) {
    form.addEventListener('submit', function(e) {
      const requiredFields = form.querySelectorAll('[required]');
      let isValid = true;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.style.borderColor = 'var(--danger-color)';
          
          // Remove error styling on input
          field.addEventListener('input', function() {
            if (this.value.trim()) {
              this.style.borderColor = '';
            }
          }, { once: true });
        } else {
          field.style.borderColor = '';
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        
        // Scroll to first error
        const firstError = form.querySelector('[style*="border-color"]');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        // Show alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Please fill in all required fields
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const messagesContainer = document.querySelector('.messages-container');
        if (messagesContainer) {
          messagesContainer.appendChild(alertDiv);
          
          // Auto dismiss after 5 seconds
          setTimeout(function() {
            alertDiv.classList.remove('show');
            setTimeout(function() {
              alertDiv.remove();
            }, 500);
          }, 5000);
        }
      }
    });
  }

  // ===================================
  // SMOOTH SCROLL TO TOP ON LOAD
  // ===================================
  
  if (window.location.hash) {
    setTimeout(function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  }

});