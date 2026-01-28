from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.product import Product


async def get_active_products(db: AsyncSession) -> List[Product]:
    query = select(Product).where(Product.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()


async def get_paginated_products(db: AsyncSession, page: int, limit: int) -> tuple[List[Product], bool]:
    offset = (page - 1) * limit
    # Fetch one extra to determine hasMore
    query = (
        select(Product)
        .where(Product.is_active.is_(True))
        .order_by(Product.id)
        .offset(offset)
        .limit(limit + 1)
    )
    result = await db.execute(query)
    products = result.scalars().all()
    
    has_more = False
    if len(products) > limit:
        has_more = True
        products = products[:limit]
        
    return products, has_more


