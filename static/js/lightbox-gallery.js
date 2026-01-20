(() => {
  const FOCUSABLE = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

  class LightboxGallery {
    constructor(options = {}) {
      const { mountEl = null, images = [], startIndex = 0, autoOpen = true } = options;
      this.mountEl = mountEl || null;
      this.images = Array.isArray(images) ? images.slice() : [];
      this.activeIndex = 0;
      this.isOpen = false;
      this.previouslyFocused = null;
      this.touchStartX = null;
      this.savedBodyOverflow = '';

      this.handleKeydown = this.handleKeydown.bind(this);
      this.handleWheel = this.handleWheel.bind(this);
      this.handleThumbClick = this.handleThumbClick.bind(this);

      this.buildOverlay();
      this.setImages(this.images);

      if (this.mountEl) {
        this.mountEl.addEventListener('click', () => this.open(this.images, startIndex));
      }

      if (autoOpen && this.images.length) {
        this.open(this.images, startIndex);
      }
    }

    buildOverlay() {
      this.overlay = document.createElement('div');
      this.overlay.className = 'lightboxGallery lightboxGallery--hidden';
      this.overlay.setAttribute('role', 'dialog');
      this.overlay.setAttribute('aria-modal', 'true');
      this.overlay.setAttribute('aria-hidden', 'true');
      this.overlay.setAttribute('aria-label', 'Image gallery viewer');

      this.closeBtn = document.createElement('button');
      this.closeBtn.type = 'button';
      this.closeBtn.className = 'lightboxGallery__close';
      this.closeBtn.setAttribute('aria-label', 'Close gallery');
      this.closeBtn.innerHTML = '&times;';
      this.closeBtn.addEventListener('click', () => this.close());

      this.main = document.createElement('div');
      this.main.className = 'lightboxGallery__main';

      this.prevBtn = this.createNavButton('Previous image', 'lightboxGallery__nav lightboxGallery__nav--prev', true);
      this.nextBtn = this.createNavButton('Next image', 'lightboxGallery__nav lightboxGallery__nav--next', false);

      this.stage = document.createElement('div');
      this.stage.className = 'lightboxGallery__stage';

      this.mainImg = document.createElement('img');
      this.mainImg.className = 'lightboxGallery__image';
      this.mainImg.alt = '';
      this.mainImg.decoding = 'async';
      this.mainImg.draggable = false;

      this.captionEl = document.createElement('div');
      this.captionEl.className = 'lightboxGallery__caption';

      this.stage.appendChild(this.mainImg);
      this.stage.appendChild(this.captionEl);

      this.main.appendChild(this.prevBtn);
      this.main.appendChild(this.stage);
      this.main.appendChild(this.nextBtn);

      this.thumbs = document.createElement('div');
      this.thumbs.className = 'lightboxGallery__thumbs';

      this.thumbsHint = document.createElement('div');
      this.thumbsHint.className = 'lightboxGallery__thumbsHint';
      this.thumbsHint.textContent = 'Scroll for more';

      this.thumbsScroller = document.createElement('div');
      this.thumbsScroller.className = 'lightboxGallery__thumbsScroller';

      this.thumbsInner = document.createElement('div');
      this.thumbsInner.className = 'lightboxGallery__thumbsInner';
      this.thumbsScroller.appendChild(this.thumbsInner);

      this.thumbs.appendChild(this.thumbsScroller);
      this.thumbs.appendChild(this.thumbsHint);

      this.overlay.appendChild(this.closeBtn);
      this.overlay.appendChild(this.main);
      this.overlay.appendChild(this.thumbs);

      this.stage.addEventListener('touchstart', (e) => this.onTouchStart(e), { passive: true });
      this.stage.addEventListener('touchend', (e) => this.onTouchEnd(e), { passive: true });
    }

    createNavButton(label, className, isPrev) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = className;
      btn.setAttribute('aria-label', label);
      btn.innerHTML = this.buildChevron(isPrev);
      btn.addEventListener('click', () => (isPrev ? this.prev() : this.next()));
      return btn;
    }

    buildChevron(isPrev) {
      const dir = isPrev ? 'M14 2 4 10l10 8' : 'M6 2l10 8-10 8';
      return `<svg viewBox="0 0 18 20" aria-hidden="true" focusable="false"><path d="${dir}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    }

    open(images = null, startIndex = 0) {
      if (images) {
        this.setImages(images);
      }

      if (!this.images.length) return;

      this.activeIndex = this.normalizeIndex(startIndex);
      this.isOpen = true;
      this.previouslyFocused = document.activeElement;

      if (!document.body.contains(this.overlay)) {
        document.body.appendChild(this.overlay);
      }

      this.overlay.classList.remove('lightboxGallery--hidden');
      this.overlay.setAttribute('aria-hidden', 'false');
      this.lockScroll();
      this.bindEvents();
      this.updateMainImage(true);
      this.closeBtn.focus({ preventScroll: true });
    }

    close() {
      if (!this.isOpen) return;
      this.isOpen = false;

      this.overlay.classList.add('lightboxGallery--hidden');
      this.overlay.setAttribute('aria-hidden', 'true');
      this.releaseScroll();
      this.unbindEvents();

      if (this.overlay.parentNode) {
        this.overlay.parentNode.removeChild(this.overlay);
      }

      const target = this.mountEl || this.previouslyFocused;
      if (target && typeof target.focus === 'function') {
        target.focus({ preventScroll: true });
      }
    }

    lockScroll() {
      this.savedBodyOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
    }

    releaseScroll() {
      document.body.style.overflow = this.savedBodyOverflow || '';
    }

    bindEvents() {
      document.addEventListener('keydown', this.handleKeydown);
      this.thumbsScroller.addEventListener('wheel', this.handleWheel, { passive: false });
      this.thumbsInner.addEventListener('click', this.handleThumbClick);
    }

    unbindEvents() {
      document.removeEventListener('keydown', this.handleKeydown);
      this.thumbsScroller.removeEventListener('wheel', this.handleWheel);
      this.thumbsInner.removeEventListener('click', this.handleThumbClick);
    }

    handleKeydown(event) {
      if (!this.isOpen) return;
      const key = event.key;

      if (key === 'Escape') {
        event.preventDefault();
        this.close();
        return;
      }

      if (key === 'ArrowLeft') {
        event.preventDefault();
        this.prev();
        return;
      }

      if (key === 'ArrowRight') {
        event.preventDefault();
        this.next();
        return;
      }

      if (key === 'Home') {
        event.preventDefault();
        this.goTo(0);
        return;
      }

      if (key === 'End') {
        event.preventDefault();
        this.goTo(this.images.length - 1);
        return;
      }

      if (key === 'Tab') {
        this.trapFocus(event);
      }
    }

    trapFocus(event) {
      const focusable = this.getFocusable();
      if (!focusable.length) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;

      if (event.shiftKey && active === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
    }

    getFocusable() {
      return Array.from(this.overlay.querySelectorAll(FOCUSABLE)).filter(
        (el) => !el.disabled && el.offsetParent !== null
      );
    }

    handleWheel(event) {
      if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
        event.preventDefault();
        this.thumbsScroller.scrollLeft += event.deltaY;
      }
    }

    handleThumbClick(event) {
      const btn = event.target.closest('.lightboxGallery__thumb');
      if (!btn) return;
      const idx = Number(btn.dataset.index);
      if (Number.isInteger(idx)) {
        this.goTo(idx);
      }
    }

    onTouchStart(event) {
      if (!event.touches || !event.touches.length) return;
      this.touchStartX = event.touches[0].clientX;
    }

    onTouchEnd(event) {
      if (this.touchStartX === null || !event.changedTouches || !event.changedTouches.length) return;
      const delta = event.changedTouches[0].clientX - this.touchStartX;
      this.touchStartX = null;
      if (Math.abs(delta) < 40) return;
      if (delta < 0) this.next();
      else this.prev();
    }

    setImages(images) {
      this.images = Array.isArray(images) ? images.slice() : [];
      this.activeIndex = 0;
      this.renderThumbs();
    }

    renderThumbs() {
      if (!this.thumbsInner) return;
      this.thumbsInner.innerHTML = '';
      this.images.forEach((item, idx) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'lightboxGallery__thumb';
        btn.dataset.index = idx;
        btn.setAttribute('aria-label', item.title ? `View ${item.title}` : 'View image');
        btn.setAttribute('aria-current', idx === this.activeIndex ? 'true' : 'false');

        const img = document.createElement('img');
        img.src = item.thumb || item.src;
        img.loading = 'lazy';
        img.alt = item.alt || item.title || `Image ${idx + 1}`;
        btn.appendChild(img);
        this.thumbsInner.appendChild(btn);
      });
    }

    updateMainImage(scrollThumb = false) {
      const item = this.images[this.activeIndex];
      if (!item) return;

      this.mainImg.classList.remove('is-loaded');
      this.mainImg.onload = () => this.mainImg.classList.add('is-loaded');
      this.mainImg.src = item.src;
      this.mainImg.alt = item.alt || item.title || 'Gallery image';
      if (this.mainImg.complete && this.mainImg.naturalWidth) {
        this.mainImg.classList.add('is-loaded');
      }

      if (item.title || item.alt) {
        this.captionEl.textContent = item.title || item.alt;
        this.captionEl.classList.add('is-visible');
      } else {
        this.captionEl.textContent = '';
        this.captionEl.classList.remove('is-visible');
      }

      this.updateThumbHighlight();
      if (scrollThumb) {
        this.scrollActiveThumbIntoView();
      }
      this.preloadNeighbors();
    }

    updateThumbHighlight() {
      const buttons = this.thumbsInner.querySelectorAll('.lightboxGallery__thumb');
      buttons.forEach((btn, idx) => {
        btn.setAttribute('aria-current', idx === this.activeIndex ? 'true' : 'false');
      });
    }

    scrollActiveThumbIntoView() {
      const active = this.thumbsInner.querySelector(`[data-index="${this.activeIndex}"]`);
      if (active && typeof active.scrollIntoView === 'function') {
        active.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }
    }

    preloadNeighbors() {
      if (this.images.length <= 1) return;
      const next = this.images[this.normalizeIndex(this.activeIndex + 1)];
      const prev = this.images[this.normalizeIndex(this.activeIndex - 1)];
      [next, prev].forEach((item) => {
        if (!item) return;
        const img = new Image();
        img.src = item.src;
      });
    }

    prev() {
      if (!this.images.length) return;
      this.activeIndex = this.normalizeIndex(this.activeIndex - 1);
      this.updateMainImage(true);
    }

    next() {
      if (!this.images.length) return;
      this.activeIndex = this.normalizeIndex(this.activeIndex + 1);
      this.updateMainImage(true);
    }

    goTo(idx) {
      if (!this.images.length) return;
      this.activeIndex = this.normalizeIndex(idx);
      this.updateMainImage(true);
    }

    normalizeIndex(idx) {
      if (!this.images.length) return 0;
      const len = this.images.length;
      return ((idx % len) + len) % len;
    }
  }

  const singleton = new LightboxGallery({ images: [], autoOpen: false });

  function openGallery(images, startIndex = 0) {
    singleton.open(images, startIndex);
  }

  if (typeof window !== 'undefined') {
    window.LightboxGallery = LightboxGallery;
    window.openGallery = openGallery;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LightboxGallery, openGallery };
  } else if (typeof define === 'function' && define.amd) {
    define(() => ({ LightboxGallery, openGallery }));
  }
})();
