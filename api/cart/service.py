"""Cart service layer for database operations."""

from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload

from packages.db.models import (
    Cart as CartModel,
    CartItem as CartItemModel,
    Product as ProductModel,
    CartStatus
)
from .models import CartCreate, CartUpdate, CartItemCreate, CartItemUpdate


class CartService:
    """Service class for cart-related database operations."""

    @staticmethod
    async def get_carts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        session_id: Optional[str] = None,
        customer_id: Optional[UUID] = None,
        status: Optional[CartStatus] = None
    ) -> tuple[List[CartModel], int]:
        """Get carts with pagination and filtering."""
        query = select(CartModel)
        filters = []

        if session_id:
            filters.append(CartModel.session_id == session_id)
        if customer_id:
            filters.append(CartModel.customer_id == customer_id)
        if status:
            filters.append(CartModel.status == status)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(CartModel.id)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results with items
        query = (
            query.options(
                selectinload(CartModel.cart_items).selectinload(CartItemModel.product)
            )
            .offset(skip)
            .limit(limit)
            .order_by(CartModel.updated_at.desc())
        )
        result = await db.execute(query)
        carts = result.scalars().all()

        return carts, total

    @staticmethod
    async def get_cart(db: AsyncSession, cart_id: UUID) -> Optional[CartModel]:
        """Get a cart by ID with all items."""
        query = (
            select(CartModel)
            .where(CartModel.id == cart_id)
            .options(
                selectinload(CartModel.cart_items).selectinload(CartItemModel.product)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_cart_by_session(
        db: AsyncSession,
        session_id: str,
        status: CartStatus = CartStatus.ACTIVE
    ) -> Optional[CartModel]:
        """Get active cart for a session."""
        query = (
            select(CartModel)
            .where(and_(CartModel.session_id == session_id, CartModel.status == status))
            .options(
                selectinload(CartModel.cart_items).selectinload(CartItemModel.product)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_cart(db: AsyncSession, cart_data: CartCreate) -> CartModel:
        """Create a new cart."""
        db_cart = CartModel(
            session_id=cart_data.session_id,
            customer_id=cart_data.customer_id,
            status=CartStatus.ACTIVE
        )
        db.add(db_cart)
        await db.commit()
        await db.refresh(db_cart)
        return db_cart

    @staticmethod
    async def update_cart(
        db: AsyncSession,
        cart_id: UUID,
        cart_update: CartUpdate
    ) -> Optional[CartModel]:
        """Update a cart."""
        cart = await CartService.get_cart(db, cart_id)
        if not cart:
            return None

        update_data = cart_update.model_dump(exclude_unset=True)
        if update_data:
            update_data['updated_at'] = datetime.now(UTC)
            stmt = (
                update(CartModel)
                .where(CartModel.id == cart_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(cart)

        return cart

    @staticmethod
    async def delete_cart(db: AsyncSession, cart_id: UUID) -> bool:
        """Delete a cart and all its items."""
        cart = await CartService.get_cart(db, cart_id)
        if not cart:
            return False

        # Delete cart items first
        await db.execute(delete(CartItemModel).where(CartItemModel.cart_id == cart_id))

        # Delete cart
        stmt = delete(CartModel).where(CartModel.id == cart_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def add_item_to_cart(
        db: AsyncSession,
        session_id: str,
        product_id: UUID,
        quantity: Decimal
    ) -> Optional[CartModel]:
        """Add item to cart or update quantity if exists."""
        try:
            # Get or create cart
            cart = await CartService.get_cart_by_session(db, session_id)
            if not cart:
                cart = await CartService.create_cart(
                    db, CartCreate(session_id=session_id)
                )

            # Get product details
            product = await db.get(ProductModel, product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            if not product.is_active:
                raise ValueError(f"Product {product.name} is not active")

            if product.stock_quantity < quantity:
                raise ValueError(f"Insufficient stock for product {product.name}")

            # Check if item already in cart
            existing_item = await db.execute(
                select(CartItemModel).where(
                    and_(
                        CartItemModel.cart_id == cart.id,
                        CartItemModel.product_id == product_id
                    )
                )
            )
            existing_item = existing_item.scalar_one_or_none()

            if existing_item:
                # Update existing item
                new_quantity = existing_item.quantity + quantity
                if product.stock_quantity < new_quantity:
                    raise ValueError(f"Insufficient stock for product {product.name}")

                existing_item.quantity = new_quantity
                existing_item.updated_at = datetime.now(UTC)
            else:
                # Create new cart item
                cart_item = CartItemModel(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=product.price_per_unit
                )
                db.add(cart_item)

            # Update cart timestamp
            cart.updated_at = datetime.now(UTC)
            await db.commit()

            # Return updated cart with items
            return await CartService.get_cart(db, cart.id)

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_cart_item(
        db: AsyncSession,
        cart_item_id: UUID,
        quantity: Decimal
    ) -> Optional[CartModel]:
        """Update cart item quantity."""
        try:
            # Get cart item
            cart_item = await db.get(CartItemModel, cart_item_id)
            if not cart_item:
                return None

            # Get product to check stock
            product = await db.get(ProductModel, cart_item.product_id)
            if not product:
                raise ValueError("Product not found")

            if product.stock_quantity < quantity:
                raise ValueError(f"Insufficient stock for product {product.name}")

            # Update quantity
            cart_item.quantity = quantity
            cart_item.updated_at = datetime.now(UTC)

            # Update cart timestamp
            cart = await db.get(CartModel, cart_item.cart_id)
            if cart:
                cart.updated_at = datetime.now(UTC)

            await db.commit()

            # Return updated cart
            return await CartService.get_cart(db, cart_item.cart_id)

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def remove_cart_item(
        db: AsyncSession,
        cart_item_id: UUID
    ) -> Optional[CartModel]:
        """Remove item from cart."""
        try:
            # Get cart item
            cart_item = await db.get(CartItemModel, cart_item_id)
            if not cart_item:
                return None

            cart_id = cart_item.cart_id

            # Delete cart item
            await db.delete(cart_item)

            # Update cart timestamp
            cart = await db.get(CartModel, cart_id)
            if cart:
                cart.updated_at = datetime.now(UTC)

            await db.commit()

            # Return updated cart
            return await CartService.get_cart(db, cart_id)

        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def clear_cart(db: AsyncSession, session_id: str) -> bool:
        """Clear all items from cart."""
        try:
            cart = await CartService.get_cart_by_session(db, session_id)
            if not cart:
                return False

            # Delete all cart items
            await db.execute(
                delete(CartItemModel).where(CartItemModel.cart_id == cart.id)
            )

            # Update cart timestamp
            cart.updated_at = datetime.now(UTC)
            await db.commit()

            return True

        except Exception as e:
            await db.rollback()
            return False

    @staticmethod
    async def get_cart_totals(db: AsyncSession, cart_id: UUID) -> dict:
        """Calculate cart totals."""
        cart = await CartService.get_cart(db, cart_id)
        if not cart:
            return {"total": 0, "item_count": 0}

        total = Decimal('0')
        item_count = 0

        for item in cart.cart_items:
            total += item.quantity * item.unit_price
            item_count += 1

        return {
            "total": float(total),
            "item_count": item_count
        }

    @staticmethod
    async def convert_cart_to_order(
        db: AsyncSession,
        cart_id: UUID
    ) -> Optional[CartModel]:
        """Mark cart as converted to order."""
        cart = await CartService.get_cart(db, cart_id)
        if not cart:
            return None

        cart.status = CartStatus.CONVERTED
        cart.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(cart)

        return cart