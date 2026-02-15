"""Orders service layer for database operations."""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload

from packages.db.models import (
    Order as OrderModel,
    OrderItem as OrderItemModel,
    Product as ProductModel,
    OrderStatus,
    PaymentStatus
)
from .models import OrderCreate, OrderUpdate, OrderItemCreate


class OrderService:
    """Service class for order-related database operations."""

    @staticmethod
    async def get_orders(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        customer_id: Optional[UUID] = None,
        farmer_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None
    ) -> tuple[List[OrderModel], int]:
        """Get orders with pagination and filtering."""
        query = select(OrderModel)
        filters = []

        if customer_id:
            filters.append(OrderModel.customer_id == customer_id)
        if farmer_id:
            filters.append(OrderModel.farmer_id == farmer_id)
        if status:
            filters.append(OrderModel.status == status)
        if payment_status:
            filters.append(OrderModel.payment_status == payment_status)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(OrderModel.id)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results with related data
        query = (
            query.options(
                selectinload(OrderModel.customer),
                selectinload(OrderModel.farmer),
                selectinload(OrderModel.order_items).selectinload(OrderItemModel.product)
            )
            .offset(skip)
            .limit(limit)
            .order_by(OrderModel.created_at.desc())
        )
        result = await db.execute(query)
        orders = result.scalars().all()

        return orders, total

    @staticmethod
    async def get_order(db: AsyncSession, order_id: UUID) -> Optional[OrderModel]:
        """Get an order by ID with all related data."""
        query = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(
                selectinload(OrderModel.customer),
                selectinload(OrderModel.farmer),
                selectinload(OrderModel.order_items).selectinload(OrderItemModel.product),
                selectinload(OrderModel.shipment)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_order(db: AsyncSession, order_data: OrderCreate) -> OrderModel:
        """Create a new order with purchase items."""
        try:
            # Create the order
            order_dict = order_data.dict(exclude={'items'})
            db_order = OrderModel(**order_dict)
            db.add(db_order)
            await db.flush()  # Get the order ID

            # Create purchase items and calculate totals
            subtotal = Decimal('0')
            for item in order_data.items:
                # Get product to verify price and stock
                product = await db.get(ProductModel, item.product_id)
                if not product:
                    raise ValueError(f"Product {item.product_id} not found")

                if product.stock_quantity < item.quantity:
                    raise ValueError(f"Insufficient stock for product {product.name}")

                # Calculate line totals
                line_subtotal = item.quantity * item.unit_price
                line_total = line_subtotal - item.line_discount

                # Create purchase item
                order_item = OrderItemModel(
                    order_id=db_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_subtotal=line_subtotal,
                    line_discount=item.line_discount,
                    line_total=line_total
                )
                db.add(order_item)
                subtotal += line_total

                # Update product stock
                product.stock_quantity -= item.quantity

            # Update order totals
            db_order.subtotal_amount = subtotal
            db_order.total_amount = subtotal + db_order.shipping_amount - db_order.discount_amount

            await db.commit()
            await db.refresh(db_order)

            # Load the order with all related data
            return await OrderService.get_order(db, db_order.id)

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_order(
        db: AsyncSession,
        order_id: UUID,
        order_update: OrderUpdate
    ) -> Optional[OrderModel]:
        """Update an order."""
        # Get the order first
        order = await OrderService.get_order(db, order_id)
        if not order:
            return None

        # Update only provided fields
        update_data = order_update.dict(exclude_unset=True)
        if update_data:
            # Recalculate total if shipping or discount changed
            if 'shipping_amount' in update_data or 'discount_amount' in update_data:
                shipping_amount = update_data.get('shipping_amount', order.shipping_amount)
                discount_amount = update_data.get('discount_amount', order.discount_amount)
                update_data['total_amount'] = order.subtotal_amount + shipping_amount - discount_amount

            stmt = (
                update(OrderModel)
                .where(OrderModel.id == order_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(order)

        return order

    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: UUID,
        status: OrderStatus
    ) -> Optional[OrderModel]:
        """Update order status."""
        order = await OrderService.get_order(db, order_id)
        if not order:
            return None

        stmt = (
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(status=status)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        order_id: UUID,
        payment_status: PaymentStatus,
        payment_reference: Optional[str] = None
    ) -> Optional[OrderModel]:
        """Update payment status."""
        order = await OrderService.get_order(db, order_id)
        if not order:
            return None

        update_data = {"payment_status": payment_status}
        if payment_reference:
            update_data["payment_reference"] = payment_reference

        stmt = (
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(order)

        return order

    @staticmethod
    async def cancel_order(db: AsyncSession, order_id: UUID) -> Optional[OrderModel]:
        """Cancel an order and restore product stock."""
        order = await OrderService.get_order(db, order_id)
        if not order:
            return None

        if order.status in [OrderStatus.CANCELLED, OrderStatus.FULFILLED]:
            raise ValueError(f"Cannot cancel order with status {order.status}")

        try:
            # Restore stock for all purchase items
            for order_item in order.order_items:
                product = await db.get(ProductModel, order_item.product_id)
                if product:
                    product.stock_quantity += order_item.quantity

            # Update order status
            order.status = OrderStatus.CANCELLED

            await db.commit()
            await db.refresh(order)
            return order

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: UUID) -> bool:
        """Delete an order (only if in DRAFT status)."""
        order = await OrderService.get_order(db, order_id)
        if not order:
            return False

        if order.status != OrderStatus.DRAFT:
            raise ValueError("Can only delete orders in DRAFT status")

        # Restore stock first
        for order_item in order.order_items:
            product = await db.get(ProductModel, order_item.product_id)
            if product:
                product.stock_quantity += order_item.quantity

        stmt = delete(OrderModel).where(OrderModel.id == order_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def get_customer_orders(
        db: AsyncSession,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[OrderModel], int]:
        """Get all orders for a specific customer."""
        return await OrderService.get_orders(
            db=db, skip=skip, limit=limit, customer_id=customer_id
        )

    @staticmethod
    async def get_farmer_orders(
        db: AsyncSession,
        farmer_id: UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[OrderStatus] = None
    ) -> tuple[List[OrderModel], int]:
        """Get all orders for a specific farmer."""
        return await OrderService.get_orders(
            db=db, skip=skip, limit=limit, farmer_id=farmer_id, status=status
        )