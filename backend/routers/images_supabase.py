"""
Image Upload Router for Supabase Storage
Handles signed URL generation for direct client uploads
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from services.supabase_storage import supabase_storage
from services.supabase_auth import get_supabase_user
from pydantic import BaseModel

router = APIRouter(prefix="/images", tags=["images"])

class UploadUrlRequest(BaseModel):
    bucket: str  # "products" or "profiles"
    filename: str

class MultipleUploadUrlRequest(BaseModel):
    bucket: str
    filenames: List[str]

@router.post("/upload-url")
async def get_upload_url(
    request: UploadUrlRequest,
    user = Depends(get_supabase_user)
):
    """
    Generate signed URL for direct client upload to Supabase Storage
    
    Client should:
    1. Call this endpoint to get signed URL
    2. Upload file directly to signed URL using PUT request
    3. Use the returned public_url in product/profile data
    """
    try:
        # Validate bucket
        if request.bucket not in ["products", "profiles"]:
            raise HTTPException(
                status_code=400, 
                detail="Invalid bucket. Use 'products' or 'profiles'"
            )
        
        # Extract user ID from Supabase user response
        user_id = user.user.id if hasattr(user, 'user') else user.id
        
        # Generate unique path
        path = supabase_storage.generate_upload_path(
            user_id=user_id,
            filename=request.filename,
            bucket_type=request.bucket
        )
        
        # Generate signed URL (valid for 1 hour)
        signed_url = supabase_storage.generate_signed_url(
            bucket=request.bucket,
            path=path,
            expires_in=3600
        )
        
        # Get public URL
        public_url = supabase_storage.get_public_url(
            bucket=request.bucket,
            path=path
        )
        
        return {
            "signed_url": signed_url,
            "path": path,
            "public_url": public_url,
            "expires_in": 3600
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload-multiple-urls")
async def get_multiple_upload_urls(
    request: MultipleUploadUrlRequest,
    user = Depends(get_supabase_user)
):
    """
    Generate multiple signed URLs for batch upload
    """
    try:
        if request.bucket not in ["products", "profiles"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid bucket. Use 'products' or 'profiles'"
            )
        
        urls = []
        for filename in request.filenames:
            # Extract user ID from Supabase user response
            user_id = user.user.id if hasattr(user, 'user') else user.id
            
            path = supabase_storage.generate_upload_path(
                user_id=user_id,
                filename=filename,
                bucket_type=request.bucket
            )
            signed_url = supabase_storage.generate_signed_url(
                bucket=request.bucket,
                path=path,
                expires_in=3600
            )
            public_url = supabase_storage.get_public_url(
                bucket=request.bucket,
                path=path
            )
            
            urls.append({
                "filename": filename,
                "signed_url": signed_url,
                "path": path,
                "public_url": public_url
            })
        
        return {"urls": urls}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{bucket}/{path:path}")
async def delete_image(
    bucket: str,
    path: str,
    user = Depends(get_supabase_user)
):
    """
    Delete image from Supabase Storage
    
    Only allows deletion of files owned by the user
    """
    try:
        # Extract user ID from Supabase user response
        user_id = user.user.id if hasattr(user, 'user') else user.id
        
        # Verify user owns the file (path starts with user_id)
        if not path.startswith(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file"
            )
        
        if bucket not in ["products", "profiles"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid bucket"
            )
        
        success = supabase_storage.delete_file(bucket, path)
        if success:
            return {"message": "Image deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete image"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

