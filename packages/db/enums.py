"""Centralized enums for the agricultural supply chain system."""

from enum import Enum


# Cart and Shopping Enums
class CartStatus(Enum):
    """Shopping cart status enumeration."""
    ACTIVE = "ACTIVE"
    ABANDONED = "ABANDONED"
    CONVERTED = "CONVERTED"


# User and Customer Enums
class UserType(Enum):
    """User type enumeration."""
    FARMER = "FARMER"
    CUSTOMER = "CUSTOMER"


class CustomerStatus(Enum):
    """Customer status enumeration."""
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    VIP = "VIP"


# Communication Enums
class CommunicationType(Enum):
    """Communication type enumeration."""
    PRODUCT_UPDATE = "PRODUCT_UPDATE"
    SEASONAL_OFFER = "SEASONAL_OFFER"
    PERSONAL_MESSAGE = "PERSONAL_MESSAGE"
    ORDER_FOLLOWUP = "ORDER_FOLLOWUP"


# Order Management Enums
class OrderStatus(str, Enum):
    """Order status enumeration."""
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    FULFILLED = "FULFILLED"


# Payment Enums
class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentProvider(str, Enum):
    """Payment provider enumeration."""
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"


# Shipment Enums
class ShipmentStatus(str, Enum):
    """Shipment status enumeration."""
    PENDING = "PENDING"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"