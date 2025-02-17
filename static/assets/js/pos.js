
var selectedColor = "";
var selectedSize = "";
var lastSelectedProduct = null; // Track last selected product ID
let cart = loadCart();

// Function to handle color selection
function addColor(element) {
    selectedColor = element.getAttribute("data-color");
}

// Function to handle size selection
function addSize(selectElement) {
    selectedSize = selectElement.value;
}

// Add item to cart
function addToCart(id, name, price, sku) {

    if (lastSelectedProduct === null) {
        lastSelectedProduct = id;
    } 

    if (lastSelectedProduct !== id){
        selectedColor = "";
        selectedSize = "";
        var selectSizeElement = document.getElementById("sizeSelect");
        if (selectSizeElement) {
            selectSizeElement.value = ""; // Reset value
            selectSizeElement.selectedIndex = 0; // Reset selection index
        }
        console.log('color reseted')
    }

    if (selectedColor === "" || selectedSize === "") {
        alert("Please select a color and size before adding to cart.");
        return;
    }

    const existingItem = cart.find(item => item.id === id && item.color === selectedColor && item.size === selectedSize);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, color: selectedColor, size: selectedSize, quantity: 1, sku });
    }

    // Save updated cart to localStorage
    saveCart();

    // Update the UI
    updateCart();

}


// Load cart from localStorage if available
function loadCart() {
    const storedCart = localStorage.getItem('cart');
    return storedCart ? JSON.parse(storedCart) : [];
}

// Save cart to localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCart() {
    let cartHtml = '';
    let totalPrice = 0;

    cart.forEach((item, index) => {
    totalPrice += item.price * item.quantity;
    cartHtml += `
        <div class="cart-item d-flex justify-content-between align-items-center mb-1 p-2 rounded-lg shadow-sm bg-white">
            <!-- Item Details -->
            <div class="item-details w-3/12 pe-3">
                <div><strong class="fs-7 text-dark">${item.name}</strong></div>
                <div class="text-muted">C: <span class="text-primary">${item.color}</span></div>
                <div class="text-muted">S: <span class="text-primary">${item.size}</span> SKU: <span class="text-primary">${item.sku}</span></div>
            </div>

            <!-- Price Column -->
            <div class="item-price text-center w-2/12">
                <div class="fw-bold fs-7 text-dark">$ ${item.price.toFixed(2)}</div>
            </div>

            <!-- Multiplication Symbol -->
            <div class="item-multiply text-center w-1/12">
                <div class="fs-7 text-dark">×</div>
            </div>

            <!-- Item Quantity -->
            <div class="item-quantity d-flex align-items-center justify-content-center w-3/12">
                <input type="number" value="${item.quantity}" min="1" class="custom-quantity-input mx-2 text-center h-8 text-sm border border-gray-300 rounded-md p-1 bg-gray-50 focus:ring-2 focus:ring-blue-500 transition-all" onchange="updateQuantity(${index}, 0, this.value)" style="width: 3rem;" />
            </div>

            <!-- Subtotal Column -->
            <div class="item-subtotal text-center w-2/12">
                <div class="fw-bold fs-7 text-dark">$ ${(item.price * item.quantity).toFixed(2)}</div>
            </div>

            <!-- Delete Button Column -->
            <div class="item-delete text-end w-1/12 ps-3">
                <button class="btn btn-xs btn-danger ms-2 mt-1" onclick="removeItem(${index})">
                    <i class="fa fa-trash"></i> <!-- Font Awesome Trash Icon -->
                </button>
            </div>
        </div>
    `;


    });

    

    document.getElementById('cartItems').innerHTML = cartHtml;
    document.getElementById('totalPrice').innerText = totalPrice.toFixed(2);
    document.getElementById('totalAmount').value = totalPrice.toFixed(2);
}

// Update quantity (minus, plus, or manual input change)
function updateQuantity(index, change, newQuantity) {
    if (change !== 0) {
        cart[index].quantity += change;
    } else if (newQuantity && newQuantity > 0) {
        cart[index].quantity = parseInt(newQuantity);
    }

    if (cart[index].quantity < 1) {
        cart[index].quantity = 1; // Prevent going below 1
    }

    saveCart(); // Save the cart after any update
    updateCart();
}

// Remove item from cart
function removeItem(index) {
    cart.splice(index, 1); // Remove item at the given index
    saveCart(); // Save the cart after removal
    updateCart();
}

document.getElementById('applyPromoCode').addEventListener('click', function() {
    const promoCode = document.getElementById('promoCode').value;
    const promoMessage = document.getElementById('promoMessage');
    
    if (promoCode === 'DISCOUNT10') {
        promoMessage.style.display = 'block';
        promoMessage.innerText = 'Promo code applied successfully! You get 10% off.';
    } else {
        promoMessage.style.display = 'none';
        alert('Invalid promo code.');
    }
});


// Initial cart update
updateCart();
