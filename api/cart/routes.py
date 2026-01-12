"""Cart API routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.session import get_async_db
from packages.db.models import CartStatus
from .service import CartService
from .models import (
    Cart, CartItem, CartList, CartWithItems, CartCreate, CartUpdate,
    AddToCartRequest, UpdateCartItemRequest
)

router = APIRouter(prefix="/cart", tags=["cart"])


def serialize_cart_with_items(cart, totals: dict) -> CartWithItems:
    """Helper to properly serialize cart ORM model to Pydantic response."""
    return CartWithItems(
        id=cart.id,
        session_id=cart.session_id,
        customer_id=cart.customer_id,
        status=cart.status.value if hasattr(cart.status, 'value') else cart.status,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
        items=[
            CartItem(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                created_at=item.created_at,
                updated_at=item.updated_at
            ) for item in cart.cart_items  # Fixed: cart_items not items
        ],
        total_amount=totals["total"],
        item_count=totals["item_count"]
    )


@router.get("/", response_model=CartList)
async def get_carts(
    skip: int = Query(0, ge=0, description="Number of carts to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of carts to return"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    customer_id: Optional[UUID] = Query(None, description="Filter by customer ID"),
    status: Optional[CartStatus] = Query(None, description="Filter by cart status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get carts with pagination and filtering."""
    carts, total = await CartService.get_carts(
        db=db,
        skip=skip,
        limit=limit,
        session_id=session_id,
        customer_id=customer_id,
        status=status
    )

    page = (skip // limit) + 1
    return CartList(
        carts=carts,
        total=total,
        page=page,
        size=limit
    )


@router.get("/{cart_id}", response_model=CartWithItems)
async def get_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a cart by ID with all items and totals."""
    cart = await CartService.get_cart(db, cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    totals = await CartService.get_cart_totals(db, cart_id)
    return serialize_cart_with_items(cart, totals)


@router.get("/session/{session_id}", response_model=CartWithItems)
async def get_cart_by_session(
    session_id: str,
    status: CartStatus = Query(CartStatus.ACTIVE, description="Cart status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get active cart for a session."""
    cart = await CartService.get_cart_by_session(db, session_id, status)
    if not cart:
        # Return empty cart structure
        return CartWithItems(
            id=None,
            session_id=session_id,
            status=status.value,
            items=[],
            total_amount=0,
            item_count=0,
            created_at=None,
            updated_at=None
        )

    totals = await CartService.get_cart_totals(db, cart.id)
    return serialize_cart_with_items(cart, totals)


@router.post("/", response_model=Cart, status_code=status.HTTP_201_CREATED)
async def create_cart(
    cart_data: CartCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new cart."""
    try:
        cart = await CartService.create_cart(db, cart_data)
        return cart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{cart_id}", response_model=Cart)
async def update_cart(
    cart_id: UUID,
    cart_update: CartUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a cart."""
    try:
        cart = await CartService.update_cart(db, cart_id, cart_update)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        return cart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(
    cart_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a cart and all its items."""
    success = await CartService.delete_cart(db, cart_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )


@router.post("/add-item", response_model=CartWithItems)
async def add_item_to_cart(
    request: AddToCartRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Add item to cart or update quantity if exists."""
    try:
        cart = await CartService.add_item_to_cart(
            db, request.session_id, request.product_id, request.quantity
        )
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add item to cart"
            )

        totals = await CartService.get_cart_totals(db, cart.id)
        return serialize_cart_with_items(cart, totals)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/items/{cart_item_id}", response_model=CartWithItems)
async def update_cart_item(
    cart_item_id: UUID,
    request: UpdateCartItemRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Update cart item quantity."""
    try:
        cart = await CartService.update_cart_item(db, cart_item_id, request.quantity)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        totals = await CartService.get_cart_totals(db, cart.id)
        return serialize_cart_with_items(cart, totals)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/items/{cart_item_id}", response_model=CartWithItems)
async def remove_cart_item(
    cart_item_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Remove item from cart."""
    try:
        cart = await CartService.remove_cart_item(db, cart_item_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        totals = await CartService.get_cart_totals(db, cart.id)
        return serialize_cart_with_items(cart, totals)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/session/{session_id}/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    session_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Clear all items from cart."""
    success = await CartService.clear_cart(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )


@router.put("/{cart_id}/convert", response_model=Cart)
async def convert_cart_to_order(
    cart_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Mark cart as converted to order."""
    cart = await CartService.convert_cart_to_order(db, cart_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart
