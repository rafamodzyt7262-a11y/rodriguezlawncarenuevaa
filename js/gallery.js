/**
 * RODRIGUEZ LAWNCARE - DYNAMIC LIVE WORK GALLERY
 * Loads real-time photos managed via the Discord Bot.
 * Highlights new photos with a glowing "🔥 NEW" badge for 3 days (72 hours),
 * Displays category badges (🏡 Front Yard, 🌿 Back Yard, 🪵 Mulch, 🌳 Tree Care, etc.),
 * and allows instant category filtering and fullscreen viewing.
 */

(function () {
  'use strict';

  const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;

  // Category Icon Map
  const CATEGORY_ICONS = {
    'Front Yard': '🏡',
    'Back Yard': '🌿',
    'Mulch': '🪵',
    'Tree Care': '🌳',
    'Shrubs & Bushes': '✂️',
    'Cleanups': '🧹',
    'Mowing & Edging': '📐',
    'General LawnCare': '🌱'
  };

  // Fallback items in case gallery.json is accessed via local file:// protocol
  const fallbackGallery = [
    {
      id: 2,
      filename: "work_2.jpg",
      url: "./assets/gallery/work_2.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 12),
      title: "Front Yard Renovation & Razor Edging",
      category: "Front Yard"
    },
    {
      id: 3,
      filename: "work_3.jpg",
      url: "./assets/gallery/work_3.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 24 * 4),
      title: "Hedge Trimming & Shrub Shaping",
      category: "Shrubs & Bushes"
    },
    {
      id: 4,
      filename: "work_4.jpg",
      url: "./assets/gallery/work_4.jpg",
      uploaded_at: Date.now() - (1000 * 60 * 60 * 24 * 5),
      title: "Fresh Dark Mulch Installation",
      category: "Mulch"
    }
  ];

  let currentItems = [];
  let currentFilter = 'all';

  document.addEventListener('DOMContentLoaded', () => {
    initGallery();
  });

  function detectCategory(title) {
    if (!title) return 'General LawnCare';
    const lower = title.toLowerCase();
    if (lower.includes('front') || lower.includes('frente') || lower.includes('delantera')) return 'Front Yard';
    if (lower.includes('back') || lower.includes('trasero') || lower.includes('atras')) return 'Back Yard';
    if (lower.includes('mulch') || lower.includes('bark') || lower.includes('acolchado')) return 'Mulch';
    if (lower.includes('tree') || lower.includes('arbol') || lower.includes('poda')) return 'Tree Care';
    if (lower.includes('shrub') || lower.includes('hedge') || lower.includes('bush') || lower.includes('arbusto')) return 'Shrubs & Bushes';
    if (lower.includes('clean') || lower.includes('limpieza') || lower.includes('junk') || lower.includes('leaf') || lower.includes('hojas')) return 'Cleanups';
    if (lower.includes('mow') || lower.includes('edg') || lower.includes('stripe') || lower.includes('corte') || lower.includes('pasto')) return 'Mowing & Edging';
    return 'General LawnCare';
  }

  function getCategoryIcon(cat) {
    return CATEGORY_ICONS[cat] || '🌱';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

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

    // Normalize category property
    items = items.map(item => {
      const cat = item.category || detectCategory(item.title);
      return {
        ...item,
        category: cat
      };
    });

    // Sort by newest first (descending id / uploaded_at)
    items.sort((a, b) => (b.id || 0) - (a.id || 0));
    currentItems = items;

    setupFilterButtons();
    updateCategoryCounts(items);
    renderGalleryCards(grid, items, currentFilter);
    setupLightbox();
  }

  function updateCategoryCounts(items) {
    const counts = { all: items.length };

    items.forEach(item => {
      const cat = item.category || 'General LawnCare';
      counts[cat] = (counts[cat] || 0) + 1;
    });

    const setBadgeCount = (id, count) => {
      const el = document.getElementById(id);
      if (el) el.textContent = String(count || 0);
    };

    setBadgeCount('countAll', counts['all']);
    setBadgeCount('countFront', counts['Front Yard']);
    setBadgeCount('countBack', counts['Back Yard']);
    setBadgeCount('countMulch', counts['Mulch']);
    setBadgeCount('countTree', counts['Tree Care']);
    setBadgeCount('countShrubs', (counts['Shrubs & Bushes'] || 0) + (counts['Cleanups'] || 0) + (counts['Mowing & Edging'] || 0) + (counts['General LawnCare'] || 0));
  }

  function setupFilterButtons() {
    const filterBar = document.getElementById('galleryFilterBar');
    if (!filterBar) return;

    filterBar.addEventListener('click', (e) => {
      const btn = e.target.closest('.gallery-filter-btn');
      if (!btn) return;

      const filter = btn.getAttribute('data-filter');
      if (!filter) return;

      filterBar.querySelectorAll('.gallery-filter-btn').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      currentFilter = filter;

      const grid = document.getElementById('galleryGrid');
      if (grid) {
        renderGalleryCards(grid, currentItems, currentFilter);
      }
    });
  }

  function renderGalleryCards(container, items, filter) {
    const now = Date.now();

    let filtered = items;
    if (filter && filter !== 'all') {
      if (filter === 'Other') {
        filtered = items.filter(item => 
          !['Front Yard', 'Back Yard', 'Mulch', 'Tree Care'].includes(item.category)
        );
      } else {
        filtered = items.filter(item => {
          const itemCat = (item.category || '').toLowerCase();
          const target = filter.toLowerCase();
          return itemCat === target || itemCat.includes(target);
        });
      }
    }

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="gallery-empty-state">
          <span class="empty-icon">🌿</span>
          <h3>No hay fotos en esta categoría aún</h3>
          <p>Pronto subiremos nuevos trabajos de este tipo. Selecciona <strong>"Todos los Trabajos"</strong> para ver más fotos.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = filtered.map((item) => {
      const upTime = item.uploaded_at || now;
      const isNew = (now - upTime) < THREE_DAYS_MS;
      const idFormatted = String(item.id).padStart(2, '0');

      const badgeHtml = isNew
        ? `<span class="gallery-badge badge-new"><span class="badge-pulse"></span>🔥 NEW</span>`
        : `<span class="gallery-badge badge-num">#${idFormatted}</span>`;

      const category = item.category || detectCategory(item.title);
      const icon = getCategoryIcon(category);
      const title = item.title || `Trabajo #${item.id}`;

      return `
        <div class="gallery-card" data-full="${item.url}" data-title="${escapeHtml(title)}" data-category="${escapeHtml(category)}" data-id="${item.id}">
          <div class="gallery-thumb-wrap">
            <div class="gallery-badges-row">
              ${badgeHtml}
              <span class="gallery-category-pill">${icon} ${escapeHtml(category)}</span>
            </div>
            <img src="${item.url}" alt="${escapeHtml(title)}" class="gallery-img" loading="lazy" onerror="this.src='./assets/images/mowing.jpg'">
            <div class="gallery-overlay">
              <span class="gallery-zoom-pill">🔍 Ampliar Foto</span>
            </div>
          </div>
          <div class="gallery-info">
            <div class="gallery-cat-row">
              <span class="gallery-cat-tag">${icon} ${escapeHtml(category)}</span>
              <span class="gallery-id-tag">#${idFormatted}</span>
            </div>
            <h3 class="gallery-title">${escapeHtml(title)}</h3>
            <div class="gallery-card-footer">
              <span class="gallery-sub-tag">📍 Killeen & Central TX</span>
              <span class="gallery-verified-badge">✓ Verificado</span>
            </div>
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

    document.addEventListener('click', (e) => {
      const card = e.target.closest('.gallery-card');
      if (card) {
        const fullSrc = card.getAttribute('data-full');
        const title = card.getAttribute('data-title');
        const category = card.getAttribute('data-category');
        const id = card.getAttribute('data-id');
        const icon = getCategoryIcon(category);

        img.src = fullSrc;
        if (caption) {
          caption.innerHTML = `
            <div class="lightbox-caption-cat">${icon} ${escapeHtml(category)}</div>
            <div class="lightbox-caption-title"><strong>Foto #${id}:</strong> ${escapeHtml(title)}</div>
          `;
        }
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });

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
