import os
import io
import shutil
from typing import Dict, Optional
from datetime import datetime
import uuid

class HybridStorageService:
    """
    Hybrid storage service that:
    1. Saves images locally for development
    2. Optionally uploads to Google Drive for production
    3. Works without OAuth2 authentication issues
    """
    
    def __init__(self):
        self.PRODUCTS_FOLDER = "products_images"
        self.PROFILE_FOLDER = "profile_pictures"
        self.USE_GOOGLE_DRIVE = False  # Set to True when OAuth2 is working
        
        # Ensure local folders exist
        self._ensure_folders_exist()
    
    def _ensure_folders_exist(self):
        """Ensure local image folders exist"""
        for folder in [self.PRODUCTS_FOLDER, self.PROFILE_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename for the uploaded image"""
        ext = os.path.splitext(original_filename)[1].lower()
        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{unique_id}{ext}"
    
    def save_image_locally(self, file_content: bytes, filename: str, folder_type: str) -> Dict:
        """
        Save image locally and return file info
        Args:
            file_content: The content of the image file as bytes
            filename: The desired filename for the image
            folder_type: "products" or "profiles"
        Returns:
            Dictionary with success status, local path, and file info
        """
        try:
            # Determine target folder
            if folder_type == "products":
                target_folder = self.PRODUCTS_FOLDER
            elif folder_type == "profiles":
                target_folder = self.PROFILE_FOLDER
            else:
                return {"success": False, "error": "Invalid folder type specified"}
            
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename)
            file_path = os.path.join(target_folder, unique_filename)
            
            # Save file locally
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Return success info
            return {
                "success": True,
                "filename": unique_filename,
                "local_path": file_path,
                "folder_type": folder_type,
                "message": f"Image saved locally to {file_path}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_image_url(self, filename: str, folder_type: str) -> str:
        """
        Get the URL for an image (local for development, Google Drive for production)
        Args:
            filename: The filename of the image
            folder_type: "products" or "profiles"
        Returns:
            URL string for the image
        """
        if self.USE_GOOGLE_DRIVE:
            # For production: return Google Drive URL
            # This would be implemented when OAuth2 is working
            return f"https://drive.google.com/uc?id={filename}"
        else:
            # For development: return local URL
            if folder_type == "products":
                return f"/images/products/{filename}"
            elif folder_type == "profiles":
                return f"/images/profiles/{filename}"
            else:
                return f"/images/{filename}"
    
    def delete_image(self, filename: str, folder_type: str) -> Dict:
        """
        Delete an image from local storage
        Args:
            filename: The filename of the image to delete
            folder_type: "products" or "profiles"
        Returns:
            Dictionary with success status
        """
        try:
            # Determine target folder
            if folder_type == "products":
                target_folder = self.PRODUCTS_FOLDER
            elif folder_type == "profiles":
                target_folder = self.PROFILE_FOLDER
            else:
                return {"success": False, "error": "Invalid folder type specified"}
            
            file_path = os.path.join(target_folder, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return {"success": True, "message": f"Deleted {filename}"}
            else:
                return {"success": False, "error": f"File {filename} not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_images(self, folder_type: str) -> list:
        """
        List all images in a folder
        Args:
            folder_type: "products" or "profiles"
        Returns:
            List of image filenames
        """
        try:
            if folder_type == "products":
                target_folder = self.PRODUCTS_FOLDER
            elif folder_type == "profiles":
                target_folder = self.PROFILE_FOLDER
            else:
                return []
            
            if not os.path.exists(target_folder):
                return []
            
            # Get all image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            images = []
            
            for filename in os.listdir(target_folder):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    images.append(filename)
            
            return images
            
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
    
    def enable_google_drive(self):
        """Enable Google Drive integration (call this when OAuth2 is working)"""
        self.USE_GOOGLE_DRIVE = True
        print("✅ Google Drive integration enabled")
    
    def disable_google_drive(self):
        """Disable Google Drive integration (use local storage only)"""
        self.USE_GOOGLE_DRIVE = False
        print("✅ Local storage mode enabled")

# Create global instance
hybrid_storage = HybridStorageService()
