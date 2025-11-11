// Cashier Online-Only Module
console.log('Cashier online module loaded');

// Simple connectivity checker for online-only mode
function checkServerConnection() {
    return fetch('/api/cashier/connectivity', {
        method: 'GET',
        cache: 'no-cache',
        headers: {
            'Cache-Control': 'no-cache'
        }
    })
    .then(response => {
        if (response.ok) {
            console.log('[CONNECTION] Server connection: ONLINE');
            return true;
        } else {
            console.log('[CONNECTION] Server connection: OFFLINE (HTTP error)');
            return false;
        }
    })
    .catch(error => {
        console.log('[CONNECTION] Server connection: OFFLINE (Network error)', error);
        return false;
    });
}

// Simple cart storage functions
function saveCartToStorage(cart) {
    try {
        localStorage.setItem('cashier_cart', JSON.stringify(cart));
        console.log(`[CART] Saved ${cart.length} items to localStorage`);
    } catch (e) {
        console.error('[CART] Failed to save cart:', e);
    }
}

function getCartFromStorage() {
    try {
        const cart = localStorage.getItem('cashier_cart');
        return cart ? JSON.parse(cart) : [];
    } catch (e) {
        console.error('[CART] Failed to load cart:', e);
        return [];
    }
}

function clearCartFromStorage() {
    localStorage.removeItem('cashier_cart');
}

// Export minimal functions for compatibility
window.cashierOnline = {
    checkServerConnection,
    saveCartToStorage,
    getCartFromStorage,
    clearCartFromStorage
};

console.log('[CASHIER] Online-only module initialized');
