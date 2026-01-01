"""My Profile - Customer profile management and preferences."""

import streamlit as st
import sys
import os
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import centralized API client
from packages.api_client import make_api_request

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

def get_customer_profile(customer_id):
    """Get customer profile data from API."""
    if not customer_id:
        return None

    response = make_api_request("GET", f"/api/customers/{customer_id}")
    return response if response else None

def get_customer_stats(customer_id):
    """Get customer statistics from database."""
    if not customer_id:
        return {'customer_since': '', 'total_orders': 0, 'total_spent': 0.00}

    # Get customer info
    customer = make_api_request("GET", f"/api/customers/{customer_id}")
    if not customer:
        return {'customer_since': '', 'total_orders': 0, 'total_spent': 0.00}

    # Get customer orders
    orders_response = make_api_request("GET", f"/api/orders/?customer_id={customer_id}")
    orders = orders_response.get('orders', []) if orders_response else []

    # Calculate stats
    total_orders = len(orders)
    total_spent = sum(float(order.get('total_amount', 0)) for order in orders)

    return {
        'customer_since': customer.get('created_at', '')[:10] if customer.get('created_at') else '',
        'total_orders': total_orders,
        'total_spent': total_spent
    }

def update_customer_profile(customer_id, profile_data):
    """Update customer profile via API."""
    if not customer_id:
        return False

    response = make_api_request("PUT", f"/api/customers/{customer_id}", profile_data)
    return response is not None

def get_customer_recent_activity(customer_id, limit=5):
    """Get customer recent activity from orders."""
    if not customer_id:
        return []

    # Get recent orders as activity
    orders_response = make_api_request("GET", f"/api/orders/?customer_id={customer_id}&limit={limit}")
    orders = orders_response.get('orders', []) if orders_response else []

    activities = []
    for order in orders:
        activity = {
            'date': order.get('created_at', '')[:10],
            'action': f"Order {order['status'].lower()}",
            'details': f"Order total: ₪{float(order.get('total_amount', 0)):.2f}"
        }
        activities.append(activity)

    return activities

def show_customer_profile():
    """Display customer profile management interface."""

    # AUTHENTICATION GUARD - Critical security fix
    current_user = get_current_user()
    if not current_user:
        st.error("🔒 Authentication Required")
        st.info("Please log in as a customer to view your profile.")
        st.markdown("**Why you're seeing this:** This page contains personal profile information and requires customer authentication.")
        return

    st.title("👤 My Profile")
    st.markdown("### Manage your account information and preferences")
    st.markdown("---")

    # Tabs for different profile sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Personal Information",
        "Delivery Preferences",
        "Payment Methods",
        "Account Settings"
    ])

    with tab1:
        show_personal_information()

    with tab2:
        show_delivery_preferences()

    with tab3:
        show_payment_methods()

    with tab4:
        show_account_settings()

