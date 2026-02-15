"""Orders & Fulfillment - Manage customer orders and fulfillment process."""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

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

def update_order_status(order_id, new_status):
    """Update order status via API."""
    return make_api_request("PUT", f"/api/orders/{order_id}", {"status": new_status})

def get_order_analytics():
    """Get order analytics via API."""
    response = make_api_request("GET", "/api/analytics/orders")
    return response if response else {
        'orders_this_month': 0,
        'avg_order_value': 0,
        'fulfillment_rate': 0,
        'customer_satisfaction': 4.8
    }

def get_farmer_dashboard_stats():
    """Get farmer dashboard statistics via API."""
    return make_api_request("GET", "/api/analytics/farmer/dashboard")

def show_orders_fulfillment():
    """Display orders and fulfillment management interface."""
    st.title("📦 Orders & Fulfillment")
    st.markdown("### Manage customer orders and fulfillment workflow")
    st.markdown("---")

    # Tabs for different order functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Pending Orders",
        "Order History",
        "Fulfillment Workflow",
        "Order Analytics"
    ])

    with tab1:
        show_pending_orders()

    with tab2:
        show_order_history()

    with tab3:
        show_fulfillment_workflow()

    with tab4:
        show_order_analytics()

def show_pending_orders():
    """Display pending orders that need attention."""
    st.subheader("⏳ Orders Requiring Attention")

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All Pending", "Payment Pending", "Paid - Ready to Fulfill", "In Progress"]
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["All Orders", "Rush Orders", "Regular Orders"]
        )

    with col3:
        date_filter = st.selectbox(
            "Order Date",
            ["All Dates", "Today", "This Week", "Overdue"]
        )

    st.markdown("---")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get pending orders from API
        pending_orders = []
        paid_orders = get_farmer_orders('PAID')
        pending_orders.extend(paid_orders)
        payment_pending_orders = get_farmer_orders('PENDING_PAYMENT')
        pending_orders.extend(payment_pending_orders)

        if not pending_orders:
            st.success("🎉 No pending orders! All caught up.")
        else:
            for order in pending_orders:
                # Generate order number from ID and date (same as dashboard)
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                customer_name = order.get('shipping_name', 'Unknown Customer')
                total_amount = float(order.get('total_amount', 0))

                # Format order items for display
                items_text = "Items not loaded"
                if order.get('items') and isinstance(order['items'], list):
                    items_text = ", ".join([f"{item.get('product_name', 'Unknown')} ({float(item.get('quantity', 0)):.1f})"
                                          for item in order['items']])

                # Determine status display
                status_display = "Paid - Ready to Fulfill" if order['status'] == 'PAID' else "Payment Pending"

                # Determine priority (rush if created today)
                try:
                    order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')).date() if order.get('created_at') else None
                    is_rush = order_date == datetime.now().date() if order_date else False
                except:
                    is_rush = False
                priority = "Rush" if is_rush else "Regular"

                with st.expander(f"📋 {order_number} - {customer_name} - ₪{total_amount:.2f}", expanded=True):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Customer:** {customer_name}")
                        st.markdown(f"**Items:** {items_text}")
                        try:
                            order_date_str = order['created_at'][:10] if order.get('created_at') else 'N/A'
                        except:
                            order_date_str = 'N/A'
                        st.markdown(f"**Order Date:** {order_date_str}")
                        st.markdown(f"**Status:** {status_display}")

                        if priority == 'Rush':
                            st.error("🚨 RUSH ORDER - High Priority")

                    with col2:
                        st.markdown("**Actions:**")

                        if order['status'] == "PAID":
                            if st.button(f"✅ Start Fulfillment", key=f"fulfill_{order['id']}", type="primary"):
                                if update_order_status(order['id'], 'FULFILLED'):
                                    st.success(f"Order {order_number} moved to fulfillment!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update order status.")

                            if st.button(f"📋 View Details", key=f"details_{order['id']}"):
                                show_order_details(order, order_number, customer_name, total_amount)

                        elif order['status'] == "PENDING_PAYMENT":
                            if st.button(f"💰 Payment Reminder", key=f"remind_{order['id']}"):
                                st.info(f"Payment reminder sent to {customer_name}")

                            if st.button(f"❌ Cancel Order", key=f"cancel_{order['id']}"):
                                if update_order_status(order['id'], 'CANCELLED'):
                                    st.warning(f"Order {order_number} cancelled")
                                    st.rerun()
                                else:
                                    st.error("Failed to cancel order.")

    except Exception as e:
        st.error("Unable to load pending orders.")
        st.caption(f"Error: {str(e)}")
        st.info("📦 Pending orders will appear here once connected to the database.")

