"""Pydantic models for customers service."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class CustomerBase(BaseModel):
    """Base customer model with common fields."""
    first_name: str = Field(..., description="Customer's first name", min_length=1, max_length=100)
    last_name: str = Field(..., description="Customer's last name", min_length=1, max_length=100)
    email: str = Field(..., description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    address_line1: Optional[str] = Field(None, description="Primary address line")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(default="Israel", description="Country")
    marketing_opt_in: bool = Field(default=False, description="Whether customer opted in for marketing")


class CustomerCreate(CustomerBase):
    """Model for creating a new customer."""
    pass


class CustomerUpdate(BaseModel):
    """Model for updating customer information."""
    first_name: Optional[str] = Field(None, description="Customer's first name", min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, description="Customer's last name", min_length=1, max_length=100)
    email: Optional[str] = Field(None, description="Customer's email address")
    phone: Optional[str] = Field(None, description="Customer's phone number")
    address_line1: Optional[str] = Field(None, description="Primary address line")
    address_line2: Optional[str] = Field(None, description="Secondary address line")
    city: Optional[str] = Field(None, description="City")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")
    marketing_opt_in: Optional[bool] = Field(None, description="Whether customer opted in for marketing")


class Customer(CustomerBase):
    """Complete customer model with all fields."""
    id: UUID = Field(..., description="Unique identifier for the customer")
    created_at: datetime = Field(..., description="Timestamp when the customer was created")
    updated_at: datetime = Field(..., description="Timestamp when the customer was last updated")

    class Config:
        from_attributes = True


class CustomerList(BaseModel):
    """Model for customer list responses."""
    customers: list[Customer]
    total: int = Field(..., description="Total number of customers")
    page: int = Field(default=1, description="Current page number")
    size: int = Field(default=50, description="Number of items per page")