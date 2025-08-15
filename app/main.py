# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db import base

from fastapi.staticfiles import StaticFiles

# Import tất cả models để Alembic có thể detect
# Điều này đảm bảo rằng tất cả models được đăng ký với SQLAlchemy
from app.models import user  # Import các models khác khi có: shop, product, etc.

def create_application() -> FastAPI:
    """
    Tạo và cấu hình ứng dụng FastAPI
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Cấu hình CORS
    setup_cors(app)
    
    # Cấu hình middleware bảo mật
    setup_middleware(app)
    
    # Đăng ký các routes
    setup_routers(app)
    
    # Cấu hình exception handlers
    setup_exception_handlers(app)

    # Serve static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    return app

def setup_cors(app: FastAPI) -> None:
    """
    Cấu hình CORS middleware
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
        ],
    )

def setup_middleware(app: FastAPI) -> None:
    """
    Cấu hình các middleware bảo mật
    """
    # Trusted Host Middleware - bảo vệ khỏi Host header attacks
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=settings.ALLOWED_HOSTS
        )

def setup_routers(app: FastAPI) -> None:
    """
    Đăng ký các API routes
    """
    # Đăng ký API v1
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """
        Endpoint kiểm tra sức khỏe của service
        """
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint - thông tin cơ bản về API
        """
        return {
            "message": f"Welcome to {settings.PROJECT_NAME}",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
            "redoc": f"{settings.API_V1_STR}/redoc"
        }

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Cấu hình các exception handlers tùy chỉnh
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handler cho HTTP exceptions
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handler cho validation errors
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "message": "Validation error",
                "status_code": 422,
                "path": request.url.path,
                "details": errors
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handler cho các exception chung (500 Internal Server Error)
        """
        # Trong production, bạn nên log lỗi chi tiết nhưng không trả về cho client
        # import logging
        # logging.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "message": "Internal server error",
                "status_code": 500,
                "path": request.url.path
            }
        )

# Tạo ứng dụng FastAPI
app = create_application()

# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Xử lý khi ứng dụng khởi động
    """
    print(f"🚀 {settings.PROJECT_NAME} is starting up...")
    print(f"📖 Documentation available at: {settings.API_V1_STR}/docs")
    print(f"🔗 API base URL: {settings.API_V1_STR}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Xử lý khi ứng dụng tắt
    """
    print(f"🛑 {settings.PROJECT_NAME} is shutting down...")

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )