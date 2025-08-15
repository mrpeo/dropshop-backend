# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Tạo engine kết nối với CSDL
engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)

# Tạo một lớp SessionLocal, mỗi instance của lớp này sẽ là một phiên làm việc với CSDL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)