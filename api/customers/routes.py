"""Customers service routes."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from packages.db.session import get_async_db
from .models import Customer, CustomerCreate, CustomerUpdate, CustomerList
from .service import CustomerService

router = APIRouter()

@router.get("/", response_model=CustomerList)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    marketing_opt_in: Optional[bool] = Query(None, description="Filter by marketing opt-in status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all customers with pagination and filtering."""
    skip = (page - 1) * size
    customers, total = await CustomerService.get_customers(
        db=db, skip=skip, limit=size, marketing_opt_in=marketing_opt_in
    )
    return CustomerList(
        customers=customers,
        total=total,
        page=page,
        size=size
    )


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific customer by ID."""
    customer = await CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new customer."""
    try:
        return await CustomerService.create_customer(db, customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: UUID,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific customer."""
    try:
        customer = await CustomerService.update_customer(db, customer_id, customer_update)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific customer."""
    success = await CustomerService.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/search/", response_model=CustomerList)
async def search_customers(
    q: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Search customers by name or email."""
    skip = (page - 1) * size
    customers, total = await CustomerService.search_customers(
        db=db, search_term=q, skip=skip, limit=size
    )
    return CustomerList(
        customers=customers,
        total=total,
        page=page,
        size=size
    )


@router.get("/{customer_id}/orders", response_model=Customer)
async def get_customer_with_orders(
    customer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a customer with their order history."""
    customer = await CustomerService.get_customer_with_orders(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer