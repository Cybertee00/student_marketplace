import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from typing import Optional, List, Dict

class OAuthGoogleDriveService:
    """Service for managing images in Google Drive using OAuth2"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    CREDENTIALS_FILE = 'oauth-credentials.json'
    TOKEN_FILE = 'token.json'
    
    def __init__(self):
        # Google Drive folder IDs
        self.PRODUCTS_FOLDER_ID = "156ZsoOjj9nUICNjGdS8_kAnzQc1569JC"
        self.PROFILE_PICTURES_FOLDER_ID = "1jknOL8yP2fDxLi9r_6mz8OK4fy54FdUM"
        
        # Initialize Google Drive service
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Drive service with OAuth2 authentication"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    print(f"❌ OAuth credentials file not found: {self.CREDENTIALS_FILE}")
                    print("Please download OAuth credentials from Google Cloud Console")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    def upload_image(self, file_content: bytes, filename: str, folder_type: str) -> dict:
        """
        Uploads an image to the specified Google Drive folder.
        Args:
            file_content: The content of the image file as bytes.
            filename: The desired filename for the image in Google Drive.
            folder_type: "products" or "profiles" to determine the target folder.
        Returns:
            A dictionary with success status, file ID, public URL, and error message if any.
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not authenticated."}

        folder_id = None
        if folder_type == "products":
            folder_id = self.PRODUCTS_FOLDER_ID
        elif folder_type == "profiles":
            folder_id = self.PROFILE_PICTURES_FOLDER_ID
        else:
            return {"success": False, "error": "Invalid folder type specified."}

        if not folder_id:
            return {"success": False, "error": f"Google Drive folder ID for {folder_type} is not configured."}

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='image/*', resumable=True)

        try:
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')

            # Make the file publicly accessible
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()

            # Construct a direct download link (uc?id=FILE_ID)
            public_url = f"https://drive.google.com/uc?id={file_id}"

            return {"success": True, "file_id": file_id, "public_url": public_url}
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"success": False, "error": str(error)}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"success": False, "error": str(e)}

    def download_image(self, file_id: str) -> Optional[bytes]:
        """
        Downloads an image from Google Drive.
        Args:
            file_id: The ID of the file to download.
        Returns:
            The content of the image file as bytes, or None if an error occurs.
        """
        if not self.service:
            return None
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
            return file_content.getvalue()
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def delete_image(self, file_id: str) -> dict:
        """
        Deletes an image from Google Drive.
        Args:
            file_id: The ID of the file to delete.
        Returns:
            A dictionary with success status and error message if any.
        """
        if not self.service:
            return {"success": False, "error": "Google Drive service not authenticated."}
        
        try:
            self.service.files().delete(fileId=file_id).execute()
            return {"success": True}
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"success": False, "error": str(error)}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"success": False, "error": str(e)}

    def list_files_in_folder(self, folder_id: str) -> List[dict]:
        """
        Lists files in a specified Google Drive folder.
        Args:
            folder_id: The ID of the folder to list files from.
        Returns:
            A list of dictionaries, each representing a file with 'id' and 'name'.
        """
        if not self.service:
            return []
        
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="files(id, name)"
            ).execute()
            items = results.get('files', [])
            return items
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

# Create global instance
oauth_google_drive_service = OAuthGoogleDriveService()
