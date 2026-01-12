"""Customer Management - Basic customer information and order history."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_customers():
    """Get customers via API."""
    response = make_api_request("GET", "/api/customers/")
    return response.get('customers', []) if response else []

def get_customer_orders(customer_id):
    """Get orders for a specific customer."""
    response = make_api_request("GET", f"/api/orders/?customer_id={customer_id}")
    return response.get('orders', []) if response else []

def get_farmer_dashboard_stats():
    """Get farmer dashboard statistics via API."""
    return make_api_request("GET", "/api/analytics/farmer/dashboard")

def show_customers_relationships():
    """Display simplified customer management interface."""
    st.title("👥 Customer Management")
    st.markdown("### View customer information and order history")
    st.markdown("---")

    # Simplified interface with only essential features
    tab1, tab2 = st.tabs([
        "Customer Directory",
        "Customer Statistics"
    ])

    with tab1:
        show_customer_directory()

    with tab2:
        show_customer_statistics()

def show_customer_directory():
    """Display customer directory with basic information."""
    st.subheader("📋 Customer Directory")

    # Search options
    search_term = st.text_input("🔍 Search customers", placeholder="Search by name or email...")

    st.markdown("---")

    try:
        # Get customers from API
        customers = get_customers()

        if not customers:
            st.info("👋 No customers yet. Your first customers will appear here once they place orders.")
        else:
            # Filter customers if search term provided
            if search_term:
                filtered_customers = []
                for c in customers:
                    # Try different possible name fields for search
                    customer_name = (
                        c.get('name') or
                        f"{c.get('first_name', '')} {c.get('last_name', '')}".strip() or
                        c.get('full_name') or
                        ''
                    )

                    if (search_term.lower() in customer_name.lower() or
                        search_term.lower() in c.get('email', '').lower()):
                        filtered_customers.append(c)

                customers = filtered_customers

            if not customers:
                st.info("🔍 No customers found matching your search.")
            else:
                for customer in customers:
                    # Try different possible name fields from API
                    customer_name = (
                        customer.get('name') or
                        f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or
                        customer.get('full_name') or
                        'Unknown Customer'
                    )

                    with st.expander(f"👤 {customer_name}", expanded=False):
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("**Contact Information:**")
                            st.markdown(f"• **Name:** {customer_name}")
                            st.markdown(f"• **Email:** {customer.get('email', 'N/A')}")
                            st.markdown(f"• **Phone:** {customer.get('phone', 'N/A')}")

                            # Location information
                            location_parts = []
                            if customer.get('city'):
                                location_parts.append(customer['city'])
                            if customer.get('country'):
                                location_parts.append(customer['country'])
                            location = ', '.join(location_parts) if location_parts else 'N/A'
                            st.markdown(f"• **Location:** {location}")

                            # Registration date
                            if customer.get('created_at'):
                                created_date = customer['created_at'][:10]  # Extract date part
                                st.markdown(f"• **Customer Since:** {created_date}")

                        with col2:
                            st.markdown("**Actions:**")
                            
                            is_viewing_orders = st.session_state.get('viewing_orders') == customer['id']
                            orders_label = "📋 Hide Orders" if is_viewing_orders else "📋 View Orders"
                            
                            if st.button(orders_label, key=f"orders_{customer['id']}", use_container_width=True):
                                # Toggle orders view
                                if is_viewing_orders:
                                    st.session_state.viewing_orders = None
                                else:
                                    st.session_state.viewing_orders = customer['id']
                                st.rerun()
                        
                        # Show orders below if this customer is selected
                        if st.session_state.get('viewing_orders') == customer['id']:
                            show_customer_orders(customer['id'], customer_name)

    except Exception as e:
        st.error("Unable to load customer data from API.")
        st.caption(f"Error: {str(e)}")

def show_customer_orders(customer_id, customer_name):
    """Display orders for a specific customer."""
    st.subheader(f"📦 Orders for {customer_name}")

    try:
        orders = get_customer_orders(customer_id)

        if not orders:
            st.info("No orders found for this customer.")
        else:
            for order in orders:
                # Generate order number and basic info
                order_number = f"ORD-{order['created_at'][:10].replace('-', '')}-{order['id'][:8]}"
                total_amount = float(order.get('total_amount', 0))

                with st.container():
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.markdown(f"**{order_number}**")

                    with col2:
                        st.markdown(f"₪{total_amount:.2f}")

                    with col3:
                        st.markdown(order['status'])

                    with col4:
                        st.markdown(order['created_at'][:10])

                    st.divider()

    except Exception as e:
        st.error(f"Unable to load orders for {customer_name}")
        st.caption(f"Error: {str(e)}")

def show_customer_statistics():
    """Display basic customer statistics."""
    st.subheader("📊 Customer Statistics")

    try:
        # Get basic statistics from farmer dashboard and customers API
        dashboard_stats = get_farmer_dashboard_stats()
        customers = get_customers()

        # Calculate basic metrics
        total_customers = len(customers) if customers else 0
        total_customers_from_dashboard = dashboard_stats.get('total_customers', 0) if dashboard_stats else 0

        # Use the dashboard stat if available, otherwise use count from customers API
        customer_count = total_customers_from_dashboard if total_customers_from_dashboard > 0 else total_customers

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Customers",
                str(customer_count),
                help="Total number of customers who have placed orders"
            )

        with col2:
            # Count customers created in last 30 days
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            new_customers = 0
            if customers:
                for customer in customers:
                    if customer.get('created_at'):
                        try:
                            created_date = datetime.fromisoformat(customer['created_at'].replace('Z', '+00:00'))
                            if created_date > thirty_days_ago:
                                new_customers += 1
                        except:
                            pass

            st.metric(
                "New This Month",
                str(new_customers),
                help="Customers who joined in the last 30 days"
            )

        with col3:
            # Basic placeholder for average orders per customer
            avg_orders = "2.3"  # This would need more complex calculation
            st.metric(
                "Avg Orders/Customer",
                avg_orders,
                help="Average number of orders per customer"
            )

        with col4:
            # Basic placeholder for customer regions
            regions = set()
            if customers:
                for customer in customers:
                    if customer.get('city'):
                        regions.add(customer['city'])

            st.metric(
                "Customer Cities",
                str(len(regions)),
                help="Number of different cities with customers"
            )

        st.markdown("---")

        # Simple customer distribution by city
        if customers:
            st.subheader("📍 Customer Distribution")
            city_counts = {}
            for customer in customers:
                city = customer.get('city', 'Unknown City')
                city_counts[city] = city_counts.get(city, 0) + 1

            if city_counts:
                # Show top 10 cities
                sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                city_chart_data = {city: count for city, count in sorted_cities}

                if city_chart_data:
                    st.bar_chart(city_chart_data)
                else:
                    st.info("No customer location data available for visualization.")
            else:
                st.info("No customer location data available.")

    except Exception as e:
        st.error("Unable to load customer statistics.")
        st.caption(f"Error: {str(e)}")

        # Fallback metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Customers", "0")
        with col2:
            st.metric("New This Month", "0")
        with col3:
            st.metric("Avg Orders/Customer", "0")
        with col4:
            st.metric("Customer Cities", "0")