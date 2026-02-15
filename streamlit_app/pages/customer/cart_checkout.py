"""My Cart & Checkout - Shopping cart and checkout process."""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request
from .paypal_components import show_paypal_payment_button, prepare_order_data_for_api
from .browse_products import get_category_emoji

def display_product_image(product, use_column_width=True, width=None):
    """Display product image with bulletproof fallback handling."""
    image_url = product.get("image_url", "")

    # ALWAYS show placeholder - this is the bulletproof approach
    # Only show real images for verified good URLs

    # Get category emoji using centralized function
    emoji = get_category_emoji(product)

    # Adjust size for different contexts
    if width and width < 100:
        # Small cart thumbnails
        font_size = 24
        padding = "15px 10px"
        min_height = 60
        name_size = 10
        caption_size = 8
    else:
        # Regular product images
        font_size = 36
        padding = "30px 15px"
        min_height = 120
        name_size = 14
        caption_size = 11

    # Create beautiful placeholder
    placeholder_html = f"""
    <div style="
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border: 2px dashed #cbd5e0;
        border-radius: 8px;
        padding: {padding};
        text-align: center;
        margin: 4px 0;
        min-height: {min_height}px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        {'width: ' + str(width) + 'px;' if width else ''}
    ">
        <div style="font-size: {font_size}px; margin-bottom: 4px;">{emoji}</div>
        <div style="color: #4a5568; font-weight: 600; margin-bottom: 1px; font-size: {name_size}px; line-height: 1.2;">{product.get('name', 'Product')}</div>
        <div style="color: #718096; font-size: {caption_size}px;">Image coming soon</div>
    </div>
    """

    st.markdown(placeholder_html, unsafe_allow_html=True)
    return True

def get_or_create_session_id():
    """Get or create customer session ID."""
    if 'customer_session_id' not in st.session_state:
        import uuid
        st.session_state.customer_session_id = str(uuid.uuid4())
    return st.session_state.customer_session_id

def create_order_api(order_data):
    """Create order via API."""
    return make_api_request("POST", "/api/orders/", order_data)

def show_cart_checkout():
    """Display shopping cart and checkout interface."""
    st.title("🛒 My Cart & Checkout")
    st.markdown("### Review your order and complete your purchase")
    st.markdown("---")

    # Get cart from session state (set by browse_products page)
    cart_items = st.session_state.get('cart', [])

    # Check if cart is empty
    if not cart_items:
        show_empty_cart()
        return

    # Calculate cart totals
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)

    # Store cart data in session state for use in other functions
    st.session_state.cart_data = {
        'items': cart_items,
        'total': cart_total,
        'item_count': total_items
    }

    # Tabs for cart and checkout
    tab1, tab2 = st.tabs(["🛒 Shopping Cart", "💳 Checkout"])

    with tab1:
        show_shopping_cart()

    with tab2:
        show_checkout_process()

def show_checkout_only():
    """Display checkout process only (redirected from cart)."""
    st.title("💳 Checkout")
    st.markdown("### Complete your purchase")
    st.markdown("---")

    # Get cart from session state (set by browse_products page)
    cart_items = st.session_state.get('cart', [])

    # Check if cart is empty
    if not cart_items:
        st.warning("Your cart is empty!")
        st.info("Add items to your cart before checking out.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Browse Products", type="primary", use_container_width=True):
                st.session_state.current_page = "Browse Products"
                st.rerun()

        with col2:
            if st.button("🛒 View Cart", use_container_width=True):
                st.session_state.current_page = "My Cart & Checkout"
                st.rerun()
        return

    # Calculate cart totals
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)

    # Store cart data in session state for use in other functions
    st.session_state.cart_data = {
        'items': cart_items,
        'total': cart_total,
        'item_count': total_items
    }

    # Back to cart button
    if st.button("← Back to Cart", type="secondary"):
        st.session_state.current_page = "My Cart & Checkout"
        st.rerun()

    st.markdown("---")

    # Show checkout process
    show_checkout_process()

def show_empty_cart():
    """Display empty cart message."""
    st.info("🛒 Your cart is empty")
    st.markdown("### Browse our fresh produce to get started!")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🔍 Browse Products", type="primary", use_container_width=True):
            st.session_state.current_page = "Browse Products"
            st.rerun()

        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "Storefront Home"
            st.rerun()

