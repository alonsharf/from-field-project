"""Analytics service layer for database operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from packages.db.models import (
    Farmer as FarmerModel,
    Customer as CustomerModel,
    Product as ProductModel,
    Order as OrderModel,
    OrderItem as OrderItemModel,
    Shipment as ShipmentModel,
    OrderStatus,
    PaymentStatus,
    ShipmentStatus
)
from .models import (
    FarmerDashboardStats,
    CustomerStats,
    OrderAnalytics,
    OrderStatusStats,
    RecentActivity,
    FarmerCustomerInfo,
    InventoryMetrics,
    CustomerMetrics,
    ShipmentInfo
)


class AnalyticsService:
    """Service class for analytics-related database operations."""

    @staticmethod
    async def get_farmer_dashboard_stats(
        db: AsyncSession,
        farmer_id: Optional[UUID] = None
    ) -> FarmerDashboardStats:
        """Get dashboard statistics for farmer portal."""
        # If no farmer_id provided, get stats for all farmers (admin view)
        farmer_filter = ProductModel.farmer_id == farmer_id if farmer_id else True
        order_filter = OrderModel.farmer_id == farmer_id if farmer_id else True

        # Total active products
        total_products_result = await db.execute(
            select(func.count(ProductModel.id)).filter(
                and_(ProductModel.is_active == True, farmer_filter)
            )
        )
        total_products = total_products_result.scalar() or 0

        # Pending orders
        pending_orders_result = await db.execute(
            select(func.count(OrderModel.id)).filter(
                and_(
                    OrderModel.status.in_([OrderStatus.PAID, OrderStatus.PENDING_PAYMENT]),
                    order_filter
                )
            )
        )
        pending_orders = pending_orders_result.scalar() or 0

        # Active shipments
        active_shipments_result = await db.execute(
            select(func.count(ShipmentModel.id))
            .select_from(ShipmentModel)
            .join(OrderModel)
            .filter(
                and_(
                    ShipmentModel.status.in_([ShipmentStatus.PACKED, ShipmentStatus.SHIPPED]),
                    order_filter
                )
            )
        )
        active_shipments = active_shipments_result.scalar() or 0

        # Total unique customers
        total_customers_result = await db.execute(
            select(func.count(func.distinct(OrderModel.customer_id))).filter(order_filter)
        )
        total_customers = total_customers_result.scalar() or 0

        return FarmerDashboardStats(
            total_products=total_products,
            pending_orders=pending_orders,
            active_shipments=active_shipments,
            total_customers=total_customers
        )

    @staticmethod
    async def get_customer_stats(
        db: AsyncSession,
        customer_id: Optional[UUID] = None
    ) -> CustomerStats:
        """Get customer account statistics."""
        if not customer_id:
            # Return demo stats
            return CustomerStats(
                total_orders=0,
                total_spent=Decimal('0.0'),
                customer_since='2024-11-24'
            )

        # Get order statistics
        total_orders_result = await db.execute(
            select(func.count(OrderModel.id)).filter(OrderModel.customer_id == customer_id)
        )
        total_orders = total_orders_result.scalar() or 0

        total_spent_result = await db.execute(
            select(func.sum(OrderModel.total_amount)).filter(OrderModel.customer_id == customer_id)
        )
        total_spent = total_spent_result.scalar() or 0

        # Get customer creation date
        customer_result = await db.execute(
            select(CustomerModel).filter(CustomerModel.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        customer_since = customer.created_at.strftime('%Y-%m-%d') if customer and customer.created_at else '2024-11-24'

        return CustomerStats(
            total_orders=total_orders,
            total_spent=Decimal(str(total_spent)),
            customer_since=customer_since
        )

    @staticmethod
    async def get_order_analytics(
        db: AsyncSession,
        farmer_id: Optional[UUID] = None
    ) -> OrderAnalytics:
        """Get order analytics data."""
        # Base query
        query = select(OrderModel)
        if farmer_id:
            query = query.filter(OrderModel.farmer_id == farmer_id)

        # Get orders from this month
        this_month = datetime.now().replace(day=1)
        orders_this_month_result = await db.execute(
            query.filter(OrderModel.created_at >= this_month)
        )
        orders_this_month = orders_this_month_result.scalars().all()

        # Calculate metrics
        total_orders = len(orders_this_month)
        total_revenue = sum(order.total_amount for order in orders_this_month)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Fulfilled orders rate
        fulfilled_orders = [o for o in orders_this_month if o.status == OrderStatus.FULFILLED]
        fulfillment_rate = (len(fulfilled_orders) / total_orders * 100) if total_orders > 0 else 0

        return OrderAnalytics(
            orders_this_month=total_orders,
            total_revenue=Decimal(str(total_revenue)),
            avg_order_value=Decimal(str(avg_order_value)),
            fulfillment_rate=fulfillment_rate,
            customer_satisfaction=4.8  # Default placeholder
        )

    @staticmethod
    async def get_farmer_order_stats(
        db: AsyncSession,
        farmer_id: UUID
    ) -> OrderStatusStats:
        """Get farmer order statistics by status."""
        # Get order counts by status
        pending_count_result = await db.execute(
            select(func.count(OrderModel.id)).filter(
                and_(
                    OrderModel.farmer_id == farmer_id,
                    OrderModel.status.in_([OrderStatus.PAID, OrderStatus.PENDING_PAYMENT])
                )
            )
        )
        pending_count = pending_count_result.scalar() or 0

        preparing_count_result = await db.execute(
            select(func.count(OrderModel.id)).filter(
                and_(
                    OrderModel.farmer_id == farmer_id,
                    OrderModel.status == OrderStatus.PAID
                )
            )
        )
        preparing_count = preparing_count_result.scalar() or 0

        fulfilled_count_result = await db.execute(
            select(func.count(OrderModel.id)).filter(
                and_(
                    OrderModel.farmer_id == farmer_id,
                    OrderModel.status == OrderStatus.FULFILLED
                )
            )
        )
        fulfilled_count = fulfilled_count_result.scalar() or 0

        return OrderStatusStats(
            pending=pending_count,
            preparing=preparing_count,
            ready_to_ship=fulfilled_count,
            packaging=0  # Placeholder
        )

    @staticmethod
    async def get_customer_recent_activity(
        db: AsyncSession,
        customer_id: Optional[UUID] = None,
        limit: int = 10
    ) -> List[RecentActivity]:
        """Get recent customer account activity."""
        if not customer_id:
            # Return empty list for demo
            return []

        activities = []

        # Get recent orders
        recent_orders_result = await db.execute(
            select(OrderModel)
            .filter(OrderModel.customer_id == customer_id)
            .order_by(desc(OrderModel.created_at))
            .limit(limit)
        )
        recent_orders = recent_orders_result.scalars().all()

        for order in recent_orders:
            activities.append(RecentActivity(
                date=order.created_at.strftime('%Y-%m-%d'),
                action='Order placed' if order.status == OrderStatus.PENDING_PAYMENT else 'Order completed',
                details=f"ORD-{order.created_at.strftime('%Y%m%d')}-{str(order.id)[:8]}"
            ))

        # Sort by date (most recent first)
        activities.sort(key=lambda x: x.date, reverse=True)

        return activities[:limit]

    @staticmethod
    async def get_farmer_customers(
        db: AsyncSession,
        farmer_id: UUID,
        limit: int = 50
    ) -> tuple[List[FarmerCustomerInfo], int]:
        """Get customers who have ordered from a specific farmer."""
        # Get customers who have placed orders with this farmer
        query = (
            select(CustomerModel)
            .join(OrderModel)
            .filter(OrderModel.farmer_id == farmer_id)
            .distinct()
            .limit(limit)
        )
        customers_result = await db.execute(query)
        customers = customers_result.scalars().all()

        customer_list = []
        for customer in customers:
            # Get customer order statistics
            customer_orders_result = await db.execute(
                select(OrderModel).filter(
                    and_(
                        OrderModel.customer_id == customer.id,
                        OrderModel.farmer_id == farmer_id
                    )
                )
            )
            customer_orders = customer_orders_result.scalars().all()

            total_orders = len(customer_orders)
            total_spent = sum(order.total_amount for order in customer_orders)
            last_order = max(customer_orders, key=lambda x: x.created_at).created_at if customer_orders else None

            # Determine status based on order history
            status = "VIP" if total_orders >= 10 else "Active" if total_orders >= 3 else "New"

            customer_list.append(FarmerCustomerInfo(
                id=customer.id,
                name=f"{customer.first_name} {customer.last_name}",
                email=customer.email,
                phone=customer.phone,
                location=f"{customer.city}, {customer.country}" if customer.city else 'N/A',
                status=status,
                total_orders=total_orders,
                total_spent=Decimal(str(total_spent)),
                last_order=last_order.strftime('%Y-%m-%d') if last_order else 'Never',
                marketing_opt_in=customer.marketing_opt_in
            ))

        return customer_list, len(customer_list)

    @staticmethod
    async def get_farmer_shipments(
        db: AsyncSession,
        farmer_id: UUID,
        status: Optional[str] = None,
        limit: int = 50
    ) -> tuple[List[ShipmentInfo], int]:
        """Get shipments for a farmer's orders."""
        query = (
            select(ShipmentModel)
            .join(OrderModel)
            .join(CustomerModel)
            .filter(OrderModel.farmer_id == farmer_id)
        )

        if status:
            query = query.filter(ShipmentModel.status == status)

        query = query.order_by(ShipmentModel.created_at.desc()).limit(limit)
        shipments_result = await db.execute(query)
        shipments = shipments_result.scalars().all()

        shipment_list = []
        for shipment in shipments:
            # Load related data
            order_result = await db.execute(
                select(OrderModel)
                .options(selectinload(OrderModel.customer))
                .filter(OrderModel.id == shipment.order_id)
            )
            order = order_result.scalar_one_or_none()

            if order:
                customer = order.customer
                shipment_list.append(ShipmentInfo(
                    id=shipment.id,
                    order_id=order.id,
                    order_number=f"ORD-{str(order.id)[:8]}",
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    status=shipment.status.value if hasattr(shipment.status, 'value') else shipment.status,
                    tracking_number=shipment.tracking_number,
                    carrier_name=shipment.carrier_name or 'Farm Delivery',
                    shipped_at=shipment.shipped_at,
                    delivered_at=shipment.delivered_at,
                    estimated_delivery_date=shipment.estimated_delivery_date,
                    created_at=shipment.created_at,
                    shipping_address=f"{order.shipping_address1}, {order.shipping_city}",
                    total_amount=order.total_amount
                ))

        return shipment_list, len(shipment_list)

    @staticmethod
    async def get_inventory_metrics(
        db: AsyncSession,
        farmer_id: Optional[UUID] = None
    ) -> InventoryMetrics:
        """Get inventory metrics."""
        farmer_filter = ProductModel.farmer_id == farmer_id if farmer_id else True

        # Total products
        total_products_result = await db.execute(
            select(func.count(ProductModel.id)).filter(farmer_filter)
        )
        total_products = total_products_result.scalar() or 0

        # Low stock products (less than 10)
        low_stock_result = await db.execute(
            select(func.count(ProductModel.id)).filter(
                and_(
                    ProductModel.stock_quantity <= 10,
                    ProductModel.stock_quantity > 0,
                    farmer_filter
                )
            )
        )
        low_stock_products = low_stock_result.scalar() or 0

        # Out of stock products
        out_of_stock_result = await db.execute(
            select(func.count(ProductModel.id)).filter(
                and_(
                    ProductModel.stock_quantity <= 0,
                    farmer_filter
                )
            )
        )
        out_of_stock_products = out_of_stock_result.scalar() or 0

        # Total stock value
        stock_value_result = await db.execute(
            select(func.sum(ProductModel.stock_quantity * ProductModel.price_per_unit)).filter(farmer_filter)
        )
        total_stock_value = stock_value_result.scalar() or 0

        return InventoryMetrics(
            total_products=total_products,
            low_stock_products=low_stock_products,
            out_of_stock_products=out_of_stock_products,
            total_stock_value=Decimal(str(total_stock_value))
        )

    @staticmethod
    async def get_customer_metrics(
        db: AsyncSession,
        farmer_id: Optional[UUID] = None
    ) -> CustomerMetrics:
        """Get customer metrics."""
        # Base query filter
        order_filter = OrderModel.farmer_id == farmer_id if farmer_id else True

        # Total customers
        total_customers_result = await db.execute(
            select(func.count(func.distinct(OrderModel.customer_id))).filter(order_filter)
        )
        total_customers = total_customers_result.scalar() or 0

        # New customers this month
        this_month = datetime.now().replace(day=1)
        new_customers_result = await db.execute(
            select(func.count(func.distinct(OrderModel.customer_id)))
            .filter(
                and_(
                    OrderModel.created_at >= this_month,
                    order_filter
                )
            )
        )
        new_customers_this_month = new_customers_result.scalar() or 0

        # Repeat customers (customers with more than 1 order)
        repeat_customers_result = await db.execute(
            select(func.count()).select_from(
                select(OrderModel.customer_id)
                .filter(order_filter)
                .group_by(OrderModel.customer_id)
                .having(func.count(OrderModel.id) > 1)
            )
        )
        repeat_customers = repeat_customers_result.scalar() or 0

        # Customer retention rate
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0

        return CustomerMetrics(
            total_customers=total_customers,
            new_customers_this_month=new_customers_this_month,
            repeat_customers=repeat_customers,
            customer_retention_rate=retention_rate
        )