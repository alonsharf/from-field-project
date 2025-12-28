"""Shipments service routes."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from packages.db.session import get_async_db
from packages.db.models import ShipmentStatus
from .models import Shipment, ShipmentCreate, ShipmentUpdate, ShipmentList, TrackingInfo
from .service import ShipmentService

router = APIRouter()


@router.get("/", response_model=ShipmentList)
async def get_shipments(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    status: Optional[ShipmentStatus] = Query(None, description="Filter by shipment status"),
    carrier_name: Optional[str] = Query(None, description="Filter by carrier name"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all shipments with pagination and filtering."""
    skip = (page - 1) * size
    shipments, total = await ShipmentService.get_shipments(
        db=db, skip=skip, limit=size, status=status, carrier_name=carrier_name
    )
    return ShipmentList(
        shipments=shipments,
        total=total,
        page=page,
        size=size
    )


@router.get("/{shipment_id}", response_model=Shipment)
async def get_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific shipment by ID with order details."""
    shipment = await ShipmentService.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.post("/", response_model=Shipment, status_code=201)
async def create_shipment(
    shipment: ShipmentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new shipment."""
    try:
        return await ShipmentService.create_shipment(db, shipment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{shipment_id}", response_model=Shipment)
async def update_shipment(
    shipment_id: UUID,
    shipment_update: ShipmentUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific shipment."""
    shipment = await ShipmentService.update_shipment(db, shipment_id, shipment_update)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.delete("/{shipment_id}", status_code=204)
async def delete_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific shipment (only if not shipped)."""
    try:
        success = await ShipmentService.delete_shipment(db, shipment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Shipment not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{shipment_id}/status", response_model=Shipment)
async def update_shipment_status(
    shipment_id: UUID,
    status: ShipmentStatus = Query(..., description="New shipment status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Update shipment status with automatic timestamp updates."""
    shipment = await ShipmentService.update_shipment_status(db, shipment_id, status)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}/deliver", response_model=Shipment)
async def deliver_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Mark shipment as delivered."""
    shipment = await ShipmentService.deliver_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}/cancel", response_model=Shipment)
async def cancel_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel a shipment."""
    try:
        shipment = await ShipmentService.cancel_shipment(db, shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return shipment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ship-order", response_model=Shipment)
async def ship_order(
    order_id: UUID = Query(..., description="Order ID to ship"),
    carrier_name: str = Query(..., description="Carrier name"),
    tracking_number: str = Query(..., description="Tracking number"),
    db: AsyncSession = Depends(get_async_db)
):
    """Ship an order by creating/updating shipment."""
    return await ShipmentService.ship_order(db, order_id, carrier_name, tracking_number)


@router.get("/order/{order_id}", response_model=Shipment)
async def get_shipment_by_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get shipment by order ID."""
    shipment = await ShipmentService.get_shipment_by_order(db, order_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found for this order")
    return shipment


@router.get("/tracking/{tracking_number}", response_model=TrackingInfo)
async def track_shipment(
    tracking_number: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Track shipment by tracking number."""
    shipment = await ShipmentService.get_shipment_by_tracking(db, tracking_number)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found with this tracking number")

    return TrackingInfo(
        tracking_number=shipment.tracking_number,
        status=shipment.status,
        carrier_name=shipment.carrier_name,
        estimated_delivery_date=shipment.estimated_delivery_date,
        shipped_at=shipment.shipped_at,
        delivered_at=shipment.delivered_at,
        shipping_name=shipment.shipping_name,
        shipping_address1=shipment.shipping_address1,
        shipping_city=shipment.shipping_city,
        shipping_country=shipment.shipping_country
    )


@router.get("/search/", response_model=ShipmentList)
async def search_shipments(
    q: str = Query(..., description="Search term (tracking number or carrier)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Search shipments by tracking number or carrier name."""
    skip = (page - 1) * size
    shipments, total = await ShipmentService.search_shipments(
        db=db, search_term=q, skip=skip, limit=size
    )
    return ShipmentList(
        shipments=shipments,
        total=total,
        page=page,
        size=size
    )


@router.get("/status/{status}", response_model=ShipmentList)
async def get_shipments_by_status(
    status: ShipmentStatus,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get shipments by status."""
    skip = (page - 1) * size
    shipments, total = await ShipmentService.get_shipments_by_status(
        db=db, status=status, skip=skip, limit=size
    )
    return ShipmentList(
        shipments=shipments,
        total=total,
        page=page,
        size=size
    )