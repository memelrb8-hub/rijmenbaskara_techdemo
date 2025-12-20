(function () {
  const thumb = document.getElementById("scrollThumb");
  if (!thumb) return;

  function updateThumb() {
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = window.innerHeight;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    const track = thumb.parentElement;
    const trackHeight = track.clientHeight;

    // If nothing to scroll, hide thumb
    if (scrollHeight <= clientHeight) {
      thumb.style.opacity = "0";
      return;
    }
    
    thumb.style.opacity = "0.95";

    // Thumb size proportional to visible area
    const ratio = clientHeight / scrollHeight;
    const minThumb = 28;
    const thumbHeight = Math.max(trackHeight * ratio, minThumb);

    // Thumb position
    const maxTop = trackHeight - thumbHeight;
    const maxScroll = scrollHeight - clientHeight;
    const top = (scrollTop / maxScroll) * maxTop;

    thumb.style.height = thumbHeight + "px";
    thumb.style.transform = `translateY(${top}px)`;
  }

  updateThumb();
  window.addEventListener("scroll", updateThumb, { passive: true });
  window.addEventListener("resize", updateThumb);
})();
