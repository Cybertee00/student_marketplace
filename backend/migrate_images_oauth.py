#!/usr/bin/env python3
"""
OAuth2 Google Drive Image Migration Tool
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from oauth_google_drive_service import oauth_google_drive_service

class OAuthImageMigrationService:
    """Service for migrating images from local storage to Google Drive using OAuth2"""
    
    def __init__(self):
        self.products_folder = "products_images"
        self.profile_folder = "profile_pictures"
        self.migration_log = []
        
    def migrate_all_images(self) -> Dict:
        """Migrate all images from local storage to Google Drive"""
        print("🚀 Starting OAuth2 image migration to Google Drive...")
        
        # Check if Google Drive service is available
        if oauth_google_drive_service.service is None:
            print("❌ Google Drive service not available. Please run test_oauth_setup.py first.")
            return {"success": False, "error": "Google Drive service not available"}
        
        result = {
            "products": self._migrate_products(),
            "profiles": self._migrate_profiles(),
            "database_update": self._create_database_mapping(),
            "migration_log": self.migration_log
        }
        
        # Save migration report
        self._save_migration_report(result)
        
        return result
    
    def _migrate_products(self) -> Dict:
        """Migrate product images"""
        print("\n📦 Migrating product images...")
        
        if not os.path.exists(self.products_folder):
            print(f"⚠️  Products folder not found: {self.products_folder}")
            return {"success": True, "migrated": [], "failed": [], "migrated_count": 0, "failed_count": 0}
        
        migrated = []
        failed = []
        
        for filename in os.listdir(self.products_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_path = os.path.join(self.products_folder, filename)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    result = oauth_google_drive_service.upload_image(
                        file_content, filename, "products"
                    )
                    
                    if result["success"]:
                        migrated.append({
                            "filename": filename,
                            "file_id": result["file_id"],
                            "public_url": result["public_url"]
                        })
                        print(f"✅ Migrated: {filename}")
                    else:
                        failed.append({
                            "filename": filename,
                            "error": result["error"]
                        })
                        print(f"❌ Failed: {filename} - {result['error']}")
                        
                except Exception as e:
                    failed.append({
                        "filename": filename,
                        "error": str(e)
                    })
                    print(f"❌ Failed: {filename} - {str(e)}")
        
        self.migration_log.append({
            "type": "product_migration",
            "timestamp": datetime.now().isoformat(),
            "migrated": migrated,
            "failed": failed
        })
        
        print(f"✅ Migrated {len(migrated)} product images")
        if failed:
            print(f"⚠️  Failed to migrate {len(failed)} product images")
        
        return {
            "success": True,
            "migrated": migrated,
            "failed": failed,
            "migrated_count": len(migrated),
            "failed_count": len(failed)
        }
    
    def _migrate_profiles(self) -> Dict:
        """Migrate profile pictures"""
        print("\n👤 Migrating profile pictures...")
        
        if not os.path.exists(self.profile_folder):
            print(f"⚠️  Profile folder not found: {self.profile_folder}")
            return {"success": True, "migrated": [], "failed": [], "migrated_count": 0, "failed_count": 0}
        
        migrated = []
        failed = []
        
        for filename in os.listdir(self.profile_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_path = os.path.join(self.profile_folder, filename)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    
                    result = oauth_google_drive_service.upload_image(
                        file_content, filename, "profiles"
                    )
                    
                    if result["success"]:
                        migrated.append({
                            "filename": filename,
                            "file_id": result["file_id"],
                            "public_url": result["public_url"]
                        })
                        print(f"✅ Migrated: {filename}")
                    else:
                        failed.append({
                            "filename": filename,
                            "error": result["error"]
                        })
                        print(f"❌ Failed: {filename} - {result['error']}")
                        
                except Exception as e:
                    failed.append({
                        "filename": filename,
                        "error": str(e)
                    })
                    print(f"❌ Failed: {filename} - {str(e)}")
        
        self.migration_log.append({
            "type": "profile_migration",
            "timestamp": datetime.now().isoformat(),
            "migrated": migrated,
            "failed": failed
        })
        
        print(f"✅ Migrated {len(migrated)} profile pictures")
        if failed:
            print(f"⚠️  Failed to migrate {len(failed)} profile pictures")
        
        return {
            "success": True,
            "migrated": migrated,
            "failed": failed,
            "migrated_count": len(migrated),
            "failed_count": len(failed)
        }
    
    def _create_database_mapping(self) -> Dict:
        """Create database mapping for migrated images"""
        print("\n🗄️  Creating database mapping...")
        
        mapping = {}
        
        # Add product mappings
        for log_entry in self.migration_log:
            if log_entry["type"] == "product_migration":
                for item in log_entry["migrated"]:
                    mapping[item["filename"]] = {
                        "file_id": item["file_id"],
                        "public_url": item["public_url"],
                        "type": "product"
                    }
        
        # Add profile mappings
        for log_entry in self.migration_log:
            if log_entry["type"] == "profile_migration":
                for item in log_entry["migrated"]:
                    mapping[item["filename"]] = {
                        "file_id": item["file_id"],
                        "public_url": item["public_url"],
                        "type": "profile"
                    }
        
        # Save mapping file
        with open('oauth_image_migration_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print("📄 Created mapping file: oauth_image_migration_mapping.json")
        
        return {
            "success": True,
            "mapping_file": "oauth_image_migration_mapping.json",
            "message": "Database update mapping created"
        }
    
    def _save_migration_report(self, result: Dict):
        """Save migration report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"oauth_migration_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n📊 Migration report saved: {report_file}")

def main():
    """Main migration function"""
    print("🔄 OAuth2 Google Drive Image Migration Tool")
    print("=" * 50)
    
    migration_service = OAuthImageMigrationService()
    result = migration_service.migrate_all_images()
    
    print("\n📋 Migration Summary:")
    print("=" * 50)
    print(f"📦 Products: {result['products']['migrated_count']} migrated, {result['products']['failed_count']} failed")
    print(f"👤 Profiles: {result['profiles']['migrated_count']} migrated, {result['profiles']['failed_count']} failed")
    
    if result['products']['migrated_count'] > 0 or result['profiles']['migrated_count'] > 0:
        print("\n🎉 Migration completed successfully!")
        print("📄 Check oauth_image_migration_mapping.json for database updates")
    else:
        print("\n⚠️  No images were migrated. Check the error messages above.")

if __name__ == "__main__":
    main()
