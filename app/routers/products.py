from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.services.product import get_paginated_products
from app.schemas.product import PaginatedProductResponse

router = APIRouter()

@router.get("/products", response_model=PaginatedProductResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_db)
):
    products, has_more = await get_paginated_products(db, page, limit)
    
    return {
        "data": products,
        "page": page,
        "hasMore": has_more
    }
