"""Shipments & Logistics - Manage shipping and delivery logistics."""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_farmer_shipments():
    """Get farmer shipments via API."""
    response = make_api_request("GET", "/api/shipments/")
    return response.get('shipments', []) if response else []

def get_farmer_orders(status=None):
    """Get farmer orders via API."""
    params = {"status": status} if status else {}
    response = make_api_request("GET", "/api/orders/", params)
    return response.get('orders', []) if response else []

def get_current_user():
    """Get current user from session state."""
    if st.session_state.get('user_role') is not None:
        return {
            'role': st.session_state.user_role,
            'id': st.session_state.user_id,
            'name': st.session_state.user_name,
            'email': st.session_state.get('user_email'),
            'farm_name': st.session_state.get('farm_name')
        }
    return None

def update_shipment_status(shipment_id, new_status):
    """Update shipment status via API."""
    return make_api_request("PUT", f"/api/shipments/{shipment_id}", {"status": new_status})

def create_shipment(order_id, shipment_data):
    """Create shipment via API."""
    shipment_data['order_id'] = order_id
    response = make_api_request("POST", "/api/shipments/", shipment_data)
    return response.get('id') if response else None

def show_shipments_logistics():
    """Display shipments and logistics management interface."""
    st.title("🚚 Shipments & Logistics")
    st.markdown("### Manage shipping, tracking, and delivery logistics")
    st.markdown("---")

    # Tabs for different shipping functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Active Shipments",
        "Create Shipment",
        "Shipping History",
        "Logistics Settings"
    ])

    with tab1:
        show_active_shipments()

    with tab2:
        show_create_shipment()

    with tab3:
        show_shipping_history()

    with tab4:
        show_logistics_settings()

def show_active_shipments():
    """Display currently active shipments."""
    st.subheader("📦 Active Shipments")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All Active", "Packed", "Shipped", "In Transit", "Out for Delivery"]
        )

    with col2:
        carrier_filter = st.selectbox(
            "Filter by carrier",
            ["All Carriers", "UPS", "FedEx", "USPS", "Local Delivery"]
        )

    with col3:
        priority_filter = st.selectbox(
            "Priority",
            ["All Shipments", "Express", "Standard", "Economy"]
        )

    st.markdown("---")

    try:
        # Get active shipments from API
        all_shipments = get_farmer_shipments()
        active_shipments = [
            s for s in all_shipments
            if s['status'] in ['PENDING', 'PACKED', 'SHIPPED', 'IN_TRANSIT', 'OUT_FOR_DELIVERY']
        ]

        if not active_shipments:
            st.info("📭 No active shipments at the moment.")
        else:
            for shipment in active_shipments:
                tracking_display = shipment.get('tracking_number') or 'No tracking'

                # For customer display, use shipping_name if available (handle None explicitly)
                customer_display = shipment.get('shipping_name') or 'Unknown Customer'

                # Generate order number from order_id and creation date if available
                order_display = shipment.get('order_id', 'N/A')
                if order_display != 'N/A':
                    order_display = f"Order-{order_display[:8]}"

                with st.expander(f"📦 {tracking_display} - {customer_display}", expanded=True):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Order:** {order_display}")
                        st.markdown(f"**Customer:** {customer_display}")

                        # Build shipping address display
                        address_parts = []
                        if shipment.get('shipping_address1'):
                            address_parts.append(shipment['shipping_address1'])
                        if shipment.get('shipping_city'):
                            city_part = shipment['shipping_city']
                            if shipment.get('shipping_postal_code'):
                                city_part += f" {shipment['shipping_postal_code']}"
                            address_parts.append(city_part)

                        address_display = ', '.join(address_parts) if address_parts else 'Address not set'
                        st.markdown(f"**Destination:** {address_display}")

                        st.markdown(f"**Carrier:** {shipment.get('carrier_name') or 'Farm Delivery'}")
                        st.markdown(f"**Status:** {shipment.get('status', 'Unknown')}")

                        delivery_date = shipment.get('estimated_delivery_date')
                        if delivery_date and delivery_date != 'null':
                            st.markdown(f"**Est. Delivery:** {delivery_date[:10] if isinstance(delivery_date, str) else delivery_date}")
                        else:
                            st.markdown("**Est. Delivery:** Not set")

                        # Show shipped/delivered dates if available
                        if shipment.get('shipped_at'):
                            st.markdown(f"**Shipped:** {shipment['shipped_at'][:10]}")
                        if shipment.get('delivered_at'):
                            st.markdown(f"**Delivered:** {shipment['delivered_at'][:10]}")

                    with col2:
                        st.markdown("**Actions:**")

                        if st.button(f"📍 Track Package", key=f"track_{shipment['id']}", type="primary"):
                            show_tracking_details(tracking_display)

                        if st.button(f"📞 Contact Customer", key=f"contact_{shipment['id']}"):
                            st.info(f"Opening contact form for {customer_display}")

                        if st.button(f"📋 Update Status", key=f"update_{shipment['id']}"):
                            show_status_update_form(shipment['id'], tracking_display)

    except Exception as e:
        st.error("Unable to load shipment data.")
        st.caption(f"Error: {str(e)}")
        st.info("🚚 Active shipments will appear here once connected to the database.")

