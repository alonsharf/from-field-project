"""PayPal payment components for customer checkout."""

import streamlit as st
import os
from typing import Dict, Any, Optional
import uuid

from packages.api_client import make_api_request


def create_paypal_payment(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create PayPal payment via API using centralized client."""
    try:
        # First, create the order using centralized API client
        order_response = make_api_request("POST", "/api/orders/", order_data)

        if not order_response:
            return {"success": False, "error": "Failed to create order"}

        order_id = order_response.get("id")
        if not order_id:
            return {"success": False, "error": "Order created but no ID returned"}

        # Create PayPal payment
        payment_data = {
            "order_id": order_id,
            "return_url": f"{os.getenv('FRONTEND_BASE_URL', 'http://localhost:8501')}/payment/success",
            "cancel_url": f"{os.getenv('FRONTEND_BASE_URL', 'http://localhost:8501')}/payment/cancel"
        }

        payment_response = make_api_request("POST", "/api/payments/paypal/create", payment_data)

        if payment_response:
            # Check if it's a successful payment response with approval_url
            if payment_response.get("approval_url"):
                return {
                    "success": True,
                    "order_id": order_id,
                    **payment_response
                }
            # Check for error in response
            elif payment_response.get("detail"):
                error_detail = payment_response.get("detail", "Unknown PayPal error")
                if 'invalid_client' in str(error_detail) or 'Authentication failed' in str(error_detail):
                    return {"success": False, "order_id": order_id, "error": "PayPal credentials not configured. Please contact the administrator."}
                else:
                    return {"success": False, "order_id": order_id, "error": f"PayPal error: {error_detail}"}
            else:
                return {
                    "success": True,
                    "order_id": order_id,
                    **payment_response
                }
        else:
            return {"success": False, "order_id": order_id, "error": "Failed to create PayPal payment"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_paypal_payment(payment_id: str, payer_id: str) -> Dict[str, Any]:
    """Execute PayPal payment after approval using centralized client."""
    try:
        execution_data = {
            "payment_id": payment_id,
            "payer_id": payer_id
        }

        response = make_api_request("POST", "/api/payments/paypal/execute", execution_data)

        if response:
            return {"success": True, **response}
        else:
            return {"success": False, "error": "Failed to execute PayPal payment"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def show_paypal_payment_button(order_data: Dict[str, Any], disabled: bool = False):
    """Display PayPal payment button with integration."""

    if disabled:
        st.button(
            "💳 Pay with PayPal",
            disabled=True,
            help="Please fill in all required fields first"
        )
        return

    if st.button("💳 Pay with PayPal", type="primary", use_container_width=True):
        with st.spinner("Creating PayPal payment..."):
            result = create_paypal_payment(order_data)

            if result["success"]:
                # Store payment info in session state
                st.session_state.paypal_payment = {
                    "payment_id": result.get("payment_id"),
                    "order_id": result.get("order_id"),
                    "amount": result.get("amount"),
                    "currency": result.get("currency")
                }

                # Redirect to PayPal
                approval_url = result.get("approval_url")
                if approval_url:
                    st.success("Payment created successfully!")
                    st.markdown("### 🔗 Click below to complete payment with PayPal:")
                    st.markdown(f"[**Complete PayPal Payment →**]({approval_url})")

                    # Show payment details
                    currency = result.get('currency', 'USD')
                    amount = result.get('amount', 0)
                    formatted_amount = f"₪{amount:.2f}" if currency == 'ILS' else f"${amount:.2f}"

                    st.info(f"""
                    **Payment Details:**
                    - Amount: {formatted_amount}
                    - Order ID: {result.get('order_id', 'N/A')}
                    - Payment ID: {result.get('payment_id', 'N/A')}
                    """)

                    st.warning("⚠️ Please complete the payment on PayPal and return to this page.")
                else:
                    st.error("PayPal approval URL not received")
            else:
                error_msg = result.get('error', 'Unknown error')

                if "PayPal credentials not configured" in error_msg:
                    st.error(f"❌ {error_msg}")

                    # Show demo mode option
                    st.info("🧪 **Demo Mode**: PayPal integration requires live credentials. For demonstration purposes, you can simulate a successful order:")

                    col1, col2 = st.columns(2)

                    with col1:
                        demo_button_key = f"demo_payment_btn_{uuid.uuid4().hex[:8]}"
                        if st.button("🎭 Demo: Simulate Successful Payment", type="secondary", use_container_width=True, key=demo_button_key):
                            # Simulate successful payment flow
                            st.session_state.demo_payment = {
                                "order_id": result.get("order_id", "demo-order"),
                                "payment_id": "demo-payment-" + str(uuid.uuid4())[:8],
                                "status": "completed"
                            }
                            st.session_state.demo_completed = True
                            st.success("✅ Demo payment completed! Order placed successfully.")

                            # Clear cart
                            st.session_state.cart = []

                            st.balloons()
                            st.rerun()

                    with col2:
                        if st.button("🏠 Back to Home", use_container_width=True):
                            st.session_state.current_page = "Storefront Home"
                            st.rerun()
                else:
                    st.error(f"PayPal payment creation failed: {error_msg}")

    # Check if demo was completed (after rerun)
    if st.session_state.get('demo_completed', False):
        st.success("✅ Demo payment completed! Order placed successfully.")
        st.balloons()

        # Show next steps
        st.markdown("---")
        st.subheader("📋 What's Next?")
        st.markdown("1. **Order Confirmation** - Your demo order is being processed")
        st.markdown("2. **Preparation** - Fresh produce will be prepared for delivery")
        st.markdown("3. **Delivery** - You'll receive updates about your delivery")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📦 View My Orders", use_container_width=True):
                st.session_state.current_page = "My Orders & Shipments"
                st.session_state.demo_completed = False  # Clear demo state
                st.rerun()

        with col2:
            if st.button("🔍 Continue Shopping", use_container_width=True):
                st.session_state.current_page = "Browse Products"
                st.session_state.demo_completed = False  # Clear demo state
                st.rerun()

        # Clear demo state after 1 page load to avoid persistence
        if st.button("✅ Got it!", type="primary"):
            st.session_state.demo_completed = False
            st.rerun()


def show_paypal_success_page():
    """Show PayPal payment success page."""
    st.title("🎉 Payment Successful!")

    # Get URL parameters
    query_params = st.experimental_get_query_params()
    payment_id = query_params.get("paymentId")
    payer_id = query_params.get("PayerID")

    # Handle list format returned by experimental_get_query_params
    if payment_id and isinstance(payment_id, list):
        payment_id = payment_id[0]
    if payer_id and isinstance(payer_id, list):
        payer_id = payer_id[0]

    if payment_id and payer_id:
        if 'payment_executed' not in st.session_state:
            with st.spinner("Completing your payment..."):
                result = execute_paypal_payment(payment_id, payer_id)

                if result["success"]:
                    st.session_state.payment_executed = True
                    st.session_state.payment_result = result
                    st.success("✅ Payment completed successfully!")

                    # Clear cart
                    st.session_state.cart = []

                    # Show order details
                    st.subheader("📋 Order Details")
                    st.markdown(f"**Payment ID:** {payment_id}")
                    st.markdown(f"**Transaction ID:** {result.get('transaction_id', 'N/A')}")
                    st.markdown(f"**Order ID:** {result.get('order_id', 'N/A')}")
                    currency = result.get('currency', 'USD')
                    amount = result.get('amount', 0)
                    formatted_amount = f"₪{amount:.2f}" if currency == 'ILS' else f"${amount:.2f}"
                    st.markdown(f"**Amount:** {formatted_amount}")

                    # Next steps
                    st.markdown("---")
                    st.subheader("📋 What's Next?")
                    st.markdown("1. **Order Confirmation** - Your order is being processed")
                    st.markdown("2. **Preparation** - Fresh produce will be prepared for delivery")
                    st.markdown("3. **Delivery** - You'll receive updates about your delivery")

                    # Action buttons
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("📦 View My Orders", use_container_width=True):
                            st.session_state.current_page = "My Orders & Shipments"
                            st.rerun()

                    with col2:
                        if st.button("🔍 Continue Shopping", use_container_width=True):
                            st.session_state.current_page = "Browse Products"
                            st.rerun()
                else:
                    st.error(f"Payment execution failed: {result.get('error', 'Unknown error')}")
        else:
            # Payment already executed
            st.success("✅ Payment already completed!")
            result = st.session_state.get('payment_result', {})

            st.subheader("📋 Order Details")
            st.markdown(f"**Payment ID:** {payment_id}")
            st.markdown(f"**Transaction ID:** {result.get('transaction_id', 'N/A')}")
            st.markdown(f"**Order ID:** {result.get('order_id', 'N/A')}")
            currency = result.get('currency', 'USD')
            amount = result.get('amount', 0)
            formatted_amount = f"₪{amount:.2f}" if currency == 'ILS' else f"${amount:.2f}"
            st.markdown(f"**Amount:** {formatted_amount}")
    else:
        st.error("Missing payment information. Please try again.")
        if st.button("🏠 Back to Home"):
            st.session_state.current_page = "Storefront Home"
            st.rerun()


def show_paypal_cancel_page():
    """Show PayPal payment cancellation page."""
    st.title("❌ Payment Cancelled")
    st.warning("Your PayPal payment was cancelled. No charges were made.")

    st.markdown("### What would you like to do?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🛒 Return to Cart", use_container_width=True):
            st.session_state.current_page = "My Cart & Checkout"
            st.rerun()

    with col2:
        if st.button("🔍 Continue Shopping", use_container_width=True):
            st.session_state.current_page = "Browse Products"
            st.rerun()

    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "Storefront Home"
            st.rerun()


def prepare_order_data_for_api(customer_info: Dict[str, Any], cart_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare order data for API submission."""

    # Get or create customer session ID
    if 'customer_session_id' not in st.session_state:
        st.session_state.customer_session_id = str(uuid.uuid4())

    # Get the current customer's ID from authenticated session
    customer_id = st.session_state.get('user_id')
    if not customer_id:
        raise ValueError("User must be logged in to place an order")

    # Get the farmer ID dynamically from API (admin farmer)
    farmer_response = make_api_request("GET", "/api/auth/farmer/admin")
    if not farmer_response or 'id' not in farmer_response:
        raise ValueError("Could not retrieve farmer information")
    farmer_id = farmer_response['id']

    # Calculate delivery fee
    cart_total = cart_data.get('total', 0)
    delivery_fee = 0.00 if cart_total >= 50.00 else 5.99
    total = cart_total + delivery_fee

    # Prepare order items with correct field names
    order_items = []
    for item in cart_data.get('items', []):
        order_items.append({
            "product_id": item['id'],
            "quantity": float(item['quantity']),  # API expects Decimal
            "unit_price": float(item['price'])  # Correct field name
        })

    # Prepare order data with correct API format
    order_data = {
        "customer_id": customer_id,
        "farmer_id": farmer_id,

        # Shipping address in API format
        "shipping_name": f"{customer_info['first_name']} {customer_info['last_name']}",
        "shipping_phone": customer_info['phone'],
        "shipping_address1": customer_info['address'],
        "shipping_address2": "",  # Optional
        "shipping_city": customer_info['city'],
        "shipping_postal_code": customer_info['zip_code'],
        "shipping_country": "Israel",

        "customer_notes": customer_info.get('delivery_instructions', ''),

        # Include shipping amount so backend calculates correct total
        "shipping_amount": delivery_fee,

        "items": order_items
    }

    return order_data


def show_payment_status_indicator(status: str):
    """Show payment status indicator."""
    status_styles = {
        "pending": ("🕒", "Payment Pending", "orange"),
        "processing": ("⚡", "Processing Payment", "blue"),
        "completed": ("✅", "Payment Completed", "green"),
        "failed": ("❌", "Payment Failed", "red"),
        "cancelled": ("❌", "Payment Cancelled", "red")
    }

    if status in status_styles:
        icon, message, color = status_styles[status]
        st.markdown(f":{color}[{icon} {message}]")
    else:
        st.markdown(f"🔍 Status: {status}")