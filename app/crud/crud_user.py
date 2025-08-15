# app/crud/crud_user.py

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import create_password_hash
import math


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Lấy user theo email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """Lấy user bằng mã uid công khai."""
    return db.query(User).filter(User.uid == uid).first()


def get_users_paginated(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    role: Optional[str] = None
) -> Tuple[List[User], dict]:
    """
    Lấy danh sách users với phân trang và filter.
    
    Args:
        db: Database session
        page: Số trang (bắt đầu từ 1)
        limit: Số items per page
        search: Từ khóa tìm kiếm (tìm trong full_name và email)
        role: Lọc theo vai trò
    
    Returns:
        Tuple[List[User], dict]: (danh sách users, thông tin pagination)
    """
    query = db.query(User)
    
    # Áp dụng filter theo search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Áp dụng filter theo role
    if role and role != "all":
        try:
            user_role = UserRole(role)
            query = query.filter(User.role == user_role)
        except ValueError:
            # Role không hợp lệ, bỏ qua filter
            pass
    
    # Đếm tổng số records
    total_items = query.count()
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 1
    
    # Tính offset
    offset = (page - 1) * limit
    
    # Lấy data với pagination, sắp xếp theo created_at desc
    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    # Tính toán thông tin pagination
    has_next = page < total_pages
    has_prev = page > 1
    
    pagination_info = {
        "current_page": page,
        "total_pages": total_pages,
        "total_items": total_items,
        "items_per_page": limit,
        "has_next": has_next,
        "has_prev": has_prev
    }
    
    return users, pagination_info


def create_user(db: Session, user_in: UserCreate) -> User:
    """Tạo user mới."""
    hashed_password = create_password_hash(user_in.password)
    
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        cccd=user_in.cccd,
        role=user_in.role,
        is_active=user_in.is_active,
        hashed_password=hashed_password,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Cập nhật thông tin user."""
    update_data = user_in.dict(exclude_unset=True)
    
    # Xử lý password riêng nếu có
    if "password" in update_data:
        password = update_data.pop("password")
        if password:  # Chỉ hash nếu password không rỗng
            update_data["hashed_password"] = create_password_hash(password)
    
    # Cập nhật các trường khác
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> bool:
    """Xóa user."""
    db.delete(user)
    db.commit()
    return True


def update_user_status(db: Session, user: User, is_active: bool) -> User:
    """Cập nhật trạng thái active của user."""
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def change_user_password(db: Session, user: User, new_password: str) -> User:
    """Đổi mật khẩu user."""
    user.hashed_password = create_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user


def check_email_exists(db: Session, email: str, exclude_uid: Optional[str] = None) -> bool:
    """Kiểm tra email đã tồn tại chưa (dùng cho validation)."""
    query = db.query(User).filter(User.email == email)
    if exclude_uid:
        query = query.filter(User.uid != exclude_uid)
    return query.first() is not None


def check_phone_exists(db: Session, phone: str, exclude_uid: Optional[str] = None) -> bool:
    """Kiểm tra số điện thoại đã tồn tại chưa."""
    query = db.query(User).filter(User.phone_number == phone)
    if exclude_uid:
        query = query.filter(User.uid != exclude_uid)
    return query.first() is not None


def check_cccd_exists(db: Session, cccd: str, exclude_uid: Optional[str] = None) -> bool:
    """Kiểm tra CCCD đã tồn tại chưa."""
    query = db.query(User).filter(User.cccd == cccd)
    if exclude_uid:
        query = query.filter(User.uid != exclude_uid)
    return query.first() is not None