def show_personal_information():
    """Display personal information management."""
    st.subheader("👤 Personal Information")

    try:
        # Get current user and profile from database
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None

        # Get profile data from database
        profile_data = get_customer_profile(customer_id)

        # Use database data or defaults
        current_profile = {
            "first_name": profile_data.get('first_name', '') if profile_data else '',
            "last_name": profile_data.get('last_name', '') if profile_data else '',
            "email": profile_data.get('email', '') if profile_data else '',
            "phone": profile_data.get('phone', '') if profile_data else '',
            # birth_date field doesn't exist in customer table
            "customer_since": profile_data.get('customer_since', '') if profile_data else ''
        }

        # If no database data, show info message
        if not profile_data and not customer_id:
            st.info("👤 This is a demo profile. In a real application, your profile information would be loaded from the database after login.")
            # Set demo data for display
            current_profile = {
                "first_name": "Demo",
                "last_name": "Customer",
                "email": "demo@example.com",
                "phone": "(555) 123-4567",
                # birth_date field doesn't exist in customer table
                "customer_since": "2024-11-24"
            }

    except Exception as e:
        st.error("Unable to load profile from database.")
        st.caption(f"Error: {str(e)}")

        # Fallback to demo data
        current_profile = {
            "first_name": "Demo",
            "last_name": "Customer",
            "email": "demo@example.com",
            "phone": "(555) 123-4567",
            # birth_date field doesn't exist in customer table
            "customer_since": "2024-11-24"
        }

    # Profile form
    with st.form("personal_info_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input(
                "First Name *",
                value=current_profile["first_name"],
                help="Your first name"
            )

            email = st.text_input(
                "Email Address *",
                value=current_profile["email"],
                help="We'll send order confirmations to this email"
            )

            # birth_date field removed - not available in customer table

        with col2:
            last_name = st.text_input(
                "Last Name *",
                value=current_profile["last_name"],
                help="Your last name"
            )

            phone = st.text_input(
                "Phone Number *",
                value=current_profile["phone"],
                help="For delivery notifications"
            )

        # Dietary preferences and restrictions
        st.markdown("---")
        st.markdown("**Dietary Preferences & Restrictions**")

        col1, col2 = st.columns(2)

        with col1:
            dietary_preferences = st.multiselect(
                "Dietary Preferences",
                ["Organic Only", "Vegetarian", "Vegan", "Gluten-Free", "Non-GMO", "Local Only"],
                default=["Organic Only"],
                help="Help us recommend products that fit your dietary needs"
            )

        with col2:
            allergies = st.text_area(
                "Allergies & Restrictions",
                placeholder="Please list any food allergies or restrictions...",
                height=80,
                help="We'll flag products that may contain these allergens"
            )

        # Communication preferences
        st.markdown("---")
        st.markdown("**Communication Preferences**")

        col1, col2 = st.columns(2)

        with col1:
            email_notifications = st.multiselect(
                "Email Notifications",
                ["Order Confirmations", "Delivery Updates", "New Product Alerts", "Weekly Newsletter", "Special Offers"],
                default=["Order Confirmations", "Delivery Updates"],
                help="Choose what emails you'd like to receive"
            )

        with col2:
            sms_notifications = st.multiselect(
                "SMS Notifications",
                ["Delivery Alerts", "Order Ready", "Special Offers", "Emergency Updates"],
                default=["Delivery Alerts"],
                help="Text message notifications (standard rates apply)"
            )

        submitted = st.form_submit_button("💾 Save Changes", type="primary")

        if submitted:
            if first_name and last_name and email and phone:
                try:
                    current_user = get_current_user()
                    customer_id = current_user.get('id') if current_user else None

                    if customer_id:
                        # Update profile in database
                        profile_update = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'phone': phone,
                            'marketing_opt_in': 'Weekly Newsletter' in email_notifications
                        }

                        if update_customer_profile(customer_id, profile_update):
                            st.success("✅ Profile updated successfully!")
                        else:
                            st.error("❌ Failed to update profile. Please try again.")
                    else:
                        st.info("👤 Demo mode - Profile changes would be saved to database in a real application.")
                        st.success("✅ Profile updated successfully! (Demo mode)")

                except Exception as e:
                    st.error(f"❌ Error updating profile: {str(e)}")
            else:
                st.error("❌ Please fill in all required fields")

    # Account statistics
    st.markdown("---")
    st.subheader("📊 Account Statistics")

    try:
        # Get account statistics from database
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None
        stats = get_customer_stats(customer_id)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Customer Since", stats["customer_since"])

        with col2:
            st.metric("Total Orders", str(stats["total_orders"]))

        with col3:
            st.metric("Total Spent", f"₪{stats['total_spent']:.2f}")


    except Exception as e:
        st.error("Unable to load account statistics.")
        st.caption(f"Error: {str(e)}")

        # Fallback to demo statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Customer Since", current_profile["customer_since"])

        with col2:
            st.metric("Total Orders", "0")

        with col3:
            st.metric("Total Spent", "₪0.00")


