#!/usr/bin/env python3
"""
OAuth2 Google Drive Setup Helper
"""

import os
import webbrowser
from urllib.parse import urlencode

def setup_oauth():
    """Help user set up OAuth2 for Google Drive"""
    print("🔧 OAuth2 Google Drive Setup Helper")
    print("=" * 50)
    
    # Check if credentials file exists
    if os.path.exists('oauth-credentials.json'):
        print("✅ OAuth credentials file already exists!")
        print("🚀 You can now run: python test_oauth_setup.py")
        return True
    
    print("❌ OAuth credentials file not found: oauth-credentials.json")
    print("\n📋 Follow these steps to get OAuth2 credentials:")
    print("=" * 50)
    
    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. Select your project: student-marketplace-personal")
    
    print("\n3. Go to APIs & Services → Credentials")
    
    print("\n4. Click 'Create Credentials' → 'OAuth client ID'")
    
    print("\n5. Choose 'Desktop application'")
    
    print("\n6. Enter name: Student Marketplace Desktop")
    
    print("\n7. Click 'Create'")
    
    print("\n8. Download the JSON file")
    
    print("\n9. Rename it to 'oauth-credentials.json'")
    
    print("\n10. Place it in this directory (backend/)")
    
    print("\n11. Run: python test_oauth_setup.py")
    
    # Ask if user wants to open Google Cloud Console
    response = input("\n🌐 Open Google Cloud Console now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        webbrowser.open('https://console.cloud.google.com/apis/credentials')
        print("✅ Google Cloud Console opened in your browser!")
    
    return False

if __name__ == "__main__":
    setup_oauth()
