"""Pydantic models for shipments service."""

from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

# Import centralized enums
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from packages.db.enums import ShipmentStatus


class ShipmentBase(BaseModel):
    """Base shipment model with common fields."""
    order_id: UUID = Field(..., description="ID of the order being shipped")
    carrier_name: Optional[str] = Field(None, description="Name of the shipping carrier")
    tracking_number: Optional[str] = Field(None, description="Tracking number for the shipment")
    estimated_delivery_date: Optional[date] = Field(None, description="Estimated delivery date")

    # Optional address override (if different from order)
    shipping_name: Optional[str] = Field(None, description="Override shipping name")
    shipping_phone: Optional[str] = Field(None, description="Override shipping phone")
    shipping_address1: Optional[str] = Field(None, description="Override primary shipping address")
    shipping_address2: Optional[str] = Field(None, description="Override secondary shipping address")
    shipping_city: Optional[str] = Field(None, description="Override shipping city")
    shipping_postal_code: Optional[str] = Field(None, description="Override shipping postal code")
    shipping_country: Optional[str] = Field(None, description="Override shipping country")


class ShipmentCreate(ShipmentBase):
    """Model for creating a new shipment."""
    pass


class ShipmentUpdate(BaseModel):
    """Model for updating shipment information."""
    status: Optional[ShipmentStatus] = Field(None, description="Shipment status")
    carrier_name: Optional[str] = Field(None, description="Name of the shipping carrier")
    tracking_number: Optional[str] = Field(None, description="Tracking number for the shipment")
    estimated_delivery_date: Optional[date] = Field(None, description="Estimated delivery date")
    shipped_at: Optional[datetime] = Field(None, description="Timestamp when shipment was shipped")
    delivered_at: Optional[datetime] = Field(None, description="Timestamp when shipment was delivered")

    # Address overrides
    shipping_name: Optional[str] = Field(None, description="Override shipping name")
    shipping_phone: Optional[str] = Field(None, description="Override shipping phone")
    shipping_address1: Optional[str] = Field(None, description="Override primary shipping address")
    shipping_address2: Optional[str] = Field(None, description="Override secondary shipping address")
    shipping_city: Optional[str] = Field(None, description="Override shipping city")
    shipping_postal_code: Optional[str] = Field(None, description="Override shipping postal code")
    shipping_country: Optional[str] = Field(None, description="Override shipping country")


class Shipment(ShipmentBase):
    """Complete shipment model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the shipment")
    status: ShipmentStatus = Field(..., description="Current shipment status")
    shipped_at: Optional[datetime] = Field(None, description="Timestamp when shipment was shipped")
    delivered_at: Optional[datetime] = Field(None, description="Timestamp when shipment was delivered")
    created_at: datetime = Field(..., description="Timestamp when the shipment was created")
    updated_at: datetime = Field(..., description="Timestamp when the shipment was last updated")

    class Config:
        from_attributes = True


class ShipmentList(BaseModel):
    """Model for shipment list responses."""
    shipments: list[Shipment]
    total: int = Field(..., description="Total number of shipments")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")


class ShipmentSummary(BaseModel):
    """Simplified shipment model for listings."""
    id: UUID = Field(..., description="Unique identifier for the shipment")
    order_id: UUID = Field(..., description="Order ID")
    status: ShipmentStatus = Field(..., description="Shipment status")
    carrier_name: Optional[str] = Field(None, description="Carrier name")
    tracking_number: Optional[str] = Field(None, description="Tracking number")
    estimated_delivery_date: Optional[date] = Field(None, description="Estimated delivery date")
    shipped_at: Optional[datetime] = Field(None, description="Ship timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")

    class Config:
        from_attributes = True


class TrackingInfo(BaseModel):
    """Model for shipment tracking information."""
    tracking_number: str = Field(..., description="Tracking number")
    status: ShipmentStatus = Field(..., description="Current status")
    carrier_name: Optional[str] = Field(None, description="Carrier name")
    estimated_delivery_date: Optional[date] = Field(None, description="Estimated delivery date")
    shipped_at: Optional[datetime] = Field(None, description="Ship timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivery timestamp")

    # Shipping address for tracking
    shipping_name: Optional[str] = Field(None, description="Shipping name")
    shipping_address1: Optional[str] = Field(None, description="Primary shipping address")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_country: Optional[str] = Field(None, description="Shipping country")