"""SQLAlchemy ORM models for the agricultural supply chain system."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Numeric, Date,
    ForeignKey, CheckConstraint, Index, UUID, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.sql import func

# Import centralized enums
from .enums import (
    CartStatus, UserType, CustomerStatus, CommunicationType,
    OrderStatus, PaymentStatus, ShipmentStatus
)


Base = declarative_base()


class Category(Base):
    """Product category table model."""
    __tablename__ = "category"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="category")

    # Indexes
    __table_args__ = (
        Index('idx_category_name', 'name'),
    )


class UnitLabel(Base):
    """Unit label table model."""
    __tablename__ = "unit_label"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False, unique=True)
    abbreviation = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="unit_label")

    # Indexes
    __table_args__ = (
        Index('idx_unit_label_name', 'name'),
        Index('idx_unit_label_abbreviation', 'abbreviation'),
    )


class Farmer(Base):
    """Farmer table model with merged profile data."""
    __tablename__ = "farmer"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(Text, nullable=False)
    farm_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    phone = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(Text)
    postal_code = Column(Text)
    country = Column(Text, default="Israel")
    is_active = Column(Boolean, nullable=False, default=True)

    # Merged from farmer_profile table
    description = Column(Text)
    farm_type = Column(Text)  # 'Organic', 'Conventional', 'Hydroponic', etc.
    farm_size_acres = Column(Numeric(10, 2))
    established_year = Column(Numeric(4, 0))
    certifications = Column(Text)  # JSON string of certifications
    website = Column(Text)
    facebook_url = Column(Text)
    instagram_handle = Column(Text)
    twitter_handle = Column(Text)
    business_hours = Column(Text)
    profile_image_url = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="farmer")
    orders = relationship("Order", back_populates="farmer")


class Customer(Base):
    """Customer table model."""
    __tablename__ = "customer"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    phone = Column(Text)
    address_line1 = Column(Text)
    address_line2 = Column(Text)
    city = Column(Text)
    postal_code = Column(Text)
    country = Column(Text, default="Israel")
    marketing_opt_in = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="customer")


class Product(Base):
    """Product table model with foreign keys to category and unit_label."""
    __tablename__ = "product"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    farmer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("farmer.id"), nullable=False)
    category_id = Column(PostgresUUID(as_uuid=True), ForeignKey("category.id"), nullable=False)
    unit_label_id = Column(PostgresUUID(as_uuid=True), ForeignKey("unit_label.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    unit_size = Column(Numeric(10, 2))
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="ILS")
    stock_quantity = Column(Numeric(12, 2), nullable=False, default=0)
    min_order_quantity = Column(Numeric(12, 2), nullable=False, default=1)
    max_order_quantity = Column(Numeric(12, 2))
    is_active = Column(Boolean, nullable=False, default=True)
    is_organic = Column(Boolean, nullable=False, default=False)
    available_from = Column(Date)
    available_until = Column(Date)
    image_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("Farmer", back_populates="products")
    category = relationship("Category", back_populates="products")
    unit_label = relationship("UnitLabel", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

    # Indexes
    __table_args__ = (
        Index('idx_product_farmer_id', 'farmer_id'),
        Index('idx_product_category_id', 'category_id'),
        Index('idx_product_unit_label_id', 'unit_label_id'),
        Index('idx_product_is_active', 'is_active'),
    )


class Order(Base):
    """Orders table model."""
    __tablename__ = "orders"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    customer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    farmer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("farmer.id"), nullable=False)

    status = Column(Enum(OrderStatus, name='order_status'), nullable=False, default=OrderStatus.DRAFT)
    payment_status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False, default=PaymentStatus.PENDING)
    payment_provider = Column(Text)
    payment_reference = Column(Text)

    subtotal_amount = Column(Numeric(12, 2), nullable=False, default=0)
    shipping_amount = Column(Numeric(12, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(12, 2), nullable=False, default=0)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="ILS")

    # Shipping address snapshot
    shipping_name = Column(Text)
    shipping_phone = Column(Text)
    shipping_address1 = Column(Text)
    shipping_address2 = Column(Text)
    shipping_city = Column(Text)
    shipping_postal_code = Column(Text)
    shipping_country = Column(Text, default="Israel")

    customer_notes = Column(Text)
    internal_notes = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    farmer = relationship("Farmer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    shipment = relationship("Shipment", back_populates="order", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_orders_customer_id', 'customer_id'),
        Index('idx_orders_farmer_id', 'farmer_id'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_created_at', 'created_at'),
    )


class OrderItem(Base):
    """Order item (individual items within an order) table model."""
    __tablename__ = "order_item"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(PostgresUUID(as_uuid=True), ForeignKey("product.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_subtotal = Column(Numeric(12, 2), nullable=False)
    line_discount = Column(Numeric(12, 2), nullable=False, default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        Index('idx_order_item_order_id', 'order_id'),
        Index('idx_order_item_product_id', 'product_id'),
    )


class Shipment(Base):
    """Shipment table model."""
    __tablename__ = "shipment"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(Enum(ShipmentStatus, name='shipment_status'), nullable=False, default=ShipmentStatus.PENDING)
    carrier_name = Column(Text)
    tracking_number = Column(Text)
    estimated_delivery_date = Column(Date)
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))

    # Optional address override
    shipping_name = Column(Text)
    shipping_phone = Column(Text)
    shipping_address1 = Column(Text)
    shipping_address2 = Column(Text)
    shipping_city = Column(Text)
    shipping_postal_code = Column(Text)
    shipping_country = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="shipment")

    # Indexes
    __table_args__ = (
        Index('idx_shipment_order_id', 'order_id'),
        Index('idx_shipment_status', 'status'),
    )


class CustomerSession(Base):
    """Customer session management for Streamlit app."""
    __tablename__ = "customer_session"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id = Column(Text, nullable=False, unique=True)
    customer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("customer.id"), nullable=True)
    user_type = Column(Enum(UserType, name='user_type'), nullable=False, default=UserType.CUSTOMER)
    is_active = Column(Boolean, nullable=False, default=True)
    last_activity = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    customer = relationship("Customer")

    # Indexes
    __table_args__ = (
        Index('idx_customer_session_session_id', 'session_id'),
        Index('idx_customer_session_customer_id', 'customer_id'),
        Index('idx_customer_session_last_activity', 'last_activity'),
    )


class Cart(Base):
    """Shopping cart for customers."""
    __tablename__ = "cart"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    session_id = Column(Text, nullable=False)  # For anonymous carts
    customer_id = Column(PostgresUUID(as_uuid=True), ForeignKey("customer.id"), nullable=True)
    status = Column(Enum(CartStatus, name='cart_status'), nullable=False, default=CartStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer")
    cart_items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_cart_session_id', 'session_id'),
        Index('idx_cart_customer_id', 'customer_id'),
        Index('idx_cart_status', 'status'),
    )


class CartItem(Base):
    """Items in shopping cart."""
    __tablename__ = "cart_item"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    cart_id = Column(PostgresUUID(as_uuid=True), ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(PostgresUUID(as_uuid=True), ForeignKey("product.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Price at time of adding to cart
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product")

    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_cart_quantity_positive'),
        Index('idx_cart_item_cart_id', 'cart_id'),
        Index('idx_cart_item_product_id', 'product_id'),
    )



