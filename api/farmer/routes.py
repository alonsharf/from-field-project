"""Farmer service routes - Single Farmer Model."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from packages.db.session import get_async_db
from .models import Farmer, FarmerCreate, FarmerUpdate, FarmerList
from .service import FarmerService

router = APIRouter()

@router.get("/admin", response_model=Farmer)
async def get_admin_farmer(
    db: AsyncSession = Depends(get_async_db)
):
    """Get the admin farmer (single farmer model)."""
    farmer = await FarmerService.get_admin_farmer(db)
    if not farmer:
        raise HTTPException(status_code=404, detail="Admin farmer not found")
    return farmer


@router.get("/{farmer_id}", response_model=Farmer)
async def get_farmer(
    farmer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific farmer by ID."""
    farmer = await FarmerService.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer


@router.post("/", response_model=Farmer, status_code=201)
async def create_farmer(
    farmer: FarmerCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new farmer."""
    return await FarmerService.create_farmer(db, farmer)


@router.put("/{farmer_id}", response_model=Farmer)
async def update_farmer(
    farmer_id: UUID,
    farmer_update: FarmerUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific farmer."""
    farmer = await FarmerService.update_farmer(db, farmer_id, farmer_update)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer


@router.delete("/{farmer_id}", status_code=204)
async def delete_farmer(
    farmer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific farmer."""
    success = await FarmerService.delete_farmer(db, farmer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Farmer not found")


@router.get("/search/", response_model=FarmerList)
async def search_farmers(
    q: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_async_db)
):
    """Search farmers by name, farm name, or email."""
    skip = (page - 1) * size
    farmers, total = await FarmerService.search_farmers(
        db=db, search_term=q, skip=skip, limit=size
    )
    return FarmerList(
        farmers=farmers,
        total=total,
        page=page,
        size=size
    )