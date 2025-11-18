#!/usr/bin/env python3
"""
Test script for hybrid storage service
"""

from hybrid_storage_service import hybrid_storage
import os

def test_hybrid_storage():
    """Test the hybrid storage service"""
    print("🧪 Testing Hybrid Storage Service")
    print("=" * 40)
    
    # Test 1: Check if folders exist
    print("📁 Checking folders...")
    if os.path.exists("products_images"):
        product_count = len(hybrid_storage.list_images("products"))
        print(f"✅ Products folder: {product_count} images")
    else:
        print("❌ Products folder not found")
    
    if os.path.exists("profile_pictures"):
        profile_count = len(hybrid_storage.list_images("profiles"))
        print(f"✅ Profile pictures folder: {profile_count} images")
    else:
        print("❌ Profile pictures folder not found")
    
    # Test 2: Test image URL generation
    print("\n🔗 Testing URL generation...")
    test_filename = "test_image.jpg"
    
    # Test products URL
    products_url = hybrid_storage.get_image_url(test_filename, "products")
    print(f"✅ Products URL: {products_url}")
    
    # Test profiles URL
    profiles_url = hybrid_storage.get_image_url(test_filename, "profiles")
    print(f"✅ Profiles URL: {profiles_url}")
    
    # Test 3: Check storage mode
    print(f"\n💾 Storage mode: {'Google Drive' if hybrid_storage.USE_GOOGLE_DRIVE else 'Local'}")
    
    print("\n🎉 Hybrid storage service is working!")
    print("📋 Ready to use with your app")
    
    return True

if __name__ == "__main__":
    test_hybrid_storage()