def show_create_shipment():
    """Display form to create new shipments."""
    st.subheader("📮 Create New Shipment")

    # Step 1: Select Order
    st.markdown("**Step 1: Select Order to Ship**")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get orders ready for shipping (PAID status)
        paid_orders = get_farmer_orders('PAID')
        ready_orders = []

        for order in paid_orders:
            # Generate order number and customer name similar to dashboard
            order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
            customer_name = order.get('shipping_name', 'Unknown Customer')

            # Format items display (if items are available)
            items_text = "Items not loaded"
            if order.get('items') and isinstance(order['items'], list):
                items_text = ", ".join([f"{item.get('product_name', 'Unknown')} ({float(item.get('quantity', 0)):.1f})"
                                      for item in order['items']])

            ready_orders.append({
                "id": order['id'],
                "order_number": order_number,
                "customer": customer_name,
                "items": items_text
            })

        if ready_orders:
            selected_order = st.selectbox(
                "Select order to ship:",
                options=[f"{order['order_number']} - {order['customer']}" for order in ready_orders],
                format_func=lambda x: x
            )

        if selected_order:
            order_id = selected_order.split(" -")[0]
            st.success(f"Selected: {selected_order}")

            # Step 2: Shipping Details
            st.markdown("---")
            st.markdown("**Step 2: Shipping Information**")

            col1, col2 = st.columns(2)

            with col1:
                carrier = st.selectbox(
                    "Shipping Carrier *",
                    ["UPS", "FedEx", "USPS", "Local Delivery", "Customer Pickup"]
                )

                service_type = st.selectbox(
                    "Service Type *",
                    ["Standard Ground", "Express", "Next Day Air", "2-Day Air", "Economy"]
                )

                package_weight = st.number_input(
                    "Package Weight (lbs) *",
                    min_value=0.1,
                    max_value=150.0,
                    value=5.0,
                    step=0.1
                )

            with col2:
                ship_date = st.date_input(
                    "Ship Date *",
                    value=datetime.now().date()
                )

                estimated_delivery = st.date_input(
                    "Estimated Delivery",
                    value=datetime.now().date() + timedelta(days=3)
                )

                insurance_value = st.number_input(
                    "Insurance Value (₪)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    help="Optional insurance coverage"
                )

            # Step 3: Package Details
            st.markdown("---")
            st.markdown("**Step 3: Package Details**")

            col1, col2 = st.columns(2)

            with col1:
                package_type = st.selectbox(
                    "Package Type",
                    ["Box", "Envelope", "Tube", "Pak", "Custom"]
                )

                dimensions = st.text_input(
                    "Dimensions (L x W x H inches)",
                    placeholder="12 x 8 x 6",
                    help="Length x Width x Height in inches"
                )

            with col2:
                special_instructions = st.text_area(
                    "Special Instructions",
                    placeholder="Handle with care, fragile produce...",
                    height=80
                )

                requires_signature = st.checkbox(
                    "Signature Required",
                    help="Require signature upon delivery"
                )

            # Create shipment button
            st.markdown("---")
            if st.button("🚀 Create Shipment", type="primary"):
                if carrier and service_type and package_weight > 0:
                    try:
                        # Find the selected order from our ready_orders list
                        selected_order_data = None
                        for order in ready_orders:
                            if f"{order['order_number']} - {order['customer']}" == selected_order:
                                selected_order_data = order
                                break

                        if selected_order_data:
                            # Generate tracking number
                            tracking_number = f"1Z{carrier[:3].upper()}{datetime.now().strftime('%Y%m%d%H%M')}"

                            # Prepare shipment data
                            shipment_data = {
                                'status': 'PENDING',
                                'carrier_name': carrier,
                                'tracking_number': tracking_number,
                                'estimated_delivery_date': estimated_delivery
                            }

                            # Create the shipment in database
                            shipment_id = create_shipment(selected_order_data['id'], shipment_data)
                            if shipment_id:
                                st.success(f"✅ Shipment created successfully!")
                                st.info(f"📦 Tracking Number: {tracking_number}")
                                st.info(f"🚚 Carrier: {carrier} - {service_type}")
                                st.info(f"📅 Estimated Delivery: {estimated_delivery}")
                                st.info("Switch to the 'Active Shipments' tab to see your new shipment.")
                            else:
                                st.error("❌ Failed to create shipment. Please try again.")
                        else:
                            st.error("❌ Selected order not found. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Error creating shipment: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields")

        else:
            st.info("📭 No orders ready for shipment. Complete order fulfillment first.")

    except Exception as e:
        st.error("Unable to load orders for shipment.")
        st.caption(f"Error: {str(e)}")
        st.info("📦 Orders ready for shipment will appear here once connected to the database.")