def show_shopping_cart():
    """Display shopping cart contents."""
    st.subheader("🛒 Your Cart")

    # Get cart data from session state
    cart_data = st.session_state.get('cart_data', {})
    cart_items = cart_data.get('items', [])
    cart_total = cart_data.get('total', 0)
    total_items = cart_data.get('item_count', 0)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Items in Cart", total_items)

    with col2:
        st.metric("Subtotal", f"₪{cart_total:.2f}")

    with col3:
        # Calculate delivery fee
        delivery_fee = 0.00 if cart_total >= 50.00 else 5.99
        st.metric("Delivery Fee", f"₪{delivery_fee:.2f}")

    st.markdown("---")

    # Cart items
    for i, item in enumerate(cart_items):
        item_total = item['price'] * item['quantity']

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([1, 3, 1, 1, 1])

            with col1:
                display_product_image(item, width=80)

            with col2:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"₪{item['price']:.2f} {item['unit']}")

            with col3:
                # Quantity selector with update functionality
                new_quantity = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=10,
                    value=int(item['quantity']),
                    key=f"qty_{item['id']}_{i}"
                )

                # Update quantity if changed
                if new_quantity != item['quantity']:
                    cart_items[i]['quantity'] = new_quantity
                    st.session_state.cart = cart_items
                    st.rerun()

            with col4:
                st.markdown(f"**₪{item_total:.2f}**")

            with col5:
                if st.button("🗑️", key=f"remove_{i}", help="Remove from cart"):
                    # Remove item from session state cart
                    cart_items.pop(i)
                    st.session_state.cart = cart_items
                    st.success("Item removed from cart!")
                    st.rerun()

            st.divider()

    # Cart actions
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗑️ Clear Cart", type="secondary"):
            st.session_state.cart = []
            st.success("Cart cleared!")
            st.rerun()

    with col2:
        if st.button("🔍 Continue Shopping"):
            st.session_state.current_page = "Browse Products"
            st.rerun()

    with col3:
        if st.button("💳 Proceed to Checkout", type="primary"):
            # Navigate directly to checkout by changing the current page
            st.session_state.current_page = "Checkout Process"
            st.rerun()

    # Order summary
    st.markdown("---")
    st.subheader("📋 Order Summary")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Delivery information
        st.markdown("**Estimated Delivery:**")
        next_tuesday = get_next_delivery_date("Tuesday")
        next_friday = get_next_delivery_date("Friday")

        delivery_option = st.radio(
            "Choose delivery date:",
            [f"Tuesday, {next_tuesday}", f"Friday, {next_friday}"],
            help="We deliver on Tuesdays and Fridays"
        )

    with col2:
        # Price breakdown
        st.markdown("**Price Breakdown:**")
        st.markdown(f"Subtotal: ₪{cart_total:.2f}")
        st.markdown(f"Delivery: ₪{delivery_fee:.2f}")

        if delivery_fee == 0:
            st.success("🎉 Free delivery (order over ₪50)")

        total = cart_total + delivery_fee
        st.markdown(f"**Total: ₪{total:.2f}**")

