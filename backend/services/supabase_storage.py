"""
Supabase Storage Service
Handles image storage operations using Supabase Storage
"""

from supabase import Client
from supabase_config import supabase
from typing import List, Optional
import uuid
from datetime import datetime

class SupabaseStorageService:
    """Service for managing images in Supabase Storage"""
    
    def __init__(self):
        self.client = supabase
        self.products_bucket = "products"
        self.profiles_bucket = "profiles"
    
    def generate_signed_url(
        self, 
        bucket: str, 
        path: str, 
        expires_in: int = 3600
    ) -> str:
        """
        Generate signed URL for direct client upload
        
        Args:
            bucket: Storage bucket name ('products' or 'profiles')
            path: File path in bucket
            expires_in: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            Signed URL string
        """
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                path=path,
                expires_in=expires_in
            )
            return response.get("signedURL") or response.get("signedUrl")
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """
        Get public URL for a file (for public buckets)
        
        Args:
            bucket: Storage bucket name
            path: File path in bucket
        
        Returns:
            Public URL string
        """
        supabase_url = self.client.supabase_url
        return f"{supabase_url}/storage/v1/object/public/{bucket}/{path}"
    
    def generate_upload_path(
        self, 
        user_id: str, 
        filename: str, 
        bucket_type: str = "products"
    ) -> str:
        """
        Generate unique upload path
        
        Args:
            user_id: User UUID
            filename: Original filename
            bucket_type: Type of bucket ('products' or 'profiles')
        
        Returns:
            Unique file path
        """
        ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{user_id}/{timestamp}_{unique_id}.{ext}"
    
    def delete_file(self, bucket: str, path: str) -> bool:
        """
        Delete file from storage
        
        Args:
            bucket: Storage bucket name
            path: File path in bucket
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(
        self, 
        bucket: str, 
        folder: Optional[str] = None
    ) -> List[str]:
        """
        List files in a bucket/folder
        
        Args:
            bucket: Storage bucket name
            folder: Optional folder path
        
        Returns:
            List of file names
        """
        try:
            if folder:
                files = self.client.storage.from_(bucket).list(folder)
            else:
                files = self.client.storage.from_(bucket).list()
            return [f["name"] for f in files]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def upload_file(
        self,
        bucket: str,
        path: str,
        file_content: bytes,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Upload file directly to Supabase Storage (server-side)
        Note: For client-side uploads, use signed URLs instead
        
        Args:
            bucket: Storage bucket name
            path: File path in bucket
            file_content: File content as bytes
            content_type: MIME type (optional)
        
        Returns:
            True if successful
        """
        try:
            options = {}
            if content_type:
                options["content-type"] = content_type
            
            self.client.storage.from_(bucket).upload(
                path=path,
                file=file_content,
                file_options=options
            )
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

# Create instance
supabase_storage = SupabaseStorageService()

