# app/api/deps.py

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core import config
from app.core.security import decode_access_token
from app.crud import crud_user
from app.db.session import SessionLocal
from app.models.user import User

# Security scheme
security = HTTPBearer()


def get_db() -> Generator:
    """Dependency để lấy database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(security)
) -> User:
    """
    Dependency để lấy user hiện tại từ JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = decode_access_token(token.credentials)
        if payload is None:
            raise credentials_exception
            
        user_uid: str = payload.get("sub")
        if user_uid is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Lấy user từ database
    user = crud_user.get_user_by_uid(db=db, uid=user_uid)
    if user is None:
        raise credentials_exception
        
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency để lấy user hiện tại và đảm bảo user đang active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency để đảm bảo user hiện tại là sysadmin.
    """
    if current_user.role != "sysadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để truy cập tính năng này"
        )
    return current_user


def get_current_shop_owner_or_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency để đảm bảo user hiện tại là shop_owner hoặc sysadmin.
    """
    if current_user.role not in ["sysadmin", "shop_owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để truy cập tính năng này"
        )
    return current_user