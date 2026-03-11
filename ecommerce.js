/* =====================================================
   ShopStyle E-Commerce - JavaScript
   ===================================================== */

// Product Data
const products = [
    {
        id: 1,
        title: "Premium Wireless Headphones",
        category: "electronics",
        price: 149.99,
        originalPrice: 199.99,
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        rating: 4.8,
        reviews: 256,
        badge: "sale",
        filter: "trending",
        description: "Experience premium sound quality with our wireless headphones featuring active noise cancellation and 30-hour battery life."
    },
    {
        id: 2,
        title: "Smart Watch Pro Series",
        category: "electronics",
        price: 299.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        rating: 4.9,
        reviews: 189,
        badge: "new",
        filter: "new",
        description: "Stay connected with our latest smart watch featuring health monitoring, GPS, and seamless smartphone integration."
    },
    {
        id: 3,
        title: "Designer Leather Handbag",
        category: "fashion",
        price: 89.99,
        originalPrice: 129.99,
        image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500",
        rating: 4.7,
        reviews: 324,
        badge: "sale",
        filter: "sale",
        description: "Elegant genuine leather handbag with multiple compartments, perfect for everyday use or special occasions."
    },
    {
        id: 4,
        title: "Men's Classic Sneakers",
        category: "fashion",
        price: 79.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
        rating: 4.6,
        reviews: 412,
        badge: "hot",
        filter: "trending",
        description: "Comfortable and stylish sneakers made with premium materials for all-day comfort."
    },
    {
        id: 5,
        title: "Minimalist Desk Lamp",
        category: "home",
        price: 45.99,
        originalPrice: 59.99,
        image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500",
        rating: 4.5,
        reviews: 156,
        badge: "sale",
        filter: "sale",
        description: "Modern LED desk lamp with adjustable brightness and color temperature for perfect lighting."
    },
    {
        id: 6,
        title: "Organic Skincare Set",
        category: "beauty",
        price: 65.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500",
        rating: 4.8,
        reviews: 287,
        badge: "new",
        filter: "new",
        description: "Complete skincare routine with natural, organic ingredients for radiant, healthy skin."
    },
    {
        id: 7,
        title: "Professional Yoga Mat",
        category: "sports",
        price: 34.99,
        originalPrice: 44.99,
        image: "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500",
        rating: 4.7,
        reviews: 198,
        badge: "sale",
        filter: "sale",
        description: "Extra thick, non-slip yoga mat with alignment lines for perfect poses every time."
    },
    {
        id: 8,
        title: "Portable Bluetooth Speaker",
        category: "electronics",
        price: 59.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500",
        rating: 4.6,
        reviews: 342,
        badge: "hot",
        filter: "trending",
        description: "Waterproof portable speaker with 360° sound and 20-hour battery life for outdoor adventures."
    },
    {
        id: 9,
        title: "Women's Summer Dress",
        category: "fashion",
        price: 54.99,
        originalPrice: 74.99,
        image: "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500",
        rating: 4.5,
        reviews: 267,
        badge: "sale",
        filter: "sale",
        description: "Flowy and comfortable summer dress perfect for beach days and casual outings."
    },
    {
        id: 10,
        title: "Cozy Throw Blanket",
        category: "home",
        price: 39.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500",
        rating: 4.9,
        reviews: 423,
        badge: "hot",
        filter: "trending",
        description: "Ultra-soft fleece throw blanket for cozy evenings at home."
    },
    {
        id: 11,
        title: "Premium Makeup Palette",
        category: "beauty",
        price: 48.99,
        originalPrice: 62.99,
        image: "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500",
        rating: 4.7,
        reviews: 312,
        badge: "sale",
        filter: "sale",
        description: "Professional makeup palette with 24 highly pigmented shades for endless looks."
    },
    {
        id: 12,
        title: "Running Shoes Elite",
        category: "sports",
        price: 129.99,
        originalPrice: null,
        image: "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?w=500",
        rating: 4.8,
        reviews: 245,
        badge: "new",
        filter: "new",
        description: "High-performance running shoes with responsive cushioning and breathable mesh upper."
    }
];

// Cart State
let cart = [];
let wishlist = [];

