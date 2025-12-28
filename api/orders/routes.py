"""Orders service routes."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from packages.db.session import get_async_db
from packages.db.models import OrderStatus, PaymentStatus
from .models import Order, OrderCreate, OrderUpdate, OrderList, OrderSummary
from .service import OrderService

router = APIRouter()


@router.get("/", response_model=OrderList)
async def get_orders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID"),
    farmer_id: Optional[UUID] = Query(None, description="Filter by farmer ID"),
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all orders with pagination and filtering."""
    skip = (page - 1) * size
    orders, total = await OrderService.get_orders(
        db=db, skip=skip, limit=size, customer_id=customer_id,
        farmer_id=farmer_id, status=status, payment_status=payment_status
    )
    return OrderList(
        orders=orders,
        total=total,
        page=page,
        size=size
    )


@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific order by ID with all details."""
    order = await OrderService.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=Order, status_code=201)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new order with purchase items."""
    try:
        return await OrderService.create_order(db, order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: UUID,
    order_update: OrderUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific order."""
    order = await OrderService.update_order(db, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.delete("/{order_id}", status_code=204)
async def delete_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific order (only DRAFT orders)."""
    try:
        success = await OrderService.delete_order(db, order_id)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: UUID,
    status: OrderStatus = Query(..., description="New order status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Update order status."""
    order = await OrderService.update_order_status(db, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/payment", response_model=Order)
async def update_payment_status(
    order_id: UUID,
    payment_status: PaymentStatus = Query(..., description="New payment status"),
    payment_reference: Optional[str] = Query(None, description="Payment reference"),
    db: AsyncSession = Depends(get_async_db)
):
    """Update payment status."""
    order = await OrderService.update_payment_status(
        db, order_id, payment_status, payment_reference
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}/cancel", response_model=Order)
async def cancel_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel an order and restore product stock."""
    try:
        order = await OrderService.cancel_order(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer/{customer_id}", response_model=OrderList)
async def get_customer_orders(
    customer_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all orders for a specific customer."""
    skip = (page - 1) * size
    orders, total = await OrderService.get_customer_orders(
        db=db, customer_id=customer_id, skip=skip, limit=size
    )
    return OrderList(
        orders=orders,
        total=total,
        page=page,
        size=size
    )


@router.get("/farmer/{farmer_id}", response_model=OrderList)
async def get_farmer_orders(
    farmer_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all orders for a specific farmer."""
    skip = (page - 1) * size
    orders, total = await OrderService.get_farmer_orders(
        db=db, farmer_id=farmer_id, skip=skip, limit=size, status=status
    )
    return OrderList(
        orders=orders,
        total=total,
        page=page,
        size=size
    )