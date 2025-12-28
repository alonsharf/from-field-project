"""Database base configuration and utilities."""

from .models import Base
from .session import engine, async_engine, create_tables, get_db, get_async_db, get_sync_session

# Import all models to ensure they're registered with SQLAlchemy
from .models import (
    Farmer,
    Customer,
    Product,
    Order,
    Purchase,
    Shipment,
    CustomerSession,
    Cart,
    CartItem,
    FarmerProfile,
    OrderStatus,
    PaymentStatus,
    ShipmentStatus,
    CartStatus,
    UserType,
)

__all__ = [
    "Base",
    "engine",
    "async_engine",
    "create_tables",
    "get_db",
    "get_async_db",
    "get_sync_session",
    "Farmer",
    "Customer",
    "Product",
    "Order",
    "Purchase",
    "Shipment",
    "CustomerSession",
    "Cart",
    "CartItem",
    "FarmerProfile",
    "OrderStatus",
    "PaymentStatus",
    "ShipmentStatus",
    "CartStatus",
    "UserType",
]