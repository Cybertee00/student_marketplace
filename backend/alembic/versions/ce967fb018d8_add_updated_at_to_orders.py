"""add_updated_at_to_orders

Revision ID: ce967fb018d8
Revises: fe61029a3361
Create Date: 2025-08-28 17:06:41.985330

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce967fb018d8'
down_revision = 'fe61029a3361'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to orders table
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set existing records to have updated_at = created_at
    op.execute("UPDATE orders SET updated_at = created_at WHERE updated_at IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('orders', 'updated_at', nullable=False)


def downgrade() -> None:
    # Remove the updated_at column
    op.drop_column('orders', 'updated_at')
