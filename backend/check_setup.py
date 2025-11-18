#!/usr/bin/env python3
"""
Quick setup checker
"""

import os
import json

def check_setup():
    print("🔍 Checking your Google Cloud setup...")
    print("=" * 50)
    
    # Check if credentials file exists
    if not os.path.exists("google-credentials.json"):
        print("❌ google-credentials.json not found")
        print("   Please download and place the JSON file in this directory")
        return False
    
    # Check if file is valid JSON
    try:
        with open("google-credentials.json", 'r') as f:
            creds = json.load(f)
        
        required_fields = ['type', 'project_id', 'client_email', 'private_key']
        for field in required_fields:
            if field not in creds:
                print(f"❌ Missing field: {field}")
                return False
        
        print("✅ Credentials file is valid!")
        print(f"   Project: {creds['project_id']}")
        print(f"   Service Account: {creds['client_email']}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if check_setup():
        print("\n🎉 Setup looks good! Next steps:")
        print("1. Share your Google Drive folders with the service account")
        print("2. Run: python test_google_drive.py")
    else:
        print("\n⚠️  Please complete the setup first")
