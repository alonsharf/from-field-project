"""Farmer Dashboard - Overview of farm operations and key metrics."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_farmer_dashboard_stats():
    """Get farmer dashboard statistics via API."""
    return make_api_request("GET", "/api/analytics/farmer/dashboard")

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

def show_farmer_dashboard():
    """Display farmer dashboard with farm overview and key metrics."""
    # Enhanced agricultural header
    header_html = """
    <div class="agricultural-header">
        <h1>📊 Farm Management Dashboard</h1>
        <p>Welcome to your comprehensive farm operations overview</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Get current user (for demo, we'll use a test farmer ID)
    current_user = get_current_user()
    farmer_id = current_user.get('id') if current_user else None

    # For demo purposes, if no farmer is set, show general stats
    try:
        # Get dashboard statistics from database
        stats = get_farmer_dashboard_stats()

        # Enhanced Key Metrics with Custom Cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_html = f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🥕</span>
                    <span style="color: var(--primary-green); font-weight: 600; font-size: 1rem;">My Products</span>
                </div>
                <div style="color: var(--secondary-green); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {stats['total_products']}
                </div>
                <div style="color: var(--accent-green); font-size: 0.9rem; font-weight: 500;">+{stats['total_products']} total</div>
                <div style="color: var(--soft-gray); font-size: 0.8rem; margin-top: 0.5rem;">Total products in inventory</div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)

        with col2:
            metric_html = f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">📦</span>
                    <span style="color: var(--primary-green); font-weight: 600; font-size: 1rem;">Pending Orders</span>
                </div>
                <div style="color: var(--secondary-green); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {stats['pending_orders']}
                </div>
                <div style="color: var(--accent-green); font-size: 0.9rem; font-weight: 500;">+{stats['pending_orders']} awaiting</div>
                <div style="color: var(--soft-gray); font-size: 0.8rem; margin-top: 0.5rem;">Orders waiting for fulfillment</div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)

        with col3:
            metric_html = f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🚚</span>
                    <span style="color: var(--primary-green); font-weight: 600; font-size: 1rem;">Active Shipments</span>
                </div>
                <div style="color: var(--secondary-green); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {stats['active_shipments']}
                </div>
                <div style="color: var(--accent-green); font-size: 0.9rem; font-weight: 500;">+{stats['active_shipments']} in transit</div>
                <div style="color: var(--soft-gray); font-size: 0.8rem; margin-top: 0.5rem;">Shipments currently in transit</div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)

        with col4:
            metric_html = f"""
            <div class="metric-card">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">👥</span>
                    <span style="color: var(--primary-green); font-weight: 600; font-size: 1rem;">Customers</span>
                </div>
                <div style="color: var(--secondary-green); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {stats['total_customers']}
                </div>
                <div style="color: var(--accent-green); font-size: 0.9rem; font-weight: 500;">+{stats['total_customers']} served</div>
                <div style="color: var(--soft-gray); font-size: 0.8rem; margin-top: 0.5rem;">Total customers you serve</div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)

        st.divider()

        # Recent Activity Section
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Recent Orders")
            with st.container():
                # Get recent orders from database
                recent_orders = get_farmer_orders()[:5]  # Limit to 5 orders

                if recent_orders:
                    for order in recent_orders:
                        # Generate order number from ID and date
                        order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                        customer_name = order.get('shipping_name', 'Unknown Customer')
                        total_amount = float(order.get('total_amount', 0))

                        with st.expander(f"Order {order_number} - {customer_name}", expanded=False):
                            st.markdown(f"**Status:** {order['status']}")
                            st.markdown(f"**Total:** ₪{total_amount:.2f}")
                            st.markdown(f"**Created:** {order['created_at'][:19].replace('T', ' ')}")
                            st.markdown(f"**Payment:** {order['payment_status']}")

                            # Note: Items would need to be fetched separately or included in API response
                            if order.get('items') and isinstance(order['items'], list):
                                st.markdown(f"**Items:** {len(order['items'])}")
                                for item in order['items']:
                                    st.markdown(f"• {item.get('product_name', 'Unknown Product')} - {item.get('quantity', 0)} × ₪{float(item.get('unit_price', 0)):.2f}")
                            else:
                                st.markdown("**Items:** Details not loaded")
                else:
                    st.info("No recent orders to display")

        with col2:
            st.subheader("⚠️ Low Stock Alerts")
            with st.container():
                # This would show products with low stock
                # For now, show placeholder
                st.info("All products have adequate stock")
                st.caption("Stock alerts will appear here when products run low")

    except Exception as e:
        st.error("Unable to load dashboard data from database.")
        st.caption(f"Error: {str(e)}")

        # Show fallback metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🥕 My Products", "0", help="Database not connected")
        with col2:
            st.metric("📦 Pending Orders", "0", help="Database not connected")
        with col3:
            st.metric("🚚 Active Shipments", "0", help="Database not connected")
        with col4:
            st.metric("👥 Customers", "0", help="Database not connected")

    # Section divider with title
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
            <span style="margin-right: 0.5rem;">⚡</span>
            <span style="color: var(--primary-green); font-weight: 600;">Quick Actions</span>
        </div>
        <div style="flex: 1; height: 3px; background: linear-gradient(90deg, transparent, var(--accent-green), transparent);"></div>
    </div>
    """
    st.markdown(divider_html, unsafe_allow_html=True)

    # Enhanced Quick Actions Section
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        action_html = """
        <div class="quick-action-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">➕</div>
            <h4 style="color: var(--primary-green); margin-bottom: 0.5rem;">Add Product</h4>
            <p style="color: var(--soft-gray); font-size: 0.9rem;">Add new products</p>
        </div>
        """
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("➕ Add New Product", key="quick_add_product", use_container_width=True, type="primary"):
            st.session_state.current_page = "Inventory & Products"
            st.rerun()

    with col2:
        action_html = """
        <div class="quick-action-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📦</div>
            <h4 style="color: var(--primary-green); margin-bottom: 0.5rem;">View Orders</h4>
            <p style="color: var(--soft-gray); font-size: 0.9rem;">Manage orders</p>
        </div>
        """
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("📦 View Orders", key="quick_view_orders", use_container_width=True):
            st.session_state.current_page = "Orders & Fulfillment"
            st.rerun()

    with col3:
        action_html = """
        <div class="quick-action-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🚚</div>
            <h4 style="color: var(--primary-green); margin-bottom: 0.5rem;">Check Shipments</h4>
            <p style="color: var(--soft-gray); font-size: 0.9rem;">Track deliveries</p>
        </div>
        """
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("🚚 Check Shipments", key="quick_check_shipments", use_container_width=True):
            st.session_state.current_page = "Shipments & Logistics"
            st.rerun()

    with col4:
        action_html = """
        <div class="quick-action-card">
            <div style="font-size: 2rem; margin-bottom: 1rem;">👥</div>
            <h4 style="color: var(--primary-green); margin-bottom: 0.5rem;">View Customers</h4>
            <p style="color: var(--soft-gray); font-size: 0.9rem;">Manage customers</p>
        </div>
        """
        st.markdown(action_html, unsafe_allow_html=True)
        if st.button("👥 View Customers", key="quick_view_customers", use_container_width=True):
            st.session_state.current_page = "Customer Relationships"
            st.rerun()

    st.divider()

    # Farm Status Overview
    st.subheader("🏡 Farm Status")

    col1, col2 = st.columns(2)

    with col1:
        st.info("**Farm Profile:** Complete your farm profile to attract more customers")
        if st.button("Update Farm Profile", key="update_profile"):
            st.session_state.current_page = "Farm Profile"
            st.rerun()

    with col2:
        st.success("**Inventory Status:** Your product catalog is ready for orders")
        if st.button("Manage Inventory", key="manage_inventory"):
            st.session_state.current_page = "Inventory & Products"
            st.rerun()