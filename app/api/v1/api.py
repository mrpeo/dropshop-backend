# app/api/v1/api.py

from fastapi import APIRouter

from app.api.v1.endpoints import auth, shops, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(shops.router, prefix="/shops", tags=["Shops"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# ... sau này sẽ include_router cho products, orders, etc.