"""Authentication service layer for From Field to You API."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from packages.db.models import Farmer as FarmerModel, Customer as CustomerModel
from .models import RegisterCustomerRequest


class AuthService:
    """Service class for authentication operations."""

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

    @staticmethod
    async def authenticate_customer(db: AsyncSession, email: str, password: str) -> Optional[CustomerModel]:
        """Authenticate customer by email and password."""
        query = select(CustomerModel).where(CustomerModel.email == email)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()

        if customer and customer.password_hash:
            # Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), customer.password_hash.encode('utf-8')):
                return customer

        return None

    @staticmethod
    async def get_customer_by_email(db: AsyncSession, email: str) -> Optional[CustomerModel]:
        """Get customer by email."""
        query = select(CustomerModel).where(CustomerModel.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def register_customer(db: AsyncSession, register_data: RegisterCustomerRequest) -> CustomerModel:
        """Register a new customer with hashed password."""
        # Check if email already exists
        existing_customer = await AuthService.get_customer_by_email(db, register_data.email)
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

    @staticmethod
    async def get_admin_farmer(db: AsyncSession) -> Optional[FarmerModel]:
        """Get the admin farmer (single farmer model)."""
        query = select(FarmerModel).where(FarmerModel.is_active == True).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()