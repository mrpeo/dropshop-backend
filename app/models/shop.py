# app/models/shop.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from app.db.base_class import Base
from app.core.utils import generate_random_uid

class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    shopid = Column(String(50), unique=True, index=True, default=lambda: generate_random_uid(15))
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, index=True, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    logo_url = Column(String)
    hotline = Column(String(128))
    address = Column(String(255))
    province_id = Column(String(64))
    district_id = Column(String(64))
    bank_account_name = Column(String(255))
    bank_account_number = Column(String(50))
    bank_name = Column(String(100))
    footer_copyright = Column(Text)
    
    tracking_scripts = Column(JSON) # {"header_script": "...", "footer_script": "..."}
    
    default_shipping_fee = Column(Numeric(15, 2), default=0)
    free_shipping_threshold = Column(Numeric(15, 2), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Mối quan hệ: Một Shop thuộc về một User (owner)
    owner = relationship("User", back_populates="shop")