"""Add user preferences table

Revision ID: 005_add_user_preferences
Revises: 004_add_fantasy_data
Create Date: 2025-08-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic
revision = '005_add_user_preferences'
down_revision = '004_add_fantasy_data'
branch_labels = None
depends_on = None

def upgrade():
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # UI Preferences
        sa.Column('theme_mode', sa.String(), nullable=True, server_default='light'),
        sa.Column('sidebar_collapsed', sa.Boolean(), nullable=True, server_default='false'),
        
        # Agent Preferences
        sa.Column('preferred_agent', sa.String(), nullable=True, server_default='intelligence'),
        sa.Column('agent_response_style', sa.String(), nullable=True, server_default='detailed'),
        
        # Fantasy Preferences
        sa.Column('league_type', sa.String(), nullable=True, server_default='h2h_9cat'),
        sa.Column('team_size', sa.Integer(), nullable=True, server_default='12'),
        sa.Column('favorite_team', sa.String(), nullable=True),
        
        # Notification Preferences
        sa.Column('email_notifications', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('injury_alerts', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('trade_alerts', sa.Boolean(), nullable=True, server_default='true'),
        
        # Display Preferences
        sa.Column('default_stat_view', sa.String(), nullable=True, server_default='season'),
        sa.Column('show_advanced_stats', sa.Boolean(), nullable=True, server_default='false'),
        
        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Create index on user_id for faster lookups
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_table('user_preferences')