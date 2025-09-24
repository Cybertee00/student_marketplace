"""
Add created_via field to products table to distinguish between Flutter app and Admin web uploads
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_created_via_field'
down_revision = None  # Update this to the latest revision
branch_labels = None
depends_on = None

def upgrade():
    # Add created_via field to products table
    op.add_column('products', sa.Column('created_via', sa.String(20), nullable=True, default='flutter'))
    
    # Update existing products to have created_via = 'admin' if they were created by admin users
    # This is a best guess - we'll assume existing products were created via admin web
    op.execute("""
        UPDATE products 
        SET created_via = 'admin' 
        WHERE created_via IS NULL
    """)

def downgrade():
    # Remove created_via field
    op.drop_column('products', 'created_via')
