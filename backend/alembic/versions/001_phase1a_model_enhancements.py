"""Phase 1A model enhancements

Revision ID: 001_phase1a
Revises: 
Create Date: 2025-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_phase1a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create all tables first
    
    # Users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Players table (Phase 1A Enhanced)
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('position', sa.String(), nullable=True),
    sa.Column('team', sa.String(), nullable=True),
    sa.Column('jersey_number', sa.Integer(), nullable=True),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('birth_date', sa.DateTime(), nullable=True),
    sa.Column('nationality', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    # Phase 1A Enhanced Fields
    sa.Column('college', sa.String(), nullable=True),
    sa.Column('playing_style', sa.String(), nullable=True),
    sa.Column('career_start', sa.DateTime(), nullable=True),
    sa.Column('career_end', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_players_id'), 'players', ['id'], unique=False)
    op.create_index(op.f('ix_players_name'), 'players', ['name'], unique=False)
    op.create_index(op.f('ix_players_team'), 'players', ['team'], unique=False)

    # Games table (Phase 1A Enhanced)
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('home_team', sa.String(), nullable=False),
    sa.Column('away_team', sa.String(), nullable=False),
    sa.Column('home_score', sa.Integer(), nullable=True),
    sa.Column('away_score', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('venue', sa.String(), nullable=True),
    sa.Column('week', sa.Integer(), nullable=True),
    sa.Column('game_type', sa.String(), nullable=True),
    sa.Column('weather_conditions', sa.JSON(), nullable=True),
    # Phase 1A Enhanced Fields
    sa.Column('season_type', sa.String(), nullable=True),
    sa.Column('season_year', sa.Integer(), nullable=True),
    sa.Column('overtime', sa.Boolean(), nullable=True),
    sa.Column('pace', sa.Float(), nullable=True),
    sa.Column('game_importance', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_games_away_team'), 'games', ['away_team'], unique=False)
    op.create_index(op.f('ix_games_date'), 'games', ['date'], unique=False)
    op.create_index(op.f('ix_games_home_team'), 'games', ['home_team'], unique=False)
    op.create_index(op.f('ix_games_id'), 'games', ['id'], unique=False)
    op.create_index(op.f('ix_games_season_type'), 'games', ['season_type'], unique=False)
    op.create_index(op.f('ix_games_season_year'), 'games', ['season_year'], unique=False)

    # Teams table (Phase 1A Enhanced)
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('abbreviation', sa.String(), nullable=True),
    sa.Column('conference', sa.String(), nullable=True),
    sa.Column('division', sa.String(), nullable=True),
    sa.Column('founded_year', sa.Integer(), nullable=True),
    sa.Column('colors', sa.JSON(), nullable=True),
    sa.Column('logo_url', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    # Phase 1A Enhanced Fields
    sa.Column('head_coach', sa.String(), nullable=True),
    sa.Column('pace_factor', sa.Float(), nullable=True),
    sa.Column('offensive_style_rating', sa.Float(), nullable=True),
    sa.Column('defensive_style_rating', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_abbreviation'), 'teams', ['abbreviation'], unique=True)
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_name'), 'teams', ['name'], unique=True)

    # GameStats table (Phase 1A Enhanced)
    op.create_table('game_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.Column('assists', sa.Integer(), nullable=True),
    sa.Column('rebounds', sa.Integer(), nullable=True),
    sa.Column('steals', sa.Integer(), nullable=True),
    sa.Column('blocks', sa.Integer(), nullable=True),
    sa.Column('turnovers', sa.Integer(), nullable=True),
    sa.Column('field_goals_made', sa.Integer(), nullable=True),
    sa.Column('field_goals_attempted', sa.Integer(), nullable=True),
    sa.Column('three_pointers_made', sa.Integer(), nullable=True),
    sa.Column('three_pointers_attempted', sa.Integer(), nullable=True),
    sa.Column('free_throws_made', sa.Integer(), nullable=True),
    sa.Column('free_throws_attempted', sa.Integer(), nullable=True),
    sa.Column('minutes_played', sa.Float(), nullable=True),
    sa.Column('plus_minus', sa.Integer(), nullable=True),
    # Phase 1A Enhanced Fields
    sa.Column('usage_rate', sa.Float(), nullable=True),
    sa.Column('game_score', sa.Float(), nullable=True),
    sa.Column('fantasy_points', sa.Float(), nullable=True),
    sa.Column('additional_stats', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_game_stats_id'), 'game_stats', ['id'], unique=False)

    # PlayerRiskAssessment table (Phase 1A New)
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

    # Agent tables
    op.create_table('agent_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('agent_type', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('context', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_sessions_id'), 'agent_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_agent_sessions_session_id'), 'agent_sessions', ['session_id'], unique=True)

    op.create_table('agent_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(), nullable=False),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('message_metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['agent_sessions.session_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_messages_id'), 'agent_messages', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_agent_messages_id'), table_name='agent_messages')
    op.drop_table('agent_messages')
    
    op.drop_index(op.f('ix_agent_sessions_session_id'), table_name='agent_sessions')
    op.drop_index(op.f('ix_agent_sessions_id'), table_name='agent_sessions')
    op.drop_table('agent_sessions')
    
    op.drop_index(op.f('ix_player_risk_assessment_id'), table_name='player_risk_assessment')
    op.drop_index(op.f('ix_player_risk_assessment_assessment_date'), table_name='player_risk_assessment')
    op.drop_table('player_risk_assessment')
    
    op.drop_index(op.f('ix_game_stats_id'), table_name='game_stats')
    op.drop_table('game_stats')
    
    op.drop_index(op.f('ix_teams_name'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_abbreviation'), table_name='teams')
    op.drop_table('teams')
    
    op.drop_index(op.f('ix_games_season_year'), table_name='games')
    op.drop_index(op.f('ix_games_season_type'), table_name='games')
    op.drop_index(op.f('ix_games_id'), table_name='games')
    op.drop_index(op.f('ix_games_home_team'), table_name='games')
    op.drop_index(op.f('ix_games_date'), table_name='games')
    op.drop_index(op.f('ix_games_away_team'), table_name='games')
    op.drop_table('games')
    
    op.drop_index(op.f('ix_players_team'), table_name='players')
    op.drop_index(op.f('ix_players_name'), table_name='players')
    op.drop_index(op.f('ix_players_id'), table_name='players')
    op.drop_table('players')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')