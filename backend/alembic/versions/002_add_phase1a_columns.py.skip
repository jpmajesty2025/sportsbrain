"""Add Phase 1A columns to existing tables

Revision ID: 002_add_phase1a_columns
Revises: 001_phase1a
Create Date: 2025-08-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_phase1a_columns'
down_revision = '001_phase1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Phase 1A columns to players table if they don't exist
    with op.batch_alter_table('players') as batch_op:
        batch_op.add_column(sa.Column('college', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('playing_style', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('career_start', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('career_end', sa.DateTime(), nullable=True))
    
    # Add Phase 1A columns to games table if they don't exist
    with op.batch_alter_table('games') as batch_op:
        batch_op.add_column(sa.Column('season_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('season_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('overtime', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('pace', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('game_importance', sa.String(), nullable=True))
    
    # Create indexes for new columns
    op.create_index(op.f('ix_games_season_type'), 'games', ['season_type'], unique=False)
    op.create_index(op.f('ix_games_season_year'), 'games', ['season_year'], unique=False)
    
    # Add Phase 1A columns to teams table if they don't exist
    with op.batch_alter_table('teams') as batch_op:
        batch_op.add_column(sa.Column('head_coach', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('pace_factor', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('offensive_style_rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('defensive_style_rating', sa.Float(), nullable=True))
    
    # Add Phase 1A columns to game_stats table if they don't exist
    with op.batch_alter_table('game_stats') as batch_op:
        batch_op.add_column(sa.Column('usage_rate', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('game_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('fantasy_points', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('additional_stats', sa.JSON(), nullable=True))
    
    # Create new player_risk_assessment table if it doesn't exist
    op.create_table('player_risk_assessment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('assessment_date', sa.DateTime(), nullable=False),
        sa.Column('games_missed_last_30', sa.Integer(), nullable=True),
        sa.Column('load_management_frequency', sa.Float(), nullable=True),
        sa.Column('injury_recurrence_risk', sa.String(), nullable=True),
        sa.Column('fantasy_point_variance', sa.Float(), nullable=True),
        sa.Column('consistency_score', sa.Float(), nullable=True),
        sa.Column('rest_vs_b2b_differential', sa.Float(), nullable=True),
        sa.Column('usage_volatility', sa.Float(), nullable=True),
        sa.Column('bench_risk_flag', sa.Boolean(), nullable=True),
        sa.Column('overall_risk_category', sa.String(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_risk_assessment_assessment_date'), 'player_risk_assessment', ['assessment_date'], unique=False)
    op.create_index(op.f('ix_player_risk_assessment_id'), 'player_risk_assessment', ['id'], unique=False)


def downgrade() -> None:
    # Drop new table
    op.drop_index(op.f('ix_player_risk_assessment_id'), table_name='player_risk_assessment')
    op.drop_index(op.f('ix_player_risk_assessment_assessment_date'), table_name='player_risk_assessment')
    op.drop_table('player_risk_assessment')
    
    # Drop indexes
    op.drop_index(op.f('ix_games_season_year'), table_name='games')
    op.drop_index(op.f('ix_games_season_type'), table_name='games')
    
    # Remove Phase 1A columns from game_stats
    with op.batch_alter_table('game_stats') as batch_op:
        batch_op.drop_column('additional_stats')
        batch_op.drop_column('fantasy_points')
        batch_op.drop_column('game_score')
        batch_op.drop_column('usage_rate')
    
    # Remove Phase 1A columns from teams
    with op.batch_alter_table('teams') as batch_op:
        batch_op.drop_column('defensive_style_rating')
        batch_op.drop_column('offensive_style_rating')
        batch_op.drop_column('pace_factor')
        batch_op.drop_column('head_coach')
    
    # Remove Phase 1A columns from games
    with op.batch_alter_table('games') as batch_op:
        batch_op.drop_column('game_importance')
        batch_op.drop_column('pace')
        batch_op.drop_column('overtime')
        batch_op.drop_column('season_year')
        batch_op.drop_column('season_type')
    
    # Remove Phase 1A columns from players
    with op.batch_alter_table('players') as batch_op:
        batch_op.drop_column('career_end')
        batch_op.drop_column('career_start')
        batch_op.drop_column('playing_style')
        batch_op.drop_column('college')