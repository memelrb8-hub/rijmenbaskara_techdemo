// Works page: single inline gallery that fetches by galleryId and enforces per-instance caps.
(function () {
  const mountEl = document.getElementById('worksInlineGallery');
  if (!mountEl || typeof GalleryViewer !== 'function') return;

  const galleryId = mountEl.dataset.galleryId || 'default';
  const addUrl = mountEl.dataset.addUrl || `/works/${galleryId}/add/`;
  const userRole = mountEl.dataset.userRole || 'viewer';
  const apiBase = `/api/galleries/${galleryId}/items/`;
  const selectId = mountEl.dataset.selectId || '';
  let viewer = null;

  function getCSRFToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  async function fetchItems() {
    const res = await fetch(apiBase, { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error('Failed to load gallery items');
    return res.json();
  }

  async function deleteItem(itemId) {
    if (userRole !== 'admin') return;
    const confirmDelete = window.confirm('Remove this picture?');
    if (!confirmDelete) return;
    const res = await fetch(`${apiBase}${encodeURIComponent(itemId)}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': getCSRFToken() },
    });
    if (!res.ok) {
      alert('Unable to delete. Please try again.');
      return;
    }
    await loadAndRender();
  }

  function initViewer(items, limit) {
    if (viewer) {
      viewer.setItems(items, limit);
      if (selectId) viewer.goToId(selectId);
      return;
    }
    viewer = new GalleryViewer({
      mountEl,
      galleryId,
      items,
      limit,
      currentUserRole: userRole,
      enableFilters: true,
      enableSearch: true,
      onAddItem: () => window.location.href = addUrl,
      onDeleteItem: (itemId) => deleteItem(itemId),
    });
    if (selectId) viewer.goToId(selectId);
  }

  async function loadAndRender() {
    try {
      const data = await fetchItems();
      const items = Array.isArray(data.items) ? data.items : [];
      const limit = data.limit;
      initViewer(items, limit);
    } catch (err) {
      console.error(err);
    }
  }

  loadAndRender();
})();
