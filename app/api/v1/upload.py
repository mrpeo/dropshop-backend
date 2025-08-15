# app/api/v1/endpoints/upload.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.core.file_handler import file_handler
from app.models.user import User

router = APIRouter()

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """Upload avatar cho user"""
    try:
        # Xóa avatar cũ nếu có
        if current_user.avatar:
            file_handler.delete_file(current_user.avatar, "avatars")
        
        # Lưu avatar mới
        filename = await file_handler.save_image(file, "avatars", resize=True)
        
        # Cập nhật user record
        current_user.avatar = filename
        db.commit()
        
        return {
            "success": True,
            "message": "Avatar uploaded successfully",
            "data": {
                "filename": filename,
                "url": file_handler.get_file_url(filename, "avatars")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.post("/product-images")
async def upload_product_images(
    files: List[UploadFile] = File(...),
    product_id: Optional[int] = Form(None),
    current_user: User = Depends(deps.get_current_user)
):
    """Upload nhiều ảnh sản phẩm"""
    if len(files) > 10:  # Giới hạn 10 ảnh
        raise HTTPException(400, "Too many files. Maximum 10 images allowed.")
    
    uploaded_files = []
    try:
        for file in files:
            filename = await file_handler.save_image(file, "products", resize=True)
            uploaded_files.append({
                "filename": filename,
                "url": file_handler.get_file_url(filename, "products"),
                "original_name": file.filename
            })
        
        return {
            "success": True,
            "message": f"Uploaded {len(uploaded_files)} images successfully",
            "data": uploaded_files
        }
    except HTTPException:
        # Cleanup đã upload nếu có lỗi
        for uploaded in uploaded_files:
            file_handler.delete_file(uploaded["filename"], "products")
        raise
    except Exception as e:
        # Cleanup
        for uploaded in uploaded_files:
            file_handler.delete_file(uploaded["filename"], "products")
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.delete("/file/{folder}/{filename}")
async def delete_file(
    folder: str,
    filename: str,
    current_user: User = Depends(deps.get_current_user)
):
    """Xóa file"""
    if folder not in ["avatars", "products"]:
        raise HTTPException(400, "Invalid folder")
    
    success = file_handler.delete_file(filename, folder)
    if success:
        return {"success": True, "message": "File deleted successfully"}
    else:
        raise HTTPException(404, "File not found")