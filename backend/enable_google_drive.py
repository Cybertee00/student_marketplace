#!/usr/bin/env python3
"""
Script to enable Google Drive integration when OAuth2 is working
"""

from hybrid_storage_service import hybrid_storage

def enable_google_drive():
    """Enable Google Drive integration"""
    print("🔧 Enabling Google Drive Integration...")
    print("=" * 40)
    
    # Enable Google Drive
    hybrid_storage.enable_google_drive()
    
    print("✅ Google Drive integration enabled!")
    print("📋 New uploads will be saved to Google Drive")
    print("🔗 Image URLs will point to Google Drive")
    
    return True

def disable_google_drive():
    """Disable Google Drive integration"""
    print("🔧 Disabling Google Drive Integration...")
    print("=" * 40)
    
    # Disable Google Drive
    hybrid_storage.disable_google_drive()
    
    print("✅ Local storage mode enabled!")
    print("📋 New uploads will be saved locally")
    print("🔗 Image URLs will point to local files")
    
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "disable":
        disable_google_drive()
    else:
        enable_google_drive()
