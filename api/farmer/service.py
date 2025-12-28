"""Farmer service layer for database operations - Single Farmer Model."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import bcrypt

from packages.db.models import Farmer as FarmerModel
from .models import FarmerCreate, FarmerUpdate


class FarmerService:
    """Service class for farmer-related database operations."""

    @staticmethod
    async def get_farmers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None
    ) -> tuple[List[FarmerModel], int]:
        """Get farmers with pagination and filtering."""
        query = select(FarmerModel)

        if is_active is not None:
            query = query.where(FarmerModel.is_active == is_active)

        # Get total count
        count_query = select(FarmerModel.id)
        if is_active is not None:
            count_query = count_query.where(FarmerModel.is_active == is_active)

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(FarmerModel.created_at.desc())
        result = await db.execute(query)
        farmers = result.scalars().all()

        return farmers, total

    @staticmethod
    async def get_farmer(db: AsyncSession, farmer_id: UUID) -> Optional[FarmerModel]:
        """Get a farmer by ID."""
        query = select(FarmerModel).where(FarmerModel.id == farmer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_farmer_with_products(db: AsyncSession, farmer_id: UUID) -> Optional[FarmerModel]:
        """Get a farmer with their products."""
        query = (
            select(FarmerModel)
            .where(FarmerModel.id == farmer_id)
            .options(selectinload(FarmerModel.products))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_farmer(db: AsyncSession, farmer_data: FarmerCreate) -> FarmerModel:
        """Create a new farmer."""
        db_farmer = FarmerModel(**farmer_data.model_dump())
        db.add(db_farmer)
        await db.commit()
        await db.refresh(db_farmer)
        return db_farmer

    @staticmethod
    async def update_farmer(
        db: AsyncSession,
        farmer_id: UUID,
        farmer_update: FarmerUpdate
    ) -> Optional[FarmerModel]:
        """Update a farmer."""
        # Get the farmer first
        farmer = await FarmerService.get_farmer(db, farmer_id)
        if not farmer:
            return None

        # Update only provided fields
        update_data = farmer_update.model_dump(exclude_unset=True)
        if update_data:
            stmt = (
                update(FarmerModel)
                .where(FarmerModel.id == farmer_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(farmer)

        return farmer

    @staticmethod
    async def delete_farmer(db: AsyncSession, farmer_id: UUID) -> bool:
        """Delete a farmer."""
        farmer = await FarmerService.get_farmer(db, farmer_id)
        if not farmer:
            return False

        stmt = delete(FarmerModel).where(FarmerModel.id == farmer_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def search_farmers(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[FarmerModel], int]:
        """Search farmers by name, farm_name, or email."""
        query = select(FarmerModel).where(
            (FarmerModel.name.ilike(f"%{search_term}%")) |
            (FarmerModel.farm_name.ilike(f"%{search_term}%")) |
            (FarmerModel.email.ilike(f"%{search_term}%"))
        )

        # Get total count
        count_query = select(FarmerModel.id).where(
            (FarmerModel.name.ilike(f"%{search_term}%")) |
            (FarmerModel.farm_name.ilike(f"%{search_term}%")) |
            (FarmerModel.email.ilike(f"%{search_term}%"))
        )

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(FarmerModel.created_at.desc())
        result = await db.execute(query)
        farmers = result.scalars().all()

        return farmers, total

    @staticmethod
    async def get_admin_farmer(db: AsyncSession) -> Optional[FarmerModel]:
        """Get the admin farmer (single farmer model)."""
        query = select(FarmerModel).where(FarmerModel.is_active == True).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_farmer(db: AsyncSession, email: str, password: str) -> Optional[FarmerModel]:
        """Authenticate farmer by email and password."""
        query = select(FarmerModel).where(
            FarmerModel.email == email,
            FarmerModel.is_active == True
        )
        result = await db.execute(query)
        farmer = result.scalar_one_or_none()

        if farmer and farmer.password_hash:
            # Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), farmer.password_hash.encode('utf-8')):
                return farmer

        return None