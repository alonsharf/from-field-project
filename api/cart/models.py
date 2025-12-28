"""Pydantic models for cart service."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    """Base cart item model with common fields."""
    product_id: UUID = Field(..., description="Product ID")
    quantity: Decimal = Field(..., description="Quantity of the product", gt=0)
    unit_price: Decimal = Field(..., description="Unit price at time of adding to cart", gt=0)


class CartItemCreate(CartItemBase):
    """Model for creating a new cart item."""
    pass


class CartItemUpdate(BaseModel):
    """Model for updating cart item information."""
    quantity: Optional[Decimal] = Field(None, description="Quantity of the product", gt=0)


class CartItem(CartItemBase):
    """Complete cart item model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the cart item")
    cart_id: UUID = Field(..., description="Cart ID this item belongs to")
    created_at: datetime = Field(..., description="Timestamp when the cart item was created")
    updated_at: datetime = Field(..., description="Timestamp when the cart item was last updated")

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    """Base cart model with common fields."""
    session_id: str = Field(..., description="Session ID for the cart")
    customer_id: Optional[UUID] = Field(None, description="Customer ID if logged in")


class CartCreate(CartBase):
    """Model for creating a new cart."""
    pass


class CartUpdate(BaseModel):
    """Model for updating cart information."""
    customer_id: Optional[UUID] = Field(None, description="Customer ID if logged in")


class Cart(CartBase):
    """Complete cart model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the cart")
    status: str = Field(..., description="Cart status")
    created_at: datetime = Field(..., description="Timestamp when the cart was created")
    updated_at: datetime = Field(..., description="Timestamp when the cart was last updated")

    class Config:
        from_attributes = True


class CartWithItems(Cart):
    """Cart model with items included."""
    items: List[CartItem] = Field(default=[], description="Items in the cart")
    total_amount: Decimal = Field(..., description="Total amount of the cart")
    item_count: int = Field(..., description="Number of items in the cart")


class AddToCartRequest(BaseModel):
    """Request model for adding item to cart."""
    session_id: str = Field(..., description="Session ID")
    product_id: UUID = Field(..., description="Product ID to add")
    quantity: Decimal = Field(..., description="Quantity to add", gt=0)


class UpdateCartItemRequest(BaseModel):
    """Request model for updating cart item."""
    quantity: Decimal = Field(..., description="New quantity", gt=0)


class CartList(BaseModel):
    """Model for cart list responses."""
    carts: List[Cart]
    total: int = Field(..., description="Total number of carts")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")