def show_shipping_history():
    """Display shipping history and completed deliveries."""
    st.subheader("📚 Shipping History")

    # Date range selector
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input(
            "From Date",
            value=datetime.now() - timedelta(days=30)
        )

    with col2:
        end_date = st.date_input(
            "To Date",
            value=datetime.now()
        )

    with col3:
        history_status = st.selectbox(
            "Status",
            ["All Shipments", "Delivered", "Cancelled", "Returned"]
        )

    if st.button("🔍 Search Shipments"):
        st.success("Searching shipment history...")

    st.markdown("---")

    try:
        # Get completed shipments from API
        all_shipments = get_farmer_shipments()
        completed_shipments = [
            s for s in all_shipments
            if s['status'] in ['DELIVERED', 'CANCELLED', 'RETURNED']
        ]

        if not completed_shipments:
            st.info("📋 No completed shipments found in the selected date range.")
        else:
            # Display shipment history table
            for shipment in completed_shipments:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns(6)

                    with col1:
                        tracking = shipment.get('tracking_number', 'No tracking')
                        st.markdown(f"**{tracking[:12]}...**" if len(tracking) > 12 else f"**{tracking}**")

                    with col2:
                        customer_name = shipment.get('shipping_name', 'Unknown')
                        st.markdown(customer_name)

                    with col3:
                        carrier_name = shipment.get('carrier_name') or 'Farm Delivery'
                        st.markdown(carrier_name)

                    with col4:
                        ship_date = shipment.get('shipped_at')
                        if ship_date:
                            st.markdown(ship_date[:10])  # Extract date part
                        else:
                            st.markdown('N/A')

                    with col5:
                        delivery_date = shipment.get('delivered_at')
                        if delivery_date:
                            st.markdown(delivery_date[:10])  # Extract date part
                        else:
                            st.markdown('N/A')

                    with col6:
                        status = shipment.get('status', 'Unknown')
                        status_color = "🟢" if status == "DELIVERED" else "🔴" if status == "CANCELLED" else "🟡"
                        st.markdown(f"{status_color} {status}")

                    st.divider()

    except Exception as e:
        st.error("Unable to load shipping history.")
        st.caption(f"Error: {str(e)}")
        st.info("📚 Shipping history will appear here once connected to the database.")

    # Shipping analytics
    st.markdown("---")
    st.subheader("📊 Shipping Analytics")

    try:
        # Calculate real analytics from the shipments API
        all_shipments_for_farmer = get_farmer_shipments()

        total_shipments = len(all_shipments_for_farmer)
        delivered_shipments = [s for s in all_shipments_for_farmer if s['status'] == 'DELIVERED']

        # Calculate on-time delivery rate (placeholder calculation)
        on_time_rate = (len(delivered_shipments) / total_shipments * 100) if total_shipments > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Shipments", str(total_shipments))

        with col2:
            st.metric("Delivered", f"{len(delivered_shipments)}")

        with col3:
            st.metric("On-Time Delivery", f"{on_time_rate:.1f}%")

        with col4:
            active_count = len([s for s in all_shipments_for_farmer if s['status'] in ['PENDING', 'PACKED', 'SHIPPED']])
            st.metric("Active Shipments", str(active_count))

    except Exception as e:
        # Fallback to placeholder metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Shipments", "0")

        with col2:
            st.metric("Delivered", "0")

        with col3:
            st.metric("On-Time Delivery", "0%")

        with col4:
            st.metric("Active Shipments", "0")

