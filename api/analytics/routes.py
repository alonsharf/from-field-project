"""Analytics API routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.session import get_async_db
from .service import AnalyticsService
from .models import (
    FarmerDashboardStats,
    CustomerStats,
    OrderAnalytics,
    OrderStatusStats,
    CustomerActivity,
    FarmerCustomersList,
    ShipmentsList,
    InventoryMetrics,
    CustomerMetrics
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/farmer/dashboard", response_model=FarmerDashboardStats)
async def get_farmer_dashboard_stats(
    farmer_id: Optional[UUID] = Query(None, description="Farmer ID for stats"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get dashboard statistics for farmer portal."""
    try:
        stats = await AnalyticsService.get_farmer_dashboard_stats(db, farmer_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmer dashboard stats"
        )


@router.get("/customer/stats", response_model=CustomerStats)
async def get_customer_stats(
    customer_id: Optional[UUID] = Query(None, description="Customer ID for stats"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get customer account statistics."""
    try:
        stats = await AnalyticsService.get_customer_stats(db, customer_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer stats"
        )


@router.get("/orders", response_model=OrderAnalytics)
async def get_order_analytics(
    farmer_id: Optional[UUID] = Query(None, description="Farmer ID for filtering"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get order analytics data."""
    try:
        analytics = await AnalyticsService.get_order_analytics(db, farmer_id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order analytics"
        )


@router.get("/farmer/{farmer_id}/order-stats", response_model=OrderStatusStats)
async def get_farmer_order_stats(
    farmer_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get farmer order statistics by status."""
    try:
        stats = await AnalyticsService.get_farmer_order_stats(db, farmer_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmer order stats"
        )


@router.get("/customer/{customer_id}/activity", response_model=CustomerActivity)
async def get_customer_recent_activity(
    customer_id: UUID,
    limit: int = Query(10, ge=1, le=50, description="Number of activities to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get recent customer account activity."""
    try:
        activities = await AnalyticsService.get_customer_recent_activity(db, customer_id, limit)
        return CustomerActivity(activities=activities)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer activity"
        )


@router.get("/farmer/{farmer_id}/customers", response_model=FarmerCustomersList)
async def get_farmer_customers(
    farmer_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Number of customers to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get customers who have ordered from a specific farmer."""
    try:
        customers, total = await AnalyticsService.get_farmer_customers(db, farmer_id, limit)
        return FarmerCustomersList(customers=customers, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmer customers"
        )


@router.get("/farmer/{farmer_id}/shipments", response_model=ShipmentsList)
async def get_farmer_shipments(
    farmer_id: UUID,
    status: Optional[str] = Query(None, description="Filter by shipment status"),
    limit: int = Query(50, ge=1, le=100, description="Number of shipments to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get shipments for a farmer's orders."""
    try:
        shipments, total = await AnalyticsService.get_farmer_shipments(db, farmer_id, status, limit)
        return ShipmentsList(shipments=shipments, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch farmer shipments"
        )


@router.get("/inventory", response_model=InventoryMetrics)
async def get_inventory_metrics(
    farmer_id: Optional[UUID] = Query(None, description="Farmer ID for filtering"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get inventory metrics."""
    try:
        metrics = await AnalyticsService.get_inventory_metrics(db, farmer_id)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory metrics"
        )


@router.get("/customers", response_model=CustomerMetrics)
async def get_customer_metrics(
    farmer_id: Optional[UUID] = Query(None, description="Farmer ID for filtering"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get customer metrics."""
    try:
        metrics = await AnalyticsService.get_customer_metrics(db, farmer_id)
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer metrics"
        )