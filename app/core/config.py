# app/core/config.py - Version đơn giản để tránh lỗi
import os
from typing import List

# Tải biến môi trường từ file .env (cần cài python-dotenv)
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # Thông tin dự án
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dropshop Backend API")
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend API for E-commerce Platform"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dropshop-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dropshop.db")
    
    # CORS
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        if cors_origins:
            return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Allowed hosts for security  
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        if allowed_hosts:
            return [host.strip() for host in allowed_hosts.split(",") if host.strip()]
        return ["localhost", "127.0.0.1"]

settings = Settings()