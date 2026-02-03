from pydantic import BaseModel
from typing import List, Optional

class AISearchQuery(BaseModel):
    query: str

class IntentData(BaseModel):
    category: Optional[str] = None
    max_price: Optional[float] = None
    keywords: List[str] = []
