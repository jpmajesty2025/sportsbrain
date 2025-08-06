"""Add missing Phase 1A columns with existence checks

Revision ID: 003_add_missing_phase1a_columns
Revises: 002_add_phase1a_columns
Create Date: 2025-08-06 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_missing_phase1a_columns'
down_revision = '001_phase1a'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # Add Phase 1A columns to players table only if they don't exist
    if not column_exists('players', 'college'):
        op.add_column('players', sa.Column('college', sa.String(), nullable=True))
    if not column_exists('players', 'playing_style'):
        op.add_column('players', sa.Column('playing_style', sa.String(), nullable=True))
    if not column_exists('players', 'career_start'):
        op.add_column('players', sa.Column('career_start', sa.DateTime(), nullable=True))
    if not column_exists('players', 'career_end'):
        op.add_column('players', sa.Column('career_end', sa.DateTime(), nullable=True))
    
    # Add Phase 1A columns to games table only if they don't exist
    if not column_exists('games', 'season_type'):
        op.add_column('games', sa.Column('season_type', sa.String(), nullable=True))
    if not column_exists('games', 'season_year'):
        op.add_column('games', sa.Column('season_year', sa.Integer(), nullable=True))
    if not column_exists('games', 'overtime'):
        op.add_column('games', sa.Column('overtime', sa.Boolean(), nullable=True))
    if not column_exists('games', 'pace'):
        op.add_column('games', sa.Column('pace', sa.Float(), nullable=True))
    if not column_exists('games', 'game_importance'):
        op.add_column('games', sa.Column('game_importance', sa.String(), nullable=True))
    
    # Create indexes for new columns if they don't exist
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('games')}
    
    if 'ix_games_season_type' not in existing_indexes:
        op.create_index(op.f('ix_games_season_type'), 'games', ['season_type'], unique=False)
    if 'ix_games_season_year' not in existing_indexes:
        op.create_index(op.f('ix_games_season_year'), 'games', ['season_year'], unique=False)
    
    # Add Phase 1A columns to teams table only if they don't exist
    if not column_exists('teams', 'head_coach'):
        op.add_column('teams', sa.Column('head_coach', sa.String(), nullable=True))
    if not column_exists('teams', 'pace_factor'):
        op.add_column('teams', sa.Column('pace_factor', sa.Float(), nullable=True))
    if not column_exists('teams', 'offensive_style_rating'):
        op.add_column('teams', sa.Column('offensive_style_rating', sa.Float(), nullable=True))
    if not column_exists('teams', 'defensive_style_rating'):
        op.add_column('teams', sa.Column('defensive_style_rating', sa.Float(), nullable=True))
    
    # Add Phase 1A columns to game_stats table only if they don't exist
    if not column_exists('game_stats', 'usage_rate'):
        op.add_column('game_stats', sa.Column('usage_rate', sa.Float(), nullable=True))
    if not column_exists('game_stats', 'game_score'):
        op.add_column('game_stats', sa.Column('game_score', sa.Float(), nullable=True))
    if not column_exists('game_stats', 'fantasy_points'):
        op.add_column('game_stats', sa.Column('fantasy_points', sa.Float(), nullable=True))
    if not column_exists('game_stats', 'additional_stats'):
        op.add_column('game_stats', sa.Column('additional_stats', sa.JSON(), nullable=True))
    
    # Create new player_risk_assessment table if it doesn't exist
    tables = {table_name for table_name in inspector.get_table_names()}
    if 'player_risk_assessment' not in tables:
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
    # For safety, downgrade is a no-op
    # We don't want to accidentally drop columns that might have data
    pass