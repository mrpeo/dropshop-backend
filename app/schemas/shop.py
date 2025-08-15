# app/schemas/shop.py

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# --- Properties chung ---
class ShopBase(BaseModel):
    name: str
    subdomain: str

# --- Schema để tạo shop ---
class ShopCreate(ShopBase):
    pass

# --- Schema để cập nhật shop ---
class ShopUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    footer_copyright: Optional[str] = None
    tracking_scripts: Optional[Dict[str, Any]] = None
    default_shipping_fee: Optional[float] = None
    free_shipping_threshold: Optional[float] = None

# --- Schema công khai cho khách xem ---
class ShopPublic(BaseModel):
    shopid: str
    name: str
    logo_url: Optional[str] = None
    footer_copyright: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schema đầy đủ trả về cho chủ shop ---
class Shop(ShopBase):
    id: int
    shopid: str
    owner_id: int
    is_active: bool
    default_shipping_fee: float
    free_shipping_threshold: Optional[float] = None
    created_at: datetime
    
    # Thêm các trường cần thiết khác nếu muốn
    bank_account_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None

    class Config:
        from_attributes = True