"""Products service layer for database operations."""

from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload

from packages.db.models import Product as ProductModel, Category, UnitLabel
from .models import ProductCreate, ProductUpdate


class ProductService:
    """Service class for product-related database operations."""

    @staticmethod
    async def get_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        farmer_id: Optional[UUID] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_organic: Optional[bool] = None,
        available_only: bool = False
    ) -> tuple[List[ProductModel], int]:
        """Get products with pagination and filtering."""
        query = select(ProductModel)
        filters = []

        if farmer_id:
            filters.append(ProductModel.farmer_id == farmer_id)
        if category:
            # Filter by category name - need to join with Category table
            filters.append(ProductModel.category.has(name=category))
        if is_active is not None:
            filters.append(ProductModel.is_active == is_active)
        if is_organic is not None:
            filters.append(ProductModel.is_organic == is_organic)
        if available_only:
            today = date.today()
            filters.append(ProductModel.stock_quantity > 0)
            filters.append(
                and_(
                    ProductModel.available_from <= today,
                    ProductModel.available_until >= today
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(ProductModel.id)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results with all relationships
        query = (
            query.options(
                selectinload(ProductModel.farmer),
                selectinload(ProductModel.category),
                selectinload(ProductModel.unit_label)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ProductModel.created_at.desc())
        )
        result = await db.execute(query)
        products = result.scalars().all()

        return products, total

    @staticmethod
    async def get_product(db: AsyncSession, product_id: UUID) -> Optional[ProductModel]:
        """Get a product by ID."""
        query = (
            select(ProductModel)
            .where(ProductModel.id == product_id)
            .options(
                selectinload(ProductModel.farmer),
                selectinload(ProductModel.category),
                selectinload(ProductModel.unit_label)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_products_by_farmer(
        db: AsyncSession,
        farmer_id: UUID,
        is_active: Optional[bool] = None
    ) -> List[ProductModel]:
        """Get all products for a specific farmer."""
        query = select(ProductModel).where(ProductModel.farmer_id == farmer_id)

        if is_active is not None:
            query = query.where(ProductModel.is_active == is_active)

        query = query.order_by(ProductModel.name)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> ProductModel:
        """Create a new product."""
        # Convert Pydantic model to dict
        product_dict = product_data.model_dump()
        
        # Look up category by name and get its ID
        category_name = product_dict.pop("category", None)
        if category_name:
            category_result = await db.execute(
                select(Category).where(Category.name == category_name)
            )
            category = category_result.scalar_one_or_none()
            if category:
                product_dict["category_id"] = category.id
            else:
                raise ValueError(f"Category '{category_name}' not found")
        
        # Look up unit_label by name and get its ID
        unit_label_name = product_dict.pop("unit_label", None)
        if unit_label_name:
            unit_label_result = await db.execute(
                select(UnitLabel).where(UnitLabel.name == unit_label_name)
            )
            unit_label = unit_label_result.scalar_one_or_none()
            if unit_label:
                product_dict["unit_label_id"] = unit_label.id
            else:
                raise ValueError(f"Unit label '{unit_label_name}' not found")
        
        db_product = ProductModel(**product_dict)
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        
        # Re-fetch with eager loading to avoid lazy load issues in async context
        return await ProductService.get_product(db, db_product.id)

    @staticmethod
    async def update_product(
        db: AsyncSession,
        product_id: UUID,
        product_update: ProductUpdate
    ) -> Optional[ProductModel]:
        """Update a product."""
        # Get the product first
        product = await ProductService.get_product(db, product_id)
        if not product:
            return None

        # Update only provided fields
        update_data = product_update.dict(exclude_unset=True)
        
        # Convert category name to category_id if provided
        if "category" in update_data:
            category_name = update_data.pop("category")
            if category_name:
                category_result = await db.execute(
                    select(Category).where(Category.name == category_name)
                )
                category = category_result.scalar_one_or_none()
                if category:
                    update_data["category_id"] = category.id
                else:
                    raise ValueError(f"Category '{category_name}' not found")
        
        # Convert unit_label name to unit_label_id if provided
        if "unit_label" in update_data:
            unit_label_name = update_data.pop("unit_label")
            if unit_label_name:
                unit_label_result = await db.execute(
                    select(UnitLabel).where(UnitLabel.name == unit_label_name)
                )
                unit_label = unit_label_result.scalar_one_or_none()
                if unit_label:
                    update_data["unit_label_id"] = unit_label.id
                else:
                    raise ValueError(f"Unit label '{unit_label_name}' not found")
        
        if update_data:
            stmt = (
                update(ProductModel)
                .where(ProductModel.id == product_id)
                .values(**update_data)
            )
            await db.execute(stmt)
            await db.commit()

        # Re-fetch with eager loading to avoid lazy load issues in async context
        return await ProductService.get_product(db, product_id)

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: UUID) -> bool:
        """Delete a product."""
        product = await ProductService.get_product(db, product_id)
        if not product:
            return False

        stmt = delete(ProductModel).where(ProductModel.id == product_id)
        await db.execute(stmt)
        await db.commit()
        return True

    @staticmethod
    async def update_stock(
        db: AsyncSession,
        product_id: UUID,
        quantity_change: Decimal
    ) -> Optional[ProductModel]:
        """Update product stock quantity (can be positive or negative)."""
        product = await ProductService.get_product(db, product_id)
        if not product:
            return None

        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock")

        stmt = (
            update(ProductModel)
            .where(ProductModel.id == product_id)
            .values(stock_quantity=new_quantity)
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(product)

        return product

    @staticmethod
    async def search_products(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None
    ) -> tuple[List[ProductModel], int]:
        """Search products by name, description, or category."""
        filters = [
            (ProductModel.name.ilike(f"%{search_term}%")) |
            (ProductModel.description.ilike(f"%{search_term}%")) |
            (ProductModel.category.has(Category.name.ilike(f"%{search_term}%")))
        ]

        if is_active is not None:
            filters.append(ProductModel.is_active == is_active)

        query = select(ProductModel).where(and_(*filters))

        # Get total count
        count_query = select(ProductModel.id).where(and_(*filters))
        total_result = await db.execute(count_query)
        total = len(total_result.fetchall())

        # Get paginated results
        query = (
            query.options(
                selectinload(ProductModel.farmer),
                selectinload(ProductModel.category),
                selectinload(ProductModel.unit_label)
            )
            .offset(skip)
            .limit(limit)
            .order_by(ProductModel.created_at.desc())
        )
        result = await db.execute(query)
        products = result.scalars().all()

        return products, total

    @staticmethod
    async def get_products_by_category(
        db: AsyncSession,
        category: str,
        is_active: bool = True
    ) -> List[ProductModel]:
        """Get all products in a specific category."""
        query = (
            select(ProductModel)
            .where(
                and_(
                    ProductModel.category.has(Category.name == category),
                    ProductModel.is_active == is_active
                )
            )
            .options(
                selectinload(ProductModel.farmer),
                selectinload(ProductModel.category),
                selectinload(ProductModel.unit_label)
            )
            .order_by(ProductModel.name)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_low_stock_products(
        db: AsyncSession,
        threshold: Decimal = Decimal('10')
    ) -> List[ProductModel]:
        """Get products with stock below threshold."""
        query = (
            select(ProductModel)
            .where(
                and_(
                    ProductModel.stock_quantity <= threshold,
                    ProductModel.is_active == True
                )
            )
            .options(
                selectinload(ProductModel.farmer),
                selectinload(ProductModel.category),
                selectinload(ProductModel.unit_label)
            )
            .order_by(ProductModel.stock_quantity.asc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def get_category_emoji(product_data):
        """Get consistent category emoji for products across all pages."""

        # Get category, handling both string and dict formats
        if isinstance(product_data.get('category'), dict):
            category = product_data.get('category', {}).get('name', 'Fresh Produce').lower()
        else:
            category = product_data.get('category', 'Fresh Produce').lower()

        # Category-specific emoji mapping (centralized)
        placeholder_map = {
            'vegetables': '🥬',
            'fruits': '🍎',
            'herbs': '🌿',
            'grains': '🌾',
            'specialty items': '🥕',
            'dairy': '🥛',
            'meat': '🥩',
            'berries': '🫐',  # Add specific mapping for berries
            'citrus': '🍊',   # Add specific mapping for citrus
            'root vegetables': '🥕',
            'leafy greens': '🥬'
        }

        # Find matching category or use default
        emoji = '🥕'  # Default
        for cat_key, cat_emoji in placeholder_map.items():
            if cat_key in category:
                emoji = cat_emoji
                break

        return emoji

    @staticmethod
    def create_product_image_placeholder(product_data):
        """Create consistent product image placeholder across all pages."""
        emoji = ProductService.get_category_emoji(product_data)

        # Create beautiful placeholder
        placeholder_html = f"""
        <div style="
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 30px 15px;
            text-align: center;
            font-size: 2.5rem;
            color: #4a5568;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            ">
            {emoji}
        </div>
        """
        return placeholder_html