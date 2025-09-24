"""
Migration script to remove product_category field from products table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import get_database_url

def migrate():
    """Remove product_category column from products table"""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        try:
            # Drop the index first
            conn.execute(text("""
                DROP INDEX IF EXISTS idx_products_product_category
            """))
            print("✅ Dropped index on product_category column")
            
            # Remove product_category column
            conn.execute(text("""
                ALTER TABLE products 
                DROP COLUMN IF EXISTS product_category
            """))
            print("✅ Removed product_category column from products table")
            
            # Commit the changes
            conn.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
