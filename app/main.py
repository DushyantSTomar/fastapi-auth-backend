from fastapi import FastAPI
from app.core.config import settings
from app.routers import health, auth, users, products

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to FastAPI Backend", "docs": "/docs"}

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
