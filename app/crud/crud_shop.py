# app/crud/crud_shop.py

from sqlalchemy.orm import Session
from app.models.shop import Shop
from app.schemas.shop import ShopCreate

def get_shop_by_owner(db: Session, owner_id: int) -> Shop | None:
    return db.query(Shop).filter(Shop.owner_id == owner_id).first()

def get_shop_by_subdomain(db: Session, subdomain: str) -> Shop | None:
    return db.query(Shop).filter(Shop.subdomain == subdomain).first()

def get_shop_by_shopid(db: Session, shopid: str) -> Shop | None:
    """Lấy shop bằng mã shopid công khai."""
    return db.query(Shop).filter(Shop.shopid == shopid).first()

def create_shop(db: Session, shop_in: ShopCreate, owner_id: int) -> Shop:
    db_shop = Shop(
        **shop_in.model_dump(),
        owner_id=owner_id
    )
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop