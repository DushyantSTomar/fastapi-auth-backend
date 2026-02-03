import json
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, desc
from app.models.product import Product
from app.schemas.ai import IntentData
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

CATEGORY_MAPPING = {
    "laptop": "electronics",
    "notebook": "electronics",
    "phone": "electronics",
    "mobile": "electronics", 
    "headphone": "electronics",
    "earbud": "electronics",
    "smartwatch": "electronics",
    "tablet": "electronics",
    "camera": "electronics",
    "tv": "electronics",
    "television": "electronics"
}

async def extract_intent(query: str) -> IntentData:
    # 1. Normalize query
    query = query.lower().strip()
    
    # 3. Category Mapping check (simple pre-check or use LLM)
    # The user rules say: "Extract main keyword... Category mapping... Do NOT expect category name from user"
    # We will let the LLM do the extraction but we can also infer category from keywords if LLM fails or for fallback.
    
    if not client:
        # Fallback extraction logic
        keywords = query.split()
        return IntentData(keywords=keywords)

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that extracts search intent. "
                               "Extract the 'main_keyword' (e.g. laptop, phone) from the query. "
                               "Extract 'max_price' only if explicitly mentioned. "
                               "Return JSON with keys: 'main_keyword' (string), 'max_price' (number or null). "
                               "Do not return markdown."
                },
                {"role": "user", "content": query}
            ],
            temperature=0
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        keywords = []
        if data.get("main_keyword"):
            keywords = [data["main_keyword"]]
        else:
            keywords = query.split() # Fallback if no keyword identified
            
        return IntentData(
            keywords=keywords,
            max_price=data.get("max_price"),
            category=None # We will map category in search_products or here. 
                          # User Rule 3 says "Category mapping: laptop -> electronics". 
                          # We can derive category from the keyword.
        )
    except Exception:
        return IntentData(keywords=query.split())

async def search_products(db: AsyncSession, intent: IntentData):
    # Rule 3 & 4: Map keywords to category, never require exact category match
    mapped_category = None
    if intent.keywords:
         for k in intent.keywords:
             if k in CATEGORY_MAPPING:
                 mapped_category = CATEGORY_MAPPING[k]
                 break
    
    # Rule 5: Search Priority (OR logic)
    # title LIKE %keyword% OR description LIKE %keyword% OR category = mapped_category
    
    stmt = select(Product).filter(Product.is_active == True)
    
    or_conditions = []
    if intent.keywords:
        for keyword in intent.keywords:
            or_conditions.append(Product.title.ilike(f"%{keyword}%"))
            or_conditions.append(Product.description.ilike(f"%{keyword}%"))
    
    if mapped_category:
        or_conditions.append(Product.category.ilike(f"%{mapped_category}%"))
        
    if or_conditions:
        stmt = stmt.filter(or_(*or_conditions))
    
    # Rule 6: Price Logic (Only if explicitly mentioned)
    if intent.max_price:
        stmt = stmt.filter(Product.price <= intent.max_price)
        
    result = await db.execute(stmt.limit(8))
    products = result.scalars().all()
    
    # Rule 7: Fallback
    # If search returns empty -> return top 6 products from electronics category
    if not products:
        stmt_fallback = select(Product).filter(
            Product.is_active == True,
            Product.category.ilike("electronics")
        ).order_by(desc(Product.created_at))
        
        result_fallback = await db.execute(stmt_fallback.limit(6))
        products = result_fallback.scalars().all()
    
    return products

async def fallback_search(db: AsyncSession, query: str):
    # Same logic but without LLM extraction
    query = query.lower().strip()
    keywords = query.split()
    
    mapped_category = None
    for k in keywords:
        if k in CATEGORY_MAPPING:
            mapped_category = CATEGORY_MAPPING[k]
            break
            
    stmt = select(Product).filter(Product.is_active == True)
    
    or_conditions = []
    for keyword in keywords:
        or_conditions.append(Product.title.ilike(f"%{keyword}%"))
        or_conditions.append(Product.description.ilike(f"%{keyword}%"))
        
    if mapped_category:
        or_conditions.append(Product.category.ilike(f"%{mapped_category}%"))
        
    if or_conditions:
        stmt = stmt.filter(or_(*or_conditions))
        
    result = await db.execute(stmt.limit(8))
    products = result.scalars().all()
    
    if not products:
        stmt_fallback = select(Product).filter(
            Product.is_active == True,
            Product.category.ilike("electronics")
        ).order_by(desc(Product.created_at))
        result_fallback = await db.execute(stmt_fallback.limit(6))
        products = result_fallback.scalars().all()
        
    return products
