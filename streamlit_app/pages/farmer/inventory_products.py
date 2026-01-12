"""Inventory & Products - Manage farm products and inventory."""

import streamlit as st
import sys
import os
import pandas as pd

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

def get_farmer_products():
    """Get farmer products via API."""
    response = make_api_request("GET", "/api/products/")
    return response.get('products', []) if response else []

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

def create_product(product_data):
    """Create a new product via API."""
    # Get current user to add farmer_id
    current_user = get_current_user()
    if current_user:
        product_data['farmer_id'] = current_user['id']

    response = make_api_request("POST", "/api/products/", product_data)
    return response['id'] if response else None

def update_product_stock(product_id, quantity_change):
    """Update product stock via API."""
    # quantity_change is passed as query parameter, not JSON body
    return make_api_request("PUT", f"/api/products/{product_id}/stock?quantity_change={quantity_change}")

def show_inventory_products():
    """Display inventory and product management interface."""
    st.title("🥕 Inventory & Products")
    st.markdown("### Manage your product catalog and inventory levels")
    st.markdown("---")

    # Tabs for different inventory functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Product Catalog",
        "Add New Product",
        "Stock Management",
        "Low Stock Alerts"
    ])

    with tab1:
        show_product_catalog()

    with tab2:
        show_add_product_form()

    with tab3:
        show_stock_management()

    with tab4:
        show_low_stock_alerts()

def show_product_catalog():
    """Display current product catalog."""
    st.subheader("📋 Your Product Catalog")

    # Search and filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("🔍 Search products", placeholder="Search by name...")

    with col2:
        category_filter = st.selectbox(
            "Filter by category",
            ["All Categories", "Vegetables", "Fruits", "Herbs", "Grains", "Other"]
        )

    with col3:
        status_filter = st.selectbox(
            "Filter by status",
            ["All Products", "In Stock", "Low Stock", "Out of Stock"]
        )

    # Refresh button
    if st.button("🔄 Refresh Product List"):
        st.success("Product list refreshed!")

    st.markdown("---")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get farmer's products from database
        products = get_farmer_products()

        if not products:
            st.info("📦 No products found. Add your first product using the 'Add New Product' tab.")
        else:
            # Apply filters
            filtered_products = products

            # Filter by search term
            if search_term:
                filtered_products = [p for p in filtered_products if search_term.lower() in p['name'].lower()]

            # Filter by category
            if category_filter != "All Categories":
                filtered_products = [p for p in filtered_products if p['category'] == category_filter]

            # Filter by status
            if status_filter == "In Stock":
                filtered_products = [p for p in filtered_products if float(p['stock_quantity']) > 0]
            elif status_filter == "Low Stock":
                filtered_products = [p for p in filtered_products if 0 < float(p['stock_quantity']) <= 10]
            elif status_filter == "Out of Stock":
                filtered_products = [p for p in filtered_products if float(p['stock_quantity']) <= 0]

            if not filtered_products:
                st.info(f"No products match your current filters.")
            else:
                # Display products
                for product in filtered_products:
                    # Determine stock status
                    stock_quantity = float(product['stock_quantity'])
                    price_per_unit = float(product['price_per_unit'])
                    unit_label = product['unit_label']

                    stock_status = "✅ In Stock"
                    if stock_quantity <= 0:
                        stock_status = "❌ Out of Stock"
                    elif stock_quantity <= 10:
                        stock_status = "⚠️ Low Stock"

                    with st.expander(f"🥕 {product['name']} - ₪{price_per_unit:.2f}/{unit_label} - {stock_status}"):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Current Stock", f"{stock_quantity:.1f} {unit_label}")

                        with col2:
                            st.metric("Price", f"₪{price_per_unit:.2f}/{unit_label}")

                        with col3:
                            st.metric("Category", product['category'])
                            if product.get('is_organic'):
                                st.markdown("🌱 **Organic**")

                        with col4:
                            st.markdown("**Actions**")
                            if st.button("✏️ Edit", key=f"edit_{product['id']}"):
                                st.session_state.editing_product = product['id']
                                st.info("Product editing would open here")

                        # Product description
                        if product.get('description'):
                            st.markdown(f"**Description:** {product['description']}")

                        # Stock level indicator
                        stock_percentage = min(100, (stock_quantity / 50) * 100)  # Assuming 50 is max display
                        st.progress(stock_percentage / 100)

    except Exception as e:
        st.error("Unable to load products from database.")
        st.caption(f"Error: {str(e)}")
        st.info("📦 Products will appear here once connected to the database.")

