#!/usr/bin/env python3
"""
Google Cloud Setup Helper
Interactive script to help set up Google Cloud Project for Google Drive integration
"""

import os
import webbrowser
import json
from datetime import datetime

def print_header():
    """Print setup header"""
    print("🚀 Google Cloud Project Setup Helper")
    print("=" * 60)
    print("This script will guide you through setting up Google Drive integration")
    print("for your Student Marketplace project.")
    print()

def check_existing_credentials():
    """Check if credentials already exist"""
    credentials_file = "google-credentials.json"
    if os.path.exists(credentials_file):
        print(f"✅ Found existing credentials: {credentials_file}")
        return True
    return False

def open_google_cloud_console():
    """Open Google Cloud Console"""
    print("🌐 Opening Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    print("✅ Google Cloud Console opened in your browser")

def print_setup_steps():
    """Print detailed setup steps"""
    print("\n📋 Step-by-Step Setup Instructions:")
    print("=" * 60)
    
    steps = [
        {
            "step": 1,
            "title": "Create/Select Project",
            "description": "In Google Cloud Console, create a new project or select existing one",
            "details": [
                "Click 'Select a project' → 'New Project'",
                "Name: 'student-marketplace-drive'",
                "Click 'Create'"
            ]
        },
        {
            "step": 2,
            "title": "Enable Google Drive API",
            "description": "Enable the Google Drive API for your project",
            "details": [
                "Go to 'APIs & Services' → 'Library'",
                "Search for 'Google Drive API'",
                "Click on it and press 'Enable'"
            ]
        },
        {
            "step": 3,
            "title": "Create Service Account",
            "description": "Create a service account for API access",
            "details": [
                "Go to 'APIs & Services' → 'Credentials'",
                "Click 'Create Credentials' → 'Service Account'",
                "Name: 'student-marketplace-drive-service'",
                "Description: 'Service account for student marketplace image storage'",
                "Click 'Create and Continue'",
                "Skip role assignment (click 'Continue')",
                "Click 'Done'"
            ]
        },
        {
            "step": 4,
            "title": "Create Service Account Key",
            "description": "Download the JSON credentials file",
            "details": [
                "In 'Credentials', find your service account",
                "Click on the service account email",
                "Go to 'Keys' tab",
                "Click 'Add Key' → 'Create new key'",
                "Choose 'JSON' format",
                "Click 'Create'",
                "The JSON file will download automatically"
            ]
        },
        {
            "step": 5,
            "title": "Configure Credentials",
            "description": "Place the credentials file in the correct location",
            "details": [
                "Rename downloaded file to 'google-credentials.json'",
                "Place it in the backend directory",
                "Ensure it's in the same folder as this script"
            ]
        },
        {
            "step": 6,
            "title": "Share Google Drive Folders",
            "description": "Share your Google Drive folders with the service account",
            "details": [
                "Open Products folder: https://drive.google.com/drive/folders/1afiYrNk7pndgxfvvYfA5I1iAMvdY8oUv",
                "Click 'Share' button",
                "Add service account email (from JSON file)",
                "Set permission to 'Editor'",
                "Repeat for Profile Pictures folder: https://drive.google.com/drive/folders/1JDkJpB1TTZzfNOhsgRIPrM9Fy_9QQ0VV"
            ]
        }
    ]
    
    for step_info in steps:
        print(f"\n🔹 Step {step_info['step']}: {step_info['title']}")
        print(f"   {step_info['description']}")
        for detail in step_info['details']:
            print(f"   • {detail}")

def validate_credentials_file():
    """Validate the credentials file"""
    credentials_file = "google-credentials.json"
    
    if not os.path.exists(credentials_file):
        print(f"❌ Credentials file not found: {credentials_file}")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        
        for field in required_fields:
            if field not in credentials:
                print(f"❌ Missing field in credentials: {field}")
                return False
        
        print("✅ Credentials file is valid!")
        print(f"   Project ID: {credentials['project_id']}")
        print(f"   Service Account: {credentials['client_email']}")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return False

def test_google_drive_access():
    """Test Google Drive access"""
    print("\n🧪 Testing Google Drive Access...")
    
    try:
        from google_drive_service import google_drive_service
        
        if not google_drive_service.service:
            print("❌ Google Drive service not initialized")
            return False
        
        # Test listing folders
        products_result = google_drive_service.list_images("products")
        profiles_result = google_drive_service.list_images("profiles")
        
        if products_result["success"] and profiles_result["success"]:
            print("✅ Google Drive access successful!")
            print(f"   Products folder: {products_result['count']} files")
            print(f"   Profiles folder: {profiles_result['count']} files")
            return True
        else:
            print("❌ Google Drive access failed")
            if not products_result["success"]:
                print(f"   Products folder error: {products_result['error']}")
            if not profiles_result["success"]:
                print(f"   Profiles folder error: {profiles_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Drive: {e}")
        return False

def create_setup_summary():
    """Create a setup summary file"""
    summary = {
        "setup_date": datetime.now().isoformat(),
        "status": "setup_completed",
        "folders": {
            "products": "1afiYrNk7pndgxfvvYfA5I1iAMvdY8oUv",
            "profiles": "1JDkJpB1TTZzfNOhsgRIPrM9Fy_9QQ0VV"
        },
        "next_steps": [
            "Run migration script: python migrate_images_to_drive.py",
            "Test image uploads in your app",
            "Update database with migrated image references"
        ]
    }
    
    with open("google_drive_setup_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("📄 Setup summary saved to: google_drive_setup_summary.json")

def main():
    """Main setup function"""
    print_header()
    
    # Check if already set up
    if check_existing_credentials():
        print("\n🔍 Validating existing setup...")
        if validate_credentials_file():
            if test_google_drive_access():
                print("\n🎉 Google Drive integration is already set up and working!")
                create_setup_summary()
                return
    
    # Show setup instructions
    print("📖 You need to set up Google Cloud Project first.")
    print("\nWould you like to:")
    print("1. Open Google Cloud Console (recommended)")
    print("2. Just show instructions")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            open_google_cloud_console()
            print_setup_steps()
        elif choice == "2":
            print_setup_steps()
        elif choice == "3":
            print("👋 Goodbye! Run this script again when you're ready to set up.")
            return
        else:
            print("❌ Invalid choice. Please run the script again.")
            return
        
        # Wait for user to complete setup
        input("\n⏸️  Press Enter when you've completed the setup steps...")
        
        # Validate setup
        print("\n🔍 Validating your setup...")
        if validate_credentials_file():
            if test_google_drive_access():
                print("\n🎉 Setup completed successfully!")
                create_setup_summary()
                print("\n🚀 Next steps:")
                print("1. Run migration: python migrate_images_to_drive.py")
                print("2. Test your app with Google Drive images")
            else:
                print("\n❌ Google Drive access failed. Please check:")
                print("• Service account permissions")
                print("• Folder sharing settings")
                print("• Google Drive API is enabled")
        else:
            print("\n❌ Credentials validation failed. Please check your setup.")
    
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled. Run this script again when ready.")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")

if __name__ == "__main__":
    main()
