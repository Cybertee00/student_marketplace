"""
Migration script to add faculty and product_category fields to products table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config import get_database_url

def migrate():
    """Add faculty and product_category columns to products table"""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        try:
            # Add faculty column
            conn.execute(text("""
                ALTER TABLE products 
                ADD COLUMN faculty VARCHAR(100)
            """))
            print("✅ Added faculty column to products table")
            
            # Add product_category column
            conn.execute(text("""
                ALTER TABLE products 
                ADD COLUMN product_category VARCHAR(100)
            """))
            print("✅ Added product_category column to products table")
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_faculty 
                ON products(faculty)
            """))
            print("✅ Created index on faculty column")
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_products_product_category 
                ON products(product_category)
            """))
            print("✅ Created index on product_category column")
            
            # Commit the changes
            conn.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
