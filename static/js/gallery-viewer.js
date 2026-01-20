(() => {
  /**
   * Inline, always-visible gallery with built-in search + filter controls.
   * Multiple instances supported: new GalleryViewer({ mountEl, items, ... }).
   */
  class GalleryViewer {
    constructor(options = {}) {
      const {
        mountEl,
        items = [],
        initialFilters = {},
        startIndex = 0,
        enableSearch = true,
        enableFilters = true,
        onAddItem = null,
        onDeleteItem = null,
        galleryId = 'default',
        currentUserRole = 'viewer',
        limit = 10,
      } = options;

      if (!mountEl) throw new Error('GalleryViewer requires mountEl');

      this.mountEl = mountEl;
      this.galleryId = galleryId;
      this.currentUserRole = currentUserRole;
      this.onDeleteItem = typeof onDeleteItem === 'function' ? onDeleteItem : null;
      this.limit = limit || 10;
      this.enableSearch = enableSearch !== false;
      this.enableFilters = enableFilters !== false;
      this.onAddItem = typeof onAddItem === 'function' ? onAddItem : null;
      this.items = this.normalizeItems(items);

      this.state = {
        searchQuery: (initialFilters.search || '').trim().toLowerCase(),
        activeTag: initialFilters.tag || 'all',
        activeIndex: Number.isInteger(startIndex) ? startIndex : 0,
      };

      this.filteredItems = [];

      this.handleKeydown = this.handleKeydown.bind(this);
      this.onThumbClick = this.onThumbClick.bind(this);
      this.onWheelThumbs = this.onWheelThumbs.bind(this);

      this.build();
      this.applyFilters(true);
    }

    normalizeItems(items) {
      if (!Array.isArray(items)) return [];
      return items
        .map((item, idx) => {
          const tags = Array.isArray(item.tags) ? item.tags.filter(Boolean) : [];
          const title = item.title || 'Untitled';
          const src = item.src || item.thumb || '';
          if (!src) return null;
          return {
            id: item.id || `item-${idx}`,
            title,
            alt: item.alt || title,
            src,
            thumb: item.thumb || item.src || src,
            tags,
          };
        })
        .filter(Boolean);
    }

    build() {
      this.root = document.createElement('div');
      this.root.className = 'galleryViewer';
      this.root.tabIndex = 0;

      if (this.enableSearch || this.enableFilters || this.onAddItem) {
        this.buildControls();
      }

      this.main = document.createElement('div');
      this.main.className = 'galleryViewer__main';

      this.prevBtn = this.createNav(true);
      this.nextBtn = this.createNav(false);

      this.stage = document.createElement('div');
      this.stage.className = 'galleryViewer__stage';

      this.mainImg = document.createElement('img');
      this.mainImg.className = 'galleryViewer__image';
      this.mainImg.alt = '';
      this.mainImg.decoding = 'async';

      this.stage.appendChild(this.mainImg);
      this.main.appendChild(this.prevBtn);
      this.main.appendChild(this.stage);
      this.main.appendChild(this.nextBtn);

      this.emptyState = document.createElement('div');
      this.emptyState.className = 'galleryViewer__empty';
      this.emptyState.textContent = 'No results. Adjust search or filters.';

      this.thumbs = document.createElement('div');
      this.thumbs.className = 'galleryViewer__thumbs';

      this.thumbsScroller = document.createElement('div');
      this.thumbsScroller.className = 'galleryViewer__thumbsScroller';
      this.thumbsInner = document.createElement('div');
      this.thumbsInner.className = 'galleryViewer__thumbsInner';
      this.thumbsScroller.appendChild(this.thumbsInner);
      this.thumbs.appendChild(this.thumbsScroller);

      this.root.appendChild(this.main);
      this.root.appendChild(this.emptyState);
      this.root.appendChild(this.thumbs);

      this.mountEl.innerHTML = '';
      this.mountEl.appendChild(this.root);

      this.root.addEventListener('keydown', this.handleKeydown);
      this.thumbsInner.addEventListener('click', this.onThumbClick);
      this.thumbsScroller.addEventListener('wheel', this.onWheelThumbs, { passive: false });
    }

    buildControls() {
      this.controls = document.createElement('div');
      this.controls.className = 'galleryViewer__controls';

      if (this.enableFilters) {
        this.filtersWrap = document.createElement('div');
        this.filtersWrap.className = 'galleryViewer__filters';
        this.controls.appendChild(this.filtersWrap);
      }

      this.counter = document.createElement('div');
      this.counter.className = 'galleryViewer__counter';
      this.controls.appendChild(this.counter);

      const right = document.createElement('div');
      right.className = 'galleryViewer__controlsRight';

      if (this.enableSearch) {
        this.searchForm = document.createElement('form');
        this.searchForm.className = 'galleryViewer__search';
        this.searchInput = document.createElement('input');
        this.searchInput.type = 'search';
        this.searchInput.placeholder = 'Search works...';
        this.searchInput.value = this.state.searchQuery || '';
        this.searchForm.appendChild(this.searchInput);
        this.searchForm.addEventListener('submit', (e) => {
          e.preventDefault();
          this.updateSearch(this.searchInput.value);
        });
        this.searchInput.addEventListener('input', () => this.updateSearch(this.searchInput.value));
        right.appendChild(this.searchForm);
      }

      this.addBtn = document.createElement('button');
      this.addBtn.type = 'button';
      this.addBtn.className = 'galleryViewer__add';
      this.addBtn.textContent = 'Add picture';
      this.addBtn.addEventListener('click', () => {
        if (this.onAddItem) {
          this.onAddItem(this);
        } else {
          this.defaultAddItem();
        }
      });
      right.appendChild(this.addBtn);

      this.limitNote = document.createElement('span');
      this.limitNote.className = 'galleryViewer__limitNote';
      this.limitNote.textContent = `Limit reached (${this.limit}). Remove one to add another.`;
      this.limitNote.hidden = true;
      right.appendChild(this.limitNote);

      this.controls.appendChild(right);
      this.root?.appendChild(this.controls);
      this.updateCounter();
      this.updateAddState();
    }

    createNav(isPrev) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `galleryViewer__nav galleryViewer__nav--${isPrev ? 'prev' : 'next'}`;
      btn.setAttribute('aria-label', isPrev ? 'Previous image' : 'Next image');
      btn.innerHTML = this.buildChevron(isPrev);
      btn.addEventListener('click', () => (isPrev ? this.prev() : this.next()));
      return btn;
    }

    buildChevron(isPrev) {
      const dir = isPrev ? 'M12 2 4 10l8 8' : 'M6 2l8 8-8 8';
      return `<svg viewBox="0 0 16 20" aria-hidden="true" focusable="false"><path d="${dir}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    }

    getAllTags() {
      const set = new Set();
      this.items.forEach((item) => (item.tags || []).forEach((t) => set.add(t)));
      return ['all', ...Array.from(set)];
    }

    buildFilterChips() {
      if (!this.filtersWrap) return;
      const tags = this.getAllTags();
      this.filtersWrap.innerHTML = '';
      tags.forEach((tag) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'galleryViewer__chip';
        btn.textContent = tag === 'all' ? 'All' : tag;
        btn.dataset.filter = tag;
        btn.addEventListener('click', () => {
          this.state.activeTag = tag;
          this.applyFilters();
        });
        this.filtersWrap.appendChild(btn);
      });
    }

    updateSearch(value) {
      this.state.searchQuery = (value || '').trim().toLowerCase();
      this.applyFilters();
    }

    matchesFilters(item) {
      const tagOk = this.state.activeTag === 'all' || (item.tags || []).includes(this.state.activeTag);
      const searchField = `${item.title || ''} ${(item.tags || []).join(' ')}`.toLowerCase();
      const searchOk = !this.state.searchQuery || searchField.includes(this.state.searchQuery);
      return tagOk && searchOk;
    }

    applyFilters(rebuildFilters = false) {
      if (rebuildFilters) this.buildFilterChips();

      this.filteredItems = this.items.filter((i) => this.matchesFilters(i));

      const activeId = this.filteredItems[this.state.activeIndex]?.id;
      if (!activeId || !this.filteredItems.find((i) => i.id === activeId)) {
        this.state.activeIndex = 0;
      }

      this.renderFiltersState();
      this.render();
    }

    renderFiltersState() {
      if (!this.filtersWrap) return;
      this.filtersWrap.querySelectorAll('.galleryViewer__chip').forEach((chip) => {
        const match =
          chip.dataset.filter === this.state.activeTag ||
          (this.state.activeTag === 'all' && chip.dataset.filter === 'all');
        chip.classList.toggle('is-active', match);
      });
    }

    render() {
      const hasItems = this.filteredItems.length > 0;
      this.emptyState.style.display = hasItems ? 'none' : 'flex';
      this.main.style.display = hasItems ? 'grid' : 'none';
      this.thumbs.style.display = hasItems ? 'block' : 'none';
      this.updateCounter();
      this.updateAddState();

      if (!hasItems) return;

      this.state.activeIndex = this.normalizeIndex(this.state.activeIndex, this.filteredItems.length);
      this.updateMainImage();
      this.renderThumbs();
      this.updateThumbState();
      this.scrollActiveThumb();
    }

    updateMainImage() {
      const item = this.filteredItems[this.state.activeIndex];
      if (!item) return;
      this.mainImg.classList.remove('is-loaded');
      this.mainImg.onload = () => this.mainImg.classList.add('is-loaded');
      this.mainImg.src = item.src;
      this.mainImg.alt = item.alt || item.title || 'Gallery image';
      if (this.mainImg.complete && this.mainImg.naturalWidth) {
        this.mainImg.classList.add('is-loaded');
      }
    }

    renderThumbs() {
      this.thumbsInner.innerHTML = '';
      this.filteredItems.forEach((item, idx) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'galleryViewer__thumb';
        btn.dataset.index = idx;
        btn.setAttribute('aria-current', idx === this.state.activeIndex ? 'true' : 'false');
        btn.setAttribute('aria-label', item.title ? `View ${item.title}` : 'View image');

        const img = document.createElement('img');
        img.src = item.thumb || item.src;
        img.alt = item.alt || item.title || `Image ${idx + 1}`;
        img.loading = 'lazy';

        btn.appendChild(img);
        if (this.currentUserRole === 'admin' && this.onDeleteItem) {
          const removeBtn = document.createElement('button');
          removeBtn.type = 'button';
          removeBtn.className = 'galleryViewer__remove';
          removeBtn.setAttribute('aria-label', `Remove ${item.title || 'image'}`);
          removeBtn.innerHTML = '&times;';
          removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.onDeleteItem(item.id);
          });
          btn.appendChild(removeBtn);
        }
        this.thumbsInner.appendChild(btn);
      });
    }

    onThumbClick(event) {
      const btn = event.target.closest('.galleryViewer__thumb');
      if (!btn) return;
      const idx = Number(btn.dataset.index);
      if (Number.isInteger(idx)) {
        this.goTo(idx);
      }
    }

    onWheelThumbs(event) {
      if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
        event.preventDefault();
        this.thumbsScroller.scrollLeft += event.deltaY;
      }
    }

    goTo(idx) {
      if (!this.filteredItems.length) return;
      this.state.activeIndex = this.normalizeIndex(idx, this.filteredItems.length);
      this.updateMainImage();
      this.updateThumbState();
      this.scrollActiveThumb();
      this.preloadNeighbors();
    }

    prev() {
      this.goTo(this.state.activeIndex - 1);
    }

    next() {
      this.goTo(this.state.activeIndex + 1);
    }

    updateThumbState() {
      this.thumbsInner.querySelectorAll('.galleryViewer__thumb').forEach((btn, idx) => {
        btn.setAttribute('aria-current', idx === this.state.activeIndex ? 'true' : 'false');
      });
    }

    scrollActiveThumb() {
      const active = this.thumbsInner.querySelector(`[data-index="${this.state.activeIndex}"]`);
      if (active && typeof active.scrollIntoView === 'function') {
        active.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }
    }

    preloadNeighbors() {
      if (this.filteredItems.length <= 1) return;
      const next = this.filteredItems[this.normalizeIndex(this.state.activeIndex + 1, this.filteredItems.length)];
      const prev = this.filteredItems[this.normalizeIndex(this.state.activeIndex - 1, this.filteredItems.length)];
      [next, prev].forEach((item) => {
        if (!item) return;
        const img = new Image();
        img.src = item.src;
      });
    }

    handleKeydown(event) {
      const key = event.key;
      if (key === 'ArrowLeft') {
        event.preventDefault();
        this.prev();
      } else if (key === 'ArrowRight') {
        event.preventDefault();
        this.next();
      } else if (key === 'Home') {
        event.preventDefault();
        this.goTo(0);
      } else if (key === 'End') {
        event.preventDefault();
        this.goTo(this.filteredItems.length - 1);
      }
    }

    normalizeIndex(idx, length) {
      if (!length) return 0;
      return ((idx % length) + length) % length;
    }

    defaultAddItem() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.addEventListener('change', () => {
        const file = input.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
          const dataUrl = reader.result;
          const id = `local-${Date.now()}`;
          this.addItems(
            [
              {
                id,
                title: file.name || 'New Upload',
                src: dataUrl,
                thumb: dataUrl,
                tags: ['Quality:Upload', 'Genre:Misc', 'Local'],
              },
            ],
            true
          );
        };
        reader.readAsDataURL(file);
      });
      input.click();
    }

    addItems(newItems = [], activateLast = false) {
      const normalized = this.normalizeItems(newItems);
      if (!normalized.length) return;
      this.items = this.items.concat(normalized);
      if (activateLast) {
        this.state.activeIndex = this.items.length - 1;
      }
      this.applyFilters(true);
    }

    setItems(newItems = [], limit = null) {
      this.items = this.normalizeItems(newItems);
      if (typeof limit === 'number') {
        this.limit = limit;
      }
      this.applyFilters(true);
    }

    goToId(itemId) {
      const idx = this.filteredItems.findIndex((i) => i.id === itemId);
      if (idx >= 0) {
        this.goTo(idx);
      }
    }

    updateCounter() {
      if (!this.counter) return;
      const used = this.items.length;
      this.counter.textContent = `${used} / ${this.limit} photos used`;
      if (used >= this.limit) {
        this.counter.classList.add('is-full');
      } else {
        this.counter.classList.remove('is-full');
      }
    }

    updateAddState() {
      if (!this.addBtn) return;
      const used = this.items.length;
      const atLimit = used >= this.limit;
      this.addBtn.disabled = atLimit;
      this.addBtn.title = atLimit ? `Limit reached (${this.limit}). Remove one to add another.` : '';
      if (this.limitNote) {
        this.limitNote.hidden = !atLimit;
      }
    }
  }

  function initGalleryViewer(mountEl, items, startIndex = 0) {
    return new GalleryViewer({
      mountEl,
      items,
      initialFilters: { tag: 'all' },
      enableFilters: true,
      enableSearch: true,
      onAddItem: null,
      startIndex,
    });
  }

  if (typeof window !== 'undefined') {
    window.GalleryViewer = GalleryViewer;
    window.initGalleryViewer = initGalleryViewer;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GalleryViewer, initGalleryViewer };
  } else if (typeof define === 'function' && define.amd) {
    define(() => ({ GalleryViewer, initGalleryViewer }));
  }
})();
