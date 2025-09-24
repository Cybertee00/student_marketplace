"""add_email_verification_fields

Revision ID: afa3d6ece52d
Revises: 024bbd27df07
Create Date: 2025-09-03 16:17:19.972892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afa3d6ece52d'
down_revision = '024bbd27df07'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email verification fields
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires_at', sa.DateTime(), nullable=True))
    
    # Add phone verification fields
    op.add_column('users', sa.Column('is_phone_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('phone_verification_code', sa.String(10), nullable=True))
    op.add_column('users', sa.Column('phone_verification_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove email verification fields
    op.drop_column('users', 'is_email_verified')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verification_expires_at')
    
    # Remove phone verification fields
    op.drop_column('users', 'is_phone_verified')
    op.drop_column('users', 'phone_verification_code')
    op.drop_column('users', 'phone_verification_expires_at')
