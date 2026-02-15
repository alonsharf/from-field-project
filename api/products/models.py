"""Pydantic models for products service."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, computed_field


class ProductBase(BaseModel):
    """Base product model with common fields."""
    farmer_id: UUID = Field(..., description="ID of the farmer who owns this product")
    name: str = Field(..., description="Product name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, description="Product category (e.g. vegetable, fruit, herb)")
    unit_label: str = Field(..., description="Unit label (e.g. kg, bundle, box)")
    unit_size: Optional[Decimal] = Field(None, description="Unit size (e.g. 1.00 kg, 0.5 kg)", ge=0)
    price_per_unit: Decimal = Field(..., description="Price per unit", ge=0)
    currency: str = Field(default="ILS", description="Currency code", max_length=3)
    stock_quantity: Decimal = Field(default=0, description="Current stock quantity", ge=0)
    min_order_quantity: Decimal = Field(default=1, description="Minimum order quantity", ge=0)
    max_order_quantity: Optional[Decimal] = Field(None, description="Maximum order quantity (null = no limit)", ge=0)
    is_active: bool = Field(default=True, description="Whether the product is active")
    is_organic: bool = Field(default=False, description="Whether the product is organic")
    available_from: Optional[date] = Field(None, description="Date when product becomes available")
    available_until: Optional[date] = Field(None, description="Date when product is no longer available")
    image_url: Optional[str] = Field(None, description="URL to product image")


class ProductCreate(ProductBase):
    """Model for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Model for updating product information."""
    farmer_id: Optional[UUID] = Field(None, description="ID of the farmer who owns this product")
    name: Optional[str] = Field(None, description="Product name", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, description="Product category")
    unit_label: Optional[str] = Field(None, description="Unit label")
    unit_size: Optional[Decimal] = Field(None, description="Unit size", ge=0)
    price_per_unit: Optional[Decimal] = Field(None, description="Price per unit", ge=0)
    currency: Optional[str] = Field(None, description="Currency code", max_length=3)
    stock_quantity: Optional[Decimal] = Field(None, description="Current stock quantity", ge=0)
    min_order_quantity: Optional[Decimal] = Field(None, description="Minimum order quantity", ge=0)
    max_order_quantity: Optional[Decimal] = Field(None, description="Maximum order quantity", ge=0)
    is_active: Optional[bool] = Field(None, description="Whether the product is active")
    is_organic: Optional[bool] = Field(None, description="Whether the product is organic")
    available_from: Optional[date] = Field(None, description="Date when product becomes available")
    available_until: Optional[date] = Field(None, description="Date when product is no longer available")
    image_url: Optional[str] = Field(None, description="URL to product image")


class Product(BaseModel):
    """Complete product model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the product")
    farmer_id: UUID = Field(..., description="ID of the farmer who owns this product")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, description="Product category")
    unit_label: Optional[str] = Field(None, description="Unit label")
    unit_size: Optional[Decimal] = Field(None, description="Unit size", ge=0)
    price_per_unit: Decimal = Field(..., description="Price per unit", ge=0)
    currency: str = Field(default="ILS", description="Currency code", max_length=3)
    stock_quantity: Decimal = Field(default=0, description="Current stock quantity", ge=0)
    min_order_quantity: Decimal = Field(default=1, description="Minimum order quantity", ge=0)
    max_order_quantity: Optional[Decimal] = Field(None, description="Maximum order quantity", ge=0)
    is_active: bool = Field(default=True, description="Whether the product is active")
    is_organic: bool = Field(default=False, description="Whether the product is organic")
    available_from: Optional[date] = Field(None, description="Date when product becomes available")
    available_until: Optional[date] = Field(None, description="Date when product is no longer available")
    image_url: Optional[str] = Field(None, description="URL to product image")
    created_at: datetime = Field(..., description="Timestamp when the product was created")
    updated_at: datetime = Field(..., description="Timestamp when the product was last updated")

    @classmethod
    def from_orm_product(cls, product):
        """Create Product from SQLAlchemy Product model."""
        return cls(
            id=product.id,
            farmer_id=product.farmer_id,
            name=product.name,
            description=product.description,
            category=product.category.name if product.category else None,
            unit_label=product.unit_label.name if product.unit_label else None,
            unit_size=product.unit_size,
            price_per_unit=product.price_per_unit,
            currency=product.currency,
            stock_quantity=product.stock_quantity,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            is_active=product.is_active,
            is_organic=product.is_organic,
            available_from=product.available_from,
            available_until=product.available_until,
            image_url=product.image_url,
            created_at=product.created_at,
            updated_at=product.updated_at
        )


class ProductList(BaseModel):
    """Model for product list responses."""
    products: list[Product]
    total: int = Field(..., description="Total number of products")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")


class ProductSummary(BaseModel):
    """Simplified product model for listings."""
    id: UUID = Field(..., description="Unique identifier for the product")
    name: str = Field(..., description="Product name")
    category: Optional[str] = Field(None, description="Product category")
    price_per_unit: Decimal = Field(..., description="Price per unit")
    currency: str = Field(..., description="Currency code")
    unit_label: str = Field(..., description="Unit label")
    is_organic: bool = Field(..., description="Whether the product is organic")
    stock_quantity: Decimal = Field(..., description="Current stock quantity")
    image_url: Optional[str] = Field(None, description="URL to product image")

    class Config:
        from_attributes = True