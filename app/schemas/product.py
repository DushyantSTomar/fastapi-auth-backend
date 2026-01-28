from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    category: str
    is_active: bool = True

class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedProductResponse(BaseModel):
    data: List[ProductOut]
    page: int
    hasMore: bool
