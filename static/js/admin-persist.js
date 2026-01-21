// Admin mode persistence for Vercel POC
// Automatically adds ?admin=true to all links if currently in admin mode

(function() {
  // Check if we're in admin mode
  const urlParams = new URLSearchParams(window.location.search);
  const isAdminMode = urlParams.get('admin') === 'true';
  
  if (isAdminMode) {
    // Add admin parameter to all internal links on page load
    document.addEventListener('DOMContentLoaded', function() {
      preserveAdminMode();
    });
    
    // Also observe for dynamically added links
    const observer = new MutationObserver(preserveAdminMode);
    observer.observe(document.body, { childList: true, subtree: true });
  }
  
  function preserveAdminMode() {
    const links = document.querySelectorAll('a[href]');
    
    links.forEach(link => {
      const href = link.getAttribute('href');
      
      // Skip if already processed, external, or anchor links
      if (!href || 
          href.startsWith('http') || 
          href.startsWith('//') || 
          href.startsWith('#') ||
          href.startsWith('mailto:') ||
          link.hasAttribute('data-admin-processed')) {
        return;
      }
      
      // Skip the toggle button itself
      if (href.includes('toggle-view')) {
        return;
      }
      
      // Add admin parameter if not already present
      const url = new URL(href, window.location.origin);
      if (!url.searchParams.has('admin')) {
        url.searchParams.set('admin', 'true');
        link.setAttribute('href', url.pathname + url.search);
      }
      
      // Mark as processed
      link.setAttribute('data-admin-processed', 'true');
    });
  }
})();
