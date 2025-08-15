# app/core/file_handler.py
import os
import uuid
import aiofiles
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

class FileHandler:
    def __init__(self, base_path: str = "app/static/uploads"):
        self.base_path = base_path
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_image_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        
        # Tạo thư mục nếu chưa có
        os.makedirs(f"{base_path}/avatars", exist_ok=True)
        os.makedirs(f"{base_path}/products", exist_ok=True)
        os.makedirs(f"{base_path}/temp", exist_ok=True)
    
    def validate_image(self, file: UploadFile) -> None:
        """Validate file type và size"""
        if file.content_type not in self.allowed_image_types:
            raise HTTPException(400, "File type not supported")
        
        if file.size and file.size > self.max_file_size:
            raise HTTPException(400, f"File too large. Max size: {self.max_file_size // (1024*1024)}MB")
    
    async def resize_image(self, image_data: bytes, max_width: int = 1366, max_height: int = 1080) -> bytes:
        """Resize ảnh để tối ưu storage"""
        image = Image.open(io.BytesIO(image_data))
        
        # Giữ aspect ratio
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Convert về RGB nếu cần
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Save về bytes
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()
    
    async def save_image(self, file: UploadFile, folder: str, resize: bool = True) -> str:
        """Lưu ảnh và return filename"""
        self.validate_image(file)
        
        # Tạo unique filename
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = f"{self.base_path}/{folder}/{filename}"
        
        # Đọc file content
        content = await file.read()
        
        # Resize nếu cần
        if resize and file.content_type.startswith("image/"):
            if folder == "avatars":
                content = await self.resize_image(content, 200, 200)  # Avatar nhỏ
            else:
                content = await self.resize_image(content, 800, 600)  # Product image
        
        # Lưu file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        return filename
    
    def delete_file(self, filename: str, folder: str) -> bool:
        """Xóa file"""
        try:
            file_path = f"{self.base_path}/{folder}/{filename}"
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    def get_file_url(self, filename: str, folder: str) -> str:
        """Tạo URL để access file"""
        return f"/static/uploads/{folder}/{filename}"

file_handler = FileHandler()