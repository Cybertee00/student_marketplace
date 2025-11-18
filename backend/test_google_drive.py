#!/usr/bin/env python3
"""
Test Google Drive Integration
Simple test script to verify Google Drive setup
"""

import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_google_drive_setup():
    """Test Google Drive service setup"""
    print("🧪 Testing Google Drive Integration...")
    print("=" * 50)
    
    # Check if credentials file exists
    credentials_path = "google-credentials.json"
    if not os.path.exists(credentials_path):
        print("❌ Google credentials file not found!")
        print(f"Expected file: {credentials_path}")
        print("\n📋 To set up Google Cloud Project:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create a service account")
        print("5. Download the JSON credentials file")
        print("6. Rename it to 'google-credentials.json'")
        print("7. Place it in the backend directory")
        print("\n📖 See GOOGLE_DRIVE_SETUP_GUIDE.md for detailed instructions")
        return False
    
    print(f"✅ Credentials file found: {credentials_path}")
    
    try:
        from google_drive_service import google_drive_service
        
        if google_drive_service.service:
            print("✅ Google Drive service initialized successfully!")
            
            # Test listing folders
            print("\n📁 Testing folder access...")
            
            # Test products folder
            products_result = google_drive_service.list_images("products")
            if products_result["success"]:
                print(f"✅ Products folder accessible: {products_result['count']} files")
            else:
                print(f"❌ Products folder error: {products_result['error']}")
            
            # Test profiles folder
            profiles_result = google_drive_service.list_images("profiles")
            if profiles_result["success"]:
                print(f"✅ Profiles folder accessible: {profiles_result['count']} files")
            else:
                print(f"❌ Profiles folder error: {profiles_result['error']}")
            
            return True
        else:
            print("❌ Google Drive service failed to initialize")
            print("Check your credentials file and folder permissions")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Drive: {e}")
        return False

def test_migration_readiness():
    """Test if we're ready to run migration"""
    print("\n🔄 Testing Migration Readiness...")
    print("=" * 50)
    
    # Check if local image folders exist
    products_folder = "products_images"
    profiles_folder = "profile_pictures"
    
    products_exist = os.path.exists(products_folder)
    profiles_exist = os.path.exists(profiles_folder)
    
    print(f"📦 Products folder exists: {'✅' if products_exist else '❌'}")
    if products_exist:
        files = [f for f in os.listdir(products_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        print(f"   Found {len(files)} image files")
    
    print(f"👤 Profiles folder exists: {'✅' if profiles_exist else '❌'}")
    if profiles_exist:
        files = [f for f in os.listdir(profiles_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
        print(f"   Found {len(files)} image files")
    
    return products_exist or profiles_exist

def main():
    """Main test function"""
    print("🚀 Google Drive Integration Test")
    print("=" * 50)
    
    # Test Google Drive setup
    drive_ready = test_google_drive_setup()
    
    # Test migration readiness
    migration_ready = test_migration_readiness()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Google Drive Setup: {'✅ Ready' if drive_ready else '❌ Not Ready'}")
    print(f"Migration Ready: {'✅ Ready' if migration_ready else '❌ No Images'}")
    
    if drive_ready and migration_ready:
        print("\n🎉 All tests passed! You can now run the migration:")
        print("   python migrate_images_to_drive.py")
    elif drive_ready:
        print("\n✅ Google Drive is ready! You can start uploading new images.")
        print("   No existing images found to migrate.")
    else:
        print("\n⚠️  Please complete the Google Cloud setup first.")
        print("   See GOOGLE_DRIVE_SETUP_GUIDE.md for instructions.")

if __name__ == "__main__":
    main()