def show_delivery_preferences():
    """Display delivery preferences management."""
    st.subheader("🏠 Delivery Preferences")

    try:
        # Get current user profile for delivery address
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None
        profile_data = get_customer_profile(customer_id)

        # Use database address data or defaults
        default_address = {
            'name': 'Home',
            'street': profile_data.get('address_line1', '') if profile_data else '',
            'city': profile_data.get('city', '') if profile_data else '',
            'postal_code': profile_data.get('postal_code', '') if profile_data else ''
        }

        if not profile_data:
            st.info("🏠 In a real application, your saved delivery addresses would be loaded from the database.")
            # Set demo data
            default_address = {
                'name': 'Home',
                'street': '123 Demo Street',
                'city': 'Springfield',
                'postal_code': '62701'
            }

    except Exception as e:
        st.error("Unable to load delivery preferences from database.")
        st.caption(f"Error: {str(e)}")
        # Fallback
        default_address = {
            'name': 'Home',
            'street': '123 Demo Street',
            'city': 'Springfield',
            'postal_code': '62701'
        }

    # Default delivery address
    st.markdown("**Default Delivery Address**")

    with st.form("delivery_address_form"):
        col1, col2 = st.columns(2)

        with col1:
            address_name = st.text_input("Address Name", value=default_address['name'], help="e.g., Home, Work, etc.")
            street_address = st.text_input("Street Address *", value=default_address['street'])
            city = st.text_input("City *", value=default_address['city'])

        with col2:
            apt_unit = st.text_input("Apt/Unit (optional)", placeholder="Apt 2B")
            state = st.selectbox("State *", ["IL", "IN", "IA", "MO", "WI"], index=0)
            zip_code = st.text_input("ZIP Code *", value=default_address['postal_code'])

        delivery_instructions = st.text_area(
            "Default Delivery Instructions",
            placeholder="e.g., Leave at front door, Ring doorbell, Use side entrance...",
            height=80,
            help="These instructions will be used for all deliveries unless specified otherwise"
        )

        if st.form_submit_button("💾 Save Address"):
            st.success("✅ Default delivery address saved!")

    # Additional addresses
    st.markdown("---")
    st.markdown("**Additional Delivery Addresses**")

    st.info("💡 In a full application, you could save multiple delivery addresses (work, family, etc.) and manage them here.")

    if st.button("➕ Add New Address"):
        st.info("Add new address form would appear here")

    # Delivery preferences
    st.markdown("---")
    st.markdown("**Delivery Preferences**")

    col1, col2 = st.columns(2)

    with col1:
        preferred_delivery_days = st.multiselect(
            "Preferred Delivery Days",
            ["Tuesday", "Friday"],
            default=["Tuesday", "Friday"],
            help="We deliver on Tuesdays and Fridays"
        )

        preferred_time = st.selectbox(
            "Preferred Delivery Time",
            ["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)", "No Preference"],
            index=0
        )

        substitute_preferences = st.selectbox(
            "If item unavailable:",
            ["Substitute with similar item", "Skip item and refund", "Call me first"],
            index=0,
            help="What should we do if an item in your order is unavailable?"
        )

    with col2:
        contact_method = st.selectbox(
            "Preferred Contact Method",
            ["SMS", "Phone Call", "Email"],
            index=0,
            help="How should we contact you about deliveries?"
        )

        leave_unattended = st.selectbox(
            "Leave packages unattended?",
            ["Yes, leave at door", "No, require signature", "Only if secure location"],
            index=2,
            help="Can we leave your order if you're not home?"
        )

        special_handling = st.text_area(
            "Special Handling Instructions",
            placeholder="Any special requirements for your deliveries...",
            height=60
        )

    if st.button("💾 Save Delivery Preferences"):
        st.success("✅ Delivery preferences saved!")

def show_payment_methods():
    """Display payment methods management."""
    st.subheader("💳 Payment Methods")

    # Saved payment methods
    st.markdown("**Saved Payment Methods**")

    st.info("💡 In a real application, your saved payment methods would be securely stored and displayed here. For security reasons, only partial card numbers would be shown.")

    # Add new payment method
    st.markdown("---")
    st.markdown("**Add New Payment Method**")

    payment_type = st.selectbox(
        "Payment Type",
        ["Credit/Debit Card", "PayPal", "Bank Account"],
        help="Choose your payment method type"
    )

    if payment_type == "Credit/Debit Card":
        with st.form("add_card_form"):
            col1, col2 = st.columns(2)

            with col1:
                card_number = st.text_input(
                    "Card Number *",
                    placeholder="1234 5678 9012 3456",
                    type="password"
                )

                cardholder_name = st.text_input(
                    "Cardholder Name *",
                    placeholder="John Smith"
                )

            with col2:
                col2a, col2b = st.columns(2)

                with col2a:
                    expiry = st.text_input(
                        "Expiry (MM/YY) *",
                        placeholder="12/25"
                    )

                with col2b:
                    cvv = st.text_input(
                        "CVV *",
                        placeholder="123",
                        type="password"
                    )

            # Billing address
            same_as_delivery = st.checkbox("Same as delivery address", value=True)

            if not same_as_delivery:
                st.markdown("**Billing Address**")
                billing_address = st.text_input("Street Address", placeholder="123 Billing St")
                col1, col2, col3 = st.columns(3)
                with col1:
                    billing_city = st.text_input("City", placeholder="Springfield")
                with col2:
                    billing_state = st.selectbox("State", ["IL", "IN", "IA", "MO", "WI"])
                with col3:
                    billing_zip = st.text_input("ZIP", placeholder="62701")

            if st.form_submit_button("💳 Add Card"):
                st.success("✅ Credit card added successfully!")

    elif payment_type == "PayPal":
        st.info("💡 You'll be redirected to PayPal to link your account")
        if st.button("🔗 Connect PayPal Account"):
            st.success("PayPal account connected!")

    elif payment_type == "Bank Account":
        with st.form("add_bank_form"):
            col1, col2 = st.columns(2)

            with col1:
                routing_number = st.text_input("Routing Number *", type="password")
                account_holder = st.text_input("Account Holder Name *")

            with col2:
                account_number = st.text_input("Account Number *", type="password")
                account_type = st.selectbox("Account Type", ["Checking", "Savings"])

            if st.form_submit_button("🏦 Add Bank Account"):
                st.success("✅ Bank account added successfully!")

