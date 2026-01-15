"""PayPal payment provider implementation."""

import os
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
import paypalrestsdk
from paypalrestsdk import Payment as PayPalPayment
from paypalrestsdk import configure

from ..base import BasePaymentProvider

logger = logging.getLogger(__name__)


class PayPalProvider(BasePaymentProvider):
    """PayPal payment provider implementation."""

    def __init__(self):
        """Initialize PayPal SDK configuration."""
        self._configure_paypal()

    def _configure_paypal(self):
        """Configure PayPal SDK with environment variables."""
        mode = os.getenv("PAYPAL_MODE", "sandbox")
        client_id = os.getenv("PAYPAL_CLIENT_ID")
        client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

        if not client_id or not client_secret:
            logger.warning("PayPal credentials not found in environment variables")
            return

        configure({
            "mode": mode,
            "client_id": client_id,
            "client_secret": client_secret
        })

        logger.info(f"PayPal SDK configured in {mode} mode")

    def create_payment(
        self,
        amount: Decimal,
        currency: str = "ILS",
        description: str = "Farm Order Payment",
        return_url: str = None,
        cancel_url: str = None,
        order_id: str = None
    ) -> Dict[str, Any]:
        """Create a PayPal payment."""
        try:
            base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:8501")
            if not return_url:
                return_url = f"{base_url}/payment/success"
            if not cancel_url:
                cancel_url = f"{base_url}/payment/cancel"

            payment_data = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": description,
                            "sku": order_id or "FARM_ORDER",
                            "price": str(amount),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": description,
                    "custom": order_id
                }]
            }

            payment = PayPalPayment(payment_data)

            if payment.create():
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break

                return {
                    "success": True,
                    "payment_id": payment.id,
                    "approval_url": approval_url
                }
            else:
                return {"success": False, "error": payment.error}

        except Exception as e:
            logger.error(f"PayPal payment creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Execute a PayPal payment after approval."""
        try:
            payment = PayPalPayment.find(payment_id)

            if payment.execute({"payer_id": payer_id}):
                transaction = payment.transactions[0] if payment.transactions else {}
                related_resources = transaction.get('related_resources', [])
                sale_info = None
                if related_resources:
                    sale_info = related_resources[0].get('sale', {})

                return {
                    "success": True,
                    "payment_id": payment.id,
                    "payment_state": payment.state,
                    "transaction_id": sale_info.get('id') if sale_info else None,
                    "amount": sale_info.get('amount', {}).get('total') if sale_info else None,
                    "currency": sale_info.get('amount', {}).get('currency') if sale_info else None,
                    "order_id": transaction.get('custom')
                }
            else:
                return {"success": False, "error": payment.error}

        except Exception as e:
            logger.error(f"PayPal payment execution error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get PayPal payment details."""
        try:
            payment = PayPalPayment.find(payment_id)
            if payment:
                return {"success": True, "payment": payment.to_dict()}
            else:
                return {"success": False, "error": "Payment not found"}
        except Exception as e:
            logger.error(f"PayPal get payment details error: {str(e)}")
            return {"success": False, "error": str(e)}

    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund a PayPal payment."""
        try:
            from paypalrestsdk import Sale

            sale = Sale.find(transaction_id)
            refund_data = {}
            if amount:
                refund_data["amount"] = {
                    "total": str(amount),
                    "currency": "ILS"
                }

            refund = sale.refund(refund_data)

            if refund.success():
                return {
                    "success": True,
                    "refund_id": refund.id,
                    "refund_state": refund.state
                }
            else:
                return {"success": False, "error": refund.error}

        except Exception as e:
            logger.error(f"PayPal refund error: {str(e)}")
            return {"success": False, "error": str(e)}


    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "PAYPAL"


# Global instance
paypal_provider = PayPalProvider()