"""Pydantic models for payments service."""

from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    """Request model for creating a PayPal payment."""
    order_id: UUID = Field(..., description="Order ID to create payment for")
    return_url: Optional[str] = Field(None, description="URL to redirect after successful payment")
    cancel_url: Optional[str] = Field(None, description="URL to redirect after cancelled payment")


class PaymentExecuteRequest(BaseModel):
    """Request model for executing a PayPal payment."""
    payment_id: str = Field(..., description="PayPal payment ID")
    payer_id: str = Field(..., description="PayPal payer ID from return URL")


class RefundRequest(BaseModel):
    """Request model for refunding a payment."""
    amount: Optional[Decimal] = Field(None, description="Refund amount (None for full refund)", ge=0)


class PaymentCreateResponse(BaseModel):
    """Response model for payment creation."""
    order_id: str = Field(..., description="Order ID")
    payment_id: str = Field(..., description="PayPal payment ID")
    approval_url: str = Field(..., description="PayPal approval URL")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")


class PaymentExecuteResponse(BaseModel):
    """Response model for payment execution."""
    payment_id: str = Field(..., description="PayPal payment ID")
    transaction_id: Optional[str] = Field(None, description="PayPal transaction ID")
    payment_state: Optional[str] = Field(None, description="PayPal payment state")
    order_id: Optional[str] = Field(None, description="Order ID")
    amount: Optional[str] = Field(None, description="Payment amount")
    currency: Optional[str] = Field(None, description="Payment currency")


class RefundResponse(BaseModel):
    """Response model for payment refund."""
    order_id: str = Field(..., description="Order ID")
    refund_id: str = Field(..., description="PayPal refund ID")
    refund_state: str = Field(..., description="PayPal refund state")
    refund_amount: float = Field(..., description="Refund amount")
    currency: str = Field(..., description="Refund currency")