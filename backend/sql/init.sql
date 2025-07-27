-- Initialize SportsBrain database

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_games_date ON games(date);
CREATE INDEX IF NOT EXISTS idx_games_teams ON games(home_team, away_team);
CREATE INDEX IF NOT EXISTS idx_game_stats_player ON game_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_game_stats_game ON game_stats(game_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Insert sample data
INSERT INTO teams (name, city, abbreviation, conference, division, founded_year, colors, is_active) VALUES
('Lakers', 'Los Angeles', 'LAL', 'Western', 'Pacific', 1947, '{"primary": "#552583", "secondary": "#FDB927"}', true),
('Warriors', 'Golden State', 'GSW', 'Western', 'Pacific', 1946, '{"primary": "#1D428A", "secondary": "#FFC72C"}', true),
('Celtics', 'Boston', 'BOS', 'Eastern', 'Atlantic', 1946, '{"primary": "#007A33", "secondary": "#BA9653"}', true),
('Heat', 'Miami', 'MIA', 'Eastern', 'Southeast', 1988, '{"primary": "#98002E", "secondary": "#F9A01B"}', true)
ON CONFLICT (name) DO NOTHING;

-- Insert sample players
INSERT INTO players (name, position, team, jersey_number, height, weight, nationality, is_active) VALUES
('LeBron James', 'SF', 'Lakers', 6, 6.75, 250, 'USA', true),
('Stephen Curry', 'PG', 'Warriors', 30, 6.25, 185, 'USA', true),
('Jayson Tatum', 'SF', 'Celtics', 0, 6.67, 210, 'USA', true),
('Jimmy Butler', 'SF', 'Heat', 22, 6.58, 230, 'USA', true)
ON CONFLICT DO NOTHING;