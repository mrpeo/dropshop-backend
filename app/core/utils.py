# app/core/utils.py

import secrets
import string

def generate_random_id(prefix: str, length: int = 16) -> str:
    """
    Tạo ra một mã định danh ngẫu nhiên, an toàn cho URL.
    Ví dụ: generate_random_id("usr") -> "usr_aB2cdEfGhI1jKlMn"
    """
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}_{random_part}"

def generate_random_uid(length: int = 16) -> str:
    """
    Tạo ra một mã định danh ngẫu nhiên, an toàn cho URL.
    Ví dụ: generate_random_id("usr") -> "usr_aB2cdEfGhI1jKlMn"
    """
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{random_part}"