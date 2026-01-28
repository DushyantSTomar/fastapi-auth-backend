from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    image_url = Column(String)
    category = Column(String, default="electronics")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