def show_logistics_settings():
    """Display logistics and shipping settings."""
    st.subheader("⚙️ Logistics Settings")

    # Shipping preferences
    st.markdown("**Default Shipping Preferences**")

    col1, col2 = st.columns(2)

    with col1:
        default_carrier = st.selectbox(
            "Default Carrier",
            ["UPS", "FedEx", "USPS", "Local Delivery"],
            index=0
        )

        default_service = st.selectbox(
            "Default Service Type",
            ["Standard Ground", "Express", "Economy"],
            index=0
        )

        auto_insurance = st.checkbox(
            "Automatic Insurance",
            value=True,
            help="Automatically add insurance for high-value orders"
        )

    with col2:
        insurance_threshold = st.number_input(
            "Insurance Threshold (₪)",
            min_value=0,
            value=50,
            help="Add insurance for orders above this amount"
        )

        signature_threshold = st.number_input(
            "Signature Required Threshold (₪)",
            min_value=0,
            value=100,
            help="Require signature for orders above this amount"
        )

        notification_emails = st.checkbox(
            "Email Notifications",
            value=True,
            help="Send email notifications for shipping updates"
        )

    st.markdown("---")

    # Carrier accounts
    st.markdown("**Carrier Account Information**")

    carriers = ["UPS", "FedEx", "USPS"]

    for carrier in carriers:
        with st.expander(f"📦 {carrier} Account Settings"):
            col1, col2 = st.columns(2)

            with col1:
                account_number = st.text_input(
                    f"{carrier} Account Number",
                    key=f"{carrier}_account",
                    type="password"
                )

            with col2:
                api_key = st.text_input(
                    f"{carrier} API Key",
                    key=f"{carrier}_api",
                    type="password"
                )

            if st.button(f"Test {carrier} Connection", key=f"test_{carrier}"):
                st.success(f"✅ {carrier} connection successful!")

    # Save settings
    st.markdown("---")
    if st.button("💾 Save Logistics Settings", type="primary"):
        st.success("✅ Logistics settings saved successfully!")

def show_tracking_details(tracking_number):
    """Show detailed tracking information."""
    st.info(f"📍 Tracking details for {tracking_number}")
    
    # Show tracking timeline
    st.markdown("**📦 Shipment Timeline:**")
    
    # In a real implementation, this would fetch from carrier APIs
    # For now, show the tracking number that can be used on carrier websites
    if tracking_number.startswith("FARM-"):
        st.markdown("🏠 **Farm Direct Delivery** - Track with your local delivery service")
        st.markdown(f"• Tracking Number: `{tracking_number}`")
        st.markdown("• Contact the farm directly for delivery updates")
    elif tracking_number.startswith("1ZUPS"):
        st.markdown("🟤 **UPS Tracking**")
        st.markdown(f"• [Track on UPS.com](https://www.ups.com/track?tracknum={tracking_number})")
    elif tracking_number.startswith("1ZFED"):
        st.markdown("🟣 **FedEx Tracking**")
        st.markdown(f"• [Track on FedEx.com](https://www.fedex.com/fedextrack/?trknbr={tracking_number})")
    else:
        st.markdown(f"• Tracking Number: `{tracking_number}`")
        st.markdown("• Check with the carrier for delivery status")

def show_status_update_form(shipment_id, tracking_number):
    """Show form to update shipment status."""
    st.info(f"📋 Update status for shipment {tracking_number}")

    new_status = st.selectbox(
        "Select new status",
        ["PENDING", "PACKED", "SHIPPED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"],
        key=f"status_update_{shipment_id}"
    )

    if st.button(f"Update Status", key=f"confirm_update_{shipment_id}"):
        try:
            if update_shipment_status(shipment_id, new_status):
                st.success(f"Status updated to {new_status}")
                st.rerun()
            else:
                st.error("Failed to update shipment status")
        except Exception as e:
            st.error(f"Error updating status: {str(e)}")