export interface UserPreferences {
  theme_mode: 'light' | 'dark';
  sidebar_collapsed: boolean;
  preferred_agent: string;
  agent_response_style: string;
  league_type: string;
  team_size: number;
  favorite_team?: string;
  email_notifications: boolean;
  injury_alerts: boolean;
  trade_alerts: boolean;
  default_stat_view: string;
  show_advanced_stats: boolean;
}

export interface UserPreferencesUpdate {
  theme_mode?: 'light' | 'dark';
  sidebar_collapsed?: boolean;
  preferred_agent?: string;
  agent_response_style?: string;
  league_type?: string;
  team_size?: number;
  favorite_team?: string;
  email_notifications?: boolean;
  injury_alerts?: boolean;
  trade_alerts?: boolean;
  default_stat_view?: string;
  show_advanced_stats?: boolean;
}