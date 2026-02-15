"""Pydantic models for orders service."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

# Import centralized enums
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from packages.db.enums import OrderStatus, PaymentStatus


class OrderItemBase(BaseModel):
    """Base order item model."""
    product_id: UUID = Field(..., description="ID of the product being ordered")
    quantity: Decimal = Field(..., description="Quantity being ordered", gt=0)
    unit_price: Decimal = Field(..., description="Price per unit at time of order", ge=0)
    line_discount: Decimal = Field(default=0, description="Discount applied to this line", ge=0)


class OrderItemCreate(OrderItemBase):
    """Model for creating an order item."""
    pass


class OrderItem(OrderItemBase):
    """Complete order item model."""
    id: UUID = Field(..., description="Unique identifier for the order item")
    order_id: UUID = Field(..., description="ID of the order this item belongs to")
    line_subtotal: Decimal = Field(..., description="Subtotal for this line (quantity * unit_price)", ge=0)
    line_total: Decimal = Field(..., description="Total for this line (subtotal - discount)", ge=0)
    created_at: datetime = Field(..., description="Timestamp when the item was created")
    updated_at: datetime = Field(..., description="Timestamp when the item was last updated")

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order model with common fields."""
    customer_id: UUID = Field(..., description="ID of the customer placing the order")
    farmer_id: UUID = Field(..., description="ID of the farmer fulfilling the order")

    # Shipping address
    shipping_name: Optional[str] = Field(None, description="Name for shipping")
    shipping_phone: Optional[str] = Field(None, description="Phone for shipping")
    shipping_address1: Optional[str] = Field(None, description="Primary shipping address")
    shipping_address2: Optional[str] = Field(None, description="Secondary shipping address")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_postal_code: Optional[str] = Field(None, description="Shipping postal code")
    shipping_country: str = Field(default="Israel", description="Shipping country")

    customer_notes: Optional[str] = Field(None, description="Notes from the customer")


class OrderCreate(OrderBase):
    """Model for creating a new order."""
    items: List[OrderItemCreate] = Field(..., description="List of items being ordered")

    # Optional amounts for order creation
    shipping_amount: Optional[Decimal] = Field(default=0, description="Shipping cost", ge=0)
    discount_amount: Optional[Decimal] = Field(default=0, description="Discount amount", ge=0)


class OrderUpdate(BaseModel):
    """Model for updating order information."""
    status: Optional[OrderStatus] = Field(None, description="Order status")
    payment_status: Optional[PaymentStatus] = Field(None, description="Payment status")
    payment_provider: Optional[str] = Field(None, description="Payment provider")
    payment_reference: Optional[str] = Field(None, description="Payment reference")

    shipping_amount: Optional[Decimal] = Field(None, description="Shipping cost", ge=0)
    discount_amount: Optional[Decimal] = Field(None, description="Discount amount", ge=0)

    shipping_name: Optional[str] = Field(None, description="Name for shipping")
    shipping_phone: Optional[str] = Field(None, description="Phone for shipping")
    shipping_address1: Optional[str] = Field(None, description="Primary shipping address")
    shipping_address2: Optional[str] = Field(None, description="Secondary shipping address")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_postal_code: Optional[str] = Field(None, description="Shipping postal code")
    shipping_country: Optional[str] = Field(None, description="Shipping country")

    customer_notes: Optional[str] = Field(None, description="Notes from the customer")
    internal_notes: Optional[str] = Field(None, description="Internal notes for farmer/backoffice")


class Order(OrderBase):
    """Complete order model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the order")

    status: OrderStatus = Field(..., description="Current order status")
    payment_status: PaymentStatus = Field(..., description="Current payment status")
    payment_provider: Optional[str] = Field(None, description="Payment provider used")
    payment_reference: Optional[str] = Field(None, description="External payment reference")

    subtotal_amount: Decimal = Field(..., description="Subtotal amount", ge=0)
    shipping_amount: Decimal = Field(..., description="Shipping cost", ge=0)
    discount_amount: Decimal = Field(..., description="Discount amount", ge=0)
    total_amount: Decimal = Field(..., description="Total order amount", ge=0)
    currency: str = Field(..., description="Currency code")

    internal_notes: Optional[str] = Field(None, description="Internal notes")

    created_at: datetime = Field(..., description="Timestamp when the order was created")
    updated_at: datetime = Field(..., description="Timestamp when the order was last updated")

    # Related items
    items: Optional[List[OrderItem]] = Field(None, description="Order items")

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """Model for order list responses."""
    orders: List[Order]
    total: int = Field(..., description="Total number of orders")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")


class OrderSummary(BaseModel):
    """Simplified order model for listings."""
    id: UUID = Field(..., description="Unique identifier for the order")
    customer_id: UUID = Field(..., description="Customer ID")
    farmer_id: UUID = Field(..., description="Farmer ID")
    status: OrderStatus = Field(..., description="Order status")
    payment_status: PaymentStatus = Field(..., description="Payment status")
    total_amount: Decimal = Field(..., description="Total order amount")
    currency: str = Field(..., description="Currency code")
    created_at: datetime = Field(..., description="Order creation date")

    class Config:
        from_attributes = True