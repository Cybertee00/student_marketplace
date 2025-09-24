"""enhance_messages_table_for_admin_messaging

Revision ID: 024bbd27df07
Revises: ce967fb018d8
Create Date: 2025-09-03 15:22:53.080937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '024bbd27df07'
down_revision = 'ce967fb018d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to messages table
    op.add_column('messages', sa.Column('message_type', sa.String(50), nullable=True, server_default='text'))
    op.add_column('messages', sa.Column('conversation_id', sa.String(100), nullable=True))
    op.add_column('messages', sa.Column('is_read', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('messages', sa.Column('is_important', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('messages', sa.Column('parent_message_id', sa.Integer(), nullable=True))
    op.add_column('messages', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Add foreign key constraint for parent_message_id
    op.create_foreign_key(
        'fk_messages_parent_message_id',
        'messages', 'messages',
        ['parent_message_id'], ['id']
    )
    
    # Create indexes for better performance
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_message_type', 'messages', ['message_type'])
    op.create_index('ix_messages_is_read', 'messages', ['is_read'])
    op.create_index('ix_messages_is_important', 'messages', ['is_important'])
    op.create_index('ix_messages_updated_at', 'messages', ['updated_at'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_messages_updated_at', 'messages')
    op.drop_index('ix_messages_is_important', 'messages')
    op.drop_index('ix_messages_is_read', 'messages')
    op.drop_index('ix_messages_message_type', 'messages')
    op.drop_index('ix_messages_conversation_id', 'messages')
    
    # Remove foreign key constraint
    op.drop_constraint('fk_messages_parent_message_id', 'messages', type_='foreignkey')
    
    # Remove columns
    op.drop_column('messages', 'updated_at')
    op.drop_column('messages', 'parent_message_id')
    op.drop_column('messages', 'is_important')
    op.drop_column('messages', 'is_read')
    op.drop_column('messages', 'conversation_id')
    op.drop_column('messages', 'message_type')
