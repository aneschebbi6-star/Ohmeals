// On place les fonctions globales à l'extérieur ou on les attache à window
// pour qu'elles soient accessibles via les attributs onclick du HTML.

let state = {
  activeCategory: '*',
  sortPrice: 'default',
  sortTaste: 'all',
  currentProduct: null,
  selectedVariant: null,
  modalQty: 1
};

document.addEventListener('DOMContentLoaded', function () {
  const productsDB = window.productsDB || [];

  // -----------------------------------------------------------
  // 2. Configuration Utilitaires
  // -----------------------------------------------------------
  productsDB.forEach(p => {
    p.get_default_variant = function () {
      if (this.variants && this.variants.length > 0) {
        const def = this.variants.find(v => v.is_default);
        return def || this.variants[0];
      }
      return null;
    };
  });

  // -----------------------------------------------------------
  // 3. Fonctions de Rendu (Accessibles en interne)
  // -----------------------------------------------------------
  function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;
    grid.innerHTML = '';

    // 1. Filtrage
    let filtered = productsDB.filter(p => {
      const matchCat = state.activeCategory === '*' || p.category === state.activeCategory;
      const matchTaste = state.sortTaste === 'all' || p.taste === state.sortTaste;
      return matchCat && matchTaste;
    });

    // 2. Tri Prix
    if (state.sortPrice !== 'default') {
      filtered.sort((a, b) => {
        const priceA = a.get_default_variant()?.price || 0;
        const priceB = b.get_default_variant()?.price || 0;
        return state.sortPrice === 'asc' ? priceA - priceB : priceB - priceA;
      });
    }

    // 3. Génération HTML
    filtered.forEach(product => {
      const defaultVariant = product.get_default_variant();
      if (!defaultVariant) return;

      const tasteLabel = product.taste ? (product.taste.charAt(0).toUpperCase() + product.taste.slice(1)) : '';
      const tasteClass = product.taste === 'sucré' ? 'taste-sucre' : 'taste-sale';
      const tasteBadge = tasteLabel ? `<span class="taste-badge ${tasteClass}">${tasteLabel}</span>` : '';

      const col = document.createElement('div');
      col.className = `col-sm-6 col-lg-4 all ${product.category}`;
      col.innerHTML = `
                <div class="box h-100">
                    <div class="img-box">
                        <img src="${product.image}" alt="${product.name}" />
                    </div>
                    <div class="detail-box">
                        <h5>${product.name}</h5>
                        <p>${tasteBadge}</p>
                        <p>${product.description || ''}</p>
                        <div class="options d-flex justify-content-between align-items-center mt-3">
                            <div>
                                <h6 class="price-preview mb-0">${defaultVariant.price.toFixed(2)} DT</h6>
                                <small class="text-muted" style="font-size:0.7rem">/ ${defaultVariant.unit}</small>
                            </div>
                            <a href="#" class="btn-order" onclick="openModal(${product.id}, event)">
                                <i class="bi bi-cart-plus"></i> Commander
                            </a>
                        </div>
                    </div>
                </div>`;
      grid.appendChild(col);
    });
  }

  // -----------------------------------------------------------
  // 4. Initialisation & Events
  // -----------------------------------------------------------
  document.querySelectorAll('#categoryFilters li').forEach(li => {
    li.addEventListener('click', (e) => {
      document.querySelectorAll('#categoryFilters li').forEach(el => el.classList.remove('active'));
      e.currentTarget.classList.add('active'); // Utilisation de currentTarget
      state.activeCategory = e.currentTarget.dataset.filter;
      renderProducts();
    });
  });

  document.getElementById('sortPrice')?.addEventListener('change', (e) => {
    state.sortPrice = e.target.value;
    renderProducts();
  });

  document.getElementById('sortTaste')?.addEventListener('change', (e) => {
    state.sortTaste = e.target.value;
    renderProducts();
  });

  // Attacher les fonctions nécessaires au window pour le HTML
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.updateModalQty = updateModalQty;
  window.addToCart = addToCart;
  window.selectVariant = selectVariant;

  renderProducts();
});

// -----------------------------------------------------------
// 5. Fonctions Logique Modal (Hors du DOMContentLoaded)
// -----------------------------------------------------------