def show_order_history():
    """Display order history and completed orders."""
    st.subheader("📚 Order History")

    # Date range selector
    col1, col2 = st.columns(2)

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

    # Status filter
    history_status = st.selectbox(
        "Order Status",
        ["All Orders", "Completed", "Cancelled", "Refunded"]
    )

    if st.button("🔍 Search Orders"):
        st.success("Searching orders...")

    st.markdown("---")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get completed orders from API
        completed_orders = get_farmer_orders('FULFILLED')

        if not completed_orders:
            st.info("📋 No completed orders found in the selected date range.")
        else:
            st.markdown("**Recent Completed Orders:**")

            for order in completed_orders:
                # Generate order number and customer name (same as other places)
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                customer_name = order.get('shipping_name', 'Unknown Customer')
                total_amount = float(order.get('total_amount', 0))

                with st.container():
                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        st.markdown(f"**{order_number}**")

                    with col2:
                        st.markdown(customer_name)

                    with col3:
                        st.markdown(f"₪{total_amount:.2f}")

                    with col4:
                        try:
                            order_date_str = order['created_at'][:10] if order.get('created_at') else 'N/A'
                        except:
                            order_date_str = 'N/A'
                        st.markdown(order_date_str)

                    with col5:
                        status_color = "🟢"
                        st.markdown(f"{status_color} Delivered")

                    st.divider()

    except Exception as e:
        st.error("Unable to load order history.")
        st.caption(f"Error: {str(e)}")
        st.info("📚 Order history will appear here once connected to the database.")

def show_fulfillment_workflow():
    """Display fulfillment workflow management."""
    st.subheader("🔄 Fulfillment Workflow")

    # Workflow stages
    st.markdown("**Order Fulfillment Pipeline:**")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get workflow statistics from dashboard stats and real order counts
        dashboard_stats = get_farmer_dashboard_stats()
        if dashboard_stats:
            stats = {
                'pending': dashboard_stats.get('pending_orders', 0),
                'preparing': dashboard_stats.get('orders_in_preparation', 0),
                'packaging': dashboard_stats.get('orders_packaging', 0),
                'ready_to_ship': dashboard_stats.get('active_shipments', 0)
            }
        else:
            # Get real order counts by status
            paid_orders = get_farmer_orders('PAID')
            pending_orders = get_farmer_orders('PENDING_PAYMENT')
            stats = {
                'pending': len(pending_orders) if pending_orders else 0,
                'preparing': len(paid_orders) if paid_orders else 0,
                'packaging': 0,
                'ready_to_ship': 0
            }

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**📋 Order Received**")
            st.metric("Count", str(stats['pending']))
            st.markdown("• Order verification")
            st.markdown("• Inventory check")

        with col2:
            st.markdown("**📦 Preparing**")
            st.metric("Count", str(stats['preparing']))
            st.markdown("• Pick products")
            st.markdown("• Quality check")

        with col3:
            st.markdown("**📮 Packaging**")
            st.metric("Count", str(stats['packaging']))
            st.markdown("• Package items")
            st.markdown("• Add labels")

        with col4:
            st.markdown("**🚚 Ready to Ship**")
            st.metric("Count", str(stats['ready_to_ship']))
            st.markdown("• Generate shipping label")
            st.markdown("• Schedule pickup")

    except Exception as e:
        st.error("Unable to load workflow statistics.")
        st.caption(f"Error: {str(e)}")

    st.markdown("---")

    # Active fulfillment tasks
    st.subheader("📋 Active Fulfillment Tasks")

    try:
        # Get paid orders that need fulfillment tasks
        paid_orders = get_farmer_orders('PAID')

        if not paid_orders:
            st.info("📋 No active fulfillment tasks. All orders are up to date!")
        else:
            for i, order in enumerate(paid_orders[:3]):  # Show first 3 orders
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                customer_name = order.get('shipping_name', 'Unknown Customer')

                # Determine priority based on order date
                try:
                    order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')).date() if order.get('created_at') else None
                    is_rush = order_date == datetime.now().date() if order_date else False
                except:
                    is_rush = False

                priority = "High" if is_rush else "Medium"
                task_description = f"Fulfill order for {customer_name}"

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{order_number}:** {task_description}")

                with col2:
                    priority_color = "🔴" if priority == "High" else "🟡"
                    st.markdown(f"{priority_color} {priority}")

                with col3:
                    if st.button(f"✅ Complete", key=f"complete_task_{i}", type="primary"):
                        if update_order_status(order['id'], 'FULFILLED'):
                            st.success(f"Order {order_number} fulfilled!")
                            st.rerun()
                        else:
                            st.error("Failed to update order status.")

    except Exception as e:
        st.error("Unable to load fulfillment tasks.")
        st.caption(f"Error: {str(e)}")

