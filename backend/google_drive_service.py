#!/usr/bin/env python3
"""
Google Drive Service for Image Storage
Handles uploading, downloading, and managing images in Google Drive
"""

import os
import io
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

class GoogleDriveService:
    """Service for managing images in Google Drive"""
    
    def __init__(self):
        # Google Drive folder IDs
        self.PRODUCTS_FOLDER_ID = "156ZsoOjj9nUICNjGdS8_kAnzQc1569JC"
        self.PROFILE_PICTURES_FOLDER_ID = "1jknOL8yP2fDxLi9r_6mz8OK4fy54FdUM"
        
        # Initialize Google Drive service
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Drive service with service account credentials"""
        try:
            # You'll need to create a service account and download the JSON key file
            # For now, we'll use a placeholder approach
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'google-credentials.json')
            
            if not os.path.exists(credentials_path):
                print(f"Warning: Google credentials file not found at {credentials_path}")
                print("Please create a service account and download the JSON key file")
                return None
            
            # Define the scopes
            SCOPES = ['https://www.googleapis.com/auth/drive']
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                credentials_path, 
                scopes=SCOPES
            )
            
            # Build the service
            service = build('drive', 'v3', credentials=credentials)
            print("Google Drive service initialized successfully")
            return service
            
        except Exception as e:
            print(f"Failed to initialize Google Drive service: {e}")
            return None
    
    def upload_image(self, file_content: bytes, filename: str, folder_type: str = "products") -> Dict:
        """
        Upload an image to Google Drive
        
        Args:
            file_content: Image file content as bytes
            filename: Name of the file
            folder_type: "products" or "profiles"
            
        Returns:
            Dict with upload result including file ID and public URL
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not initialized"}
        
        try:
            # Choose folder based on type
            folder_id = self.PRODUCTS_FOLDER_ID if folder_type == "products" else self.PROFILE_PICTURES_FOLDER_ID
            
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Create media upload
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=self._get_mime_type(filename),
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            # Get public URL (you might need to make the file public)
            file_id = file.get('id')
            public_url = self._get_public_url(file_id)
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "public_url": public_url,
                "web_view_link": file.get('webViewLink'),
                "web_content_link": file.get('webContentLink')
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Drive API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Upload failed: {e}"}
    
    def download_image(self, file_id: str) -> Dict:
        """
        Download an image from Google Drive
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Dict with file content and metadata
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not initialized"}
        
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            
            return {
                "success": True,
                "content": file_content.read(),
                "filename": file_metadata.get('name'),
                "mime_type": file_metadata.get('mimeType'),
                "size": file_metadata.get('size')
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Drive API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Download failed: {e}"}
    
    def delete_image(self, file_id: str) -> Dict:
        """
        Delete an image from Google Drive
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Dict with deletion result
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not initialized"}
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return {"success": True, "message": "File deleted successfully"}
            
        except HttpError as e:
            return {"success": False, "error": f"Google Drive API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Deletion failed: {e}"}
    
    def list_images(self, folder_type: str = "products") -> Dict:
        """
        List all images in a folder
        
        Args:
            folder_type: "products" or "profiles"
            
        Returns:
            Dict with list of files
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not initialized"}
        
        try:
            folder_id = self.PRODUCTS_FOLDER_ID if folder_type == "products" else self.PROFILE_PICTURES_FOLDER_ID
            
            # Query files in folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id,name,size,createdTime,webViewLink,webContentLink)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except HttpError as e:
            return {"success": False, "error": f"Google Drive API error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"List failed: {e}"}
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    def _get_public_url(self, file_id: str) -> str:
        """Generate public URL for a file"""
        return f"https://drive.google.com/uc?id={file_id}"
    
    def migrate_local_images(self, local_folder: str, folder_type: str = "products") -> Dict:
        """
        Migrate local images to Google Drive
        
        Args:
            local_folder: Path to local images folder
            folder_type: "products" or "profiles"
            
        Returns:
            Dict with migration results
        """
        if not os.path.exists(local_folder):
            return {"success": False, "error": "Local folder not found"}
        
        migrated_files = []
        failed_files = []
        
        for filename in os.listdir(local_folder):
            if self._is_image_file(filename):
                file_path = os.path.join(local_folder, filename)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    result = self.upload_image(file_content, filename, folder_type)
                    
                    if result["success"]:
                        migrated_files.append({
                            "filename": filename,
                            "file_id": result["file_id"],
                            "public_url": result["public_url"]
                        })
                    else:
                        failed_files.append({
                            "filename": filename,
                            "error": result["error"]
                        })
                        
                except Exception as e:
                    failed_files.append({
                        "filename": filename,
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "migrated": migrated_files,
            "failed": failed_files,
            "migrated_count": len(migrated_files),
            "failed_count": len(failed_files)
        }
    
    def _is_image_file(self, filename: str) -> bool:
        """Check if file is an image"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

# Global instance
google_drive_service = GoogleDriveService()