// DOM Elements
const productsGrid = document.getElementById('productsGrid');
const cartBtn = document.getElementById('cartBtn');
const cartModal = document.getElementById('cartModal');
const closeCartModal = document.getElementById('closeCartModal');
const cartItems = document.getElementById('cartItems');
const cartEmpty = document.getElementById('cartEmpty');
const cartFooter = document.getElementById('cartFooter');
const cartCount = document.getElementById('cartCount');
const cartSubtotal = document.getElementById('cartSubtotal');
const cartTotal = document.getElementById('cartTotal');
const wishlistCount = document.getElementById('wishlistCount');
const quickViewModal = document.getElementById('quickViewModal');
const closeQuickViewModal = document.getElementById('closeQuickViewModal');
const quickViewContent = document.getElementById('quickViewContent');
const toastContainer = document.getElementById('toastContainer');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const categoriesNav = document.getElementById('categoriesNav');
const startShoppingBtn = document.getElementById('startShoppingBtn');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const newsletterForm = document.getElementById('newsletterForm');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    setupEventListeners();
    setupCountdown();
    loadCartFromStorage();
    loadWishlistFromStorage();
});

// Load products
function loadProducts(filter = 'all', searchTerm = '') {
    productsGrid.innerHTML = '';
    
    let filteredProducts = products;
    
    // Filter by category or filter type
    if (filter !== 'all') {
        filteredProducts = products.filter(product => 
            product.filter === filter || product.category === filter
        );
    }
    
    // Filter by search term
    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filteredProducts = filteredProducts.filter(product =>
            product.title.toLowerCase().includes(term) ||
            product.category.toLowerCase().includes(term) ||
            product.description.toLowerCase().includes(term)
        );
    }
    
    if (filteredProducts.length === 0) {
        productsGrid.innerHTML = `
            <div class="empty-products" style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-search" style="font-size: 3rem; color: #e5e7eb; margin-bottom: 20px;"></i>
                <p style="color: #6b7280; font-size: 1.1rem;">No products found matching your criteria.</p>
            </div>
        `;
        return;
    }
    
    filteredProducts.forEach((product, index) => {
        const productCard = createProductCard(product);
        productCard.style.animationDelay = `${index * 0.1}s`;
        productsGrid.appendChild(productCard);
    });
}

// Create product card
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.style.animation = 'fadeInUp 0.5s ease forwards';
    
    const isInWishlist = wishlist.includes(product.id);
    
    card.innerHTML = `
        <div class="product-badges">
            ${product.badge ? `<span class="product-badge badge-${product.badge}">${product.badge === 'sale' ? 'Sale' : product.badge === 'new' ? 'New' : 'Hot'}</span>` : ''}
        </div>
        <div class="product-image">
            <img src="${product.image}" alt="${product.title}">
            <div class="product-actions">
                <button class="action-btn wishlist-btn ${isInWishlist ? 'active' : ''}" data-id="${product.id}" title="${isInWishlist ? 'Remove from Wishlist' : 'Add to Wishlist'}">
                    <i class="fas fa-heart"></i>
                </button>
                <button class="action-btn quickview-btn" data-id="${product.id}" title="Quick View">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn add-to-cart-btn" data-id="${product.id}" title="Add to Cart">
                    <i class="fas fa-shopping-cart"></i>
                </button>
            </div>
        </div>
        <div class="product-info">
            <span class="product-category">${product.category}</span>
            <h3 class="product-title">${product.title}</h3>
            <div class="product-rating">
                ${generateStars(product.rating)}
                <span>(${product.reviews})</span>
            </div>
            <div class="product-price">
                <span class="current-price">$${product.price.toFixed(2)}</span>
                ${product.originalPrice ? `<span class="original-price">$${product.originalPrice.toFixed(2)}</span>` : ''}
            </div>
        </div>
    `;
    
    // Add event listeners
    const wishlistBtn = card.querySelector('.wishlist-btn');
    const quickviewBtn = card.querySelector('.quickview-btn');
    const addToCartBtn = card.querySelector('.add-to-cart-btn');
    
    wishlistBtn.addEventListener('click', () => toggleWishlist(product.id));
    quickviewBtn.addEventListener('click', () => openQuickView(product.id));
    addToCartBtn.addEventListener('click', () => addToCart(product.id));
    
    return card;
}