def show_order_analytics():
    """Display order analytics and insights."""
    st.subheader("📊 Order Analytics")

    # Summary metrics
    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get analytics data
        analytics = get_order_analytics() if farmer_id else {
            'orders_this_month': 0,
            'avg_order_value': 0,
            'fulfillment_rate': 0,
            'customer_satisfaction': 4.8
        }

        # Convert to numbers (API might return strings)
        orders_this_month = int(analytics.get('orders_this_month', 0) or 0)
        avg_order_value = float(analytics.get('avg_order_value', 0) or 0)
        fulfillment_rate = float(analytics.get('fulfillment_rate', 0) or 0)
        customer_satisfaction = float(analytics.get('customer_satisfaction', 4.8) or 4.8)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Orders This Month",
                str(orders_this_month),
                help="Total orders received this month"
            )

        with col2:
            st.metric(
                "Average Order Value",
                f"₪{avg_order_value:.2f}",
                help="Average value per order"
            )

        with col3:
            st.metric(
                "Fulfillment Rate",
                f"{fulfillment_rate:.1f}%",
                help="Percentage of orders fulfilled on time"
            )

        with col4:
            st.metric(
                "Customer Satisfaction",
                f"{customer_satisfaction:.1f}/5",
                help="Average customer rating"
            )

    except Exception as e:
        st.error("Unable to load analytics data.")
        st.caption(f"Error: {str(e)}")

    st.divider()

    # Charts section with basic visualizations
    st.subheader("📊 Analytics Dashboard")

    # Create basic charts using available data
    col1, col2 = st.columns(2)

    with col1:
        # Order fulfillment status chart
        st.markdown("**📈 Order Status Overview**")
        try:
            # Get order counts by status
            paid_orders = get_farmer_orders('PAID') or []
            pending_orders = get_farmer_orders('PENDING_PAYMENT') or []
            fulfilled_orders = get_farmer_orders('FULFILLED') or []

            status_data = {
                'Status': ['Pending Payment', 'Paid', 'Fulfilled'],
                'Count': [len(pending_orders), len(paid_orders), len(fulfilled_orders)]
            }

            if any(status_data['Count']):  # Only show if there's data
                st.bar_chart(status_data, x='Status', y='Count')
            else:
                st.info("No order data available for chart")

        except Exception as e:
            st.error(f"Unable to load order status chart: {str(e)}")

    with col2:
        # Monthly performance metrics
        st.markdown("**📊 Key Performance Metrics**")
        try:
            # Convert analytics values to numbers (API might return strings)
            chart_orders = int(analytics.get('orders_this_month', 0) or 0)
            chart_avg_value = float(analytics.get('avg_order_value', 0) or 0)
            chart_fulfillment = float(analytics.get('fulfillment_rate', 0) or 0)
            chart_satisfaction = float(analytics.get('customer_satisfaction', 0) or 0)
            
            # Create a simple metrics visualization
            metrics_data = {
                'Metric': ['Orders', 'Avg Value (₪)', 'Fulfillment %', 'Satisfaction'],
                'Value': [
                    chart_orders,
                    chart_avg_value,
                    chart_fulfillment,
                    chart_satisfaction * 20  # Scale to make visible
                ]
            }

            if any(metrics_data['Value']):  # Only show if there's data
                st.bar_chart(metrics_data, x='Metric', y='Value')
            else:
                st.info("No analytics data available for chart")

        except Exception as e:
            st.error(f"Unable to load metrics chart: {str(e)}")

    # Order value trends (simulated data based on current orders)
    st.markdown("**💰 Recent Order Values**")
    try:
        # Get recent orders for trend analysis
        recent_orders = []
        for status in ['PAID', 'FULFILLED', 'PENDING_PAYMENT']:
            orders = get_farmer_orders(status) or []
            recent_orders.extend(orders)

        if recent_orders:
            # Sort by date and take last 10 orders
            recent_orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            recent_orders = recent_orders[:10]

            # Create trend data
            order_values = []
            order_dates = []

            for i, order in enumerate(reversed(recent_orders)):  # Show oldest to newest
                try:
                    total_amount = float(order.get('total_amount', 0))
                    order_values.append(total_amount)
                    # Use order index as x-axis since dates might be complex to parse
                    order_dates.append(f"Order {i+1}")
                except:
                    continue

            if order_values:
                trend_data = {
                    'Order': order_dates,
                    'Value (₪)': order_values
                }
                st.line_chart(trend_data, x='Order', y='Value (₪)')
            else:
                st.info("No recent order data available for trend chart")
        else:
            st.info("No recent orders available for trend analysis")

    except Exception as e:
        st.error(f"Unable to load order trends: {str(e)}")
        st.info("Order trend chart will be available when order data is loaded")

