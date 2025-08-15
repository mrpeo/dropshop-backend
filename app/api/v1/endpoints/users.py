# app/api/v1/endpoints/users.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_user
from app.schemas.user import (
    User, UserCreate, UserUpdate, UserListResponse, 
    UserStatusUpdate, UserPasswordUpdate
)

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1, description="Số trang"),
    limit: int = Query(10, ge=1, le=100, description="Số items per page"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc email"),
    role: Optional[str] = Query(None, description="Lọc theo vai trò"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Lấy danh sách users với phân trang.
    
    - **page**: Số trang (bắt đầu từ 1)
    - **limit**: Số lượng users trên mỗi trang (tối đa 100)
    - **search**: Tìm kiếm theo tên hoặc email
    - **role**: Lọc theo vai trò (customer, affiliator, shop_owner, sysadmin)
    """
    # Kiểm tra quyền (chỉ sysadmin và shop_owner có thể xem danh sách users)
    if current_user.role not in ["sysadmin", "shop_owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để truy cập tính năng này"
        )
    
    users, pagination_info = crud_user.get_users_paginated(
        db=db, 
        page=page, 
        limit=limit, 
        search=search, 
        role=role
    )
    
    return UserListResponse(
        data=users,
        pagination=pagination_info
    )


@router.get("/{uid}", response_model=User)
def get_user(
    uid: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Lấy thông tin chi tiết một user theo UID."""
    # Kiểm tra quyền
    if current_user.role not in ["sysadmin", "shop_owner"] and current_user.uid != uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để truy cập thông tin này"
        )
    
    user = crud_user.get_user_by_uid(db=db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Tạo user mới."""
    # Kiểm tra quyền (chỉ sysadmin có thể tạo user)
    if current_user.role != "sysadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ sysadmin mới có quyền tạo user"
        )
    
    # Kiểm tra email đã tồn tại
    if crud_user.check_email_exists(db=db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Kiểm tra số điện thoại (nếu có)
    if user_in.phone_number and crud_user.check_phone_exists(db=db, phone=user_in.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại đã được sử dụng"
        )
    
    # Kiểm tra CCCD (nếu có)
    if user_in.cccd and crud_user.check_cccd_exists(db=db, cccd=user_in.cccd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số CCCD đã được sử dụng"
        )
    
    user = crud_user.create_user(db=db, user_in=user_in)
    return user


@router.put("/{uid}", response_model=User)
def update_user(
    uid: str,
    user_in: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Cập nhật thông tin user."""
    # Tìm user cần cập nhật
    user = crud_user.get_user_by_uid(db=db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Kiểm tra quyền
    if current_user.role not in ["sysadmin", "shop_owner"] and current_user.uid != uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để cập nhật thông tin này"
        )
    
    # Kiểm tra email trùng lặp (nếu có thay đổi)
    if user_in.email and user_in.email != user.email:
        if crud_user.check_email_exists(db=db, email=user_in.email, exclude_uid=uid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
    
    # Kiểm tra phone trùng lặp (nếu có thay đổi)
    if user_in.phone_number and user_in.phone_number != user.phone_number:
        if crud_user.check_phone_exists(db=db, phone=user_in.phone_number, exclude_uid=uid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số điện thoại đã được sử dụng"
            )
    
    # Kiểm tra CCCD trùng lặp (nếu có thay đổi)
    if user_in.cccd and user_in.cccd != user.cccd:
        if crud_user.check_cccd_exists(db=db, cccd=user_in.cccd, exclude_uid=uid):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Số CCCD đã được sử dụng"
            )
    
    # Không cho phép user thường thay đổi role của mình
    if current_user.uid == uid and current_user.role != "sysadmin" and user_in.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không thể thay đổi vai trò của chính mình"
        )
    
    user = crud_user.update_user(db=db, user=user, user_in=user_in)
    return user


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    uid: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Xóa user."""
    # Tìm user cần xóa
    user = crud_user.get_user_by_uid(db=db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Kiểm tra quyền (chỉ sysadmin có thể xóa user)
    if current_user.role != "sysadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ sysadmin mới có quyền xóa user"
        )
    
    # Không cho phép xóa chính mình
    if current_user.uid == uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa chính mình"
        )
    
    crud_user.delete_user(db=db, user=user)
    return None


@router.patch("/{uid}/status", response_model=User)
def update_user_status(
    uid: str,
    status_in: UserStatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Kích hoạt/vô hiệu hóa user."""
    # Tìm user
    user = crud_user.get_user_by_uid(db=db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Kiểm tra quyền
    if current_user.role not in ["sysadmin", "shop_owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để thực hiện hành động này"
        )
    
    # Không cho phép vô hiệu hóa chính mình
    if current_user.uid == uid and not status_in.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể vô hiệu hóa chính mình"
        )
    
    user = crud_user.update_user_status(db=db, user=user, is_active=status_in.is_active)
    return user


@router.patch("/{uid}/password", status_code=status.HTTP_204_NO_CONTENT)
def change_user_password(
    uid: str,
    password_in: UserPasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Đổi mật khẩu user."""
    # Tìm user
    user = crud_user.get_user_by_uid(db=db, uid=uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy user"
        )
    
    # Kiểm tra quyền
    if current_user.role not in ["sysadmin", "shop_owner"] and current_user.uid != uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để thay đổi mật khẩu này"
        )
    
    crud_user.change_user_password(db=db, user=user, new_password=password_in.password)
    return None