// Generate star rating HTML
function generateStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    for (let i = fullStars + (hasHalfStar ? 1 : 0); i < 5; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    
    return stars;
}

// Setup event listeners
function setupEventListeners() {
    // Cart modal
    cartBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openCartModal();
    });
    
    closeCartModal.addEventListener('click', closeCart);
    
    cartModal.addEventListener('click', (e) => {
        if (e.target === cartModal) {
            closeCart();
        }
    });
    
    // Quick view modal
    closeQuickViewModal.addEventListener('click', closeQuickView);
    
    quickViewModal.addEventListener('click', (e) => {
        if (e.target === quickViewModal) {
            closeQuickView();
        }
    });
    
    // Start shopping button
    if (startShoppingBtn) {
        startShoppingBtn.addEventListener('click', (e) => {
            e.preventDefault();
            closeCart();
        });
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            loadProducts(this.dataset.filter);
        });
    });
    
    // Category navigation
    document.querySelectorAll('.category-list a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelectorAll('.category-list a').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            loadProducts(this.dataset.category);
        });
    });
    
    // Category cards
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.dataset.category;
            loadProducts(category);
            document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
            
            // Update active state in nav
            document.querySelectorAll('.category-list a').forEach(link => {
                link.classList.remove('active');
                if (link.dataset.category === category) {
                    link.classList.add('active');
                }
            });
        });
    });
    
    // Search
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Mobile menu
    mobileMenuBtn.addEventListener('click', () => {
        categoriesNav.classList.toggle('active');
    });
    
    // Load more button
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            showToast('All Products Loaded', 'You\'ve seen all our products!', 'info');
        });
    }
    
    // Newsletter form
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = newsletterForm.querySelector('input').value;
            if (email) {
                showToast('Subscribed!', 'Thanks for subscribing to our newsletter!', 'success');
                newsletterForm.reset();
            }
        });
    }
    
    // Checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
            if (cart.length > 0) {
                showToast('Checkout', 'Redirecting to checkout...', 'info');
                // In a real app, this would redirect to checkout
            }
        });
    }
    
    // Escape key to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeCart();
            closeQuickView();
        }
    });
}

// Search functionality
function performSearch() {
    const searchTerm = searchInput.value.trim();
    loadProducts('all', searchTerm);
    
    if (searchTerm) {
        document.getElementById('products').scrollIntoView({ behavior: 'smooth' });
    }
}

// Cart functions
function addToCart(productId, quantity = 1) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: product.id,
            title: product.title,
            price: product.price,
            image: product.image,
            quantity: quantity
        });
    }
    
    updateCartUI();
    saveCartToStorage();
    showToast('Added to Cart', `${product.title} has been added to your cart`, 'success');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCartUI();
    saveCartToStorage();
    showToast('Removed from Cart', 'Item has been removed from your cart', 'info');
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (!item) return;
    
    item.quantity += change;
    
    if (item.quantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    updateCartUI();
    saveCartToStorage();
}

function updateCartUI() {
    // Update cart count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
    
    // Update cart modal content
    if (cart.length === 0) {
        cartItems.classList.add('hidden');
        cartEmpty.classList.remove('hidden');
        cartFooter.classList.add('hidden');
    } else {
        cartItems.classList.remove('hidden');
        cartEmpty.classList.add('hidden');
        cartFooter.classList.remove('hidden');
        
        cartItems.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-image">
                    <img src="${item.image}" alt="${item.title}">
                </div>
                <div class="cart-item-details">
                    <h4 class="cart-item-title">${item.title}</h4>
                    <span class="cart-item-price">$${item.price.toFixed(2)}</span>
                    <div class="cart-item-quantity">
                        <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
                <button class="cart-item-remove" onclick="removeFromCart(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
        
        // Update totals
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        cartSubtotal.textContent = `$${subtotal.toFixed(2)}`;
        cartTotal.textContent = `$${subtotal.toFixed(2)}`;
    }
}

