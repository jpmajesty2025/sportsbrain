import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { AuthTokens, LoginCredentials, RegisterData, User, Player, Game, GameStats, AgentSession, AgentMessage } from '../types';
import { UserPreferences, UserPreferencesUpdate } from '../types/preferences';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response: AxiosResponse<AuthTokens> = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
  }

  async register(data: RegisterData): Promise<User> {
    const response: AxiosResponse<User> = await this.client.post('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/auth/me');
    return response.data;
  }

  // Users
  async getUsers(skip = 0, limit = 100): Promise<User[]> {
    const response: AxiosResponse<User[]> = await this.client.get(`/users?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getUser(userId: number): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get(`/users/${userId}`);
    return response.data;
  }

  // Players
  async getPlayers(skip = 0, limit = 100): Promise<Player[]> {
    const response: AxiosResponse<Player[]> = await this.client.get(`/players?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getPlayer(playerId: number): Promise<Player> {
    const response: AxiosResponse<Player> = await this.client.get(`/players/${playerId}`);
    return response.data;
  }

  async createPlayer(playerData: Partial<Player>): Promise<Player> {
    const response: AxiosResponse<Player> = await this.client.post('/players', playerData);
    return response.data;
  }

  async updatePlayer(playerId: number, playerData: Partial<Player>): Promise<Player> {
    const response: AxiosResponse<Player> = await this.client.put(`/players/${playerId}`, playerData);
    return response.data;
  }

  async getPlayerStats(playerId: number): Promise<GameStats[]> {
    const response: AxiosResponse<GameStats[]> = await this.client.get(`/players/${playerId}/stats`);
    return response.data;
  }

  // Games
  async getGames(skip = 0, limit = 100): Promise<Game[]> {
    const response: AxiosResponse<Game[]> = await this.client.get(`/games?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getGame(gameId: number): Promise<Game> {
    const response: AxiosResponse<Game> = await this.client.get(`/games/${gameId}`);
    return response.data;
  }

  async createGame(gameData: Partial<Game>): Promise<Game> {
    const response: AxiosResponse<Game> = await this.client.post('/games', gameData);
    return response.data;
  }

  async updateGame(gameId: number, gameData: Partial<Game>): Promise<Game> {
    const response: AxiosResponse<Game> = await this.client.put(`/games/${gameId}`, gameData);
    return response.data;
  }

  async getGameStats(gameId: number): Promise<GameStats[]> {
    const response: AxiosResponse<GameStats[]> = await this.client.get(`/games/${gameId}/stats`);
    return response.data;
  }

  // Agents
  async createAgentSession(agentType: string, context?: any): Promise<AgentSession> {
    const response: AxiosResponse<AgentSession> = await this.client.post('/agents/sessions', {
      agent_type: agentType,
      context
    });
    return response.data;
  }

  async getAgentSessions(skip = 0, limit = 100): Promise<AgentSession[]> {
    const response: AxiosResponse<AgentSession[]> = await this.client.get(`/agents/sessions?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async getAgentSession(sessionId: string): Promise<AgentSession> {
    const response: AxiosResponse<AgentSession> = await this.client.get(`/agents/sessions/${sessionId}`);
    return response.data;
  }

  async sendAgentMessage(sessionId: string, role: string, content: string, message_metadata?: any): Promise<AgentMessage> {
    const response: AxiosResponse<AgentMessage> = await this.client.post(`/agents/sessions/${sessionId}/messages`, {
      role,
      content,
      message_metadata
    });
    return response.data;
  }

  // User Preferences
  async getUserPreferences(): Promise<UserPreferences> {
    const response = await this.client.get<UserPreferences>('/users/preferences');
    return response.data;
  }

  async updateUserPreferences(preferences: UserPreferencesUpdate): Promise<UserPreferences> {
    const response = await this.client.put<UserPreferences>('/users/preferences', preferences);
    return response.data;
  }

  async toggleTheme(): Promise<{ theme_mode: 'light' | 'dark' }> {
    const response = await this.client.patch<{ theme_mode: 'light' | 'dark' }>('/users/preferences/theme');
    return response.data;
  }

  async resetPreferences(): Promise<UserPreferences> {
    const response = await this.client.post<UserPreferences>('/users/preferences/reset');
    return response.data;
  }

  async getAgentMessages(sessionId: string, skip = 0, limit = 100): Promise<AgentMessage[]> {
    const response: AxiosResponse<AgentMessage[]> = await this.client.get(`/agents/sessions/${sessionId}/messages?skip=${skip}&limit=${limit}`);
    return response.data;
  }
}

export default new ApiService();