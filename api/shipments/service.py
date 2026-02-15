"""Shipments service layer for database operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload

from packages.db.models import (
    Shipment as ShipmentModel,
    Order as OrderModel,
    ShipmentStatus
)
from .models import ShipmentCreate, ShipmentUpdate


class ShipmentService:
    """Service class for shipment-related database operations."""

    @staticmethod
    async def get_shipments(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        status: Optional[ShipmentStatus] = None,
        carrier_name: Optional[str] = None
    ) -> tuple[List[ShipmentModel], int]:
        """Get shipments with pagination and filtering."""
        query = select(ShipmentModel)
        filters = []

        if status:
            filters.append(ShipmentModel.status == status)
        if carrier_name:
            filters.append(ShipmentModel.carrier_name.ilike(f"%{carrier_name}%"))

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(ShipmentModel.id)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results with order info
        query = (
            query.options(
                selectinload(ShipmentModel.order).selectinload(OrderModel.customer),
                selectinload(ShipmentModel.order).selectinload(OrderModel.farmer)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ShipmentModel.created_at.desc())
        )
        result = await db.execute(query)
        shipments = result.scalars().all()

        return shipments, total

    @staticmethod
    async def get_shipment(db: AsyncSession, shipment_id: UUID) -> Optional[ShipmentModel]:
        """Get a shipment by ID with order details."""
        query = (
            select(ShipmentModel)
            .where(ShipmentModel.id == shipment_id)
            .options(
                selectinload(ShipmentModel.order).selectinload(OrderModel.customer),
                selectinload(ShipmentModel.order).selectinload(OrderModel.farmer)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_shipment_by_order(db: AsyncSession, order_id: UUID) -> Optional[ShipmentModel]:
        """Get shipment by order ID."""
        query = (
            select(ShipmentModel)
            .where(ShipmentModel.order_id == order_id)
            .options(
                selectinload(ShipmentModel.order).selectinload(OrderModel.customer),
                selectinload(ShipmentModel.order).selectinload(OrderModel.farmer)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_shipment_by_tracking(db: AsyncSession, tracking_number: str) -> Optional[ShipmentModel]:
        """Get shipment by tracking number."""
        query = (
            select(ShipmentModel)
            .where(ShipmentModel.tracking_number == tracking_number)
            .options(
                selectinload(ShipmentModel.order).selectinload(OrderModel.customer),
                selectinload(ShipmentModel.order).selectinload(OrderModel.farmer)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_shipment(db: AsyncSession, shipment_data: ShipmentCreate) -> ShipmentModel:
        """Create a new shipment."""
        # Check if order exists and doesn't already have a shipment
        order = await db.get(OrderModel, shipment_data.order_id)
        if not order:
            raise ValueError("Order not found")

        existing_shipment = await ShipmentService.get_shipment_by_order(db, shipment_data.order_id)
        if existing_shipment:
            raise ValueError("Order already has a shipment")

        db_shipment = ShipmentModel(**shipment_data.model_dump())
        db.add(db_shipment)
        await db.commit()
        await db.refresh(db_shipment)

        # Load with order details
        return await ShipmentService.get_shipment(db, db_shipment.id)

    @staticmethod
    async def update_shipment(
        db: AsyncSession,
        shipment_id: UUID,
        shipment_update: ShipmentUpdate
    ) -> Optional[ShipmentModel]:
        """Update a shipment."""
        # Get the shipment first
        shipment = await ShipmentService.get_shipment(db, shipment_id)
        if not shipment:
            return None

        # Update only provided fields
        update_data = shipment_update.model_dump(exclude_unset=True)
        if update_data:
            stmt = (
                update(ShipmentModel)
                .where(ShipmentModel.id == shipment_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(shipment)

        return shipment

    @staticmethod
    async def update_shipment_status(
        db: AsyncSession,
        shipment_id: UUID,
        status: ShipmentStatus,
        update_timestamps: bool = True
    ) -> Optional[ShipmentModel]:
        """Update shipment status with automatic timestamp updates."""
        shipment = await ShipmentService.get_shipment(db, shipment_id)
        if not shipment:
            return None

        update_data = {"status": status}

        # Automatically update timestamps based on status
        if update_timestamps:
            now = datetime.now(UTC)
            if status == ShipmentStatus.SHIPPED and not shipment.shipped_at:
                update_data["shipped_at"] = now
            elif status == ShipmentStatus.DELIVERED and not shipment.delivered_at:
                update_data["delivered_at"] = now

        stmt = (
            update(ShipmentModel)
            .where(ShipmentModel.id == shipment_id)
            .values(**update_data)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(shipment)

        return shipment

    @staticmethod
    async def ship_order(
        db: AsyncSession,
        order_id: UUID,
        carrier_name: str,
        tracking_number: str
    ) -> ShipmentModel:
        """Ship an order by creating/updating shipment."""
        # Check if shipment already exists
        shipment = await ShipmentService.get_shipment_by_order(db, order_id)

        if shipment:
            # Update existing shipment
            shipment_update = ShipmentUpdate(
                carrier_name=carrier_name,
                tracking_number=tracking_number,
                status=ShipmentStatus.SHIPPED,
                shipped_at=datetime.now(UTC)
            )
            return await ShipmentService.update_shipment(db, shipment.id, shipment_update)
        else:
            # Create new shipment
            shipment_create = ShipmentCreate(
                order_id=order_id,
                carrier_name=carrier_name,
                tracking_number=tracking_number
            )
            shipment = await ShipmentService.create_shipment(db, shipment_create)
            return await ShipmentService.update_shipment_status(
                db, shipment.id, ShipmentStatus.SHIPPED
            )

    @staticmethod
    async def deliver_shipment(
        db: AsyncSession,
        shipment_id: UUID
    ) -> Optional[ShipmentModel]:
        """Mark shipment as delivered."""
        return await ShipmentService.update_shipment_status(
            db, shipment_id, ShipmentStatus.DELIVERED, update_timestamps=True
        )

    @staticmethod
    async def cancel_shipment(
        db: AsyncSession,
        shipment_id: UUID
    ) -> Optional[ShipmentModel]:
        """Cancel a shipment."""
        shipment = await ShipmentService.get_shipment(db, shipment_id)
        if not shipment:
            return None

        if shipment.status == ShipmentStatus.DELIVERED:
            raise ValueError("Cannot cancel delivered shipment")

        return await ShipmentService.update_shipment_status(
            db, shipment_id, ShipmentStatus.CANCELLED, update_timestamps=False
        )

    @staticmethod
    async def delete_shipment(db: AsyncSession, shipment_id: UUID) -> bool:
        """Delete a shipment (only if not shipped)."""
        shipment = await ShipmentService.get_shipment(db, shipment_id)
        if not shipment:
            return False

        if shipment.status in [ShipmentStatus.SHIPPED, ShipmentStatus.DELIVERED]:
            raise ValueError("Cannot delete shipped or delivered shipment")

        stmt = delete(ShipmentModel).where(ShipmentModel.id == shipment_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def get_shipments_by_status(
        db: AsyncSession,
        status: ShipmentStatus,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[ShipmentModel], int]:
        """Get shipments by status."""
        return await ShipmentService.get_shipments(
            db=db, skip=skip, limit=limit, status=status
        )

    @staticmethod
    async def search_shipments(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[ShipmentModel], int]:
        """Search shipments by tracking number or carrier name."""
        query = select(ShipmentModel).where(
            (ShipmentModel.tracking_number.ilike(f"%{search_term}%")) |
            (ShipmentModel.carrier_name.ilike(f"%{search_term}%"))
        )

        # Get total count
        count_query = select(ShipmentModel.id).where(
            (ShipmentModel.tracking_number.ilike(f"%{search_term}%")) |
            (ShipmentModel.carrier_name.ilike(f"%{search_term}%"))
        )

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = (
            query.options(
                selectinload(ShipmentModel.order).selectinload(OrderModel.customer),
                selectinload(ShipmentModel.order).selectinload(OrderModel.farmer)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ShipmentModel.created_at.desc())
        )
        result = await db.execute(query)
        shipments = result.scalars().all()

        return shipments, total