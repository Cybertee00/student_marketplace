from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from typing import List
import shutil

from database import get_db
from models import User
from auth import get_current_user
from rbac import require_permission, Permissions
from hybrid_storage_service import hybrid_storage

router = APIRouter(prefix="/images", tags=["images"])

# Configuration
IMAGES_DIR = "products_images"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGES_PER_PRODUCT = 5

def ensure_images_directory():
    """Ensure the images directory exists"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

def is_valid_image_file(filename: str) -> bool:
    """Check if the file is a valid image"""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename for the uploaded image"""
    ext = os.path.splitext(original_filename)[1].lower()
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"

def save_uploaded_file(file: UploadFile, directory: str) -> str:
    """Save an uploaded file to a specific directory and return the filename"""
    # Ensure directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    file_path = os.path.join(directory, filename)
    
    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return filename
    except Exception as e:
        raise Exception(f"Failed to save file: {str(e)}")

@router.post("/upload")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a product image to Google Drive
    Returns the Google Drive file ID and public URL
    """
    
    print(f"Image upload request from user {current_user.username}")
    print(f"File: {file.filename}, Size: {file.size}")
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        print(f"File too large: {file.size} bytes")
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Check file extension
    if not is_valid_image_file(file.filename):
        print(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Google Drive
        result = hybrid_storage.save_image_locally(file_content, filename, "products")
        
        if result["success"]:
            print(f"Image uploaded to Google Drive successfully: {filename}")
            return {
                "success": True,
                "filename": filename,
                "file_id": result["file_id"],
                "public_url": result["public_url"],
                "url": result["public_url"],  # For backward compatibility
                "message": "Image uploaded successfully to Google Drive"
            }
        else:
            print(f"Failed to upload to Google Drive: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Failed to upload to Google Drive: {result['error']}")
        
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_product_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple product images to Google Drive
    Returns list of file IDs and public URLs
    """
    
    if len(files) > MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=400,
            detail=f"Too many images. Maximum {MAX_IMAGES_PER_PRODUCT} images allowed"
        )
    
    uploaded_files = []
    failed_files = []
    
    for file in files:
        try:
            # Check file size
            if file.size and file.size > MAX_FILE_SIZE:
                failed_files.append({
                    "filename": file.filename,
                    "error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
                })
                continue
            
            # Check file extension
            if not is_valid_image_file(file.filename):
                failed_files.append({
                    "filename": file.filename,
                    "error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                })
                continue
            
            # Generate unique filename
            filename = generate_unique_filename(file.filename)
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Google Drive
            result = hybrid_storage.save_image_locally(file_content, filename, "products")
            
            if result["success"]:
                uploaded_files.append({
                    "filename": filename,
                    "file_id": result["file_id"],
                    "public_url": result["public_url"],
                    "url": result["public_url"],  # For backward compatibility
                    "original_name": file.filename
                })
            else:
                failed_files.append({
                    "filename": file.filename,
                    "error": result["error"]
                })
            
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(uploaded_files) > 0,
        "uploaded": uploaded_files,
        "failed": failed_files,
        "message": f"Uploaded {len(uploaded_files)} images successfully"
    }

@router.get("/{filename}")
async def get_product_image(filename: str):
    """
    Serve a product image by filename
    """
    file_path = os.path.join(IMAGES_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)

@router.delete("/{filename}")
async def delete_product_image(
    filename: str,
    current_user: User = Depends(require_permission(Permissions.PRODUCTS_DELETE)),
    db: Session = Depends(get_db)
):
    """
    Delete a product image (admin only)
    """
    file_path = os.path.join(IMAGES_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        os.remove(file_path)
        return {
            "success": True,
            "message": f"Image {filename} deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

@router.get("/info/stats")
async def get_image_stats(
    current_user: User = Depends(require_permission(Permissions.PRODUCTS_READ)),
    db: Session = Depends(get_db)
):
    """
    Get image storage statistics (admin only)
    """
    ensure_images_directory()
    
    try:
        files = os.listdir(IMAGES_DIR)
        total_files = len(files)
        total_size = 0
        
        for filename in files:
            file_path = os.path.join(IMAGES_DIR, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
        
        return {
            "total_images": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": os.path.abspath(IMAGES_DIR)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/profile/{filename}")
async def get_profile_picture(filename: str):
    """Serve profile pictures"""
    profile_dir = "profile_pictures"
    file_path = os.path.join(profile_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Profile picture not found")
    
    return FileResponse(file_path)
