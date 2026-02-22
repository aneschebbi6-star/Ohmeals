/**
 * OHMEALS — Product Display Modern JS (2026)
 * menu.js — Cards Rendering + Advanced Gallery + Dynamic Modal
 */

// --- Global State ---
const state = {
  products: window.productsDB || [],
  filteredProducts: [],
  categories: [],
  activeCategory: '*',
  sortBy: 'default',
  tasteFilter: 'all',
  modal: {
    product: null,
    currentImgIndex: 0,
    selectedVariant: null,
    qty: 1
  }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  initProducts();
  initFilters();
  initSorting();
  handleOverlayClick();
});

function initProducts() {
  const grid = document.getElementById('productsGrid');
  if (grid) {
    grid.innerHTML = `
      <div class="pm-skeleton-grid w-100">
        ${Array(6).fill().map(() => `
          <div class="pm-skeleton-card">
            <div class="skeleton-img"></div>
            <div class="skeleton-content">
              <div class="skeleton-line short"></div>
              <div class="skeleton-line mid"></div>
              <div class="skeleton-line"></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // Simulate loading delay for smooth transition (or remove for instant)
  setTimeout(() => {
    state.filteredProducts = [...state.products];
    renderProducts();
  }, 800);
}

function initFilters() {
  const filterItems = document.querySelectorAll('.filters_menu li');
  filterItems.forEach(item => {
    item.addEventListener('click', () => {
      filterItems.forEach(li => li.classList.remove('active'));
      item.classList.add('active');
      state.activeCategory = item.getAttribute('data-filter');
      applyFilters();
    });
  });
}

function initSorting() {
  const sortPrice = document.getElementById('sortPrice');
  const sortTaste = document.getElementById('sortTaste');

  if (sortPrice) {
    sortPrice.addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      applyFilters();
    });
  }

  if (sortTaste) {
    sortTaste.addEventListener('change', (e) => {
      state.tasteFilter = e.target.value;
      applyFilters();
    });
  }
}

function handleOverlayClick() {
  const overlay = document.getElementById('productModalOverlay');
  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal();
    });
  }
}

// --- Filter & Sort Logic ---
function applyFilters() {
  let list = [...state.products];

  // Category
  if (state.activeCategory !== '*') {
    list = list.filter(p => p.category === state.activeCategory);
  }

  // Taste
  if (state.tasteFilter !== 'all') {
    list = list.filter(p => p.taste === state.tasteFilter);
  }

  // Sort
  if (state.sortBy === 'asc') {
    list.sort((a, b) => getMinPrice(a) - getMinPrice(b));
  } else if (state.sortBy === 'desc') {
    list.sort((a, b) => getMinPrice(b) - getMinPrice(a));
  }

  state.filteredProducts = list;
  renderProducts();
}

function getMinPrice(product) {
  if (!product.variants || product.variants.length === 0) return 0;
  const defaultVar = product.variants.find(v => v.is_default);
  return defaultVar ? defaultVar.price : product.variants[0].price;
}

