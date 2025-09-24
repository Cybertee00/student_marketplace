"""update_revenue_table_for_cash_on_delivery

Revision ID: fe61029a3361
Revises: 002
Create Date: 2025-08-28 16:38:19.136200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe61029a3361'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to revenue table
    op.add_column('revenue', sa.Column('commission', sa.Float(), nullable=True, default=0.0))
    op.add_column('revenue', sa.Column('platform_fee', sa.Float(), nullable=True, default=0.0))
    op.add_column('revenue', sa.Column('seller_revenue', sa.Float(), nullable=True, default=0.0))
    op.add_column('revenue', sa.Column('payment_method', sa.String(50), nullable=True))
    
    # Update existing records to have default values
    op.execute("UPDATE revenue SET commission = 0.0 WHERE commission IS NULL")
    op.execute("UPDATE revenue SET platform_fee = 0.0 WHERE platform_fee IS NULL")
    op.execute("UPDATE revenue SET seller_revenue = amount WHERE seller_revenue IS NULL")
    op.execute("UPDATE revenue SET payment_method = 'unknown' WHERE payment_method IS NULL")
    
    # Make payment_method not nullable after setting default values
    op.alter_column('revenue', 'payment_method', nullable=False)


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('revenue', 'payment_method')
    op.drop_column('revenue', 'seller_revenue')
    op.drop_column('revenue', 'platform_fee')
    op.drop_column('revenue', 'commission')
