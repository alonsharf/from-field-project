"""Main Streamlit application for From Field to You - Single Farmer Admin System."""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized API client
from packages.api_client import make_api_request

# Authentication functions
def authenticate_farmer(email: str, password: str):
    """Authenticate farmer via API."""
    # Normalize email: trim whitespace and convert to lowercase
    clean_email = email.strip().lower() if email else ""
    clean_password = password.strip() if password else ""
    
    response = make_api_request("POST", "/api/auth/farmer/login", {
        "email": clean_email,
        "password": clean_password
    })
    return response

def authenticate_customer(email: str, password: str):
    """Authenticate customer via API."""
    # Normalize email: trim whitespace and convert to lowercase
    clean_email = email.strip().lower() if email else ""
    clean_password = password.strip() if password else ""
    
    response = make_api_request("POST", "/api/auth/customer/login", {
        "email": clean_email,
        "password": clean_password
    })
    return response

def register_customer(first_name: str, last_name: str, email: str, password: str,
                     phone: str = None, address_data: dict = None):
    """Register new customer via API."""
    # Normalize inputs: trim whitespace, lowercase email
    clean_email = email.strip().lower() if email else ""
    clean_password = password.strip() if password else ""
    clean_first_name = first_name.strip() if first_name else ""
    clean_last_name = last_name.strip() if last_name else ""
    clean_phone = phone.strip() if phone else None
    
    register_data = {
        "first_name": clean_first_name,
        "last_name": clean_last_name,
        "email": clean_email,
        "password": clean_password,
        "phone": clean_phone,
    }

    if address_data:
        register_data.update({
            "address_line1": address_data.get('line1'),
            "address_line2": address_data.get('line2'),
            "city": address_data.get('city'),
            "postal_code": address_data.get('postal_code'),
            "country": address_data.get('country', 'Israel')
        })

    response = make_api_request("POST", "/api/auth/customer/register", register_data)
    return response['id'] if response else None

# Session management functions
def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.get('user_role') is not None

def get_current_user():
    """Get current user info from session state."""
    if is_authenticated():
        return {
            'role': st.session_state.user_role,
            'id': st.session_state.user_id,
            'name': st.session_state.user_name,
            'email': st.session_state.get('user_email'),
            'farm_name': st.session_state.get('farm_name'),
            'first_name': st.session_state.get('first_name'),
            'last_name': st.session_state.get('last_name')
        }
    return None

def login_user(user_data):
    """Login user and store in session state."""
    st.session_state.user_role = user_data['role']
    st.session_state.user_id = user_data['id']
    st.session_state.user_name = user_data['name']
    st.session_state.user_email = user_data['email']

    # Store role-specific data
    if user_data['role'] == 'farmer':
        st.session_state.farm_name = user_data.get('farm_name')
    elif user_data['role'] == 'customer':
        st.session_state.first_name = user_data.get('first_name')
        st.session_state.last_name = user_data.get('last_name')

def logout_user():
    """Logout user and clear session state."""
    keys_to_clear = ['user_role', 'user_id', 'user_name', 'user_email',
                     'farm_name', 'first_name', 'last_name', 'current_page',
                     'show_admin_access', 'active_tab']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Import portal modules (fixed to use API)
from pages.farmer.farmer_dashboard import show_farmer_dashboard
from pages.farmer.inventory_products import show_inventory_products
from pages.farmer.farm_profile import show_farm_profile
from pages.farmer.orders_fulfillment import show_orders_fulfillment
from pages.farmer.shipments_logistics import show_shipments_logistics
from pages.farmer.customers_relationships import show_customers_relationships

from pages.customer.storefront_home import show_storefront_home
from pages.customer.browse_products import show_browse_products
from pages.customer.cart_checkout import show_cart_checkout, show_checkout_only
from pages.customer.orders_shipments import show_customer_orders_shipments
from pages.customer.customer_profile import show_customer_profile

# Set page config
st.set_page_config(
    page_title="From Field to You",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS for agricultural theme
def load_custom_css():
    """Load custom CSS styling for agricultural theme."""
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'styles', 'agricultural_theme.css')
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            return True
        else:
            return False
    except Exception:
        return False

def initialize_session_state():
    """Initialize session state variables."""
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None

