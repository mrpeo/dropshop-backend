#!/usr/bin/env python3
"""
Script để chạy development server
Usage: python run_dev.py
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,  # Auto reload khi code thay đổi
        log_level="debug",
        access_log=True,
        reload_dirs=["app"],  # Chỉ watch thư mục app
    )