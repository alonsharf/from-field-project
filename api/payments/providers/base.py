"""Base payment provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class BasePaymentProvider(ABC):
    """Abstract base class for payment providers."""

    @abstractmethod
    def create_payment(
        self,
        amount: Decimal,
        currency: str,
        description: str,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a payment."""
        pass

    @abstractmethod
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Execute a payment after approval."""
        pass

    @abstractmethod
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get payment details."""
        pass

    @abstractmethod
    def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Refund a payment."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass