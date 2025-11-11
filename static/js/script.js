// Hurtrock Music Store - Interactive JavaScript

// Immediate theme application to prevent flicker
(function() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (document.body) {
        document.body.setAttribute('data-theme', savedTheme);
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Functionality - Enhanced to prevent flicker
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // Load saved theme immediately to prevent flicker
    const savedTheme = localStorage.getItem('theme') || 'dark';
    // Apply theme to both body and html for comprehensive coverage
    document.documentElement.setAttribute('data-theme', savedTheme);
    body.setAttribute('data-theme', savedTheme);
    
    // Only update icon if themeToggle element exists
    if (themeToggle) {
        updateThemeIcon(savedTheme);

        themeToggle.addEventListener('click', function() {
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            // Add smooth transition class temporarily
            body.classList.add('theme-transitioning');
            
            // Apply theme to both body and html for comprehensive coverage
            document.documentElement.setAttribute('data-theme', newTheme);
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Remove transition class after animation completes
            setTimeout(() => {
                body.classList.remove('theme-transitioning');
            }, 300);
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
            } else {
                icon.className = 'fas fa-moon';
            }
        }
    }

    // Real-time Search Functionality
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;
    let currentFocus = -1;

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            currentFocus = -1;

            if (query.length < 2) {
                hideSearchResults();
                return;
            }

            // Show loading state
            searchResults.innerHTML = '<div class="search-result-item text-center"><i class="fas fa-spinner fa-spin"></i> Mencari...</div>';
            searchResults.style.display = 'block';

            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });

        searchInput.addEventListener('blur', function() {
            setTimeout(hideSearchResults, 200);
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const items = searchResults.querySelectorAll('.search-result-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentFocus++;
                if (currentFocus >= items.length) currentFocus = 0;
                addActive(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentFocus--;
                if (currentFocus < 0) currentFocus = items.length - 1;
                addActive(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentFocus > -1 && items[currentFocus]) {
                    items[currentFocus].click();
                }
            } else if (e.key === 'Escape') {
                hideSearchResults();
                this.blur();
            }
        });
    }

    function addActive(items) {
        if (!items) return;
        removeActive(items);
        if (currentFocus >= 0 && items[currentFocus]) {
            items[currentFocus].classList.add('search-active');
        }
    }

    function removeActive(items) {
        items.forEach(item => item.classList.remove('search-active'));
    }

    function performSearch(query) {
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                searchResults.innerHTML = '<div class="search-result-item text-center text-muted">Terjadi kesalahan saat mencari. Silakan coba lagi.</div>';
                searchResults.style.display = 'block';
            });
    }

    function displaySearchResults(products) {
        if (!products || products.length === 0) {
            hideSearchResults();
            return;
        }

        // Handle error response
        if (products.error) {
            console.error('Search error:', products.error);
            hideSearchResults();
            return;
        }

        const resultsHTML = products.map(product => `
            <div class="search-result-item" onclick="goToProduct(${product.id})" data-product-id="${product.id}">
                <div class="d-flex align-items-center">
                    <img src="${product.image_url}" alt="${product.name}" 
                         style="width: 40px; height: 40px; object-fit: cover; border-radius: 5px; margin-right: 10px;"
                         onerror="this.src='https://via.placeholder.com/40x40/FF6B35/FFFFFF?text=P'">
                    <div class="flex-grow-1">
                        <div class="fw-bold">${product.name}</div>
                        ${product.brand ? `<div class="text-muted small">${product.brand}</div>` : ''}
                        <div class="text-orange small fw-bold">Rp ${parseFloat(product.price).toLocaleString('id-ID')}</div>
                    </div>
                </div>
            </div>
        `).join('');

        searchResults.innerHTML = resultsHTML;
        searchResults.style.display = 'block';
    }

    function hideSearchResults() {
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }

    window.goToProduct = function(productId) {
        window.location.href = `/product/${productId}`;
    };

    // Cart Count Update
    updateCartCount();

    function updateCartCount() {
        const cartBadge = document.getElementById('cartCount');
        if (cartBadge) {
            // Make AJAX call to get actual cart count
            fetch('/api/cart/count')
                .then(response => response.json())
                .then(data => {
                    cartBadge.textContent = data.count || '0';
                    // Hide badge if count is 0
                    if (data.count > 0) {
                        cartBadge.style.display = 'inline';
                    } else {
                        cartBadge.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching cart count:', error);


cartBadge.textContent = '0';
                    cartBadge.style.display = 'none';
                });
        }
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Add animation classes when elements come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe cards and feature boxes
    document.querySelectorAll('.card, .feature-box').forEach(el => {
        observer.observe(el);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Quantity controls for product pages
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(control => {
        const decreaseBtn = control.querySelector('.decrease');
        const increaseBtn = control.querySelector('.increase');
        const input = control.querySelector('input');

        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                }
            });
        }

        if (increaseBtn) {
            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 1;
                const maxValue = parseInt(input.getAttribute('max')) || 999;
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                }
            });
        }
    });

    // Toast notifications for better UX
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    }

    // Make showToast globally available
    window.showToast = showToast;

});

// Add to cart functionality
function addToCart(productId, quantity = 1) {
    fetch('/add_to_cart/' + productId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'quantity=' + quantity
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Produk berhasil ditambahkan ke keranjang!');
            updateCartCount();
        } else {
            showToast(data.message || 'Terjadi kesalahan', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Terjadi kesalahan saat menambahkan ke keranjang', 'error');
    });
}