// --- Rendering ---
function renderProducts() {
  const grid = document.getElementById('productsGrid');
  if (!grid) return;

  if (state.filteredProducts.length === 0) {
    grid.innerHTML = '<div class="col-12 text-center py-5 text-muted">Acuun produit trouvé.</div>';
    return;
  }

  grid.innerHTML = state.filteredProducts.map(p => {
    const primaryImg = p.image || '/static/images/default-food.jpg';
    const hasMedia = (p.images && p.images.length > 1) || p.video_url;

    // Stock Check
    const anyInStock = p.variants?.some(v => v.is_in_stock);
    const soldOutClass = !anyInStock ? 'is-sold-out' : '';
    const soldOutBadge = !anyInStock ? `<div class="badge-soldout">ÉPUISÉ</div>` : '';

    const discountBadge = p.discount > 0 ? `<div class="badge-discount">-${p.discount}%</div>` : '';
    const mediaBadge = hasMedia ? `
            <div class="badge-media-count">
                <i class="fa ${p.video_url ? 'fa-video-camera' : 'fa-camera'}"></i>
                ${p.images ? p.images.length : 1}
            </div>` : '';

    const defVar = p.variants?.find(v => v.is_default) || p.variants?.[0];
    const priceFinal = defVar ? (defVar.price * (1 - (p.discount || 0) / 100)).toFixed(2) : '0.00';
    const priceOrig = p.discount > 0 && defVar ? `<span class="price-original">${defVar.price.toFixed(2)}</span>` : '';

    return `
            <div class="product-card ${soldOutClass}" onclick="openModal(${p.id})">
                <div class="card-img-box">
                    <img src="${primaryImg}" alt="${p.name}" loading="lazy">
                    <div class="card-img-overlay"></div>
                    ${discountBadge}
                    ${soldOutBadge}
                    ${mediaBadge}
                    <button class="quick-order-btn">${anyInStock ? 'Commander' : 'Voir Détails'}</button>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <h3 class="card-title">${p.name}</h3>
                        <span class="taste-badge-modern ${p.taste === 'sucre' ? 'sucre' : 'sale'}">
                            ${p.taste === 'sucre' ? '🍭 Sucré' : '🧂 Salé'}
                        </span>
                    </div>
                    <p class="card-description">${p.description || "Découvrez notre savoureuse création préparée avec passion."}</p>
                    <div class="card-price-row">
                        <div class="price-box">
                            ${priceOrig}
                            <span class="price-final">${priceFinal} DT</span>
                            <span class="price-unit">${defVar ? '/ ' + defVar.unit : ''}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
  }).join('');
}

// --- Modal Logic ---
window.openModal = function (productId) {
  const product = state.products.find(p => p.id === productId);
  if (!product) return;

  state.modal.product = product;
  state.modal.currentImgIndex = 0;
  state.modal.qty = 1;
  state.modal.selectedVariant = product.variants?.find(v => v.is_default) || product.variants?.[0] || null;

  renderModalContent();
  const overlay = document.getElementById('productModalOverlay');
  if (overlay) {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
};

window.closeModal = function () {
  const overlay = document.getElementById('productModalOverlay');
  if (overlay) {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    state.modal.product = null;
    // Stop video if playing
    const vidContainer = document.getElementById('pmVideoContainer');
    if (vidContainer) vidContainer.innerHTML = '';
  }
};

function renderModalContent() {
  const p = state.modal.product;

  // Gallery
  renderGallery();

  // Info
  document.getElementById('pmTitle').innerText = p.name;
  document.getElementById('pmDesc').innerText = p.description || "";

  // Taste Badge
  const badgeRow = document.getElementById('pmBadgesRow');
  badgeRow.innerHTML = `<span class="taste-badge-modern ${p.taste === 'sucre' ? 'sucre' : 'sale'}">
        ${p.taste === 'sucre' ? '🍭 Sucré' : '🧂 Salé'}
    </span>`;

  // Video
  renderVideo();

  // Variants
  renderVariants();

  // Qty & Price
  updateModalPrice();
}

function renderGallery() {
  const p = state.modal.product;
  const galleryContainer = document.getElementById('pmGallery');
  const thumbContainer = document.getElementById('pmThumbnails');

  const allImages = p.images && p.images.length > 0
    ? p.images.sort((a, b) => a.position - b.position)
    : [{ image_url: p.image || '/static/images/default-food.jpg' }];

  // Main View
  let html = `<img src="${allImages[state.modal.currentImgIndex].image_url}" class="pm-main-img" id="pmMainImg">`;

  if (allImages.length > 1) {
    html += `
            <button class="pm-arrow left" onclick="changeImg(-1)">❮</button>
            <button class="pm-arrow right" onclick="changeImg(1)">❯</button>
            <div class="pm-img-counter">${state.modal.currentImgIndex + 1} / ${allImages.length}</div>
        `;
  }
  galleryContainer.innerHTML = html;

  // Thumbnails
  if (allImages.length > 1) {
    thumbContainer.style.display = 'flex';
    thumbContainer.innerHTML = allImages.map((img, idx) => `
            <img src="${img.image_url}" class="pm-thumb ${idx === state.modal.currentImgIndex ? 'active' : ''}" 
                 onclick="goToImg(${idx})" loading="lazy">
        `).join('');
  } else {
    thumbContainer.style.display = 'none';
  }
}

window.changeImg = function (dir) {
  const p = state.modal.product;
  const count = p.images?.length || 1;
  state.modal.currentImgIndex = (state.modal.currentImgIndex + dir + count) % count;
  renderGallery();
};

window.goToImg = function (idx) {
  state.modal.currentImgIndex = idx;
  renderGallery();
};

function renderVideo() {
  const p = state.modal.product;
  const section = document.getElementById('pmVideoSection');
  const container = document.getElementById('pmVideoContainer');

  if (!p.video_url) {
    section.style.display = 'none';
    return;
  }

  section.style.display = 'block';

  if (p.video_url.includes('youtube.com') || p.video_url.includes('youtu.be')) {
    let videoId = '';
    if (p.video_url.includes('v=')) {
      videoId = p.video_url.split('v=')[1].split('&')[0];
    } else {
      videoId = p.video_url.split('/').pop();
    }
    container.innerHTML = `
            <div class="pm-video-wrapper">
                <iframe width="100%" height="315" src="https://www.youtube.com/embed/${videoId}" 
                        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        `;
  } else {
    container.innerHTML = `
            <div class="pm-video-wrapper">
                <video controls width="100%">
                    <source src="${p.video_url}" type="video/mp4">
                    Votre navigateur ne supporte pas la lecture de vidéos.
                </video>
            </div>
        `;
  }
}

function renderVariants() {
  const p = state.modal.product;
  const grid = document.getElementById('pmVariantsGrid');

  if (!p.variants || p.variants.length === 0) {
    grid.innerHTML = '<div class="text-muted">Aucune variante disponible.</div>';
    return;
  }

  grid.innerHTML = p.variants.map(v => {
    const isSelected = state.modal.selectedVariant?.id === v.id;
    return `
            <div class="pm-variant-item ${isSelected ? 'selected' : ''} ${!v.is_available ? 'disabled' : ''}" 
                 onclick="${v.is_available ? `selectVariant(${v.id})` : ''}">
                <div class="d-flex flex-column">
                    <span class="pm-variant-name">${v.variant_name}</span>
                    <span class="pm-variant-price">${v.price.toFixed(2)} DT / ${v.unit}</span>
                </div>
                ${isSelected ? '<i class="fa fa-check-circle pm-variant-check"></i>' : ''}
                ${!v.is_available ? '<span class="pm-variant-unavail">Indisponible</span>' : ''}
            </div>
        `;
  }).join('');
}

window.selectVariant = function (variantId) {
  const v = state.modal.product.variants.find(varItem => varItem.id === variantId);
  if (v) {
    state.modal.selectedVariant = v;
    renderVariants();
    updateModalPrice();
    // Finalize UI
    requestAnimationFrame(() => {
      updateModalBtnText(); // Update button text with qty
    });
  }
};

function updateModalBtnText() {
  const btn = document.querySelector('.pm-add-btn');
  if (btn) {
    const qty = state.modal.qty;
    btn.innerHTML = `<i class="fa fa-shopping-basket"></i> Ajouter ${qty} au panier`;
  }
}

window.updateModalQty = function (delta) {
  state.modal.qty = Math.max(1, state.modal.qty + delta);
  document.getElementById('pmQtyValue').innerText = state.modal.qty;
  updateModalPrice();
  updateModalBtnText(); // Update button text when qty changes
};

function updateModalPrice() {
  if (!state.modal.selectedVariant) return;
  const p = state.modal.product;
  const v = state.modal.selectedVariant;
  const unitPrice = v.price * (1 - (p.discount || 0) / 100);
  const total = (unitPrice * state.modal.qty).toFixed(2);
  document.getElementById('pmTotalPrice').innerText = `${total} DT`;
}

// --- Cart Integration ---
window.handleModalAddToCart = function () {
  if (!state.modal.selectedVariant) return;

  const p = state.modal.product;
  const v = state.modal.selectedVariant;
  const qty = state.modal.qty;

  const cartItem = {
    id: p.id,
    name: p.name,
    price: v.price * (1 - (p.discount || 0) / 100),
    unit: v.unit,
    variantId: v.id,
    variantName: v.variant_name,
    quantity: qty
  };

  // Use ohmeals_cart key for compatibility with cart.js
  const CART_KEY = 'ohmeals_cart';
  let cart = JSON.parse(localStorage.getItem(CART_KEY) || '[]');

  const existingIndex = cart.findIndex(
    item => item.id === cartItem.id && item.variantId === cartItem.variantId
  );

  if (existingIndex > -1) {
    cart[existingIndex].quantity += qty;
  } else {
    cart.push(cartItem);
  }

  // Save and Update UI
  localStorage.setItem(CART_KEY, JSON.stringify(cart));

  // Call legacy functions if they exist in cart.js
  if (typeof window.updateCartBadge === 'function') {
    window.updateCartBadge();
  }

  // Show visual +1 feedback
  if (typeof window.showAddToCartAnimation === 'function') {
    window.showAddToCartAnimation(qty);
  }

  if (typeof window.showNotification === 'function') {
    window.showNotification(`${p.name} ajouté au panier !`);
  } else {
    showToast(`${p.name} ajouté au panier !`);
  }

  closeModal();
};

function showToast(msg) {
  const toast = document.getElementById('pmToast');
  if (toast) {
    toast.innerText = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  }
}