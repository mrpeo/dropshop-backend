# app/db/base.py

# File này dùng để tập hợp và cung cấp Base class cùng với các models
# cho các phần khác của ứng dụng.

from app.db.base_class import Base  # MỚI: Import từ file base_class
from app.models.user import User
from app.models.shop import Shop
# ... sau này import các model khác như Product, Order ở đây