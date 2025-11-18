#!/usr/bin/env python3
"""
Image Migration Script
Migrates existing local images to Google Drive and updates database references
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_drive_service import google_drive_service
from models import Product, User
from database import get_db

class ImageMigrationService:
    """Service for migrating images from local storage to Google Drive"""
    
    def __init__(self):
        self.products_folder = "products_images"
        self.profile_folder = "profile_pictures"
        self.migration_log = []
        
    def migrate_all_images(self) -> Dict:
        """Migrate all images from local storage to Google Drive"""
        print("🚀 Starting image migration to Google Drive...")
        
        results = {
            "products": self.migrate_product_images(),
            "profiles": self.migrate_profile_images(),
            "database_update": self.update_database_references(),
            "migration_log": self.migration_log
        }
        
        print("✅ Migration completed!")
        return results
    
    def migrate_product_images(self) -> Dict:
        """Migrate product images to Google Drive"""
        print("📦 Migrating product images...")
        
        if not os.path.exists(self.products_folder):
            print(f"⚠️  Products folder not found: {self.products_folder}")
            return {"success": False, "error": "Products folder not found"}
        
        result = google_drive_service.migrate_local_images(self.products_folder, "products")
        
        if result["success"]:
            print(f"✅ Migrated {result['migrated_count']} product images")
            if result["failed_count"] > 0:
                print(f"⚠️  Failed to migrate {result['failed_count']} images")
            
            self.migration_log.extend([
                {
                    "type": "product_migration",
                    "timestamp": datetime.now().isoformat(),
                    "migrated": result["migrated"],
                    "failed": result["failed"]
                }
            ])
        
        return result
    
    def migrate_profile_images(self) -> Dict:
        """Migrate profile pictures to Google Drive"""
        print("👤 Migrating profile pictures...")
        
        if not os.path.exists(self.profile_folder):
            print(f"⚠️  Profile folder not found: {self.profile_folder}")
            return {"success": False, "error": "Profile folder not found"}
        
        result = google_drive_service.migrate_local_images(self.profile_folder, "profiles")
        
        if result["success"]:
            print(f"✅ Migrated {result['migrated_count']} profile pictures")
            if result["failed_count"] > 0:
                print(f"⚠️  Failed to migrate {result['failed_count']} images")
            
            self.migration_log.extend([
                {
                    "type": "profile_migration",
                    "timestamp": datetime.now().isoformat(),
                    "migrated": result["migrated"],
                    "failed": result["failed"]
                }
            ])
        
        return result
    
    def update_database_references(self) -> Dict:
        """Update database to reference Google Drive file IDs instead of local filenames"""
        print("🗄️  Updating database references...")
        
        try:
            # This would need to be implemented based on your database setup
            # For now, we'll create a mapping file that you can use to update manually
            
            mapping_file = "image_migration_mapping.json"
            mapping = {
                "products": {},
                "profiles": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Read migration log to create mapping
            for log_entry in self.migration_log:
                if log_entry["type"] == "product_migration":
                    for item in log_entry["migrated"]:
                        mapping["products"][item["filename"]] = {
                            "file_id": item["file_id"],
                            "public_url": item["public_url"]
                        }
                elif log_entry["type"] == "profile_migration":
                    for item in log_entry["migrated"]:
                        mapping["profiles"][item["filename"]] = {
                            "file_id": item["file_id"],
                            "public_url": item["public_url"]
                        }
            
            # Save mapping file
            with open(mapping_file, 'w') as f:
                json.dump(mapping, f, indent=2)
            
            print(f"📄 Created mapping file: {mapping_file}")
            print("⚠️  You'll need to manually update your database using this mapping")
            
            return {
                "success": True,
                "mapping_file": mapping_file,
                "message": "Database update mapping created"
            }
            
        except Exception as e:
            print(f"❌ Failed to create database mapping: {e}")
            return {"success": False, "error": str(e)}
    
    def create_database_update_script(self, mapping_file: str) -> str:
        """Create SQL script to update database references"""
        try:
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
            
            script_content = "-- Image Migration Database Update Script\n"
            script_content += f"-- Generated on {datetime.now().isoformat()}\n\n"
            
            # Update products table
            script_content += "-- Update products table\n"
            for filename, drive_info in mapping["products"].items():
                script_content += f"""
-- Update product images for file: {filename}
UPDATE products 
SET images = ARRAY_REPLACE(images, '{filename}', '{drive_info['file_id']}')
WHERE '{filename}' = ANY(images);
"""
            
            # Update users table for profile pictures
            script_content += "\n-- Update users table (profile pictures)\n"
            for filename, drive_info in mapping["profiles"].items():
                script_content += f"""
-- Update profile picture for file: {filename}
UPDATE users 
SET profile_img = '{drive_info['file_id']}'
WHERE profile_img = '{filename}';
"""
            
            script_file = "update_database_images.sql"
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            print(f"📄 Created SQL update script: {script_file}")
            return script_file
            
        except Exception as e:
            print(f"❌ Failed to create SQL script: {e}")
            return ""

def main():
    """Main migration function"""
    print("🔄 Google Drive Image Migration Tool")
    print("=" * 50)
    
    # Check if Google Drive service is available
    if not google_drive_service.service:
        print("❌ Google Drive service not initialized!")
        print("Please ensure you have:")
        print("1. Created a Google Cloud Project")
        print("2. Enabled Google Drive API")
        print("3. Created a service account")
        print("4. Downloaded the JSON credentials file")
        print("5. Set GOOGLE_CREDENTIALS_PATH environment variable")
        return
    
    # Initialize migration service
    migration_service = ImageMigrationService()
    
    # Run migration
    results = migration_service.migrate_all_images()
    
    # Create database update script if mapping was created
    if results["database_update"]["success"]:
        mapping_file = results["database_update"]["mapping_file"]
        sql_script = migration_service.create_database_update_script(mapping_file)
        
        if sql_script:
            print(f"\n📋 Next steps:")
            print(f"1. Review the mapping file: {mapping_file}")
            print(f"2. Run the SQL script: {sql_script}")
            print(f"3. Test your application with Google Drive images")
            print(f"4. Remove local image folders after confirming everything works")
    
    # Save migration report
    report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Migration report saved: {report_file}")

if __name__ == "__main__":
    main()
