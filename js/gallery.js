/**
 * RODRIGUEZ LAWNCARE - DYNAMIC LIVE WORK GALLERY
 * Loads real-time photos managed via the Discord Bot.
 * Highlights new photos with a glowing "🔥 NEW" badge for 3 days (72 hours),
 * then transitions smoothly to standard photo numbers (#01, #02, etc.).
 */

(function () {
  'use strict';

  const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;

  // Fallback items in case gallery.json is accessed via local file:// protocol
  const fallbackGallery = [
    {
      id: 1,
      filename: "work_1.jpg",
      url: "./assets/gallery/work_1.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 12), // 12 hours ago (NEW)
      title: "Commercial Striping & Front Yard Cut"
    },
    {
      id: 2,
      filename: "work_2.jpg",
      url: "./assets/gallery/work_2.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 24), // 24 hours ago (NEW)
      title: "Full Lawn Renovation & Edging"
    },
    {
      id: 3,
      filename: "work_3.jpg",
      url: "./assets/gallery/work_3.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 24 * 5), // 5 days ago (Normal)
      title: "Hedge Trimming & Shrub Shaping"
    },
    {
      id: 4,
      filename: "work_4.jpg",
      url: "./assets/gallery/work_4.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 24 * 6), // 6 days ago (Normal)
      title: "Fresh Dark Mulch Installation"
    }
  ];

  document.addEventListener('DOMContentLoaded', () => {
    initGallery();
  });

  async function initGallery() {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;

    let items = [];
    try {
      const response = await fetch('./gallery.json?t=' + Date.now());
      if (response.ok) {
        items = await response.json();
      } else {
        items = fallbackGallery;
      }
    } catch (err) {
      console.warn('[Gallery] Using fallback items:', err);
      items = fallbackGallery;
    }

    if (!Array.isArray(items) || items.length === 0) {
      items = fallbackGallery;
    }

    // Sort by newest first (descending id / uploaded_at)
    items.sort((a, b) => (b.id || 0) - (a.id || 0));

    renderGalleryCards(grid, items);
    setupLightbox();
  }

  function renderGalleryCards(container, items) {
    const now = Date.now();

    container.innerHTML = items.map((item) => {
      const upTime = item.uploaded_at || now;
      const isNew = (now - upTime) < THREE_DAYS_MS;
      const idFormatted = String(item.id).padStart(2, '0');

      const badgeHtml = isNew
        ? `<span class="gallery-badge badge-new"><span class="badge-pulse"></span>🔥 NEW</span>`
        : `<span class="gallery-badge badge-num">#${idFormatted}</span>`;

      const title = item.title || `Job #${item.id}`;

      return `
        <div class="gallery-card" data-full="${item.url}" data-title="${title}" data-id="${item.id}">
          <div class="gallery-thumb-wrap">
            ${badgeHtml}
            <img src="${item.url}" alt="${title}" class="gallery-img" loading="lazy" onerror="this.src='./assets/images/mowing.jpg'">
            <div class="gallery-overlay">
              <span class="gallery-zoom-icon">🔍</span>
              <span class="gallery-overlay-text">${title}</span>
            </div>
          </div>
          <div class="gallery-info">
            <span class="gallery-title">${title}</span>
            <span class="gallery-sub-tag">📸 Verified LawnCare Job</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function setupLightbox() {
    const modal = document.getElementById('lightboxModal');
    const img = document.getElementById('lightboxImg');
    const caption = document.getElementById('lightboxCaption');
    const closeBtn = document.getElementById('lightboxClose');

    if (!modal || !img) return;

    // Delegate click from gallery cards
    document.addEventListener('click', (e) => {
      const card = e.target.closest('.gallery-card');
      if (card) {
        const fullSrc = card.getAttribute('data-full');
        const title = card.getAttribute('data-title');
        const id = card.getAttribute('data-id');

        img.src = fullSrc;
        if (caption) {
          caption.innerHTML = `<strong>Foto #${id}:</strong> ${title}`;
        }
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });

    // Close on button click or outside click
    function closeModal() {
      modal.classList.remove('active');
      document.body.style.overflow = '';
      img.src = '';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target.classList.contains('lightbox-content')) {
        closeModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('active')) {
        closeModal();
      }
    });
  }

})();
