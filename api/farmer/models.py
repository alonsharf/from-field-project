"""Pydantic models for farmers service."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class FarmerBase(BaseModel):
    """Base farmer model with common fields."""
    name: str = Field(..., description="Person name of the farmer", min_length=1, max_length=200)
    farm_name: str = Field(..., description="Brand name used in UI", min_length=1, max_length=200)
    email: str = Field(..., description="Email address of the farmer")
    phone: Optional[str] = Field(None, description="Phone number of the farmer")
    address_line1: Optional[str] = Field(None, description="Primary address line")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(default="Israel", description="Country")
    is_active: bool = Field(default=True, description="Whether the farmer account is active")


class FarmerCreate(FarmerBase):
    """Model for creating a new farmer."""
    pass


class FarmerUpdate(BaseModel):
    """Model for updating farmer information."""
    name: Optional[str] = Field(None, description="Person name of the farmer", min_length=1, max_length=200)
    farm_name: Optional[str] = Field(None, description="Brand name used in UI", min_length=1, max_length=200)
    email: Optional[str] = Field(None, description="Email address of the farmer")
    phone: Optional[str] = Field(None, description="Phone number of the farmer")
    address_line1: Optional[str] = Field(None, description="Primary address line")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    is_active: Optional[bool] = Field(None, description="Whether the farmer account is active")


class Farmer(FarmerBase):
    """Complete farmer model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the farmer")
    created_at: datetime = Field(..., description="Timestamp when the farmer was created")
    updated_at: datetime = Field(..., description="Timestamp when the farmer was last updated")

    class Config:
        from_attributes = True


class FarmerList(BaseModel):
    """Model for farmer list responses."""
    farmers: list[Farmer]
    total: int = Field(..., description="Total number of farmers")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")