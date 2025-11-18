#!/usr/bin/env python3
"""
Simple test to check if OAuth2 setup is working
"""

import os
import sys

def test_setup():
    """Test if OAuth2 setup files exist and are accessible"""
    print("🔍 Testing OAuth2 Setup Files...")
    print("=" * 40)
    
    # Check if OAuth credentials file exists
    if os.path.exists('oauth-credentials.json'):
        print("✅ OAuth credentials file found")
    else:
        print("❌ OAuth credentials file not found")
        return False
    
    # Check if OAuth service file exists
    if os.path.exists('oauth_google_drive_service.py'):
        print("✅ OAuth service file found")
    else:
        print("❌ OAuth service file not found")
        return False
    
    # Check if migration script exists
    if os.path.exists('migrate_images_oauth.py'):
        print("✅ OAuth migration script found")
    else:
        print("❌ OAuth migration script not found")
        return False
    
    # Check if local image folders exist
    if os.path.exists('products_images'):
        product_count = len([f for f in os.listdir('products_images') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))])
        print(f"✅ Products folder found with {product_count} images")
    else:
        print("❌ Products folder not found")
        return False
    
    if os.path.exists('profile_pictures'):
        profile_count = len([f for f in os.listdir('profile_pictures') if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))])
        print(f"✅ Profile pictures folder found with {profile_count} images")
    else:
        print("❌ Profile pictures folder not found")
        return False
    
    print("\n🎉 All setup files are ready!")
    print("📋 Next step: Run the migration script")
    print("   python migrate_images_oauth.py")
    
    return True

if __name__ == "__main__":
    test_setup()
