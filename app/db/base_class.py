# app/db/base_class.py

from sqlalchemy.orm import declarative_base

# Khai báo Base ở đây.
# Bất kỳ model nào cũng sẽ import Base từ file này.
Base = declarative_base()