function openCartModal() {
    cartModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeCart() {
    cartModal.classList.remove('active');
    document.body.style.overflow = '';
}

// Wishlist functions
function toggleWishlist(productId) {
    const index = wishlist.indexOf(productId);
    
    if (index === -1) {
        wishlist.push(productId);
        showToast('Added to Wishlist', 'Item has been added to your wishlist', 'success');
    } else {
        wishlist.splice(index, 1);
        showToast('Removed from Wishlist', 'Item has been removed from your wishlist', 'info');
    }
    
    updateWishlistUI();
    saveWishlistToStorage();
    loadProducts(getCurrentFilter());
}

function updateWishlistUI() {
    wishlistCount.textContent = wishlist.length;
}

function getCurrentFilter() {
    const activeFilter = document.querySelector('.filter-btn.active');
    return activeFilter ? activeFilter.dataset.filter : 'all';
}

// Quick View functions
function openQuickView(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    quickViewContent.innerHTML = `
        <div class="quickview-image">
            <img src="${product.image}" alt="${product.title}">
        </div>
        <div class="quickview-details">
            <span class="quickview-category">${product.category}</span>
            <h2 class="quickview-title">${product.title}</h2>
            <div class="quickview-rating">
                ${generateStars(product.rating)}
                <span>(${product.reviews} reviews)</span>
            </div>
            <div class="quickview-price">
                <span class="current-price">$${product.price.toFixed(2)}</span>
                ${product.originalPrice ? `<span class="original-price">$${product.originalPrice.toFixed(2)}</span>` : ''}
            </div>
            <p class="quickview-description">${product.description}</p>
            <div class="quickview-actions">
                <div class="quickview-qty">
                    <button class="qty-btn" id="qvQtyMinus"><i class="fas fa-minus"></i></button>
                    <span class="qty-value" id="qvQtyValue">1</span>
                    <button class="qty-btn" id="qvQtyPlus"><i class="fas fa-plus"></i></button>
                </div>
                <button class="btn btn-primary" id="qvAddToCart">
                    <i class="fas fa-shopping-cart"></i> Add to Cart
                </button>
            </div>
        </div>
    `;
    
    // Add event listeners for quick view
    let quantity = 1;
    const qtyValue = document.getElementById('qvQtyValue');
    
    document.getElementById('qvQtyMinus').addEventListener('click', () => {
        if (quantity > 1) {
            quantity--;
            qtyValue.textContent = quantity;
        }
    });
    
    document.getElementById('qvQtyPlus').addEventListener('click', () => {
        quantity++;
        qtyValue.textContent = quantity;
    });
    
    document.getElementById('qvAddToCart').addEventListener('click', () => {
        addToCart(product.id, quantity);
        closeQuickView();
    });
    
    quickViewModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeQuickView() {
    quickViewModal.classList.remove('active');
    document.body.style.overflow = '';
}

// Toast notifications
function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon;
    switch (type) {
        case 'success':
            icon = 'fa-check';
            break;
        case 'error':
            icon = 'fa-exclamation-circle';
            break;
        default:
            icon = 'fa-info-circle';
    }
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${icon}"></i>
        </div>
        <div class="toast-content">
            <h4>${title}</h4>
            <p>${message}</p>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove toast after delay
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Countdown timer
function setupCountdown() {
    // Set end date to 7 days from now
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 7);
    
    function updateCountdown() {
        const now = new Date();
        const diff = endDate - now;
        
        if (diff <= 0) {
            // Reset countdown when it reaches zero
            endDate.setDate(endDate.getDate() + 7);
            return;
        }
        
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        document.getElementById('days').textContent = String(days).padStart(2, '0');
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
        document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// Local Storage functions
function saveCartToStorage() {
    localStorage.setItem('shopstyle_cart', JSON.stringify(cart));
}

function loadCartFromStorage() {
    const savedCart = localStorage.getItem('shopstyle_cart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        updateCartUI();
    }
}

function saveWishlistToStorage() {
    localStorage.setItem('shopstyle_wishlist', JSON.stringify(wishlist));
}

function loadWishlistFromStorage() {
    const savedWishlist = localStorage.getItem('shopstyle_wishlist');
    if (savedWishlist) {
        wishlist = JSON.parse(savedWishlist);
        updateWishlistUI();
    }
}

// Make functions available globally for onclick handlers
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
