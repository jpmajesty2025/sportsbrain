"""Add FantasyData table for draft prep

Revision ID: 004
Revises: 003
Create Date: 2025-08-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers
revision = '004_add_fantasy_data'
down_revision = '003_add_missing_phase1a_columns'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('fantasy_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('season', sa.String(), nullable=True),
        
        # Draft data
        sa.Column('adp_rank', sa.Integer(), nullable=True),
        sa.Column('adp_round', sa.Integer(), nullable=True),
        sa.Column('yahoo_rank', sa.Integer(), nullable=True),
        sa.Column('espn_rank', sa.Integer(), nullable=True),
        
        # Keeper/Dynasty values
        sa.Column('keeper_round', sa.Integer(), nullable=True),
        sa.Column('dynasty_value', sa.Integer(), nullable=True),
        
        # Projections for 2024-25
        sa.Column('projected_ppg', sa.Float(), nullable=True),
        sa.Column('projected_rpg', sa.Float(), nullable=True),
        sa.Column('projected_apg', sa.Float(), nullable=True),
        sa.Column('projected_spg', sa.Float(), nullable=True),
        sa.Column('projected_bpg', sa.Float(), nullable=True),
        sa.Column('projected_fg_pct', sa.Float(), nullable=True),
        sa.Column('projected_ft_pct', sa.Float(), nullable=True),
        sa.Column('projected_3pm', sa.Float(), nullable=True),
        sa.Column('projected_fantasy_ppg', sa.Float(), nullable=True),
        
        # Strategic values
        sa.Column('punt_ft_fit', sa.Boolean(), nullable=True),
        sa.Column('punt_fg_fit', sa.Boolean(), nullable=True),
        sa.Column('punt_ast_fit', sa.Boolean(), nullable=True),
        sa.Column('punt_3pm_fit', sa.Boolean(), nullable=True),
        
        # Analysis flags
        sa.Column('sleeper_score', sa.Float(), nullable=True),
        sa.Column('breakout_candidate', sa.Boolean(), nullable=True),
        sa.Column('injury_risk', sa.String(), nullable=True),
        sa.Column('consistency_rating', sa.Float(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fantasy_data_adp_rank'), 'fantasy_data', ['adp_rank'], unique=False)
    op.create_index(op.f('ix_fantasy_data_id'), 'fantasy_data', ['id'], unique=False)
    op.create_index(op.f('ix_fantasy_data_player_id'), 'fantasy_data', ['player_id'], unique=True)
    op.create_index(op.f('ix_fantasy_data_season'), 'fantasy_data', ['season'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_fantasy_data_season'), table_name='fantasy_data')
    op.drop_index(op.f('ix_fantasy_data_player_id'), table_name='fantasy_data')
    op.drop_index(op.f('ix_fantasy_data_id'), table_name='fantasy_data')
    op.drop_index(op.f('ix_fantasy_data_adp_rank'), table_name='fantasy_data')
    op.drop_table('fantasy_data')