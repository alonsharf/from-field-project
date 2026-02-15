"""Browse Products - Customer product catalog and search interface."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_products():
    """Get products from API."""
    response = make_api_request("GET", "/api/products/")
    return response.get('products', []) if response else []

def get_category_emoji(product):
    """Get consistent category emoji for products (CENTRALIZED)."""
    # Get category, handling both string and dict formats
    if isinstance(product.get('category'), dict):
        category = product.get('category', {}).get('name', 'Fresh Produce').lower()
    else:
        category = product.get('category', 'Fresh Produce').lower()

    # Category-specific emoji placeholders (CENTRALIZED MAPPING)
    placeholder_map = {
        'vegetables': '🥬',
        'fruits': '🍎',
        'herbs': '🌿',
        'grains': '🌾',
        'specialty items': '🥕',
        'dairy': '🥛',
        'meat': '🥩',
        'berries': '🫐',  # Specific mapping for berries
        'citrus': '🍊',   # Specific mapping for citrus
        'root vegetables': '🥕',
        'leafy greens': '🥬'
    }

    # Find matching category or use default
    emoji = '🥕'  # Default
    for cat_key, cat_emoji in placeholder_map.items():
        if cat_key in category:
            emoji = cat_emoji
            break

    return emoji

def add_to_cart_api(product_id, quantity, session_id):
    """Add product to cart via API."""
    cart_data = {
        'product_id': str(product_id),  # Ensure string UUID format
        'quantity': float(quantity),     # Ensure numeric (Decimal-compatible)
        'session_id': str(session_id)
    }
    return make_api_request("POST", "/api/cart/add-item", cart_data)

def get_or_create_session_id():
    """Get or create customer session ID."""
    if 'customer_session_id' not in st.session_state:
        import uuid
        st.session_state.customer_session_id = str(uuid.uuid4())
    return st.session_state.customer_session_id

def display_product_image(product, use_column_width=True):
    """Display product image with bulletproof fallback handling."""
    image_url = product.get("image_url", "")

    # ALWAYS show placeholder - this is the bulletproof approach
    # Only show real images for verified good URLs

    # Get category emoji using centralized function
    emoji = get_category_emoji(product)

    # Create beautiful placeholder
    placeholder_html = f"""
    <div style="
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border: 2px dashed #cbd5e0;
        border-radius: 12px;
        padding: 30px 15px;
        text-align: center;
        margin: 8px 0;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 36px; margin-bottom: 6px;">{emoji}</div>
        <div style="color: #4a5568; font-weight: 600; margin-bottom: 2px; font-size: 14px;">{product.get('name', 'Product')}</div>
        <div style="color: #718096; font-size: 11px;">Image coming soon</div>
    </div>
    """

    st.markdown(placeholder_html, unsafe_allow_html=True)
    return True

def show_browse_products():
    """Display product browsing interface for customers."""
    st.title("🔍 Browse Products")
    st.markdown("### Discover fresh, locally grown produce")
    
    # ============================================================
    # PROMINENT SEARCH & FILTER SECTION (Top of Page)
    # ============================================================
    
    # Large Search Bar
    search_term = st.text_input(
        "🔍 Search",
        placeholder="Search for tomatoes, herbs, organic produce...",
        label_visibility="collapsed",
        key="main_search"
    )
    
    st.markdown("")  # Spacing
    
    # Category Quick-Select Buttons
    st.markdown("**🛒 Shop by Category**")
    
    category_options = [
        ("🛒", "All", "All Categories"),
        ("🥬", "Veggies", "Vegetables"),
        ("🍎", "Fruits", "Fruits"),
        ("🌿", "Herbs", "Herbs"),
        ("🌾", "Grains", "Grains"),
        ("🥛", "Dairy", "Dairy"),
        ("⭐", "Special", "Specialty Items"),
    ]
    
    # Initialize category in session state
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "All Categories"
    
    # Create category button row
    cat_cols = st.columns(len(category_options))
    for i, (emoji, label, value) in enumerate(category_options):
        with cat_cols[i]:
            is_selected = st.session_state.selected_category == value
            btn_type = "primary" if is_selected else "secondary"
            if st.button(f"{emoji} {label}", key=f"cat_{value}", use_container_width=True, type=btn_type):
                st.session_state.selected_category = value
                st.rerun()
    
    category_filter = st.session_state.selected_category
    
    st.markdown("---")
    
    # Refine Results Row
    st.markdown("**⚙️ Refine Results**")
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 2, 2, 1, 1])
    
    with filter_col1:
        price_options = ["Any Price", "Under ₪5", "₪5-10", "₪10-15", "₪15+"]
        price_selection = st.selectbox("💰 Price", price_options, label_visibility="collapsed")
        price_map = {"Any Price": 100.0, "Under ₪5": 5.0, "₪5-10": 10.0, "₪10-15": 15.0, "₪15+": 100.0}
        price_range = price_map.get(price_selection, 100.0)
    
    with filter_col2:
        availability = st.selectbox("📦 Stock", ["All Products", "In Stock Only", "Coming Soon"], label_visibility="collapsed")
    
    with filter_col3:
        sort_by = st.selectbox("↕️ Sort", ["Name A-Z", "Name Z-A", "Price Low-High", "Price High-Low"], label_visibility="collapsed")
    
    with filter_col4:
        organic_only = st.checkbox("🌱 Organic", value=False)
    
    with filter_col5:
        view_mode = st.radio("View", ["Grid", "List"], horizontal=True, label_visibility="collapsed")
    
    # Active filters display
    active_filters = []
    if search_term:
        active_filters.append(f"🔍 '{search_term}'")
    if category_filter != "All Categories":
        active_filters.append(f"📁 {category_filter}")
    if price_selection != "Any Price":
        active_filters.append(f"💰 {price_selection}")
    if availability != "All Products":
        active_filters.append(f"📦 {availability}")
    if organic_only:
        active_filters.append("🌱 Organic")
    
    if active_filters:
        filter_col_a, filter_col_b = st.columns([4, 1])
        with filter_col_a:
            st.caption(f"**Active filters:** {' · '.join(active_filters)}")
        with filter_col_b:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.selected_category = "All Categories"
                st.rerun()
    
    st.markdown("---")
    st.markdown("**Showing fresh produce from our farm**")

    try:
        # Get products from API
        all_products = get_products()

        # Apply filters
        filtered_products = []

        if all_products:
            for product in all_products:
                # Convert API response to expected format
                price_per_unit = float(product.get('price_per_unit', 0))
                stock_quantity = float(product.get('stock_quantity', 0))

                # Search filter
                if search_term:
                    search_lower = search_term.lower()
                    name_match = search_lower in product.get('name', '').lower()
                    desc_match = search_lower in product.get('description', '').lower()
                    if not (name_match or desc_match):
                        continue

                # Category filter
                if category_filter != "All Categories":
                    if product.get('category', '') != category_filter:
                        continue

                # Availability filter
                in_stock = stock_quantity > 0
                if availability == "In Stock Only" and not in_stock:
                    continue
                elif availability == "Coming Soon" and in_stock:
                    continue

                # Organic filter
                if organic_only and not product.get('is_organic', False):
                    continue

                # Price filter
                if price_per_unit > price_range:
                    continue

                # Add converted product to filtered results
                filtered_product = {
                    'id': product['id'],
                    'name': product.get('name', 'Unknown Product'),
                    'price': price_per_unit,
                    'unit': product.get('unit_label', 'unit'),
                    'stock': stock_quantity,
                    'in_stock': in_stock,
                    'is_organic': product.get('is_organic', False),
                    'category': product.get('category', 'Fresh Produce'),
                    'description': product.get('description', 'Fresh local produce'),
                    'farmer_name': 'Green Valley Farm',  # Default farmer name
                    'image_url': product.get('image_url', "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&q=80")
                }
                filtered_products.append(filtered_product)

        # Display products
        st.markdown(f"**{len(filtered_products)} products found**")
        st.markdown("---")

        if not filtered_products:
            if not all_products:
                st.info("🌱 No products available yet. Check back soon for fresh produce!")
            else:
                st.info("🔍 No products match your current filters. Try adjusting your search criteria.")
        else:
            # Sort products
            if sort_by == "Name A-Z":
                filtered_products.sort(key=lambda x: x['name'])
            elif sort_by == "Name Z-A":
                filtered_products.sort(key=lambda x: x['name'], reverse=True)
            elif sort_by == "Price Low-High":
                filtered_products.sort(key=lambda x: x['price'])
            elif sort_by == "Price High-Low":
                filtered_products.sort(key=lambda x: x['price'], reverse=True)
            # "Newest First" would need created_at field

            if view_mode == "Grid":
                show_products_grid(filtered_products)
            else:
                show_products_list(filtered_products)

    except Exception as e:
        st.error("Unable to load products from API.")
        st.caption(f"Error: {str(e)}")
        st.info("Please check your connection and try again.")

def show_products_grid(products):
    """Display products in grid view."""
    # Display products in rows of 3
    for i in range(0, len(products), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(products):
                product = products[i + j]
                with col:
                    show_product_card(product)

def show_products_list(products):
    """Display products in list view."""
    for product in products:
        show_product_list_item(product)

def show_product_card(product):
    """Display individual product card."""
    with st.container():
        # Product image with fallback
        display_product_image(product, use_column_width=True)

        # Product name and price
        st.markdown(f"**{product['name']}**")
        st.markdown(f"**₪{product['price']:.2f}** /{product['unit']}")

        # Organic badge
        if product.get('is_organic', False):
            st.success("🌱 Organic")

        # Stock status
        if product['in_stock']:
            stock_qty = product.get('stock', 0)
            st.markdown(f"✅ {stock_qty:.0f} {product['unit']} available")
        else:
            st.warning(f"⏳ Out of stock")

        # Farmer info
        farmer_name = product.get('farmer_name', 'Local Farm')
        st.caption(f"🌾 From {farmer_name}")

        # Description
        description = product.get('description', 'Fresh local produce')
        st.markdown(f"_{description}_")

        # Add to cart button
        if product['in_stock']:
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=10,
                    value=1,
                    key=f"qty_grid_{product['id']}"
                )
            with col2:
                # Add CSS margin to align button with quantity input
                st.markdown('<div style="margin-top: 24px;">', unsafe_allow_html=True)
                if st.button(f"🛒 Add", key=f"add_grid_{product['id']}", use_container_width=True, type="primary"):
                    add_to_cart(product, quantity)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Add CSS margin to align out of stock button
            st.markdown('<div style="margin-top: 24px;">', unsafe_allow_html=True)
            st.button("❌ Out of Stock", disabled=True, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Product details button
        if st.button("👁️ Details", key=f"details_grid_{product['id']}", use_container_width=True):
            show_product_details(product)

        st.divider()

def show_product_list_item(product):
    """Display individual product in list view."""
    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            display_product_image(product, use_column_width=True)

        with col2:
            # Product header
            col2a, col2b = st.columns([2, 1])

            with col2a:
                st.markdown(f"### {product['name']}")
                if product.get('is_organic', False):
                    st.success("🌱 Organic")

            with col2b:
                st.markdown(f"## **₪{product['price']:.2f}**")
                st.markdown(f"_{product['unit']}_")

            # Description
            description = product.get('description', 'Fresh local produce')
            st.markdown(description)

            # Stock and harvest info
            col2c, col2d = st.columns(2)

            with col2c:
                if product['in_stock']:
                    stock_qty = product.get('stock', 0)
                    st.markdown(f"✅ **{stock_qty:.1f} {product['unit']} available**")
                else:
                    st.warning(f"⏳ **Out of stock**")

            with col2d:
                farmer_name = product.get('farmer_name', 'Local Farm')
                st.caption(f"🌾 From {farmer_name}")

            # Actions
            col2e, col2f, col2g = st.columns(3)

            with col2e:
                if product['in_stock']:
                    quantity = st.number_input(
                        "Qty",
                        min_value=1,
                        max_value=10,
                        value=1,
                        key=f"qty_list_{product['id']}"
                    )

            with col2f:
                if product['in_stock']:
                    # Use CSS to push button down to align with input field
                    st.markdown(
                        f"""
                        <div style="margin-top: 24px;">
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"🛒 Add to Cart", key=f"add_list_{product['id']}", type="primary", use_container_width=True):
                        add_to_cart(product, quantity)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"""
                        <div style="margin-top: 24px;">
                        """,
                        unsafe_allow_html=True
                    )
                    st.button("❌ Out of Stock", disabled=True, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with col2g:
                if st.button("👁️ View Details", key=f"details_list_{product['id']}"):
                    show_product_details(product)

        st.divider()

def add_to_cart(product, quantity):
    """Add product to cart using both API and session state."""
    # Initialize cart if it doesn't exist
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    # Get session ID for API call
    session_id = get_or_create_session_id()
    
    # Call API to persist cart (non-blocking - continue even if fails)
    api_response = add_to_cart_api(product['id'], quantity, session_id)
    
    if not api_response:
        # API failed, but continue with session state for UI
        st.warning("⚠️ Cart sync issue - your cart will be saved locally.")

    # Check if product already in cart (session state for UI responsiveness)
    for item in st.session_state.cart:
        if item['id'] == product['id']:
            item['quantity'] += quantity
            st.success(f"Added {quantity} more {product['name']} to your cart!")
            return

    # Add new item to cart
    st.session_state.cart.append({
        'id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'unit': product['unit'],
        'quantity': quantity,
        'image_url': product.get('image_url', '')
    })

    st.success(f"Added {quantity} {product['name']} to your cart!")

def show_product_details(product):
    """Show detailed product information."""
    with st.expander(f"📋 {product['name']} - Details", expanded=False):
        col1, col2 = st.columns([1, 2])

        with col1:
            display_product_image(product, use_column_width=True)

        with col2:
            st.markdown(f"**Price:** ₪{product['price']:.2f} /{product['unit']}")
            category = product.get('category', 'Fresh Produce')
            st.markdown(f"**Category:** {category}")

            if product.get('is_organic', False):
                st.success("🌱 **Certified Organic**")

            # Available from/until dates
            available_from = product.get('available_from')
            available_until = product.get('available_until')
            if available_from or available_until:
                availability_text = "Available "
                if available_from:
                    availability_text += f"from {available_from}"
                if available_until:
                    availability_text += f" until {available_until}"
                st.markdown(f"**Seasonal Availability:** {availability_text}")

            farmer_name = product.get('farmer_name', 'Local Farm')
            st.markdown(f"**From:** {farmer_name}")

            if product['in_stock']:
                stock_qty = product.get('stock', 0)
                st.success(f"✅ **In Stock:** {stock_qty:.1f} {product['unit']} available")
            else:
                st.warning(f"⏳ **Status:** Out of stock")

        st.markdown("---")
        st.markdown("**Description:**")
        description = product.get('description', 'Fresh local produce')
        st.markdown(description)

        # Nutritional info placeholder
        st.markdown("**Nutritional Benefits:**")
        st.info("Rich in vitamins and minerals. Locally grown for maximum freshness and flavor.")

        # Storage tips
        st.markdown("**Storage Tips:**")
        st.info("Store in refrigerator. Best consumed within 3-5 days of delivery for optimal freshness.")