def show_checkout_process():
    """Display checkout process."""
    cart_data = st.session_state.get('cart_data', {})
    if not cart_data or not cart_data.get('items'):
        st.warning("Your cart is empty. Add items to your cart first.")
        return

    st.subheader("💳 Checkout")

    # Initialize payment method in session state if not set
    if 'selected_payment_method' not in st.session_state:
        st.session_state.selected_payment_method = "PayPal"

    # Progress indicator
    col1, col2, col3, col4 = st.columns(4)

    # Checkout form
    with st.form("checkout_form"):
        st.subheader("📞 Contact Information")

        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "Email Address *",
                placeholder="your.email@example.com",
                help="We'll send order confirmation to this email"
            )

            phone = st.text_input(
                "Phone Number *",
                placeholder="(050) 123-4567",
                help="For delivery notifications"
            )

        with col2:
            first_name = st.text_input("First Name *", placeholder="Israel")
            last_name = st.text_input("Last Name *", placeholder="Israeli")

        st.markdown("---")
        st.subheader("🏠 Delivery Address")

        address = st.text_input(
            "Street Address *",
            placeholder="123 Main Street"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            city = st.text_input("City *", placeholder="Tel-Aviv")

        with col2:
            state = st.selectbox("State *", ["IL", "IN", "IA", "MO", "WI"])

        with col3:
            zip_code = st.text_input("ZIP Code *", placeholder="62701")

        delivery_instructions = st.text_area(
            "Delivery Instructions (optional)",
            placeholder="e.g., Leave at front door, Ring doorbell, etc.",
            height=80
        )

        st.markdown("---")
        st.subheader("📅 Delivery Options")

        # Delivery date selection
        next_tuesday = get_next_delivery_date("Tuesday")
        next_friday = get_next_delivery_date("Friday")

        delivery_date = st.radio(
            "Preferred Delivery Date:",
            [f"Tuesday, {next_tuesday}", f"Friday, {next_friday}"],
            help="Orders must be placed by Sunday for Tuesday delivery, or Wednesday for Friday delivery"
        )

        delivery_time = st.selectbox(
            "Preferred Delivery Time:",
            ["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)", "No Preference"]
        )

        st.markdown("---")
        st.subheader("💳 Payment Information")

        payment_method = st.radio(
            "Payment Method:",
            ["PayPal", "Credit/Debit Card", "Pay on Delivery (Cash/Check)"],
            help="All payment methods are secure and encrypted"
        )

        # Store payment method in session state for access outside form
        st.session_state.selected_payment_method = payment_method

        # Store payment method and other form data in session state for PayPal integration
        if payment_method == "PayPal":
            st.info("💡 Complete your order details above, then click 'Pay with PayPal' below to proceed.")
            # PayPal payment will be handled outside the form after validation

        elif payment_method == "Credit/Debit Card":
            st.warning("⚠️ Credit card processing is not yet implemented. Please use PayPal or Pay on Delivery.")
            col1, col2 = st.columns(2)

            with col1:
                card_number = st.text_input(
                    "Card Number *",
                    placeholder="1234 5678 9012 3456",
                    type="password",
                    disabled=True
                )

                cardholder_name = st.text_input(
                    "Cardholder Name *",
                    placeholder="John Smith",
                    disabled=True
                )

            with col2:
                col2a, col2b = st.columns(2)

                with col2a:
                    expiry = st.text_input(
                        "Expiry (MM/YY) *",
                        placeholder="12/25",
                        disabled=True
                    )

                with col2b:
                    cvv = st.text_input(
                        "CVV *",
                        placeholder="123",
                        type="password",
                        disabled=True
                    )

                billing_same = st.checkbox(
                    "Billing address same as delivery",
                    value=True,
                    disabled=True
                )

        elif payment_method == "Pay on Delivery (Cash/Check)":
            st.info("💡 Please have exact change ready or a check made out to 'Green Valley Farm'.")

        st.markdown("---")
        st.subheader("📋 Order Review")

        # Order summary using session state cart data
        cart_total = cart_data.get('total', 0)
        total_items = cart_data.get('item_count', 0)
        delivery_fee = 0.00 if cart_total >= 50.00 else 5.99
        total = cart_total + delivery_fee

        st.markdown(f"**Items:** {total_items}")
        st.markdown(f"**Subtotal:** ₪{cart_total:.2f}")
        st.markdown(f"**Delivery:** ₪{delivery_fee:.2f}")
        st.markdown(f"**Total:** ₪{total:.2f}")

        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy *",
            help="Required to complete your order"
        )

        # Submit order - different handling for PayPal vs other methods
        if payment_method == "PayPal":
            # For PayPal, validate form but don't submit yet
            validate_button = st.form_submit_button(
                "✅ Validate Order Information",
                type="secondary",
                use_container_width=True
            )

            if validate_button:
                if validate_checkout_form(email, phone, first_name, last_name, address, city, zip_code, payment_method, agree_terms):
                    # Store validated form data in session state for PayPal processing
                    st.session_state.checkout_form_data = {
                        'email': email,
                        'phone': phone,
                        'first_name': first_name,
                        'last_name': last_name,
                        'address': address,
                        'city': city,
                        'state': state,
                        'zip_code': zip_code,
                        'delivery_instructions': delivery_instructions,
                        'delivery_date': delivery_date,
                        'delivery_time': delivery_time,
                        'payment_method': payment_method,
                        'total': total
                    }
                    st.success("✅ Order information validated! Now click 'Pay with PayPal' below.")
                    st.session_state.form_validated = True
                else:
                    st.error("❌ Please fill in all required fields and agree to the terms.")
        else:
            # For other payment methods, proceed as before
            submitted = st.form_submit_button(
                "🎉 Place Order",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if validate_checkout_form(email, phone, first_name, last_name, address, city, zip_code, payment_method, agree_terms):
                    process_order(
                        email, phone, first_name, last_name, address, city, state, zip_code,
                        delivery_instructions, delivery_date, delivery_time, payment_method, total
                    )
                else:
                    st.error("❌ Please fill in all required fields and agree to the terms.")

    # PayPal payment button (outside the form)
    if st.session_state.get('selected_payment_method') == "PayPal" and st.session_state.get('form_validated', False):
        st.markdown("---")
        st.subheader("💳 Complete Payment")

        # Prepare order data for PayPal
        customer_info = st.session_state.checkout_form_data
        cart_data = st.session_state.cart_data

        # Prepare order data for API
        order_data = prepare_order_data_for_api(customer_info, cart_data)

        # Check if all required fields are filled
        form_complete = all([
            customer_info.get('email'),
            customer_info.get('phone'),
            customer_info.get('first_name'),
            customer_info.get('last_name'),
            customer_info.get('address'),
            customer_info.get('city'),
            customer_info.get('zip_code')
        ])

        # Show PayPal button
        show_paypal_payment_button(order_data, disabled=not form_complete)

def validate_checkout_form(email, phone, first_name, last_name, address, city, zip_code, payment_method, agree_terms):
    """Validate checkout form data."""
    required_fields = [email, phone, first_name, last_name, address, city, zip_code]

    if not all(required_fields):
        return False

    if not agree_terms:
        return False

    # Additional validation for payment method
    if payment_method == "Credit/Debit Card":
        # In a real app, you'd validate card details
        pass

    return True

def process_order(email, phone, first_name, last_name, address, city, state, zip_code,
                 delivery_instructions, delivery_date, delivery_time, payment_method, total):
    """Process the order submission by calling the API."""
    # Get cart data
    cart_data = st.session_state.get('cart_data', {})
    cart_items = cart_data.get('items', [])
    
    if not cart_items:
        st.error("❌ Cart is empty. Cannot place order.")
        return
    
    # Get customer ID from session
    customer_id = st.session_state.get('user_id')
    if not customer_id:
        st.error("❌ Please log in to place an order.")
        return
    
    # Get farmer ID from first product or use admin farmer
    farmer_response = make_api_request("GET", "/api/auth/farmer/admin")
    if not farmer_response or 'id' not in farmer_response:
        st.error("❌ Could not retrieve farmer information. Please try again.")
        return
    farmer_id = farmer_response['id']
    
    # Calculate delivery fee
    cart_total = cart_data.get('total', 0)
    delivery_fee = 0.00 if cart_total >= 50.00 else 5.99
    
    # Prepare order items
    order_items = []
    for item in cart_items:
        order_items.append({
            "product_id": item['id'],
            "quantity": float(item['quantity']),
            "unit_price": float(item['price'])
        })
    
    # Prepare order data for API
    order_data = {
        "customer_id": customer_id,
        "farmer_id": farmer_id,
        "shipping_name": f"{first_name} {last_name}",
        "shipping_phone": phone,
        "shipping_address1": address,
        "shipping_address2": "",
        "shipping_city": city,
        "shipping_postal_code": zip_code,
        "shipping_country": "Israel",
        "customer_notes": delivery_instructions or f"Delivery: {delivery_date} - {delivery_time}",
        "shipping_amount": delivery_fee,
        "items": order_items
    }
    
    # Call API to create order
    with st.spinner("Creating your order..."):
        order_response = create_order_api(order_data)
    
    if not order_response:
        st.error("❌ Failed to create order. Please try again.")
        return
    
    # Get order details from response
    order_id = order_response.get('id', 'N/A')
    order_number = f"ORD-{str(order_id)[:8].upper()}"

    # Clear cart from session state
    st.session_state.cart = []

    # Show success message
    st.success("🎉 Order placed successfully!")

    st.balloons()

    # Order confirmation details
    st.markdown("---")
    st.subheader("📧 Order Confirmation")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Order Number:** {order_number}")
        st.markdown(f"**Order ID:** `{order_id}`")
        st.markdown(f"**Customer:** {first_name} {last_name}")
        st.markdown(f"**Email:** {email}")
        st.markdown(f"**Phone:** {phone}")

    with col2:
        st.markdown(f"**Delivery Address:**")
        st.markdown(f"{address}")
        st.markdown(f"{city}, {state} {zip_code}")
        st.markdown(f"**Total:** ₪{total:.2f}")

    st.markdown(f"**Delivery:** {delivery_date} - {delivery_time}")
    st.markdown(f"**Payment:** {payment_method}")

    if delivery_instructions:
        st.markdown(f"**Special Instructions:** {delivery_instructions}")

    st.info("📧 A confirmation email has been sent to your email address.")
    st.info("📱 You'll receive SMS updates about your order status and delivery.")

    # Next steps
    st.markdown("---")
    st.subheader("📋 What's Next?")

    st.markdown("1. **Confirmation Email** - Check your email for order details")
    st.markdown("2. **Order Preparation** - We'll prepare your fresh produce")
    st.markdown("3. **Delivery Notification** - You'll get an SMS when we're on our way")
    st.markdown("4. **Enjoy** - Fresh, local produce delivered to your door!")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 Track My Orders", use_container_width=True):
            st.session_state.current_page = "My Orders & Shipments"
            st.rerun()

    with col2:
        if st.button("🔍 Continue Shopping", use_container_width=True):
            st.session_state.current_page = "Browse Products"
            st.rerun()

def get_next_delivery_date(day_name):
    """Get the next delivery date for a given day."""
    today = datetime.now()
    days_ahead = {"Tuesday": 1, "Friday": 4}[day_name] - today.weekday()

    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    next_date = today + timedelta(days=days_ahead)
    return next_date.strftime("%B %d, %Y")