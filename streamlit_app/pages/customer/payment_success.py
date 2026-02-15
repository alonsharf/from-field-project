"""PayPal payment success page."""

import streamlit as st
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from .paypal_components import show_paypal_success_page


def show_payment_success():
    """Display payment success page."""
    show_paypal_success_page()


if __name__ == "__main__":
    show_payment_success()