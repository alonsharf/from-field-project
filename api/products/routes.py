"""Products service routes."""

from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from packages.db.session import get_async_db
from .models import Product, ProductCreate, ProductUpdate, ProductList, ProductSummary
from .service import ProductService

router = APIRouter()


@router.get("/", response_model=ProductList)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    farmer_id: Optional[UUID] = Query(None, description="Filter by farmer ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_organic: Optional[bool] = Query(None, description="Filter by organic status"),
    available_only: bool = Query(False, description="Show only available products"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all products with pagination and filtering."""
    skip = (page - 1) * size
    products, total = await ProductService.get_products(
        db=db, skip=skip, limit=size, farmer_id=farmer_id,
        category=category, is_active=is_active, is_organic=is_organic,
        available_only=available_only
    )
    return ProductList(
        products=[Product.from_orm_product(p) for p in products],
        total=total,
        page=page,
        size=size
    )


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific product by ID."""
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product.from_orm_product(product)


@router.post("/", response_model=Product, status_code=201)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new product."""
    db_product = await ProductService.create_product(db, product)
    return Product.from_orm_product(db_product)


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: UUID,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific product."""
    product = await ProductService.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product.from_orm_product(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific product."""
    success = await ProductService.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")


@router.get("/search/", response_model=ProductList)
async def search_products(
    q: str = Query(..., description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Search products by name, description, or category."""
    skip = (page - 1) * size
    products, total = await ProductService.search_products(
        db=db, search_term=q, skip=skip, limit=size, is_active=is_active
    )
    return ProductList(
        products=[Product.from_orm_product(p) for p in products],
        total=total,
        page=page,
        size=size
    )


@router.get("/category/{category}", response_model=list[Product])
async def get_products_by_category(
    category: str,
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all products in a specific category."""
    products = await ProductService.get_products_by_category(db, category, is_active)
    return [Product.from_orm_product(p) for p in products]


@router.get("/farmer/{farmer_id}", response_model=list[Product])
async def get_products_by_farmer(
    farmer_id: UUID,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all products for a specific farmer."""
    products = await ProductService.get_products_by_farmer(db, farmer_id, is_active)
    return [Product.from_orm_product(p) for p in products]


@router.put("/{product_id}/stock", response_model=Product)
async def update_product_stock(
    product_id: UUID,
    quantity_change: Decimal = Query(..., description="Stock quantity change (can be negative)"),
    db: AsyncSession = Depends(get_async_db)
):
    """Update product stock quantity."""
    try:
        product = await ProductService.update_stock(db, product_id, quantity_change)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return Product.from_orm_product(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/low-stock/", response_model=list[Product])
async def get_low_stock_products(
    threshold: Decimal = Query(10, description="Stock threshold"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get products with stock below threshold."""
    products = await ProductService.get_low_stock_products(db, threshold)
    return [Product.from_orm_product(p) for p in products]