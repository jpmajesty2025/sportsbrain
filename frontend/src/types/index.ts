export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Player {
  id: number;
  name: string;
  position?: string;
  team?: string;
  jersey_number?: number;
  height?: number;
  weight?: number;
  birth_date?: string;
  nationality?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Game {
  id: number;
  date: string;
  home_team: string;
  away_team: string;
  home_score?: number;
  away_score?: number;
  status: string;
  venue?: string;
  season?: string;
  week?: number;
  game_type?: string;
  weather_conditions?: any;
  created_at: string;
  updated_at?: string;
}

export interface GameStats {
  id: number;
  player_id: number;
  game_id: number;
  points: number;
  assists: number;
  rebounds: number;
  steals: number;
  blocks: number;
  turnovers: number;
  field_goals_made: number;
  field_goals_attempted: number;
  three_pointers_made: number;
  three_pointers_attempted: number;
  free_throws_made: number;
  free_throws_attempted: number;
  minutes_played: number;
  plus_minus: number;
  created_at: string;
  updated_at?: string;
}

export interface AgentSession {
  id: number;
  user_id: number;
  session_id: string;
  agent_type: string;
  status: string;
  context?: any;
  created_at: string;
  updated_at?: string;
}

export interface AgentMessage {
  id: number;
  session_id: string;
  role: string;
  content: string;
  message_metadata?: any;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}