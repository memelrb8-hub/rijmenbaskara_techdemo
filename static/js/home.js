// Home page interactive functionality
// Handles works filtering, sorting, and article filtering

document.addEventListener('DOMContentLoaded', function() {
  // Works Section Filtering
  const worksGrid = document.getElementById('worksGrid');
  const searchInput = document.getElementById('worksSearch');
  const sortDropdown = document.getElementById('worksSort');
  const filterChips = document.querySelectorAll('.works-section .filter-chip');
  
  // Article Section Filtering
  const articleFilters = document.querySelectorAll('.article-filters .filter-chip');
  const articleRows = document.querySelectorAll('.article-row');

  // Check if worksGrid exists before proceeding
  if (!worksGrid) {
    console.error('Works grid not found');
    return;
  }

  let currentCategory = 'all';
  let currentSearchTerm = '';
  let currentSort = 'newest';

  // Check for URL parameters on page load
  const urlParams = new URLSearchParams(window.location.search);
  const categoryParam = urlParams.get('category');
  const searchParam = urlParams.get('search');
  
  if (categoryParam) {
    currentCategory = categoryParam;
    // Update active filter chip
    filterChips.forEach(chip => {
      chip.classList.remove('active');
      if (chip.dataset.category === categoryParam) {
        chip.classList.add('active');
      }
    });
  }
  
  if (searchParam) {
    currentSearchTerm = searchParam.toLowerCase();
    if (searchInput) {
      searchInput.value = searchParam;
    }
  }
  
  // Apply initial filters if set from URL
  if (categoryParam || searchParam) {
    filterWorks();
  }

  // Works: Filter by category
  filterChips.forEach(chip => {
    chip.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log('Filter chip clicked:', this.dataset.category);
      filterChips.forEach(c => c.classList.remove('active'));
      this.classList.add('active');
      currentCategory = this.dataset.category;
      updateURL();
      filterWorks();
    });
  });

  // Works: Search
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      currentSearchTerm = this.value.toLowerCase().trim();
      updateURL();
      filterWorks();
    });
  }

  // Works: Sort
  if (sortDropdown) {
    sortDropdown.addEventListener('change', function() {
      currentSort = this.value;
      sortWorks();
    });
  }

  function updateURL() {
    const params = new URLSearchParams();
    
    if (currentCategory && currentCategory !== 'all') {
      params.set('category', currentCategory);
    }
    
    if (currentSearchTerm) {
      params.set('search', currentSearchTerm);
    }
    
    const newURL = params.toString() 
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;
    
    window.history.replaceState({}, '', newURL);
  }

  function filterWorks() {
    if (!worksGrid) return;
    
    const cards = worksGrid.querySelectorAll('.work-card');
    console.log('Filtering works:', { currentCategory, currentSearchTerm, totalCards: cards.length });
    
    cards.forEach(card => {
      const category = card.dataset.category || 'all';
      const title = card.dataset.title || '';
      
      const categoryMatch = currentCategory === 'all' || category === currentCategory;
      const searchMatch = currentSearchTerm === '' || title.includes(currentSearchTerm);
      
      if (categoryMatch && searchMatch) {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  }

  function sortWorks() {
    if (!worksGrid) return;
    
    const cards = Array.from(worksGrid.querySelectorAll('.work-card'));
    
    cards.sort((a, b) => {
      const titleA = (a.dataset.title || '').toLowerCase();
      const titleB = (b.dataset.title || '').toLowerCase();
      
      switch(currentSort) {
        case 'az':
          return titleA.localeCompare(titleB);
        case 'za':
          return titleB.localeCompare(titleA);
        case 'oldest':
          // For oldest, we'd need a date attribute
          // For now, reverse the current order
          return 1;
        case 'newest':
        default:
          return -1;
      }
    });
    
    // Re-append cards in sorted order
    cards.forEach(card => worksGrid.appendChild(card));
    
    // Re-apply filters after sorting
    filterWorks();
  }

  // Articles: Filter by category
  articleFilters.forEach(filter => {
    filter.addEventListener('click', function() {
      articleFilters.forEach(f => f.classList.remove('active'));
      this.classList.add('active');
      
      const category = this.dataset.filter;
      
      articleRows.forEach(row => {
        const rowCategory = row.dataset.category;
        
        if (category === 'all' || rowCategory === category) {
          row.style.display = 'grid';
        } else {
          row.style.display = 'none';
        }
      });
    });
  });

  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href.length > 1) {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
  
  console.log('Home.js loaded successfully', {
    filterChips: filterChips.length,
    worksGrid: !!worksGrid,
    searchInput: !!searchInput,
    sortDropdown: !!sortDropdown
  });
});
