"""Authentication routes for From Field to You API."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.session import get_async_db
from .models import LoginRequest, RegisterCustomerRequest, AuthResponse
from .service import AuthService

router = APIRouter()


@router.post("/farmer/login", response_model=AuthResponse)
async def farmer_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate farmer and return user info."""
    farmer = await AuthService.authenticate_farmer(db, login_data.email, login_data.password)
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(
        id=str(farmer.id),
        name=farmer.name,
        email=farmer.email,
        farm_name=farmer.farm_name,
        role="farmer"
    )


@router.post("/customer/login", response_model=AuthResponse)
async def customer_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate customer and return user info."""
    customer = await AuthService.authenticate_customer(db, login_data.email, login_data.password)
    if not customer:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(
        id=str(customer.id),
        name=f"{customer.first_name} {customer.last_name}",
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name,
        role="customer"
    )


@router.post("/customer/register", response_model=AuthResponse, status_code=201)
async def customer_register(
    register_data: RegisterCustomerRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new customer and return user info."""
    try:
        customer = await AuthService.register_customer(db, register_data)
        return AuthResponse(
            id=str(customer.id),
            name=f"{customer.first_name} {customer.last_name}",
            email=customer.email,
            first_name=customer.first_name,
            last_name=customer.last_name,
            role="customer"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/farmer/admin", response_model=AuthResponse)
async def get_admin_farmer(
    db: AsyncSession = Depends(get_async_db)
):
    """Get the admin farmer info (single farmer model)."""
    farmer = await AuthService.get_admin_farmer(db)
    if not farmer:
        raise HTTPException(status_code=404, detail="Admin farmer not found")

    return AuthResponse(
        id=str(farmer.id),
        name=farmer.name,
        email=farmer.email,
        farm_name=farmer.farm_name,
        role="farmer"
    )