// Carousel functionality for project galleries
document.addEventListener('DOMContentLoaded', function() {
  const carousels = document.querySelectorAll('.project-carousel');
  
  carousels.forEach(carousel => {
    const slides = carousel.querySelectorAll('.carousel-slide');
    const thumbs = carousel.querySelectorAll('.pagination-thumb');
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    let currentIndex = 0;
    
    // Show specific slide
    function showSlide(index) {
      // Remove active class from all slides and thumbs
      slides.forEach(slide => slide.classList.remove('active'));
      thumbs.forEach(thumb => thumb.classList.remove('active'));
      
      // Add active class to current slide and thumb
      slides[index].classList.add('active');
      thumbs[index].classList.add('active');
    }
    
    // Next slide
    function nextSlide() {
      currentIndex = (currentIndex + 1) % slides.length;
      showSlide(currentIndex);
    }
    
    // Previous slide
    function prevSlide() {
      currentIndex = (currentIndex - 1 + slides.length) % slides.length;
      showSlide(currentIndex);
    }
    
    // Event listeners for navigation buttons
    if (prevBtn) {
      prevBtn.addEventListener('click', prevSlide);
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', nextSlide);
    }
    
    // Event listeners for pagination thumbnails
    thumbs.forEach((thumb, index) => {
      thumb.addEventListener('click', () => {
        currentIndex = index;
        showSlide(currentIndex);
      });
    });
    
    // Keyboard navigation
    carousel.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        prevSlide();
      } else if (e.key === 'ArrowRight') {
        nextSlide();
      }
    });
    
    // Click on slide to open lightbox
    slides.forEach(slide => {
      slide.addEventListener('click', () => {
        const imageSrc = slide.dataset.image;
        const lightboxGroup = slide.dataset.lightbox;
        
        // Find all images in this project
        const projectSlides = carousel.querySelectorAll('.carousel-slide');
        const images = Array.from(projectSlides).map(s => s.dataset.image);
        
        // Open lightbox with current image
        if (typeof openLightbox === 'function') {
          openLightbox(imageSrc, images);
        }
      });
    });
  });
});
