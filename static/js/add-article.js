// Medium-inspired editor interactions
(function(){
  const form = document.getElementById('articleForm');
  const bodyField = document.getElementById('bodyInput');
  const editor = document.getElementById('editorBody');
  const toolbar = document.querySelector('.toolbar');
  const coverInput = document.getElementById('coverInput');
  const coverPreview = document.getElementById('coverPreview');
  const coverPreviewImg = document.getElementById('coverPreviewImg');
  const removeCover = document.getElementById('removeCover');
  const insertImageBtn = document.getElementById('insertImageBtn');
  const inlineImageInput = document.getElementById('inlineImageInput');

  if (!form || !editor) return;

  // Hydrate editor from hidden textarea (keeps HTML intact)
  if (bodyField && bodyField.value) {
    editor.innerHTML = bodyField.value;
  }

  // Sync HTML to hidden textarea on submit
  form.addEventListener('submit', () => {
    if (bodyField) {
      bodyField.value = editor.innerHTML.trim();
    }
  });

  // Basic toolbar actions
  if (toolbar) {
    toolbar.addEventListener('click', (evt) => {
      const btn = evt.target.closest('button[data-command]');
      if (!btn) return;

      const [command, value] = btn.dataset.command.split(':');
      if (command === 'createLink') {
        const url = prompt('Enter URL');
        if (url) document.execCommand('createLink', false, url);
        return;
      }

      if (command === 'formatBlock') {
        document.execCommand('formatBlock', false, value || 'p');
      } else {
        document.execCommand(command, false, value || null);
      }

      // visual active state (lightweight)
      btn.classList.add('is-active');
      setTimeout(() => btn.classList.remove('is-active'), 160);
    });
  }

  // Markdown-ish quick shortcuts (#, ##, > + space)
  editor.addEventListener('keydown', (evt) => {
    if (evt.key !== ' ') return;

    const sel = window.getSelection();
    if (!sel || !sel.anchorNode) return;

    const anchor = sel.anchorNode;
    const textNode = anchor.nodeType === 3 ? anchor : anchor.firstChild;
    if (!textNode) return;

    const raw = (textNode.textContent || '').trim();

    if (raw === '##') {
      evt.preventDefault();
      textNode.textContent = '';
      document.execCommand('formatBlock', false, 'h2');
    } else if (raw === '#') {
      evt.preventDefault();
      textNode.textContent = '';
      document.execCommand('formatBlock', false, 'h1');
    } else if (raw === '>') {
      evt.preventDefault();
      textNode.textContent = '';
      document.execCommand('formatBlock', false, 'blockquote');
    }
  });

  // Cover preview
  function resetCover(){
    if (coverPreview) {
      coverPreview.hidden = true;
    }
    if (coverPreviewImg) {
      coverPreviewImg.src = '';
    }
  }

  if (coverInput) {
    coverInput.addEventListener('change', (evt) => {
      const file = evt.target.files?.[0];
      if (!file) {
        resetCover();
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        if (!coverPreviewImg || !coverPreview) return;
        coverPreviewImg.src = e.target?.result;
        coverPreview.hidden = false;
      };
      reader.readAsDataURL(file);
    });
  }

  if (removeCover) {
    removeCover.addEventListener('click', () => {
      if (coverInput) coverInput.value = '';
      resetCover();
    });
  }

  // Inline image insertion
  if (insertImageBtn && inlineImageInput) {
    insertImageBtn.addEventListener('click', (evt) => {
      evt.preventDefault();
      inlineImageInput.click();
    });

    inlineImageInput.addEventListener('change', (evt) => {
      const files = evt.target.files;
      if (!files || files.length === 0) return;

      // Save current selection/range
      const sel = window.getSelection();
      let range = null;
      if (sel.rangeCount > 0) {
        range = sel.getRangeAt(0);
      }

      Array.from(files).forEach((file) => {
        if (!file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (e) => {
          const img = document.createElement('img');
          img.src = e.target.result;
          img.alt = file.name;
          img.className = 'inline-image';
          img.style.maxWidth = '100%';
          img.style.height = 'auto';
          img.style.display = 'block';
          img.style.margin = '20px 0';

          // Insert at saved range or at end
          if (range) {
            sel.removeAllRanges();
            sel.addRange(range);
            range.insertNode(img);
            
            // Move cursor after image
            range.setStartAfter(img);
            range.setEndAfter(img);
            sel.removeAllRanges();
            sel.addRange(range);

            // Add line break after image for better editing
            const br = document.createElement('br');
            range.insertNode(br);
          } else {
            editor.appendChild(img);
            const br = document.createElement('br');
            editor.appendChild(br);
          }
        };
        reader.readAsDataURL(file);
      });

      // Reset input for reuse
      inlineImageInput.value = '';
    });
  }
})();
