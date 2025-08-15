# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
from app.core import security

router = APIRouter()

# Schema cho login request với JSON
class LoginRequest(BaseModel):
    username: str  # hoặc email
    password: str

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(deps.get_db)
):
    """
    Đăng nhập để lấy access token.
    Nhận JSON với username (email) và password.
    """
    user = crud.crud_user.get_user_by_email(db, email=login_data.username)
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=user.uid)
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint cũ cho compatibility (nếu cần)
@router.post("/login/form", response_model=schemas.Token)
def login_form_for_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Đăng nhập với form data (OAuth2 standard).
    Username chính là email.
    """
    user = crud.crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
):
    user = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email này đã được sử dụng.",
        )
    user = crud.crud_user.create_user(db, user_in=user_in)
    return user

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Lấy thông tin của user đang đăng nhập."""
    return current_user