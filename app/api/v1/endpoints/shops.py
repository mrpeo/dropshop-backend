# app/api/v1/endpoints/shops.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.Shop, status_code=201)
def create_shop(
    *,
    db: Session = Depends(deps.get_db),
    shop_in: schemas.ShopCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    User đã đăng nhập tạo một shop mới.
    """
    # Kiểm tra xem user đã có shop chưa
    existing_shop = crud.crud_shop.get_shop_by_owner(db, owner_id=current_user.id)
    if existing_shop:
        raise HTTPException(status_code=400, detail="User already owns a shop.")
    
    # Kiểm tra subdomain đã tồn tại chưa
    existing_subdomain = crud.crud_shop.get_shop_by_subdomain(db, subdomain=shop_in.subdomain)
    if existing_subdomain:
        raise HTTPException(status_code=400, detail="Subdomain already registered.")
        
    shop = crud.crud_shop.create_shop(db=db, shop_in=shop_in, owner_id=current_user.id)
    
    # Cập nhật vai trò user thành shop_owner
    current_user.role = models.user.UserRole.shop_owner
    db.add(current_user)
    db.commit()
    
    return shop

@router.get("/my-shop", response_model=schemas.Shop)
def get_my_shop(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy thông tin shop của chủ shop đang đăng nhập."""
    if current_user.role != models.user.UserRole.shop_owner:
        raise HTTPException(status_code=403, detail="User is not a shop owner.")
        
    shop = crud.crud_shop.get_shop_by_owner(db, owner_id=current_user.id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found.")
        
    return shop