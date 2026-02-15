"""Storefront Home - Customer homepage with featured products and farm information."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def display_product_image(product, use_column_width=True):
    """Display product image with enhanced agricultural styling."""
    # Get category for appropriate emoji
    category = product.get('category', 'Fresh Produce').lower()

    # Category-specific emoji placeholders
    placeholder_map = {
        'vegetables': '🥬',
        'fruits': '🍎',
        'herbs': '🌿',
        'grains': '🌾',
        'specialty items': '🥕',
        'dairy': '🥛',
        'meat': '🥩'
    }

    # Find matching category or use default
    emoji = '🥕'  # Default
    for cat_key, cat_emoji in placeholder_map.items():
        if cat_key in category:
            emoji = cat_emoji
            break

    # Create enhanced product image placeholder using CSS classes
    placeholder_html = f"""
    <div class="product-image-placeholder">
        <div style="font-size: 36px; margin-bottom: 6px;">{emoji}</div>
        <div style="color: #4a5568; font-weight: 600; margin-bottom: 2px; font-size: 14px;">{product.get('name', 'Product')}</div>
        <div style="color: #718096; font-size: 11px;">Fresh from our farm</div>
    </div>
    """

    st.markdown(placeholder_html, unsafe_allow_html=True)
    return True

def get_customer_products(limit=4):
    """Get products from API for customer display."""
    try:
        # Get products from API
        response = make_api_request("GET", "/api/products/")
        all_products = response.get('products', []) if response else []

        # Convert API products to expected format
        customer_products = []
        for product in all_products[:limit]:  # Limit results
            customer_product = {
                'id': product['id'],
                'name': product.get('name', 'Unknown Product'),
                'price': float(product.get('price_per_unit', 0)),
                'unit': product.get('unit_label', 'unit'),
                'stock_quantity': float(product.get('stock_quantity', 0)),
                'in_stock': float(product.get('stock_quantity', 0)) > 0,
                'description': product.get('description', 'Fresh local produce'),
                'image_url': product.get('image_url', "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&q=80")
            }
            customer_products.append(customer_product)

        return customer_products
    except Exception as e:
        return []

def get_or_create_session_id():
    """Get or create customer session ID."""
    if 'customer_session_id' not in st.session_state:
        import uuid
        st.session_state.customer_session_id = str(uuid.uuid4())
    return st.session_state.customer_session_id

def show_storefront_home():
    """Display customer storefront homepage."""
    # Enhanced agricultural header
    header_html = """
    <div class="farm-hero">
        <h1 style="color: white; margin-bottom: 1rem; font-size: 2.5rem;">🏠 From Field to You</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-bottom: 2rem;">Fresh, locally grown produce delivered to your door</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Hero section
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 🌾 Welcome to Our Farm Store")
        st.markdown("""
        **Fresh • Local • Sustainable**

        Browse our selection of farm-fresh produce, grown with care using sustainable farming practices.
        From crisp vegetables to sweet fruits, we bring the best of our harvest directly to your table.
        """)

        # Quick action buttons
        col1a, col1b, col1c = st.columns(3)

        with col1a:
            if st.button("🛒 Start Shopping", type="primary", use_container_width=True):
                st.session_state.current_page = "Browse Products"
                st.rerun()

        with col1b:
            if st.button("📦 My Orders", use_container_width=True):
                st.session_state.current_page = "My Orders & Shipments"
                st.rerun()

        with col1c:
            if st.button("🛒 View Cart", use_container_width=True):
                st.session_state.current_page = "My Cart & Checkout"
                st.rerun()

    with col2:
        # Farm image placeholder
        st.image(
            "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
            caption="Our farm fields",
            use_column_width=True
        )

    st.divider()

    # Featured products section
    st.subheader("⭐ Featured Products")

    try:
        # Get featured products from database (limit to 4)
        featured_products = get_customer_products(limit=4)

        if not featured_products:
            st.info("🌱 No featured products available yet. Check back soon for fresh produce!")
        else:
            # Display featured products in a grid
            cols = st.columns(min(4, len(featured_products)))

            for i, product in enumerate(featured_products):
                with cols[i]:
                    display_product_image(product, use_column_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"**₪{product['price']:.2f}** {product['unit']}")
                    st.markdown(f"_{product['description']}_")

                    if product["in_stock"]:
                        if st.button(f"🛒 Add to Cart", key=f"add_{i}", use_container_width=True, type="primary"):
                            add_to_cart(product)
                    else:
                        st.button("❌ Out of Stock", key=f"out_{i}", disabled=True, use_container_width=True)

    except Exception as e:
        st.error("Unable to load featured products.")
        st.caption(f"Error: {str(e)}")

        # Fallback message
        st.info("🌱 Featured products will appear here once connected to the database.")

    st.divider()

    # Farm information section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏡 About Our Farm")
        st.markdown("""
        **Green Valley Farm** has been growing fresh, sustainable produce for over 15 years.
        Located in the heart of Illinois, we practice organic farming methods and prioritize
        environmental stewardship.

        **Our Commitment:**
        • 🌱 100% Organic & Sustainable
        • 🚫 No Pesticides or Chemicals
        • 🌍 Environmentally Responsible
        • 📦 Fresh Harvest to Your Door
        """)

        if st.button("📖 Learn More About Us"):
            st.info("More farm information coming soon!")

    with col2:
        st.subheader("🚚 Delivery Information")
        st.markdown("""
        **Delivery Areas:**
        • Springfield, IL and surrounding areas
        • Chicago metro area
        • Central Illinois communities

        **Delivery Schedule:**
        • Tuesday & Friday deliveries
        • Order by Sunday for Tuesday delivery
        • Order by Wednesday for Friday delivery

        **Delivery Fee:** ₪5.99 (Free on orders over ₪50)
        """)

        if st.button("📍 Check Delivery to My Area"):
            show_delivery_checker()

    st.divider()

    # Section divider for testimonials
    divider_html = """
    <div style="
        display: flex;
        align-items: center;
        margin: 2rem 0;
        text-align: center;
    ">
        <div style="flex: 1; height: 3px; background: linear-gradient(90deg, transparent, var(--accent-green), transparent);"></div>
        <div style="
            background: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border: 2px solid var(--accent-green);
            margin: 0 1rem;
        ">
            <span style="margin-right: 0.5rem;">💬</span>
            <span style="color: var(--primary-green); font-weight: 600;">What Our Customers Say</span>
        </div>
        <div style="flex: 1; height: 3px; background: linear-gradient(90deg, transparent, var(--accent-green), transparent);"></div>
    </div>
    """
    st.markdown(divider_html, unsafe_allow_html=True)

    testimonials = [
        {
            "name": "Sarah M.",
            "text": "The freshest vegetables I've ever had! Delivery is always on time and the quality is amazing.",
            "rating": "⭐⭐⭐⭐⭐"
        },
        {
            "name": "Mike R.",
            "text": "Love supporting local farming. The organic tomatoes are incredible - you can taste the difference!",
            "rating": "⭐⭐⭐⭐⭐"
        },
        {
            "name": "Jennifer L.",
            "text": "Convenient ordering and great customer service. My kids love the sweet corn!",
            "rating": "⭐⭐⭐⭐⭐"
        }
    ]

    cols = st.columns(3)

    for i, testimonial in enumerate(testimonials):
        with cols[i]:
            testimonial_html = f"""
            <div class="testimonial-card">
                <div style="margin-bottom: 1rem; font-size: 1.2rem;">{testimonial['rating']}</div>
                <p style="font-style: italic; color: var(--dark-gray); margin-bottom: 1rem;">"{testimonial['text']}"</p>
                <p style="font-weight: 600; color: var(--primary-green); margin: 0;">- {testimonial['name']}</p>
            </div>
            """
            st.markdown(testimonial_html, unsafe_allow_html=True)

    st.divider()

    # Contact Information
    st.subheader("📞 Contact Us")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("Have questions about our products or need help with your order?")
        st.markdown("**Phone:** (555) 123-4567")
        st.markdown("**Email:** info@fromfieldtoyou.com")
        st.markdown("**Hours:** Mon-Sat 8:00 AM - 6:00 PM")

    with col2:
        st.markdown("**Follow Us:**")
        st.markdown("📘 Facebook: @GreenValleyFarm")
        st.markdown("📷 Instagram: @greenvalleyfresh")
        st.markdown("🐦 Twitter: @gvfarm")

