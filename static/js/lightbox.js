// Lightbox functionality for works gallery
let currentImages = [];
let currentIndex = 0;

const lightbox = document.getElementById('lightbox');
const lightboxImage = document.getElementById('lightbox-image');
const closeBtn = document.querySelector('.lightbox-close');
const prevBtn = document.querySelector('.lightbox-prev');
const nextBtn = document.querySelector('.lightbox-next');

function openLightbox(src, images = null) {
  if (images) {
    currentImages = images;
    currentIndex = currentImages.indexOf(src);
  } else {
    currentImages = [src];
    currentIndex = 0;
  }
  
  lightboxImage.src = src;
  lightbox.classList.add('is-open');
  document.body.style.overflow = 'hidden';
}

function closeLightbox() {
  lightbox.classList.remove('is-open');
  document.body.style.overflow = '';
}

function showNext() {
  currentIndex = (currentIndex + 1) % currentImages.length;
  lightboxImage.src = currentImages[currentIndex];
}

function showPrev() {
  currentIndex = (currentIndex - 1 + currentImages.length) % currentImages.length;
  lightboxImage.src = currentImages[currentIndex];
}

// Event listeners
if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
if (nextBtn) nextBtn.addEventListener('click', showNext);
if (prevBtn) prevBtn.addEventListener('click', showPrev);

// Close on background click
if (lightbox) {
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (!lightbox || !lightbox.classList.contains('is-open')) return;
  
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowRight') showNext();
  if (e.key === 'ArrowLeft') showPrev();
});
