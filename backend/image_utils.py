#!/usr/bin/env python3
"""
Image Management Utilities
Helper functions for managing product images
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

class ImageManager:
    """Utility class for managing product images"""
    
    def __init__(self, base_url: str = "http://172.16.8.138:8000"):
        self.base_url = base_url
        self.images_dir = "products_images"
    
    def upload_single_image(self, image_path: str, auth_token: str) -> Dict:
        """
        Upload a single image to the server
        
        Args:
            image_path: Path to the image file
            auth_token: Authentication token
            
        Returns:
            Dict with upload result
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": "Image file not found"}
        
        url = f"{self.base_url}/api/images/upload"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            with open(image_path, "rb") as file:
                files = {"file": file}
                response = requests.post(url, headers=headers, files=files)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_multiple_images(self, image_paths: List[str], auth_token: str) -> Dict:
        """
        Upload multiple images to the server
        
        Args:
            image_paths: List of paths to image files
            auth_token: Authentication token
            
        Returns:
            Dict with upload results
        """
        url = f"{self.base_url}/api/images/upload-multiple"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            files = []
            for i, image_path in enumerate(image_paths):
                if os.path.exists(image_path):
                    files.append(("files", open(image_path, "rb")))
                else:
                    return {"success": False, "error": f"Image file not found: {image_path}"}
            
            response = requests.post(url, headers=headers, files=files)
            
            # Close all files
            for _, file in files:
                file.close()
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_image_url(self, filename: str) -> str:
        """
        Get the full URL for an image
        
        Args:
            filename: Image filename
            
        Returns:
            Full URL to the image
        """
        return f"{self.base_url}/images/{filename}"
    
    def delete_image(self, filename: str, auth_token: str) -> Dict:
        """
        Delete an image from the server
        
        Args:
            filename: Image filename
            auth_token: Authentication token
            
        Returns:
            Dict with deletion result
        """
        url = f"{self.base_url}/images/{filename}"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_image_stats(self, auth_token: str) -> Dict:
        """
        Get image storage statistics
        
        Args:
            auth_token: Authentication token
            
        Returns:
            Dict with storage statistics
        """
        url = f"{self.base_url}/api/images/info/stats"
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup_orphaned_images(self, used_filenames: List[str], auth_token: str) -> Dict:
        """
        Clean up orphaned images (images not used by any product)
        
        Args:
            used_filenames: List of filenames currently in use
            auth_token: Authentication token
            
        Returns:
            Dict with cleanup results
        """
        if not os.path.exists(self.images_dir):
            return {"success": True, "deleted": 0, "message": "No images directory"}
        
        deleted_count = 0
        failed_deletions = []
        
        for filename in os.listdir(self.images_dir):
            if filename not in used_filenames:
                result = self.delete_image(filename, auth_token)
                if result.get("success"):
                    deleted_count += 1
                else:
                    failed_deletions.append({"filename": filename, "error": result.get("error")})
        
        return {
            "success": True,
            "deleted": deleted_count,
            "failed": failed_deletions,
            "message": f"Deleted {deleted_count} orphaned images"
        }

def validate_image_file(file_path: str) -> Dict:
    """
    Validate an image file before upload
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dict with validation result
    """
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    if not os.path.exists(file_path):
        return {"valid": False, "error": "File does not exist"}
    
    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False, 
            "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB"
        }
    
    return {"valid": True, "size": file_size}

def generate_image_filename(original_name: str) -> str:
    """
    Generate a unique filename for an image
    
    Args:
        original_name: Original filename
        
    Returns:
        Unique filename
    """
    import uuid
    ext = os.path.splitext(original_name)[1].lower()
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"
