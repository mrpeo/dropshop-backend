# app/schemas/user.py

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    sysadmin = "sysadmin"
    shop_owner = "shop_owner"
    affiliator = "affiliator"
    customer = "customer"


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    cccd: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.customer
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    cccd: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


class UserInDB(UserBase):
    uid: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """User schema for response (không trả về password)"""
    pass


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=6)


# Pagination schemas
class PaginationInfo(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    items_per_page: int
    has_next: bool
    has_prev: bool


class UserListResponse(BaseModel):
    data: list[User]
    pagination: PaginationInfo