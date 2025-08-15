# app/models/user.py

import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

from app.core.utils import generate_random_uid

class UserRole(str, enum.Enum):
    sysadmin = "sysadmin"
    shop_owner = "shop_owner"
    affiliator = "affiliator"
    customer = "customer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(50), unique=True, index=True, default=lambda: generate_random_uid(16))
    full_name = Column(String(255))
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String)
    cccd = Column(String(20), unique=True)
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Mối quan hệ: Một User (shop_owner) có một Shop
    shop = relationship("Shop", back_populates="owner", uselist=False)