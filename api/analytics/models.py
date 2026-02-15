"""Pydantic models for analytics service."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class FarmerDashboardStats(BaseModel):
    """Model for farmer dashboard statistics."""
    total_products: int = Field(..., description="Total number of active products")
    pending_orders: int = Field(..., description="Number of pending orders")
    active_shipments: int = Field(..., description="Number of active shipments")
    total_customers: int = Field(..., description="Total number of unique customers")


class CustomerStats(BaseModel):
    """Model for customer statistics."""
    total_orders: int = Field(..., description="Total number of orders")
    total_spent: Decimal = Field(..., description="Total amount spent")
    customer_since: str = Field(..., description="Date when customer joined")


class OrderAnalytics(BaseModel):
    """Model for order analytics data."""
    orders_this_month: int = Field(..., description="Number of orders this month")
    total_revenue: Decimal = Field(..., description="Total revenue this month")
    avg_order_value: Decimal = Field(..., description="Average order value")
    fulfillment_rate: float = Field(..., description="Order fulfillment rate percentage")
    customer_satisfaction: float = Field(default=4.8, description="Customer satisfaction rating")


class OrderStatusStats(BaseModel):
    """Model for order status statistics."""
    pending: int = Field(..., description="Number of pending orders")
    preparing: int = Field(..., description="Number of orders being prepared")
    ready_to_ship: int = Field(..., description="Number of orders ready to ship")
    packaging: int = Field(default=0, description="Number of orders being packaged")


class RecentActivity(BaseModel):
    """Model for recent activity item."""
    date: str = Field(..., description="Activity date")
    action: str = Field(..., description="Action description")
    details: str = Field(..., description="Activity details")


class CustomerActivity(BaseModel):
    """Model for customer activity response."""
    activities: List[RecentActivity] = Field(default=[], description="List of recent activities")


class ProductCategoryStats(BaseModel):
    """Model for product category statistics."""
    category: str = Field(..., description="Category name")
    product_count: int = Field(..., description="Number of products in category")
    total_revenue: Decimal = Field(..., description="Total revenue from category")


class SalesMetrics(BaseModel):
    """Model for sales metrics."""
    daily_sales: List[Dict[str, Any]] = Field(default=[], description="Daily sales data")
    weekly_sales: List[Dict[str, Any]] = Field(default=[], description="Weekly sales data")
    monthly_sales: List[Dict[str, Any]] = Field(default=[], description="Monthly sales data")


class InventoryMetrics(BaseModel):
    """Model for inventory metrics."""
    total_products: int = Field(..., description="Total number of products")
    low_stock_products: int = Field(..., description="Number of products with low stock")
    out_of_stock_products: int = Field(..., description="Number of out-of-stock products")
    total_stock_value: Decimal = Field(..., description="Total value of inventory")


class CustomerMetrics(BaseModel):
    """Model for customer metrics."""
    total_customers: int = Field(..., description="Total number of customers")
    new_customers_this_month: int = Field(..., description="New customers this month")
    repeat_customers: int = Field(..., description="Number of repeat customers")
    customer_retention_rate: float = Field(..., description="Customer retention rate percentage")


class FarmerCustomerInfo(BaseModel):
    """Model for farmer customer information."""
    id: UUID = Field(..., description="Customer ID")
    name: str = Field(..., description="Customer full name")
    email: str = Field(..., description="Customer email")
    phone: Optional[str] = Field(None, description="Customer phone")
    location: str = Field(..., description="Customer location")
    status: str = Field(..., description="Customer status (New, Active, VIP)")
    total_orders: int = Field(..., description="Total number of orders")
    total_spent: Decimal = Field(..., description="Total amount spent")
    last_order: str = Field(..., description="Date of last order")
    marketing_opt_in: bool = Field(..., description="Marketing opt-in status")


class FarmerCustomersList(BaseModel):
    """Model for farmer customers list response."""
    customers: List[FarmerCustomerInfo]
    total: int = Field(..., description="Total number of customers")


class ShipmentInfo(BaseModel):
    """Model for shipment information."""
    id: UUID = Field(..., description="Shipment ID")
    order_id: UUID = Field(..., description="Order ID")
    order_number: str = Field(..., description="Order number")
    customer_name: str = Field(..., description="Customer name")
    status: str = Field(..., description="Shipment status")
    tracking_number: Optional[str] = Field(None, description="Tracking number")
    carrier_name: str = Field(..., description="Carrier name")
    shipped_at: Optional[datetime] = Field(None, description="Shipped timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivered timestamp")
    estimated_delivery_date: Optional[date] = Field(None, description="Estimated delivery date")
    created_at: datetime = Field(..., description="Created timestamp")
    shipping_address: str = Field(..., description="Shipping address")
    total_amount: Decimal = Field(..., description="Order total amount")


class ShipmentsList(BaseModel):
    """Model for shipments list response."""
    shipments: List[ShipmentInfo]
    total: int = Field(..., description="Total number of shipments")