def show_order_details(order, order_number, customer_name, total_amount):
    """Show detailed order information."""
    st.info(f"📋 **Order Details: {order_number}**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Customer Information:**")
        st.markdown(f"• Name: {customer_name}")
        st.markdown(f"• Phone: {order.get('shipping_phone', 'N/A')}")
        st.markdown(f"• Email: {order.get('customer_email', 'N/A')}")

    with col2:
        st.markdown("**Order Information:**")
        st.markdown(f"• Status: {order['status']}")
        st.markdown(f"• Payment: {order['payment_status']}")
        st.markdown(f"• Total: ₪{total_amount:.2f}")

    st.markdown("**Delivery Address:**")
    st.markdown(f"{order.get('shipping_address1', 'N/A')}")
    st.markdown(f"{order.get('shipping_city', 'N/A')}, {order.get('shipping_postal_code', 'N/A')}")

    if order.get('items') and isinstance(order['items'], list):
        st.markdown("**Order Items:**")
        for item in order['items']:
            product_name = item.get('product_name', 'Unknown Product')
            quantity = float(item.get('quantity', 0))
            unit_price = float(item.get('unit_price', 0))
            st.markdown(f"• {product_name} - {quantity:.1f} @ ₪{unit_price:.2f}")
    else:
        st.markdown("**Order Items:** Items not loaded")

    if order.get('customer_notes'):
        st.markdown("**Customer Notes:**")
        st.markdown(order['customer_notes'])