def show_login_page():
    """Display login page with authentication."""
    # Load custom CSS
    load_custom_css()

    # Enhanced agricultural header
    header_html = """
    <div class="agricultural-header">
        <h1>🌱 From Field to You</h1>
        <p>Agricultural Supply Chain Management System</p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Initialize admin access visibility in session state
    if 'show_admin_access' not in st.session_state:
        st.session_state.show_admin_access = False
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

    # Create tabs for Login and Registration
    tab_list = ["🛒 Customer Login", "📝 Register New Account"]
    tab_content = ["customer_login", "customer_register"]

    # Add admin tab if it should be visible (always at the end)
    if st.session_state.show_admin_access:
        tab_list.append("🔐 Administrative Access")
        tab_content.append("admin_login")

    # Reorder tabs to show the active tab first if it's admin
    if st.session_state.show_admin_access and st.session_state.active_tab == 2:
        # Put admin tab first to auto-select it, but keep customer/register in original order
        tab_list = ["🛒 Customer Login", "📝 Register New Account", "🔐 Administrative Access"]
        tab_content = ["customer_login", "customer_register", "admin_login"]

    tabs = st.tabs(tab_list)

    # Render tab content based on the current tab order
    for i, content_type in enumerate(tab_content):
        with tabs[i]:
            if content_type == "customer_login":
                st.header("Customer Login")

                with st.form("customer_login"):
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col2:
                        email = st.text_input("Email", placeholder="customer@example.com", key="customer_email")
                        password = st.text_input("Password", type="password", placeholder="Enter your password", key="customer_password")
                        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

                    if submitted:
                        if email and password:
                            user_data = authenticate_customer(email, password)
                            if user_data:
                                login_user(user_data)
                                st.session_state.current_page = "Storefront Home"
                                st.success(f"Welcome back, {user_data['name']}!")
                                st.rerun()
                            else:
                                st.error("Invalid email or password")
                        else:
                            st.error("Please enter both email and password")

            elif content_type == "customer_register":
                st.header("Register New Customer Account")
                st.markdown("Create a new account to start shopping from our farm.")

                with st.form("customer_register"):
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name", placeholder="John")
                    with col2:
                        last_name = st.text_input("Last Name", placeholder="Doe")

                    email = st.text_input("Email", placeholder="john.doe@example.com", key="register_email")
                    phone = st.text_input("Phone (Optional)", placeholder="+972-50-123-4567")

                    col1, col2 = st.columns(2)
                    with col1:
                        password = st.text_input("Password", type="password", placeholder="Choose a strong password", key="register_password")
                    with col2:
                        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")

                    # Address fields
                    st.subheader("Delivery Address")
                    address_line1 = st.text_input("Address Line 1", placeholder="123 Main Street")
                    address_line2 = st.text_input("Address Line 2 (Optional)", placeholder="Apt 4B")

                    col1, col2 = st.columns(2)
                    with col1:
                        city = st.text_input("City", placeholder="Tel Aviv")
                    with col2:
                        postal_code = st.text_input("Postal Code", placeholder="12345")

                    submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                    if submitted:
                        # Validation
                        if not all([first_name, last_name, email, password, confirm_password]):
                            st.error("Please fill in all required fields")
                        elif password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long")
                        else:
                            # Prepare address data
                            address_data = None
                            if address_line1 or city:
                                address_data = {
                                    'line1': address_line1,
                                    'line2': address_line2,
                                    'city': city,
                                    'postal_code': postal_code,
                                    'country': 'Israel'
                                }

                            # Register customer
                            customer_id = register_customer(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                password=password,
                                phone=phone,
                                address_data=address_data
                            )

                            if customer_id:
                                st.success("Account created successfully! Please login with your new credentials.")
                                st.balloons()
                            else:
                                st.error("Registration failed. Email may already exist.")

            elif content_type == "admin_login":
                st.header("Farm Admin Login")

                with st.form("admin_login"):
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col2:
                        email = st.text_input("Admin Email", placeholder="admin@farm.com")
                        password = st.text_input("Admin Password", type="password", placeholder="Enter your password")
                        submitted = st.form_submit_button("Login as Admin", type="primary", use_container_width=True)

                    if submitted:
                        if email and password:
                            user_data = authenticate_farmer(email, password)
                            if user_data:
                                login_user(user_data)
                                st.session_state.current_page = "Farmer Dashboard"
                                st.success(f"Welcome back, {user_data['name']}!")
                                st.rerun()
                            else:
                                st.error("Invalid email or password")
                        else:
                            st.error("Please enter both email and password")

    # Button to toggle admin access visibility
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if not st.session_state.show_admin_access:
            if st.button("🔐 Administrative Access", use_container_width=True, type="secondary"):
                st.session_state.show_admin_access = True
                st.session_state.active_tab = 2  # Set active tab to admin
                st.rerun()
        else:
            if st.button("🔒 Hide Admin Access", use_container_width=True, type="secondary"):
                st.session_state.show_admin_access = False
                st.session_state.active_tab = 0  # Reset to customer login tab
                st.rerun()

def show_farmer_portal():
    """Display farmer portal with navigation."""
    # Load custom CSS
    load_custom_css()

    # Sidebar navigation for farmer
    with st.sidebar:
        st.markdown("# 👨‍🌾 Farmer Portal")
        farmer_name = st.session_state.get('user_name', 'Farmer')
        st.markdown(f"Welcome, {farmer_name}!")
        st.markdown("---")

        # Navigation menu items for farmer
        farmer_pages = [
            ("Farmer Dashboard", "📊"),
            ("Farm Profile", "🏡"),
            ("Inventory & Products", "🥕"),
            ("Orders & Fulfillment", "📦"),
            ("Shipments & Logistics", "🚚"),
            ("Customer Relationships", "👥")
        ]

        for page_name, icon in farmer_pages:
            if st.button(f"{icon} {page_name}", key=f"farmer_{page_name}", use_container_width=True,
                        type="primary" if st.session_state.current_page == page_name else "secondary"):
                st.session_state.current_page = page_name
                st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

    # Display selected farmer page
    if st.session_state.current_page == "Farmer Dashboard":
        show_farmer_dashboard()
    elif st.session_state.current_page == "Inventory & Products":
        show_inventory_products()
    elif st.session_state.current_page == "Farm Profile":
        show_farm_profile()
    elif st.session_state.current_page == "Orders & Fulfillment":
        show_orders_fulfillment()
    elif st.session_state.current_page == "Shipments & Logistics":
        show_shipments_logistics()
    elif st.session_state.current_page == "Customer Relationships":
        show_customers_relationships()
    else:
        # Default to dashboard if no page is selected
        st.session_state.current_page = "Farmer Dashboard"
        st.rerun()

def show_customer_portal():
    """Display customer portal with navigation."""
    # Load custom CSS
    load_custom_css()

    # Sidebar navigation for customer
    with st.sidebar:
        st.markdown("# 🛒 Customer Portal")
        customer_name = st.session_state.get('user_name', 'Customer')
        st.markdown(f"Welcome, {customer_name}!")
        st.markdown("---")

        # Navigation menu items for customer
        customer_pages = [
            ("Storefront Home", "🏠"),
            ("Browse Products", "🔍"),
            ("My Cart & Checkout", "🛒"),
            ("My Orders & Shipments", "📦"),
            ("My Profile", "👤")
        ]

        for page_name, icon in customer_pages:
            if st.button(f"{icon} {page_name}", key=f"customer_{page_name}", use_container_width=True,
                        type="primary" if st.session_state.current_page == page_name else "secondary"):
                st.session_state.current_page = page_name
                st.rerun()

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

    # Display selected customer page
    if st.session_state.current_page == "Storefront Home":
        show_storefront_home()
    elif st.session_state.current_page == "Browse Products":
        show_browse_products()
    elif st.session_state.current_page == "My Cart & Checkout":
        show_cart_checkout()
    elif st.session_state.current_page == "Checkout Process":
        show_checkout_only()
    elif st.session_state.current_page == "My Orders & Shipments":
        show_customer_orders_shipments()
    elif st.session_state.current_page == "My Profile":
        show_customer_profile()
    else:
        # Default to storefront home if no page is selected
        st.session_state.current_page = "Storefront Home"
        st.rerun()

def main():
    """Main application entry point."""
    initialize_session_state()

    # Check for PayPal callback URLs first
    query_params = st.experimental_get_query_params()
    if "paymentId" in query_params and "PayerID" in query_params:
        # PayPal success callback
        from streamlit_app.pages.customer.payment_success import show_payment_success
        show_payment_success()
        return
    elif "token" in query_params and query_params.get("token") and not query_params.get("PayerID"):
        # PayPal cancel callback (has token but no PayerID)
        from streamlit_app.pages.customer.payment_cancel import show_payment_cancel
        show_payment_cancel()
        return

    # Route based on authentication status
    if not is_authenticated():
        show_login_page()
    else:
        user = get_current_user()
        if user['role'] == "farmer":
            show_farmer_portal()
        elif user['role'] == "customer":
            show_customer_portal()
        else:
            st.error("Invalid user role")
            logout_user()
            st.rerun()

if __name__ == "__main__":
    main()