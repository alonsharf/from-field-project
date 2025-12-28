"""Customers service layer for database operations."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import bcrypt

from packages.db.models import Customer as CustomerModel
from .models import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service class for customer-related database operations."""

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        marketing_opt_in: Optional[bool] = None
    ) -> tuple[List[CustomerModel], int]:
        """Get customers with pagination and filtering."""
        query = select(CustomerModel)

        if marketing_opt_in is not None:
            query = query.where(CustomerModel.marketing_opt_in == marketing_opt_in)

        # Get total count
        count_query = select(CustomerModel.id)
        if marketing_opt_in is not None:
            count_query = count_query.where(CustomerModel.marketing_opt_in == marketing_opt_in)

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(CustomerModel.created_at.desc())
        result = await db.execute(query)
        customers = result.scalars().all()

        return customers, total

    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: UUID) -> Optional[CustomerModel]:
        """Get a customer by ID."""
        query = select(CustomerModel).where(CustomerModel.id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_by_email(db: AsyncSession, email: str) -> Optional[CustomerModel]:
        """Get a customer by email."""
        query = select(CustomerModel).where(CustomerModel.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_with_orders(db: AsyncSession, customer_id: UUID) -> Optional[CustomerModel]:
        """Get a customer with their orders."""
        query = (
            select(CustomerModel)
            .where(CustomerModel.id == customer_id)
            .options(selectinload(CustomerModel.orders))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> CustomerModel:
        """Create a new customer."""
        # Check if email already exists
        existing_customer = await CustomerService.get_customer_by_email(db, customer_data.email)
        if existing_customer:
            raise ValueError("Customer with this email already exists")

        db_customer = CustomerModel(**customer_data.model_dump())
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer_id: UUID,
        customer_update: CustomerUpdate
    ) -> Optional[CustomerModel]:
        """Update a customer."""
        # Get the customer first
        customer = await CustomerService.get_customer(db, customer_id)
        if not customer:
            return None

        # Check email uniqueness if email is being updated
        if customer_update.email and customer_update.email != customer.email:
            existing_customer = await CustomerService.get_customer_by_email(db, customer_update.email)
            if existing_customer:
                raise ValueError("Customer with this email already exists")

        # Update only provided fields
        update_data = customer_update.model_dump(exclude_unset=True)
        if update_data:
            stmt = (
                update(CustomerModel)
                .where(CustomerModel.id == customer_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(customer)

        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: UUID) -> bool:
        """Delete a customer."""
        customer = await CustomerService.get_customer(db, customer_id)
        if not customer:
            return False

        stmt = delete(CustomerModel).where(CustomerModel.id == customer_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def search_customers(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[CustomerModel], int]:
        """Search customers by name or email."""
        query = select(CustomerModel).where(
            (CustomerModel.first_name.ilike(f"%{search_term}%")) |
            (CustomerModel.last_name.ilike(f"%{search_term}%")) |
            (CustomerModel.email.ilike(f"%{search_term}%"))
        )

        # Get total count
        count_query = select(CustomerModel.id).where(
            (CustomerModel.first_name.ilike(f"%{search_term}%")) |
            (CustomerModel.last_name.ilike(f"%{search_term}%")) |
            (CustomerModel.email.ilike(f"%{search_term}%"))
        )

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(CustomerModel.created_at.desc())
        result = await db.execute(query)
        customers = result.scalars().all()

        return customers, total

    @staticmethod
    async def authenticate_customer(db: AsyncSession, email: str, password: str) -> Optional[CustomerModel]:
        """Authenticate customer by email and password."""
        customer = await CustomerService.get_customer_by_email(db, email)

        if customer and customer.password_hash:
            # Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), customer.password_hash.encode('utf-8')):
                return customer

        return None

    @staticmethod
    async def register_customer(db: AsyncSession, register_data) -> CustomerModel:
        """Register a new customer with hashed password."""
        # Check if email already exists
        existing_customer = await CustomerService.get_customer_by_email(db, register_data.email)
        if existing_customer:
            raise ValueError("Customer with this email already exists")

        # Hash the password
        password_hash = bcrypt.hashpw(register_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Create customer data
        customer_data = {
            'first_name': register_data.first_name,
            'last_name': register_data.last_name,
            'email': register_data.email,
            'password_hash': password_hash,
            'phone': register_data.phone,
            'address_line1': register_data.address_line1,
            'address_line2': register_data.address_line2,
            'city': register_data.city,
            'postal_code': register_data.postal_code,
            'country': register_data.country,
            'marketing_opt_in': False
        }

        db_customer = CustomerModel(**customer_data)
        db.add(db_customer)
        await db.commit()
        await db.refresh(db_customer)
        return db_customer