function openModal(productId, event) {
  if (event) event.preventDefault();
  const productsDB = window.productsDB || [];
  const product = productsDB.find(p => p.id === productId);
  if (!product) return;

  state.currentProduct = product;
  state.selectedVariant = product.get_default_variant();
  state.modalQty = 1;

  document.getElementById('modalProductName').innerText = product.name;
  document.getElementById('modalProductDesc').innerText = product.description || '';

  renderVariants(product.variants);
  updateModalDisplay();

  const modal = document.getElementById('productModal');
  if (modal) modal.classList.add('active');
}

function renderVariants(variants) {
  const container = document.getElementById('modalVariantsList');
  if (!container) return;
  container.innerHTML = '';

  variants.forEach(variant => {
    const isAvailable = variant.is_available;
    const isSelected = state.selectedVariant && state.selectedVariant.id === variant.id;

    let className = 'variant-option';
    if (!isAvailable) className += ' disabled';
    if (isSelected && isAvailable) className += ' selected';

    const div = document.createElement('div');
    div.className = className;
    if (isAvailable) {
      div.onclick = () => selectVariant(variant);
    }

    const vName = variant.variant_name || variant.name;
    div.innerHTML = `
            <div>
                <span class="fw-bold">${vName}</span>
                <div class="small text-muted">${variant.price.toFixed(2)} DT / ${variant.unit}</div>
            </div>
            ${isSelected ? '<i class="bi bi-check-circle-fill text-success"></i>' : ''}
            ${!isAvailable ? '<span class="text-danger small">Indisponible</span>' : ''}
        `;
    container.appendChild(div);
  });
}

function selectVariant(variant) {
  state.selectedVariant = variant;
  renderVariants(state.currentProduct.variants);
  updateModalDisplay();
}

function updateModalQty(delta) {
  const newQty = state.modalQty + delta;
  if (newQty >= 1) {
    state.modalQty = newQty;
    updateModalDisplay();
  }
}

function updateModalDisplay() {
  const qtyEl = document.getElementById('modalQty');
  const totalEl = document.getElementById('modalTotalPrice');

  if (qtyEl) qtyEl.innerText = state.modalQty;
  if (state.selectedVariant && totalEl) {
    const total = state.selectedVariant.price * state.modalQty;
    totalEl.innerText = `${total.toFixed(2)} DT`;
  }
}

function addToCart() {
  if (!state.selectedVariant || !state.currentProduct) return;

  // Utiliser la fonction addToCart de cart.js
  const product = {
    id: state.currentProduct.id,
    name: state.currentProduct.name,
    price: state.selectedVariant.price,
    unit: state.selectedVariant.unit,
    variantId: state.selectedVariant.id,
    variantName: state.selectedVariant.variant_name || state.selectedVariant.name
  };

  // Ajouter la quantité sélectionnée
  for (let i = 0; i < state.modalQty; i++) {
    if (typeof window.addToCartFromMenu === 'function') {
      window.addToCartFromMenu(product);
    }
  }

  closeModal();
}

function closeModal() {
  const modal = document.getElementById('productModal');
  if (modal) modal.classList.remove('active');
}

// Fonction appelée par menu.js pour ajouter au panier via cart.js
window.addToCartFromMenu = function (product) {
  // Utiliser les fonctions de cart.js
  const cart = JSON.parse(localStorage.getItem('ohmeals_cart') || '[]');

  const existingIndex = cart.findIndex(
    item => item.id === product.id && item.variantId === product.variantId
  );

  if (existingIndex > -1) {
    cart[existingIndex].quantity += 1;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      unit: product.unit,
      variantId: product.variantId || null,
      variantName: product.variantName || '',
      quantity: 1
    });
  }

  localStorage.setItem('ohmeals_cart', JSON.stringify(cart));

  // Mettre à jour le badge
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById('cart-count');
  if (badge) {
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? 'inline-block' : 'none';
  }

  // Notification
  showCartNotification('Produit ajouté au panier !');
};

function showCartNotification(message) {
  let notif = document.getElementById('cart-notification');
  if (!notif) {
    notif = document.createElement('div');
    notif.id = 'cart-notification';
    notif.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #28a745;
      color: white;
      padding: 15px 25px;
      border-radius: 8px;
      z-index: 9999;
      opacity: 0;
      transition: opacity 0.3s;
    `;
    document.body.appendChild(notif);
  }

  notif.textContent = message;
  notif.style.opacity = '1';

  setTimeout(() => {
    notif.style.opacity = '0';
  }, 2000);
}