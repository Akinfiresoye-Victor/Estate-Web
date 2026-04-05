// ============================================
// FAQ ACCORDION
// ============================================
document.addEventListener('DOMContentLoaded', function() {
  const faqItems = document.querySelectorAll('.faq-item');
  
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    
    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');
      
      // Close all FAQ items
      faqItems.forEach(faq => faq.classList.remove('active'));
      
      // Open clicked item if it wasn't active
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
});

// ============================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    
    // Only prevent default for internal anchors (not just #)
    if (href !== '#' && href !== '#terms' && href !== '#privacy') {
      e.preventDefault();
      const target = document.querySelector(href);
      
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    }
  });
});

// ============================================
// FORM VALIDATION & SUBMISSION
// ============================================
const partnershipForm = document.getElementById('partnershipForm');

if (partnershipForm) {
  partnershipForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Check if at least one property type is selected
    const propertyTypes = document.querySelectorAll('input[type="checkbox"][id="residential"], input[type="checkbox"][id="commercial"], input[type="checkbox"][id="land"], input[type="checkbox"][id="industrial"]');
    const isPropertyTypeChecked = Array.from(propertyTypes).some(cb => cb.checked);
    
    if (!isPropertyTypeChecked) {
      alert('Please select at least one property type you deal with.');
      return;
    }
    
    // Check if at least one transaction type is selected
    const transactionTypes = document.querySelectorAll('input[type="checkbox"][id="sale"], input[type="checkbox"][id="rent"], input[type="checkbox"][id="lease"]');
    const isTransactionTypeChecked = Array.from(transactionTypes).some(cb => cb.checked);
    
    if (!isTransactionTypeChecked) {
      alert('Please select at least one transaction type.');
      return;
    }
    
    // Check if agreement is checked
    const agreement = document.getElementById('agreement');
    if (!agreement.checked) {
      alert('Please agree to the Terms & Conditions and Privacy Policy.');
      return;
    }
    
    // If all validation passes, collect form data
    const formData = {
      company_name: document.getElementById('companyName').value,
      company_type: document.getElementById('companyType').value,
      years_in_business: document.getElementById('yearsInBusiness').value,
      rc_number: document.getElementById('rcNumber').value,
      company_address: document.getElementById('companyAddress').value,
      city: document.getElementById('city').value,
      state: document.getElementById('state').value,
      contact_name: document.getElementById('contactName').value,
      contact_position: document.getElementById('contactPosition').value,
      contact_email: document.getElementById('contactEmail').value,
      contact_phone: document.getElementById('contactPhone').value,
      property_count: document.getElementById('propertyCount').value,
      property_types: Array.from(propertyTypes).filter(cb => cb.checked).map(cb => cb.value),
      transaction_types: Array.from(transactionTypes).filter(cb => cb.checked).map(cb => cb.value),
      website: document.getElementById('website').value,
      message: document.getElementById('message').value
    };
    
    // Show success message (replace with actual backend call)
    alert('Thank you for your interest in partnering with Estate Web! We will review your application and get back to you within 24-48 hours.');
    
    // Reset form
    partnershipForm.reset();
    
    // In production, you would do something like:
    // fetch('/api/partnership-application', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(formData)
    // })
    // .then(response => response.json())
    // .then(data => {
    //   if (data.success) {
    //     alert('Application submitted successfully!');
    //     partnershipForm.reset();
    //   }
    // })
    // .catch(error => {
    //   console.error('Error:', error);
    //   alert('An error occurred. Please try again.');
    // });
  });
}

// ============================================
// FORM INPUT ANIMATIONS
// ============================================
const formInputs = document.querySelectorAll('.form-control');

formInputs.forEach(input => {
  input.addEventListener('focus', function() {
    this.parentElement.classList.add('focused');
  });
  
  input.addEventListener('blur', function() {
    if (this.value === '') {
      this.parentElement.classList.remove('focused');
    }
  });
});

// ============================================
// SCROLL ANIMATIONS
// ============================================
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, observerOptions);

// Observe elements for scroll animation
document.querySelectorAll('.benefit-card, .partner-type-card, .step-card, .faq-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});