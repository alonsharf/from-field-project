"""Authentication models for From Field to You API."""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class RegisterCustomerRequest(BaseModel):
    """Customer registration request model."""
    first_name: str
    last_name: str
    email: str
    password: str
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "Israel"


class AuthResponse(BaseModel):
    """Authentication response model."""
    id: str
    name: str
    email: str
    role: str
    # Role-specific fields
    farm_name: Optional[str] = None  # For farmers
    first_name: Optional[str] = None  # For customers
    last_name: Optional[str] = None   # For customers