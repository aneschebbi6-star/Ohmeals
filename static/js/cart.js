/**
 * OHMEALS - Cart Management
 * Gère le panier via localStorage
 */

// ============================================
// UTILITAIRES PANIER
// ============================================

function getCart() {
    const cart = localStorage.getItem('ohmeals_cart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('ohmeals_cart', JSON.stringify(cart));
    updateCartBadge();
}

function clearCart() {
    localStorage.removeItem('ohmeals_cart');
    updateCartBadge();
}

// ============================================
// ACTIONS PANIER
// ============================================

/**
 * Ajouter un produit au panier
 * @param {Object} product - {id, name, price, unit, variantId, variantName}
 */
function addToCart(product) {
    const cart = getCart();

    // Chercher si le produit (même variante) existe déjà
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

    saveCart(cart);
    showNotification('Produit ajouté au panier !');
}

function removeFromCart(productId, variantId) {
    let cart = getCart();
    cart = cart.filter(item => !(item.id === productId && item.variantId === variantId));
    saveCart(cart);
    renderCart();
}

function updateQuantity(productId, variantId, newQuantity) {
    const cart = getCart();
    const item = cart.find(i => i.id === productId && i.variantId === variantId);

    if (item) {
        if (newQuantity <= 0) {
            removeFromCart(productId, variantId);
        } else {
            item.quantity = newQuantity;
            saveCart(cart);
            renderCart();
        }
    }
}

// ============================================
// AFFICHAGE
// ============================================

function updateCartBadge() {
    const cart = getCart();
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const badge = document.getElementById('cart-count');
    if (badge) {
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'inline-block' : 'none';
    }
}

function calculateTotal() {
    const cart = getCart();
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

function renderCart() {
    const cart = getCart();
    const tbody = document.getElementById('cart-items');
    const totalSpan = document.getElementById('cart-total-value');
    const emptyMessage = document.getElementById('cart-empty');
    const cartTable = document.getElementById('cart-table');
    const checkoutBtn = document.getElementById('checkout-btn');

    if (!tbody) return; // Pas sur la page panier

    if (cart.length === 0) {
        if (emptyMessage) emptyMessage.style.display = 'block';
        if (cartTable) cartTable.style.display = 'none';
        if (checkoutBtn) checkoutBtn.style.display = 'none';
        return;
    }

    if (emptyMessage) emptyMessage.style.display = 'none';
    if (cartTable) cartTable.style.display = 'table';
    if (checkoutBtn) checkoutBtn.style.display = 'inline-block';

    tbody.innerHTML = '';

    cart.forEach(item => {
        const lineTotal = item.price * item.quantity;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <strong>${item.name}</strong>
                ${item.variantName ? `<br><small>${item.variantName}</small>` : ''}
            </td>
            <td>${item.price.toFixed(2)} DT / ${item.unit}</td>
            <td>
                <button class="qty-btn" onclick="updateQuantity(${item.id}, ${item.variantId}, ${item.quantity - 1})">-</button>
                <span class="qty-value">${item.quantity}</span>
                <button class="qty-btn" onclick="updateQuantity(${item.id}, ${item.variantId}, ${item.quantity + 1})">+</button>
            </td>
            <td class="line-total">${lineTotal.toFixed(2)} DT</td>
            <td>
                <button class="remove-btn" onclick="removeFromCart(${item.id}, ${item.variantId})">
                    <i class="fa fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    if (totalSpan) {
        totalSpan.textContent = calculateTotal().toFixed(2);
    }
}

// ============================================
// CHECKOUT MODAL
// ============================================

function openCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function submitOrder(event) {
    event.preventDefault();

    const form = event.target;
    const cart = getCart();

    if (cart.length === 0) {
        alert('Votre panier est vide !');
        return;
    }

    // Vérifier la zone de livraison
    const city = form.city ? form.city.value : '';
    const deliveryCities = ['Tunis', 'Ariana', 'Ben Arous'];

    if (city && !deliveryCities.includes(city)) {
        alert('Désolé, la livraison n\'est pas disponible dans votre ville actuellement.');
        return;
    }

    const orderData = {
        customer_name: form.name.value,
        customer_phone: form.phone.value,
        customer_email: form.email.value || '',
        delivery_address: form.address.value,
        city: city,
        items: cart.map(item => ({
            product_id: item.id,
            variant_id: item.variantId,
            quantity: item.quantity,
            unit: item.unit,
            price: item.price
        }))
    };

    try {
        const response = await fetch('/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (response.ok) {
            clearCart();
            closeCheckoutModal();
            showConfirmation(result.order_id);
        } else {
            alert('Erreur: ' + (result.error || 'Commande échouée'));
        }
    } catch (error) {
        console.error('Order error:', error);
        alert('Erreur de connexion. Veuillez réessayer.');
    }
}

function showConfirmation(orderId) {
    const container = document.querySelector('.cart_section .container');
    if (container) {
        container.innerHTML = `
            <div class="order-confirmation">
                <i class="fa fa-check-circle" style="font-size: 4rem; color: #28a745;"></i>
                <h2>Commande Confirmée !</h2>
                <p>Votre commande #${orderId} a été enregistrée avec succès.</p>
                <p>Nous vous contacterons sous peu pour confirmation.</p>
                <a href="/" class="btn main-btn">Retour à l'accueil</a>
            </div>
        `;
    }
}

function showNotification(message) {
    // Créer une notification temporaire
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

// ============================================
// DELIVERY ZONE CHECK
// ============================================

const DELIVERY_CITIES = ['Tunis', 'Ariana', 'Ben Arous'];

function checkDeliveryZone() {
    const citySelect = document.getElementById('city-select');
    const message = document.getElementById('delivery-message');
    const submitBtn = document.getElementById('checkout-submit-btn');

    if (!citySelect || !message) return;

    const selectedCity = citySelect.value;

    if (!selectedCity) {
        message.style.display = 'none';
        return;
    }

    if (DELIVERY_CITIES.includes(selectedCity)) {
        message.style.display = 'block';
        message.style.background = '#d4edda';
        message.style.color = '#155724';
        message.innerHTML = '<i class="fa fa-check"></i> Livraison disponible à ' + selectedCity + ' !';
        if (submitBtn) submitBtn.disabled = false;
    } else {
        message.style.display = 'block';
        message.style.background = '#f8d7da';
        message.style.color = '#721c24';
        message.innerHTML = '<i class="fa fa-times"></i> Désolé, la livraison n\'est pas encore disponible à ' + selectedCity + '. Zones desservies: Tunis, Ariana, Ben Arous.';
        if (submitBtn) submitBtn.disabled = true;
    }
}

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    updateCartBadge();
    renderCart();

    // Fermer modal en cliquant dehors
    const modal = document.getElementById('checkout-modal');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeCheckoutModal();
            }
        });
    }
});