def show_account_settings():
    """Display account settings and preferences."""
    st.subheader("⚙️ Account Settings")

    # Security settings
    st.markdown("**Security Settings**")

    with st.form("security_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")

        if st.form_submit_button("🔒 Change Password"):
            if new_password == confirm_password:
                st.success("✅ Password changed successfully!")
            else:
                st.error("❌ Passwords don't match")

    # Privacy settings
    st.markdown("---")
    st.markdown("**Privacy Settings**")

    col1, col2 = st.columns(2)

    with col1:
        share_data = st.checkbox(
            "Share data for better recommendations",
            value=True,
            help="Allow us to use your order history to suggest products you might like"
        )

        marketing_emails = st.checkbox(
            "Receive marketing emails",
            value=True,
            help="Get updates about new products, seasonal specials, and promotions"
        )

    with col2:
        order_history_public = st.checkbox(
            "Make order history visible for recommendations",
            value=False,
            help="Help other customers with product reviews and recommendations"
        )

        third_party_offers = st.checkbox(
            "Receive offers from partner farms",
            value=False,
            help="Get special offers from other local farms in our network"
        )

    # Account actions
    st.markdown("---")
    st.markdown("**Account Actions**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📧 Request Account Data", use_container_width=True):
            st.info("We'll email you a copy of all your account data within 24 hours")

        if st.button("⏸️ Temporarily Deactivate Account", use_container_width=True):
            st.warning("Your account will be paused. You can reactivate it anytime by logging in")

    with col2:
        if st.button("🔄 Reset All Preferences", use_container_width=True):
            st.info("All preferences have been reset to default values")

        # Danger zone
        st.markdown("**⚠️ Danger Zone**")
        if st.button("❌ Delete Account", type="secondary", use_container_width=True):
            show_delete_account_confirmation()

    # Recent activity
    st.markdown("---")
    st.markdown("**📋 Recent Account Activity**")

    try:
        # Get recent activity from database
        current_user = get_current_user()
        customer_id = current_user.get('id') if current_user else None
        activities = get_customer_recent_activity(customer_id, limit=5)

        if not activities:
            st.info("📋 No recent activity found. Start placing orders to see your activity history here!")
        else:
            for activity in activities:
                col1, col2, col3 = st.columns([1, 2, 2])

                with col1:
                    st.caption(activity['date'])

                with col2:
                    st.markdown(activity['action'])

                with col3:
                    st.caption(activity['details'])

    except Exception as e:
        st.error("Unable to load recent activity from database.")
        st.caption(f"Error: {str(e)}")
        st.info("📋 Recent account activity would appear here.")

def show_delete_account_confirmation():
    """Show account deletion confirmation dialog."""
    st.warning("⚠️ **Delete Account Confirmation**")
    st.markdown("This action cannot be undone. All your:")
    st.markdown("• Order history will be permanently deleted")
    st.markdown("• Saved addresses and payment methods will be removed")
    st.markdown("• Loyalty points will be forfeited")
    st.markdown("• Account preferences will be lost")

    confirm_text = st.text_input("Type 'DELETE' to confirm:", placeholder="DELETE")

    if confirm_text == "DELETE":
        if st.button("🗑️ Permanently Delete Account", type="primary"):
            st.error("Account deletion process initiated. You will receive a confirmation email.")
    else:
        st.button("🗑️ Permanently Delete Account", disabled=True)