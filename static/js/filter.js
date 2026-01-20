// Search and filter functionality for gallery
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const filterButtons = document.querySelectorAll('.filter-btn');
  const projects = document.querySelectorAll('.project-section[data-project]');
  const gallery = document.querySelector('.works-gallery-grid');
  
  let currentFilter = 'all';
  let currentSearch = '';
  
  // Create no results message if it doesn't exist
  let noResults = gallery.querySelector('.no-results');
  if (!noResults) {
    noResults = document.createElement('div');
    noResults.className = 'no-results';
    noResults.textContent = 'No projects found matching your criteria.';
    gallery.appendChild(noResults);
  }
  
  // Filter and search function
  function filterProjects() {
    let visibleCount = 0;
    
    projects.forEach(project => {
      const title = project.dataset.title || '';
      const category = project.dataset.category || 'all';
      
      // Check if project matches search
      const matchesSearch = title.includes(currentSearch.toLowerCase());
      
      // Check if project matches filter
      const matchesFilter = currentFilter === 'all' || category === currentFilter;
      
      // Show/hide project
      if (matchesSearch && matchesFilter) {
        project.classList.remove('hidden');
        visibleCount++;
      } else {
        project.classList.add('hidden');
      }
    });
    
    // Show/hide no results message
    if (visibleCount === 0) {
      noResults.classList.add('show');
    } else {
      noResults.classList.remove('show');
    }
  }
  
  // Search input handler
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value;
      filterProjects();
    });
  }
  
  // Filter button handlers
  filterButtons.forEach(button => {
    button.addEventListener('click', () => {
      // Update active state
      filterButtons.forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      
      // Update current filter
      currentFilter = button.dataset.filter;
      
      // Apply filter
      filterProjects();
    });
  });
  
  // Initialize
  filterProjects();
});
