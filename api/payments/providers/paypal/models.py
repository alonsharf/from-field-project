"""PayPal-specific models."""

from typing import Optional
from pydantic import BaseModel, Field


class PayPalPaymentRequest(BaseModel):
    """PayPal payment creation request."""
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="ILS", description="Currency code")
    description: str = Field(..., description="Payment description")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")
    order_id: Optional[str] = Field(None, description="Internal order ID")


class PayPalExecuteRequest(BaseModel):
    """PayPal payment execution request."""
    payment_id: str = Field(..., description="PayPal payment ID")
    payer_id: str = Field(..., description="PayPal payer ID")


class PayPalRefundRequest(BaseModel):
    """PayPal refund request."""
    transaction_id: str = Field(..., description="PayPal transaction ID")
    amount: Optional[float] = Field(None, description="Refund amount (None for full refund)")
    currency: str = Field(default="ILS", description="Currency code")