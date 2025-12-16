// Home page specific JavaScript

// Smooth scroll for articles section
const articlesScroll = document.querySelector('.articles-scroll');

// Optional: Add touch/drag scrolling enhancement
if (articlesScroll) {
  let isDown = false;
  let startX;
  let scrollLeft;

  articlesScroll.addEventListener('mousedown', (e) => {
    isDown = true;
    articlesScroll.style.cursor = 'grabbing';
    startX = e.pageX - articlesScroll.offsetLeft;
    scrollLeft = articlesScroll.scrollLeft;
  });

  articlesScroll.addEventListener('mouseleave', () => {
    isDown = false;
    articlesScroll.style.cursor = 'grab';
  });

  articlesScroll.addEventListener('mouseup', () => {
    isDown = false;
    articlesScroll.style.cursor = 'grab';
  });

  articlesScroll.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - articlesScroll.offsetLeft;
    const walk = (x - startX) * 2;
    articlesScroll.scrollLeft = scrollLeft - walk;
  });
  
  // Set initial cursor
  articlesScroll.style.cursor = 'grab';
}

// Play button functionality (placeholder)
const playButton = document.querySelector('.play-button');
if (playButton) {
  playButton.addEventListener('click', () => {
    alert('Video player would open here');
    // In production, you would open a video modal or redirect to video
  });
}

// Add click handlers to article cards
const articleCards = document.querySelectorAll('.article-card');
articleCards.forEach(card => {
  card.addEventListener('click', () => {
    // In production, redirect to article detail page
    console.log('Article clicked');
  });
});

// Add click handlers to work cards
const workCards = document.querySelectorAll('.work-card');
workCards.forEach(card => {
  card.addEventListener('click', () => {
    // In production, redirect to work detail page
    console.log('Work clicked');
  });
});
