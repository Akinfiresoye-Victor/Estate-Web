// Vacancy Form JavaScript
document.addEventListener('DOMContentLoaded', function() {
  
  // ========== Auto-dismiss Alerts ==========
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.classList.remove('show');
      setTimeout(function() {
        alert.remove();
      }, 500);
    }, 5000);
  });

  // ========== Form Validation ==========
  const form = document.getElementById('vacancyForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        isValid = false;
        field.style.borderColor = 'var(--danger-color, #dc3545)';
        
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
      showAlert('danger', 'Please fill in all required fields');
    }
  });

  // ========== Salary Range Validation ==========
  const minPayField = form.querySelector('[name="min_pay"]');
  const maxPayField = form.querySelector('[name="max_pay"]');
  
  if (minPayField && maxPayField) {
    function validateSalaryRange() {
      const minPay = parseFloat(minPayField.value);
      const maxPay = parseFloat(maxPayField.value);
      
      if (minPay && maxPay && minPay > maxPay) {
        maxPayField.setCustomValidity('Maximum salary must be greater than minimum salary');
        maxPayField.reportValidity();
        return false;
      } else {
        maxPayField.setCustomValidity('');
        return true;
      }
    }
    
    minPayField.addEventListener('blur', validateSalaryRange);
    maxPayField.addEventListener('blur', validateSalaryRange);
    
    // Real-time salary preview
    const currencyField = form.querySelector('[name="salary_currency"]');
    const periodField = form.querySelector('[name="salary_period"]');
    
    function updateSalaryPreview() {
      const minPay = parseFloat(minPayField.value);
      const maxPay = parseFloat(maxPayField.value);
      const currency = currencyField ? currencyField.value : 'NGN';
      const period = periodField ? periodField.value : 'Monthly';
      
      const salaryPreview = document.querySelector('.salary-preview');
      if (!salaryPreview) return;
      
      if (minPay || maxPay) {
        let previewText = '<i class="bi bi-currency-dollar"></i> <strong>Salary Range:</strong> ';
        
        const currencySymbols = {
          'NGN': '₦',
          'USD': '$',
          'GBP': '£',
          'EUR': '€'
        };
        
        const symbol = currencySymbols[currency] || currency;
        
        if (minPay && maxPay) {
          previewText += `${symbol}${formatNumber(minPay)} - ${symbol}${formatNumber(maxPay)} ${period}`;
        } else if (minPay) {
          previewText += `From ${symbol}${formatNumber(minPay)} ${period}`;
        } else if (maxPay) {
          previewText += `Up to ${symbol}${formatNumber(maxPay)} ${period}`;
        }
        
        salaryPreview.innerHTML = previewText;
        salaryPreview.style.color = 'var(--success-color, #28a745)';
      } else {
        salaryPreview.innerHTML = '<i class="bi bi-info-circle"></i> <span>Leave salary fields blank if you prefer not to disclose compensation information</span>';
        salaryPreview.style.color = '';
      }
    }
    
    minPayField.addEventListener('input', updateSalaryPreview);
    maxPayField.addEventListener('input', updateSalaryPreview);
    if (currencyField) currencyField.addEventListener('change', updateSalaryPreview);
    if (periodField) periodField.addEventListener('change', updateSalaryPreview);
    
    // Initial preview
    updateSalaryPreview();
  }

  // ========== Character Counter for Short Description ==========
  const shortDescField = form.querySelector('[name="short_description"]');
  if (shortDescField) {
    const maxLength = 250;
    
    // Create counter element
    const counterDiv = document.createElement('div');
    counterDiv.className = 'character-counter';
    counterDiv.textContent = `${shortDescField.value.length} / ${maxLength} characters`;
    shortDescField.parentElement.appendChild(counterDiv);
    
    shortDescField.addEventListener('input', function() {
      const length = this.value.length;
      counterDiv.textContent = `${length} / ${maxLength} characters`;
      
      if (length > maxLength) {
        counterDiv.style.color = 'var(--danger-color, #dc3545)';
      } else if (length > maxLength * 0.9) {
        counterDiv.style.color = 'var(--warning-color, #ffc107)';
      } else {
        counterDiv.style.color = 'var(--text-light, #6c757d)';
      }
    });
  }

  // ========== Application Deadline Date Picker Enhancement ==========
  const deadlineField = form.querySelector('[name="application_deadline"]');
  if (deadlineField) {
    // Add helpful text showing days from now
    deadlineField.addEventListener('change', function() {
      if (this.value) {
        const selectedDate = new Date(this.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const diffTime = selectedDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        let hint = this.parentElement.querySelector('.deadline-hint');
        if (!hint) {
          hint = document.createElement('small');
          hint.className = 'deadline-hint field-hint';
          this.parentElement.appendChild(hint);
        }
        
        if (diffDays < 0) {
          hint.textContent = 'Warning: Date is in the past';
          hint.style.color = 'var(--danger-color, #dc3545)';
        } else if (diffDays === 0) {
          hint.textContent = 'Applications close today';
          hint.style.color = 'var(--warning-color, #ffc107)';
        } else if (diffDays === 1) {
          hint.textContent = 'Applications close tomorrow';
          hint.style.color = 'var(--info-color, #0dcaf0)';
        } else {
          hint.textContent = `Applications close in ${diffDays} days`;
          hint.style.color = 'var(--success-color, #28a745)';
        }
      }
    });
  }

  // ========== Smart Skills Input ==========
  const skillsField = form.querySelector('[name="skills_required"]');
  if (skillsField) {
    skillsField.addEventListener('blur', function() {
      // Auto-format comma-separated skills to one per line
      const value = this.value.trim();
      if (value.includes(',') && !value.includes('\n')) {
        const skills = value.split(',').map(s => s.trim()).filter(s => s);
        this.value = skills.join('\n');
      }
    });
  }

  // ========== Form Auto-save to localStorage (Draft) ==========
  let autoSaveTimer;
  const formInputs = form.querySelectorAll('input, textarea, select');
  
  // Load saved draft on page load
  loadFormDraft();
  
  formInputs.forEach(input => {
    input.addEventListener('input', function() {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(saveFormDraft, 2000); // Save after 2 seconds of inactivity
    });
  });
  
  // Clear draft on successful submission
  form.addEventListener('submit', function() {
    localStorage.removeItem('vacancyFormDraft');
  });

  // ========== Helper Functions ==========
  function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    const alertClass = type === 'danger' ? 'alert-danger' : 
                      type === 'warning' ? 'alert-warning' : 
                      type === 'info' ? 'alert-info' : 'alert-success';
    
    const icon = type === 'danger' ? 'exclamation-triangle-fill' : 
                 type === 'warning' ? 'exclamation-circle-fill' : 
                 type === 'info' ? 'info-circle-fill' : 'check-circle-fill';
    
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
      <i class="bi bi-${icon} me-2"></i>
      ${message}
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

  function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  function saveFormDraft() {
    const formData = {};
    formInputs.forEach(input => {
      if (input.name && input.type !== 'file') {
        formData[input.name] = input.value;
      }
    });
    
    try {
      localStorage.setItem('vacancyFormDraft', JSON.stringify(formData));
    } catch (e) {
      // Failed to save draft
    }
  }

  function loadFormDraft() {
    try {
      const draft = localStorage.getItem('vacancyFormDraft');
      if (draft && confirm('A saved draft was found. Would you like to restore it?')) {
        const formData = JSON.parse(draft);
        
        Object.keys(formData).forEach(name => {
          const input = form.querySelector(`[name="${name}"]`);
          if (input && !input.value) { // Only restore if field is empty
            input.value = formData[name];
          }
        });
        
        showAlert('info', 'Draft restored successfully');
      }
    } catch (e) {
      // Failed to load draft
    }
  }

  // ========== Submit Button Loading State ==========
  form.addEventListener('submit', function() {
    const submitBtn = form.querySelector('.btn-submit');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Submitting...';
    }
  });

});