def add_to_cart(product):
    """Add product to cart using session state."""
    try:
        # Initialize cart if it doesn't exist
        if 'cart' not in st.session_state:
            st.session_state.cart = []

        # Check if product already in cart
        for item in st.session_state.cart:
            if item.get('id') == product['id']:
                item['quantity'] += 1
                st.success(f"Added another {product['name']} to your cart!")
                return

        # Add new item to cart
        st.session_state.cart.append({
            'id': product['id'],
            'name': product['name'],
            'quantity': 1,
            'price': product['price'],
            'unit': product['unit'],
            'image_url': product['image_url']
        })

        st.success(f"Added {product['name']} to your cart!")

    except Exception as e:
        st.error(f"Error adding to cart: {str(e)}")

def show_delivery_checker():
    """Show delivery area checker."""
    with st.form("delivery_check"):
        zip_code = st.text_input("Enter your ZIP code", placeholder="62701")

        if st.form_submit_button("Check Delivery"):
            if zip_code:
                # Mock delivery check
                if zip_code.startswith(('621', '622', '623', '606', '607')):
                    st.success(f"✅ Great news! We deliver to {zip_code}")
                    st.info("Delivery fee: ₪5.99 (Free on orders over ₪50)")
                else:
                    st.warning(f"❌ Sorry, we don't currently deliver to {zip_code}")
                    st.info("We're always expanding! Check back soon or contact us for special arrangements.")
            else:
                st.error("Please enter your ZIP code.")