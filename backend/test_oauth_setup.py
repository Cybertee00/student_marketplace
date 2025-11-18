#!/usr/bin/env python3
"""
Test script for OAuth2 Google Drive setup
"""

import os
from oauth_google_drive_service import oauth_google_drive_service

def test_oauth_setup():
    """Test OAuth2 Google Drive setup"""
    print("🔍 Testing OAuth2 Google Drive Setup...")
    print("=" * 50)
    
    # Check if credentials file exists
    if not os.path.exists('oauth-credentials.json'):
        print("❌ OAuth credentials file not found: oauth-credentials.json")
        print("📋 Please follow the OAUTH_SETUP_GUIDE.md to download credentials")
        return False
    
    print("✅ OAuth credentials file found")
    
    # Test Google Drive service initialization
    if oauth_google_drive_service.service is None:
        print("❌ Google Drive service failed to initialize")
        print("🔧 This usually means OAuth2 authentication failed")
        return False
    
    print("✅ Google Drive service initialized successfully")
    
    # Test folder access
    print("\n📁 Testing folder access...")
    
    try:
        # Test products folder
        products_files = oauth_google_drive_service.list_files_in_folder(
            oauth_google_drive_service.PRODUCTS_FOLDER_ID
        )
        print(f"✅ Products folder accessible: {len(products_files)} files")
        
        # Test profiles folder
        profiles_files = oauth_google_drive_service.list_files_in_folder(
            oauth_google_drive_service.PROFILE_PICTURES_FOLDER_ID
        )
        print(f"✅ Profiles folder accessible: {len(profiles_files)} files")
        
    except Exception as e:
        print(f"❌ Error accessing folders: {e}")
        return False
    
    print("\n🎉 OAuth2 setup successful!")
    print("✅ You can now run: python migrate_images_oauth.py")
    return True

if __name__ == "__main__":
    test_oauth_setup()
