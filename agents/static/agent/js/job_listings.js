// Job Listings Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
  
  // ========== Elements ==========
  const searchInput = document.getElementById('searchInput');
  const clearSearchBtn = document.getElementById('clearSearch');
  const jobTypeSelect = document.getElementById('jobType');
  const locationSelect = document.getElementById('location');
  const experienceSelect = document.getElementById('experience');
  const salaryRangeSelect = document.getElementById('salaryRange');
  const datePostedSelect = document.getElementById('datePosted');
  const sortBySelect = document.getElementById('sortBy');
  const clearFiltersBtn = document.getElementById('clearFilters');
  const resetFromNoResults = document.getElementById('resetFromNoResults');
  const resultsCount = document.getElementById('resultsCount');
  const noResults = document.getElementById('noResults');
  const jobListings = document.getElementById('jobListings');
  
  const cards = Array.from(document.querySelectorAll('.job-card'));
  const totalJobs = cards.length;

  // ========== Helper Functions ==========
  
  function hasActiveFilters() {
    return jobTypeSelect.value || 
           locationSelect.value || 
           experienceSelect.value ||
           salaryRangeSelect.value || 
           datePostedSelect.value || 
           searchInput.value.trim();
  }

  function matchesSearch(card, query) {
    if (!query) return true;
    
    const searchLower = query.toLowerCase();
    const jobTitle = (card.dataset.jobTitle || '').toLowerCase();
    const company = (card.dataset.company || '').toLowerCase();
    const jobType = (card.dataset.jobType || '').toLowerCase();
    const location = (card.dataset.location || '').toLowerCase();
    const experience = (card.dataset.experience || '').toLowerCase();
    const skills = (card.dataset.skills || '').toLowerCase();
    const fullDescription = (card.dataset.fullDescription || '').toLowerCase();
    
    const descriptionEl = card.querySelector('.job-description');
    const shortDescription = descriptionEl ? descriptionEl.textContent.toLowerCase() : '';
    
    return jobTitle.includes(searchLower) || 
           company.includes(searchLower) || 
           jobType.includes(searchLower) || 
           location.includes(searchLower) ||
           experience.includes(searchLower) ||
           skills.includes(searchLower) ||
           shortDescription.includes(searchLower) ||
           fullDescription.includes(searchLower);
  }

  function matchesExperience(cardExp, selectedExp) {
    if (!selectedExp) return true;
    if (!cardExp) return true; // Show jobs without experience requirement
    
    const expLower = cardExp.toLowerCase();
    
    switch(selectedExp) {
      case 'entry':
        return expLower.includes('entry') || 
               expLower.includes('0') || 
               expLower.includes('no experience') ||
               expLower.includes('graduate');
      case 'junior':
        return expLower.includes('junior') || 
               expLower.includes('1') || 
               expLower.includes('2') || 
               expLower.includes('3');
      case 'mid':
        return expLower.includes('mid') || 
               expLower.includes('3') || 
               expLower.includes('4') || 
               expLower.includes('5');
      case 'senior':
        return expLower.includes('senior') || 
               expLower.includes('5') || 
               expLower.includes('6') || 
               expLower.includes('7') ||
               expLower.includes('8') ||
               expLower.includes('9') ||
               expLower.includes('10');
      default:
        return true;
    }
  }

  function matchesDate(cardDays, selected) {
    const days = parseInt(cardDays, 10);
    if (!selected) return true;
    if (isNaN(days)) return true;
    
    switch (selected) {
      case 'today':
        return days === 0;
      case '3days':
        return days <= 3;
      case 'week':
        return days <= 7;
      case 'month':
        return days <= 30;
      default:
        return true;
    }
  }

  function matchesSalary(minPay, maxPay, selectedRange) {
    if (!selectedRange) return true;
    
    const [rangeMin, rangeMax] = selectedRange.split('-').map(Number);
    const cardMin = parseFloat(minPay) || 0;
    const cardMax = parseFloat(maxPay) || 0;
    
    // If no salary data, show it
    if (cardMin === 0 && cardMax === 0) return true;
    
    // Check if job salary overlaps with selected range
    return (cardMin >= rangeMin && cardMin <= rangeMax) || 
           (cardMax >= rangeMin && cardMax <= rangeMax) ||
           (cardMin <= rangeMin && cardMax >= rangeMax);
  }

  function getSortValue(card, sortType) {
    switch(sortType) {
      case 'newest':
        return -parseInt(card.dataset.days || 0);
      case 'oldest':
        return parseInt(card.dataset.days || 0);
      case 'salary-high':
        return -(parseFloat(card.dataset.maxPay) || parseFloat(card.dataset.minPay) || 0);
      case 'salary-low':
        return parseFloat(card.dataset.minPay) || parseFloat(card.dataset.maxPay) || 999999999;
      case 'deadline':
        const deadline = card.dataset.deadline;
        if (!deadline) return 999999999;
        return new Date(deadline).getTime();
      default:
        return 0;
    }
  }

  // ========== Main Filter & Sort Function ==========
  
  function applyFiltersAndSort() {
    const searchQuery = searchInput.value.trim();
    const typeVal = (jobTypeSelect.value || '').trim().toLowerCase();
    const locVal = (locationSelect.value || '').trim().toLowerCase();
    const expVal = (experienceSelect.value || '').trim();
    const salaryVal = (salaryRangeSelect.value || '');
    const dateVal = (datePostedSelect.value || '');
    const sortVal = (sortBySelect.value || 'newest');

    let visibleCards = [];

    // Filter
    cards.forEach(card => {
      const cardType = (card.dataset.jobType || '').toLowerCase();
      const cardLoc = (card.dataset.location || '').toLowerCase();
      const cardExp = card.dataset.experience;
      const cardDays = card.dataset.days;
      const cardMinPay = card.dataset.minPay;
      const cardMaxPay = card.dataset.maxPay;

      const searchMatch = matchesSearch(card, searchQuery);
      const typeMatch = !typeVal || cardType.includes(typeVal) || typeVal.includes(cardType);
      const locMatch = !locVal || cardLoc.includes(locVal);
      const expMatch = matchesExperience(cardExp, expVal);
      const dateMatch = matchesDate(cardDays, dateVal);
      const salaryMatch = matchesSalary(cardMinPay, cardMaxPay, salaryVal);

      if (searchMatch && typeMatch && locMatch && expMatch && dateMatch && salaryMatch) {
        card.style.display = '';
        visibleCards.push(card);
      } else {
        card.style.display = 'none';
      }
    });

    // Sort
    if (visibleCards.length > 0) {
      visibleCards.sort((a, b) => {
        return getSortValue(a, sortVal) - getSortValue(b, sortVal);
      });

      // Re-append in sorted order
      visibleCards.forEach(card => {
        jobListings.appendChild(card);
      });
    }

    // Update UI
    updateUI(visibleCards.length);
  }

  function updateUI(visibleCount) {
    // Update results count
    if (hasActiveFilters()) {
      resultsCount.textContent = `Showing ${visibleCount} of ${totalJobs} job${totalJobs !== 1 ? 's' : ''}`;
      clearFiltersBtn.style.display = 'inline-flex';
    } else {
      resultsCount.textContent = `Showing all ${totalJobs} job${totalJobs !== 1 ? 's' : ''}`;
      clearFiltersBtn.style.display = 'none';
    }

    // Show/hide no results message
    if (visibleCount === 0 && totalJobs > 0) {
      noResults.style.display = 'flex';
      jobListings.style.display = 'none';
    } else {
      noResults.style.display = 'none';
      jobListings.style.display = 'grid';
    }

    // Show/hide clear search button
    if (searchInput.value.trim()) {
      clearSearchBtn.style.display = 'flex';
    } else {
      clearSearchBtn.style.display = 'none';
    }
  }

  // ========== Clear Functions ==========
  
  function clearAllFilters() {
    searchInput.value = '';
    jobTypeSelect.value = '';
    locationSelect.value = '';
    experienceSelect.value = '';
    salaryRangeSelect.value = '';
    datePostedSelect.value = '';
    sortBySelect.value = 'newest';
    applyFiltersAndSort();
  }

  function clearSearch() {
    searchInput.value = '';
    searchInput.focus();
    applyFiltersAndSort();
  }

  // ========== Event Listeners ==========
  
  // Filter changes
  [jobTypeSelect, locationSelect, experienceSelect, salaryRangeSelect, datePostedSelect, sortBySelect].forEach(el => {
    if (el) el.addEventListener('change', applyFiltersAndSort);
  });

  // Search input with debounce
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(applyFiltersAndSort, 300);
    });
  }

  // Clear buttons
  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', clearAllFilters);
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', clearSearch);
  }

  if (resetFromNoResults) {
    resetFromNoResults.addEventListener('click', clearAllFilters);
  }

  // ========== Keyboard Shortcuts ==========
  
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
    }
    
    // Escape to clear search/filters
    if (e.key === 'Escape') {
      if (searchInput === document.activeElement) {
        clearSearch();
      } else if (hasActiveFilters()) {
        clearAllFilters();
      }
    }
  });

  // ========== Save Filter State ==========
  
  function saveFilterState() {
    const state = {
      search: searchInput.value,
      jobType: jobTypeSelect.value,
      location: locationSelect.value,
      experience: experienceSelect.value,
      salary: salaryRangeSelect.value,
      date: datePostedSelect.value,
      sort: sortBySelect.value
    };
    
    try {
      sessionStorage.setItem('jobFilters', JSON.stringify(state));
    } catch (e) {
      console.error('Failed to save filter state:', e);
    }
  }

  function loadFilterState() {
    try {
      const state = sessionStorage.getItem('jobFilters');
      if (state) {
        const filters = JSON.parse(state);
        searchInput.value = filters.search || '';
        jobTypeSelect.value = filters.jobType || '';
        locationSelect.value = filters.location || '';
        experienceSelect.value = filters.experience || '';
        salaryRangeSelect.value = filters.salary || '';
        datePostedSelect.value = filters.date || '';
        sortBySelect.value = filters.sort || 'newest';
        applyFiltersAndSort();
      }
    } catch (e) {
      console.error('Failed to load filter state:', e);
    }
  }

  // Save on change
  [searchInput, jobTypeSelect, locationSelect, experienceSelect, salaryRangeSelect, datePostedSelect, sortBySelect].forEach(el => {
    if (el) el.addEventListener('change', saveFilterState);
  });

  // ========== Animations ==========
  
  // Animate cards on load
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      card.style.transition = 'all 0.3s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 50);
  });

  // ========== Initialize ==========
  
  // Load saved filters
  loadFilterState();
  
  // Initial count display
  if (!hasActiveFilters()) {
    resultsCount.textContent = `Showing all ${totalJobs} job${totalJobs !== 1 ? 's' : ''}`;
  }

  // Add tooltips to featured badges
  const featuredBadges = document.querySelectorAll('.badge-featured');
  featuredBadges.forEach(badge => {
    badge.title = 'Featured Job - Highlighted by employer';
  });

});