def show_add_product_form():
    """Display form to add new products."""
    st.subheader("➕ Add New Product")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            product_name = st.text_input(
                "Product Name *",
                placeholder="e.g., Organic Tomatoes",
                help="The name customers will see"
            )

            category = st.selectbox(
                "Category *",
                ["Vegetables", "Fruits", "Herbs", "Grains", "Dairy", "Other"],
                help="Product category for organization"
            )

            price = st.number_input(
                "Price per Unit *",
                min_value=0.01,
                max_value=1000.00,
                value=1.00,
                step=0.01,
                help="Price in dollars"
            )

            unit = st.selectbox(
                "Unit of Measure *",
                ["lb", "kg", "oz", "g", "each", "dozen", "bunch", "bag"],
                help="How the product is sold"
            )

        with col2:
            current_stock = st.number_input(
                "Current Stock Quantity *",
                min_value=0,
                value=0,
                help="Current available quantity"
            )

            min_stock_level = st.number_input(
                "Minimum Stock Level",
                min_value=0,
                value=5,
                help="Alert threshold for low stock"
            )

            harvest_season = st.multiselect(
                "Harvest Season",
                ["Spring", "Summer", "Fall", "Winter", "Year-round"],
                default=["Summer"],
                help="When this product is typically available"
            )

            organic = st.checkbox(
                "Organic Product",
                help="Check if this is an organic product"
            )

        description = st.text_area(
            "Product Description",
            placeholder="Describe your product, growing methods, taste, best uses, etc...",
            height=100,
            help="Detailed description for customers"
        )


        submitted = st.form_submit_button("💾 Add Product", type="primary")

        if submitted:
            if product_name and category and price > 0 and current_stock >= 0:
                try:
                    # Get current user (farmer)
                    current_user = get_current_user()
                    farmer_id = current_user.get('id') if current_user else None

                    if farmer_id:
                        # Prepare product data
                        product_data = {
                            'name': product_name,
                            'description': description,
                            'category': category,
                            'unit_label': unit,
                            'price_per_unit': price,
                            'stock_quantity': current_stock,
                            'is_organic': organic,
                            'is_active': True
                        }

                        # Create the product
                        product_id = create_product(product_data)
                        if product_id:
                            st.success(f"✅ {product_name} added to your catalog successfully!")
                            st.info("Switch to the 'Product Catalog' tab to see your new product.")
                        else:
                            st.error("❌ Failed to add product. Please try again.")
                    else:
                        st.error("❌ Please log in as a farmer to add products.")

                except Exception as e:
                    st.error(f"❌ Error adding product: {str(e)}")
            else:
                st.error("❌ Please fill in all required fields")

def show_stock_management():
    """Display stock management interface."""
    st.subheader("📦 Stock Management")

    st.markdown("**Quick Stock Updates**")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get farmer's products from database
        products = get_farmer_products()

        if not products:
            st.info("No products available. Add products first in the 'Add New Product' tab.")
        else:
            for i, product in enumerate(products):
                stock_quantity = float(product['stock_quantity'])
                unit_label = product['unit_label']

                with st.expander(f"📦 {product['name']} - Current: {stock_quantity:.1f} {unit_label}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        new_stock = st.number_input(
                            "New Stock Level",
                            min_value=0.0,
                            value=stock_quantity,
                            step=0.1,
                            key=f"stock_{i}"
                        )

                    with col2:
                        adjustment = st.number_input(
                            "Add (+) or Remove (-) Stock",
                            value=0.0,
                            step=0.5,
                            key=f"adjustment_{i}",
                            help="Add or subtract from current stock"
                        )

                    with col3:
                        st.markdown("**Actions**")
                        if st.button(f"Update Stock", key=f"update_{i}", type="primary"):
                            final_stock = new_stock + adjustment
                            # API expects quantity_change (delta), not absolute value
                            quantity_change = final_stock - stock_quantity
                            try:
                                if update_product_stock(product['id'], quantity_change):
                                    st.success(f"Stock updated to {final_stock:.1f} {unit_label}")
                                    st.rerun()
                                else:
                                    st.error("Failed to update stock. Please try again.")
                            except Exception as e:
                                st.error(f"Error updating stock: {str(e)}")

                    # Stock status
                    stock_status = "✅ Good"
                    if stock_quantity <= 0:
                        stock_status = "❌ Out of Stock"
                    elif stock_quantity <= 10:
                        stock_status = "⚠️ Low Stock"

                    st.markdown(f"**Current Status:** {stock_status}")

    except Exception as e:
        st.error("Unable to load products for stock management.")
        st.caption(f"Error: {str(e)}")

def show_low_stock_alerts():
    """Display low stock alerts and management."""
    st.subheader("⚠️ Low Stock Alerts")

    try:
        # Get current user (farmer)
        current_user = get_current_user()
        farmer_id = current_user.get('id') if current_user else None

        # Get farmer's products from database
        products = get_farmer_products()

        # Filter for low stock items (less than or equal to 10)
        low_stock_items = [p for p in products if float(p['stock_quantity']) <= 10]

        if not low_stock_items:
            st.success("🎉 All products have adequate stock levels!")
        else:
            st.warning(f"⚠️ {len(low_stock_items)} products are running low on stock")

            for item in low_stock_items:
                stock_quantity = float(item['stock_quantity'])
                unit_label = item['unit_label']

                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.markdown(f"**{item['name']}**")
                        st.markdown(f"Current: {stock_quantity:.1f} {unit_label} | Category: {item['category']}")

                    with col2:
                        urgency = "🔴 Critical" if stock_quantity <= 2 else "🟡 Low"
                        st.markdown(f"**Status:** {urgency}")

                    with col3:
                        if st.button(f"Restock", key=f"restock_{item['id']}", type="primary"):
                            st.success(f"Restock reminder set for {item['name']}")

                    st.divider()

    except Exception as e:
        st.error("Unable to load low stock alerts.")
        st.caption(f"Error: {str(e)}")
        st.info("⚠️ Low stock alerts will appear here once connected to the database.")

    # Alert Settings
    st.markdown("---")
    st.subheader("🔔 Alert Settings")

    col1, col2 = st.columns(2)

    with col1:
        email_alerts = st.checkbox(
            "Email notifications for low stock",
            value=True,
            help="Receive email alerts when products are running low"
        )

    with col2:
        alert_threshold = st.slider(
            "Default alert threshold (%)",
            min_value=10,
            max_value=50,
            value=20,
            help="Alert when stock falls below this percentage of minimum level"
        )

    if st.button("💾 Save Alert Settings"):
        st.success("Alert settings saved!")