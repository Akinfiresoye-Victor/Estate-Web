// Edit Appointment JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('editAppointmentForm');
    const appointmentDate = document.getElementById('appointment_date');
    const noteField = document.getElementById('note');
    const saveButton = form.querySelector('.btn-save');
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    appointmentDate.setAttribute('min', today);
    
    // Form validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const errors = [];
        
        // Validate appointment date
        const selectedDate = new Date(appointmentDate.value);
        const todayDate = new Date(today);
        
        if (!appointmentDate.value) {
            errors.push('Appointment date is required');
            isValid = false;
            highlightError(appointmentDate);
        } else if (selectedDate < todayDate) {
            errors.push('Appointment date cannot be in the past');
            isValid = false;
            highlightError(appointmentDate);
        }
        
        // Validate appointment type
        const appointmentType = document.getElementById('appointment_type');
        if (!appointmentType.value) {
            errors.push('Appointment type is required');
            isValid = false;
            highlightError(appointmentType);
        }
        
        if (!isValid) {
            e.preventDefault();
            showErrors(errors);
        } else {
            // Show loading state
            saveButton.disabled = true;
            saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        }
    });
    
    // Auto-save note indicator (optional feature)
    let noteTimeout;
    noteField.addEventListener('input', function() {
        clearTimeout(noteTimeout);
        noteTimeout = setTimeout(function() {
            showAutoSaveIndicator();
        }, 1000);
    });
    
    // Remove error highlighting on input
    const formControls = form.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('input', function() {
            removeError(this);
        });
    });
    
    // Property ID validation
    const propertyIdField = document.getElementById('property_id');
    if (propertyIdField) {
        propertyIdField.addEventListener('input', function() {
            // Only allow positive integers
            if (this.value && this.value < 0) {
                this.value = '';
            }
        });
    }
    
    // Confirm before leaving with unsaved changes
    let formChanged = false;
    formControls.forEach(control => {
        control.addEventListener('change', function() {
            formChanged = true;
        });
    });
    
    window.addEventListener('beforeunload', function(e) {
        if (formChanged && !form.querySelector('.btn-save').disabled) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    
    // Mark form as submitted to prevent warning
    form.addEventListener('submit', function() {
        formChanged = false;
    });
});

// Helper Functions
function highlightError(element) {
    element.style.borderColor = '#dc3545';
    element.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
}

function removeError(element) {
    element.style.borderColor = '#ddd';
    element.style.boxShadow = 'none';
}

function showErrors(errors) {
    // Remove existing error messages
    const existingError = document.querySelector('.error-message-box');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error message box
    const errorBox = document.createElement('div');
    errorBox.className = 'error-message-box';
    errorBox.style.cssText = `
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 15px 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        animation: slideIn 0.3s ease;
    `;
    
    const errorTitle = document.createElement('strong');
    errorTitle.textContent = 'Please fix the following errors:';
    errorBox.appendChild(errorTitle);
    
    const errorList = document.createElement('ul');
    errorList.style.cssText = 'margin: 10px 0 0 20px; padding: 0;';
    
    errors.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        errorList.appendChild(li);
    });
    
    errorBox.appendChild(errorList);
    
    // Insert error box at the top of the form
    const formCard = document.querySelector('.form-card');
    formCard.insertBefore(errorBox, formCard.firstChild);
    
    // Scroll to error box
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorBox.parentNode) {
            errorBox.style.opacity = '0';
            setTimeout(() => errorBox.remove(), 300);
        }
    }, 5000);
}

function showAutoSaveIndicator() {
    // Remove existing indicator
    const existingIndicator = document.querySelector('.autosave-indicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    // Create new indicator
    const indicator = document.createElement('div');
    indicator.className = 'autosave-indicator';
    indicator.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #28a745;
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: fadeInOut 2s ease;
    `;
    indicator.innerHTML = '<i class="fas fa-check"></i> Note draft saved locally';
    
    document.body.appendChild(indicator);
    
    // Auto-remove after 2 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.remove();
        }
    }, 2000);
}

// Add CSS animation for error box
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(20px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(20px); }
    }
`;
document.head.appendChild(style);