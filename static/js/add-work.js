// Client-side previews for Add Work form
(function () {
  const imgInput = document.getElementById('workImage');
  const thumbInput = document.getElementById('workThumb');
  const submitBtn = document.querySelector('[data-work-submit]');
  const counter = document.querySelector('[data-work-counter]');
  const limitNote = document.querySelector('[data-limit-note]');

  function bindPreview(input, selector) {
    const target = document.querySelector(`[data-preview="${selector}"]`);
    if (!input || !target) return;
    input.addEventListener('change', () => {
      const file = input.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        target.innerHTML = '';
        const img = document.createElement('img');
        img.src = reader.result;
        img.alt = file.name;
        target.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  }

  bindPreview(imgInput, 'image');
  bindPreview(thumbInput, 'thumb');

  function enforceLimit() {
    if (!counter) return;
    const used = parseInt(counter.dataset.used, 10) || 0;
    const limit = parseInt(counter.dataset.limit, 10) || 0;
    const atLimit = used >= limit && limit > 0;
    if (atLimit) {
      submitBtn?.setAttribute('disabled', 'true');
      imgInput?.setAttribute('disabled', 'true');
      thumbInput?.setAttribute('disabled', 'true');
      if (limitNote) limitNote.hidden = false;
    } else {
      submitBtn?.removeAttribute('disabled');
      imgInput?.removeAttribute('disabled');
      thumbInput?.removeAttribute('disabled');
      if (limitNote) limitNote.hidden = true;
    }
  }

  enforceLimit();
})();
