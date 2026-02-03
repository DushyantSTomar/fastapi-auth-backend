from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.schemas.ai import AISearchQuery
from app.schemas.product import ProductOut
from app.services.ai_search import extract_intent, search_products, fallback_search

router = APIRouter()

@router.post("/ai/search", response_model=List[ProductOut])
async def ai_product_search(
    search_query: AISearchQuery,
    db: AsyncSession = Depends(get_db)
):
    intent = await extract_intent(search_query.query)
    
    # If extraction was successful (has category or max_price), use smart search
    if intent.category or intent.max_price:
        results = await search_products(db, intent)
    else:
        # If extraction failed or returned only keywords, use fallback/robust search
        # Note: extract_intent returns just keywords on failure or if no specific intent found
        # We can still use search_products with just keywords, but let's stick to the plan's logic flow
        # actually search_products handles keywords too, so we can use it if intent has anything useful
        # but let's follow the requested flow: if AI fails -> fallback
        if not intent.keywords and not intent.category and not intent.max_price:
             results = await fallback_search(db, search_query.query)
        else:
             results = await search_products(db, intent)
             
    return results
