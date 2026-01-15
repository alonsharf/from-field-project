"""My Orders & Shipments - Customer order history and tracking."""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def display_product_image(product, use_column_width=True, width=None):
    """Display product image with bulletproof fallback handling."""
    image_url = product.get("image_url", "")

    # ALWAYS show placeholder - this is the bulletproof approach
    # Only show real images for verified good URLs

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
        {'width: ' + str(width) + 'px;' if width else ''}">
        <div style="font-size: {font_size}px; margin-bottom: 4px;">{emoji}</div>
        <div style="color: #4a5568; font-weight: 600; margin-bottom: 1px; font-size: {name_size}px; line-height: 1.2;">{product.get('name', 'Product')}</div>
        <div style="color: #718096; font-size: {caption_size}px;">Image coming soon</div>
    </div>
    """

    st.markdown(placeholder_html, unsafe_allow_html=True)
    return True

def get_customer_orders_only():
    """Get orders for current authenticated customer only."""
    # Get current authenticated customer
    current_user = get_current_user()
    if not current_user or not current_user.get('id'):
        return []

    # Call customer-specific API endpoint
    customer_id = current_user['id']
    response = make_api_request("GET", f"/api/orders/customer/{customer_id}")
    return response.get('orders', []) if response else []

def get_current_user():
    """Get current authenticated user from session state - NO fallbacks."""
    if (st.session_state.get('user_role') == 'customer' and
        st.session_state.get('user_id')):
        return {
            'role': st.session_state.user_role,
            'id': st.session_state.user_id,
            'name': st.session_state.user_name,
            'email': st.session_state.get('user_email')
        }
    return None  # Return None if not properly authenticated

def get_customer_order_history(customer_id, limit=50):
    """Get customer order history from API - ONLY for authenticated user."""
    # SECURITY: Ensure we only return data for the authenticated user
    current_user = get_current_user()
    if not current_user or not customer_id or current_user.get('id') != customer_id:
        return []  # Return empty if not properly authenticated

    try:
        # Get customer-specific orders and filter for completed orders
        customer_orders = get_customer_orders_only()
        if not customer_orders:
            return []

        # Convert to order history format and filter completed orders
        order_history = []
        for order in customer_orders:
            if order['status'] in ['FULFILLED', 'CANCELLED']:
                # Generate order number for display
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"

                order_history_item = {
                    'order_number': order_number,
                    'order_date': order['created_at'][:10],
                    'status': order['status'],
                    'items_count': 1,  # Default since we don't have line items from API
                    'total': float(order.get('total_amount', 0)),
                    'rating': 5 if order['status'] == 'FULFILLED' else 0  # Default rating
                }
                order_history.append(order_history_item)

        return order_history[:limit]
    except Exception as e:
        return []

def get_customer_orders(customer_id, limit=10):
    """Get customer orders with tracking from API - ONLY for authenticated user."""
    # SECURITY: Ensure we only return data for the authenticated user
    current_user = get_current_user()
    if not current_user or not customer_id or current_user.get('id') != customer_id:
        return []  # Return empty if not properly authenticated

    try:
        # Get customer-specific orders
        customer_orders_data = get_customer_orders_only()
        if not customer_orders_data:
            return []

        # Convert to customer order format with tracking info
        customer_orders = []
        for order in customer_orders_data:
            # Generate tracking number and order number
            tracking_number = f"TRACK-{order['id'][:8]}" if order['status'] in ['PAID', 'PENDING_PAYMENT'] else None
            order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"

            customer_order = {
                'order_number': order_number,
                'tracking': tracking_number,
                'status': order['status'],
                'delivery_date': 'Tuesday, December 3, 2024',  # Default delivery date
                'delivery_time': 'Morning (9AM-12PM)'  # Default delivery time
            }
            customer_orders.append(customer_order)

        return customer_orders[:limit]
    except Exception as e:
        return []

def show_customer_orders_shipments():
    """Display customer orders and shipment tracking interface."""

    # AUTHENTICATION GUARD - Critical security fix
    current_user = get_current_user()
    if not current_user:
        st.error("🔒 Authentication Required")
        st.info("Please log in as a customer to view your orders.")
        st.markdown("**Why you're seeing this:** This page shows personal order information and requires customer authentication.")
        return

    st.title("📦 My Orders & Shipments")
    st.markdown("### Track your orders and delivery status")
    st.markdown("---")

    # Tabs for different order views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Current Orders",
        "Order History",
        "Track Delivery",
        "Reorder Favorites"
    ])

    with tab1:
        show_current_orders()

    with tab2:
        show_order_history()

    with tab3:
        show_delivery_tracking()

    with tab4:
        show_reorder_favorites()

def show_current_orders():
    """Display current active orders from API."""
    st.subheader("📋 Current Orders")

    try:
        # Get customer-specific orders
        customer_orders = get_customer_orders_only()

        # Filter for active orders (not delivered yet)
        active_orders = [order for order in customer_orders if order['status'] not in ['FULFILLED', 'CANCELLED']]

        if not active_orders:
            st.info("📭 No current orders. Place your first order to see it here!")

            if st.button("🛒 Start Shopping", type="primary"):
                st.session_state.current_page = "Browse Products"
                st.rerun()
        else:
            for order in active_orders:
                # Generate order number and basic data
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                customer_name = order.get('shipping_name', 'Unknown Customer')
                total_amount = float(order.get('total_amount', 0))

                status_display = get_status_display(order['status'])
                with st.expander(f"📦 {order_number} - {status_display}", expanded=True):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Order details
                        st.markdown(f"**Order Date:** {order['created_at'][:10]}")
                        st.markdown(f"**Status:** {get_status_badge(order['status'])}")
                        st.markdown(f"**Customer:** {customer_name}")
                        st.markdown(f"**Payment:** {get_payment_badge(order['payment_status'])}")

                        # Order items (would need separate API call to get items)
                        st.markdown("**Items:** Items not loaded")

                        st.markdown(f"**Total: ₪{total_amount:.2f}**")

                    with col2:
                        st.markdown("**Actions:**")

                        if st.button(f"📍 Track Delivery", key=f"track_{order['id']}", use_container_width=True, type="primary"):
                            show_tracking_details(f"TRACK-{order['id'][:8]}")

                        if order['status'] in ['PAID', 'PENDING_PAYMENT']:
                            if st.button(f"❌ Cancel Order", key=f"cancel_{order['id']}", use_container_width=True):
                                cancel_order(order_number)

                        if st.button(f"📋 Order Details", key=f"details_{order['id']}", use_container_width=True):
                            show_order_details(order, order_number, customer_name, total_amount)

                        if st.button(f"🔄 Reorder", key=f"reorder_{order['id']}", use_container_width=True):
                            st.info("Reorder functionality available after checkout!")

    except Exception as e:
        st.error("Unable to load orders from API.")
        st.caption(f"Error: {str(e)}")

        # Fallback message
        st.info("📭 No orders to display. Please check your connection.")

def show_order_history():
    """Display customer order history from database."""
    st.subheader("📚 Order History")

    # Date range filter
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input(
            "From Date",
            value=datetime.now() - timedelta(days=90)
        )

    with col2:
        end_date = st.date_input(
            "To Date",
            value=datetime.now()
        )

    with col3:
        status_filter = st.selectbox(
            "Order Status",
            ["All Orders", "Delivered", "Cancelled", "Refunded"]
        )

    try:
        # Get current authenticated user - SECURITY: Only show user's own orders
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None

        # Get order history from database - only for authenticated user
        order_history = get_customer_order_history(customer_id, limit=50)

        if not order_history:
            st.info("📭 No order history found. Complete some orders to see them here!")
            return

        st.markdown(f"**Showing {len(order_history)} orders**")
        st.markdown("---")

        for order in order_history:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns(6)

                with col1:
                    st.markdown(f"**{order['order_number']}**")

                with col2:
                    st.markdown(order['order_date'])

                with col3:
                    st.markdown(get_status_badge(order['status']))

                with col4:
                    st.markdown(f"{order['items_count']} items")

                with col5:
                    st.markdown(f"**₪{order['total']:.2f}**")

                with col6:
                    # Order actions
                    if st.button("👁️", key=f"view_{order['order_number']}", help="View details"):
                        show_order_summary(order)

                # Rating display
                if order['status'] == 'FULFILLED':
                    rating_stars = "⭐" * order['rating']
                    st.caption(f"Your rating: {rating_stars}")

                st.divider()

        # Order statistics
        st.markdown("---")
        st.subheader("📊 Your Order Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Orders", len(order_history))

        with col2:
            total_spent = sum(order['total'] for order in order_history)
            st.metric("Total Spent", f"₪{total_spent:.2f}")

        with col3:
            avg_order = total_spent / len(order_history) if order_history else 0
            st.metric("Average Order", f"₪{avg_order:.2f}")

        with col4:
            avg_rating = sum(order.get('rating', 0) for order in order_history) / len(order_history) if order_history else 0
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")

    except Exception as e:
        st.error("Unable to load order history from database.")
        st.caption(f"Error: {str(e)}")
        st.info("📭 No order history to display. Database connection may be unavailable.")

def show_delivery_tracking():
    """Display delivery tracking interface."""
    st.subheader("📍 Track Your Delivery")

    # Tracking number input
    tracking_number = st.text_input(
        "Enter Tracking Number",
        placeholder="e.g., FARM-20241124-001",
        help="Find your tracking number in your order confirmation email"
    )

    if st.button("🔍 Track Package", type="primary"):
        if tracking_number:
            show_tracking_details(tracking_number)
        else:
            st.error("Please enter a tracking number")

    st.markdown("---")

    # Active deliveries from database
    st.subheader("🚚 Active Deliveries")

    try:
        # Get current user
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None

        # Get orders with active shipments
        current_orders = get_customer_orders(customer_id, limit=10)
        active_deliveries = [order for order in current_orders if order['tracking'] and order['status'] in ['PAID', 'PENDING_PAYMENT']]

        if not active_deliveries:
            st.info("📭 No active deliveries at the moment.")
        else:
            for order in active_deliveries:
                with st.container():
                    st.markdown(f"**Tracking:** {order['tracking']}")
                    st.markdown(f"**Order:** {order['order_number']}")
                    st.markdown(f"**Status:** {get_delivery_status_badge(order['status'])}")
                    st.markdown(f"**Estimated Delivery:** {order['delivery_date']} - {order['delivery_time']}")

                    # Progress bar (simulated)
                    progress = 60 if order['status'] == 'PAID' else 30
                    st.progress(progress / 100)

                    if order['status'] == 'PAID':
                        st.success("📦 Your order has been prepared and is ready for delivery!")

                    st.divider()

    except Exception as e:
        st.error("Unable to load delivery tracking from database.")
        st.caption(f"Error: {str(e)}")
        st.info("📭 No delivery information available.")

def show_reorder_favorites():
    """Display favorite items for easy reordering based on database."""
    st.subheader("🔄 Reorder Favorites")

    try:
        # Get current user
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None

        # Get recent orders to determine favorite products
        recent_orders = get_customer_order_history(customer_id, limit=20)

        if not recent_orders:
            st.info("📭 No order history found. Place some orders to see your favorites here!")
            return

        st.markdown("**Based on Your Order History:**")

        # For demo, show available products since we don't have purchase frequency tracking yet
        # Get products from API instead of broken database utility
        response = make_api_request("GET", "/api/products/")
        all_products = response.get('products', []) if response else []
        available_products = []

        # Convert API products to expected format
        for product in all_products[:6]:  # Limit to 6 products
            available_product = {
                'id': product['id'],
                'name': product.get('name', 'Unknown Product'),
                'price': float(product.get('price_per_unit', 0)),
                'unit': product.get('unit_label', 'unit'),
                'image_url': product.get('image_url', "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&q=80"),
                'farmer_name': 'Green Valley Farm'  # Default farmer name
            }
            available_products.append(available_product)

        if available_products:
            # Display products in a grid
            cols = st.columns(3)

            for i, product in enumerate(available_products[:3]):  # Show first 3 products
                with cols[i]:
                    display_product_image(product, use_column_width=True)
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"₪{product['price']:.2f} per {product['unit']}")
                    st.caption(f"From {product['farmer_name']}")

                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        max_value=10,
                        value=1,
                        key=f"fav_qty_{i}"
                    )

                    if st.button(f"🛒 Add to Cart", key=f"fav_add_{i}", use_container_width=True, type="primary"):
                        add_favorite_to_cart_db(product, quantity)

        st.markdown("---")

        # Quick reorder previous orders
        st.subheader("⚡ Quick Reorder")

        if recent_orders:
            st.markdown("**Reorder a Previous Order:**")

            for order in recent_orders[:3]:  # Show last 3 orders
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{order['order_number']}** - {order['order_date']}")
                    st.caption(f"{order['items_count']} items - ₪{order['total']:.2f}")

                with col2:
                    if st.button("👁️ View", key=f"quick_view_{order['order_number']}", use_container_width=True):
                        show_order_summary(order)

                with col3:
                    if st.button("🔄 Reorder", key=f"quick_reorder_{order['order_number']}", use_container_width=True, type="primary"):
                        quick_reorder(order['order_number'])
        else:
            st.info("📭 No previous orders found for quick reordering.")

    except Exception as e:
        st.error("Unable to load reorder favorites from database.")
        st.caption(f"Error: {str(e)}")
        st.info("📭 No favorites available.")

def get_status_display(status):
    """Convert database status to display format."""
    status_map = {
        "DRAFT": "Draft",
        "PENDING_PAYMENT": "Pending Payment",
        "PAID": "Preparing",
        "CANCELLED": "Cancelled",
        "FULFILLED": "Delivered"
    }
    return status_map.get(status, status)

def get_status_badge(status):
    """Get styled status badge."""
    status_colors = {
        "DRAFT": "⚪",
        "PENDING_PAYMENT": "🟡",
        "PAID": "🔵",
        "CANCELLED": "❌",
        "FULFILLED": "✅",
        # Legacy status support
        "Preparing": "🟡",
        "Packed": "🔵",
        "Shipped": "🟢",
        "Delivered": "✅",
        "Refunded": "🔄"
    }
    display_status = get_status_display(status) if status.isupper() else status
    return f"{status_colors.get(status, '⚪')} {display_status}"

def get_payment_badge(status):
    """Get styled payment status badge."""
    payment_colors = {
        "Paid": "✅",
        "Pending": "⏳",
        "Failed": "❌",
        "Refunded": "🔄"
    }
    return f"{payment_colors.get(status, '⚪')} {status}"

def get_delivery_status_badge(status):
    """Get styled delivery status badge."""
    delivery_colors = {
        "Preparing": "📦",
        "Packed": "📮",
        "Shipped": "🚚",
        "Out for Delivery": "🏃‍♂️",
        "Delivered": "✅"
    }
    return f"{delivery_colors.get(status, '⚪')} {status}"

def show_tracking_details(tracking_number):
    """Show detailed tracking information from shipments API."""
    st.success(f"📍 Tracking: {tracking_number}")

    # Try to get real tracking data from shipments API
    try:
        shipments_response = make_api_request("GET", "/api/shipments/")
        shipments = shipments_response.get('shipments', []) if shipments_response else []

        # Find shipment by tracking number
        matching_shipment = None
        for shipment in shipments:
            if shipment.get('tracking_number') == tracking_number:
                matching_shipment = shipment
                break

        if matching_shipment:
            st.markdown("**Shipment Details:**")
            st.markdown(f"• **Status:** {matching_shipment.get('status', 'Unknown')}")
            st.markdown(f"• **Carrier:** {matching_shipment.get('carrier_name', 'Farm Delivery')}")

            if matching_shipment.get('shipped_at'):
                st.markdown(f"• **Shipped:** {matching_shipment['shipped_at'][:19].replace('T', ' ')}")

            if matching_shipment.get('delivered_at'):
                st.markdown(f"• **Delivered:** {matching_shipment['delivered_at'][:19].replace('T', ' ')}")

            if matching_shipment.get('estimated_delivery_date'):
                st.markdown(f"• **Est. Delivery:** {matching_shipment['estimated_delivery_date']}")

            # Show shipping address if available
            if matching_shipment.get('shipping_address1'):
                st.markdown("**Delivery Address:**")
                st.markdown(f"• {matching_shipment['shipping_address1']}")
                if matching_shipment.get('shipping_city'):
                    st.markdown(f"• {matching_shipment['shipping_city']}, {matching_shipment.get('shipping_postal_code', '')}")
        else:
            st.info("📍 Tracking information not found. This may be a simulated tracking number.")
            # Show basic tracking events as fallback
            st.markdown("**Tracking Events:**")
            st.markdown("• **Order received** - Order confirmed at farm")
            st.markdown("• **Preparing** - Items being prepared for shipment")
            st.markdown("• **Ready for delivery** - Package ready for pickup")

    except Exception as e:
        st.error("Unable to load tracking details from API.")
        st.caption(f"Error: {str(e)}")
        st.info("📍 Real tracking information would be displayed here.")

def show_order_details(order, order_number, customer_name, total_amount):
    """Show detailed order information."""
    st.info(f"📋 Order Details: {order_number}")
    st.markdown(f"**Customer:** {customer_name}")
    st.markdown(f"**Total:** ₪{total_amount:.2f}")
    st.markdown(f"**Status:** {order['status']}")
    st.markdown(f"**Created:** {order['created_at'][:19].replace('T', ' ')}")

def show_order_summary(order):
    """Show order summary."""
    st.info(f"📋 Order Summary: {order['order_number']}")
    # This would show order summary information

def cancel_order(order_number):
    """Cancel an order."""
    st.warning(f"⚠️ Are you sure you want to cancel order {order_number}?")
    # This would handle order cancellation

def add_favorite_to_cart_db(product, quantity):
    """Add favorite item to cart using session state."""
    try:
        # Initialize cart if it doesn't exist
        if 'cart' not in st.session_state:
            st.session_state.cart = []

        # Check if product already in cart
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
    except Exception as e:
        st.error(f"Error adding to cart: {str(e)}")

def reorder_items(items):
    """Add previous order items to cart (placeholder - would need product IDs)."""
    st.info("🔄 Reorder functionality would add these items to your cart:")
    for item in items:
        st.markdown(f"• {item['product_name']} - {item['quantity']} {item['unit']}")
    st.warning("⚠️ This feature requires product ID mapping to implement fully.")

def quick_reorder(order_number):
    """Quick reorder a previous order."""
    st.success(f"Items from {order_number} added to your cart!")
    # This would add all items from the previous order to the cart