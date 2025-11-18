#!/usr/bin/env python3
"""
Update Google Drive folder IDs for your personal account
"""

import os
import re

def update_folder_ids():
    print("📁 Updating Google Drive Folder IDs")
    print("=" * 50)
    
    print("Please provide your Google Drive folder IDs:")
    print("(You can find these in the folder URLs)")
    print()
    
    # Get folder IDs from user
    products_id = input("Enter Products folder ID: ").strip()
    profiles_id = input("Enter Profiles folder ID: ").strip()
    
    if not products_id or not profiles_id:
        print("❌ Please provide both folder IDs")
        return False
    
    # Validate folder ID format (Google Drive IDs are usually 28 characters)
    if len(products_id) < 20 or len(profiles_id) < 20:
        print("⚠️  Warning: Folder IDs seem too short. Please double-check.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Update the google_drive_service.py file
    service_file = "google_drive_service.py"
    
    if not os.path.exists(service_file):
        print(f"❌ {service_file} not found")
        return False
    
    try:
        # Read the current file
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Replace the folder IDs
        content = re.sub(
            r'PRODUCTS_FOLDER_ID = "[^"]*"',
            f'PRODUCTS_FOLDER_ID = "{products_id}"',
            content
        )
        
        content = re.sub(
            r'PROFILE_PICTURES_FOLDER_ID = "[^"]*"',
            f'PROFILE_PICTURES_FOLDER_ID = "{profiles_id}"',
            content
        )
        
        # Write back to file
        with open(service_file, 'w') as f:
            f.write(content)
        
        print("✅ Folder IDs updated successfully!")
        print(f"   Products: {products_id}")
        print(f"   Profiles: {profiles_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating file: {e}")
        return False

def show_folder_id_example():
    """Show example of how to find folder IDs"""
    print("\n📖 How to find Folder IDs:")
    print("=" * 50)
    print("1. Go to your Google Drive folder")
    print("2. Look at the URL in your browser:")
    print("   https://drive.google.com/drive/folders/1ABC123DEF456GHI789")
    print("3. Copy the part after '/folders/': 1ABC123DEF456GHI789")
    print("4. That's your folder ID!")

if __name__ == "__main__":
    print("🚀 Google Drive Folder ID Updater")
    print("=" * 50)
    
    show_folder_id_example()
    
    if update_folder_ids():
        print("\n🎉 Setup complete! Next steps:")
        print("1. Create Google Cloud Project")
        print("2. Enable Google Drive API")
        print("3. Create service account")
        print("4. Share folders with service account")
    else:
        print("\n❌ Setup failed. Please try again.")
