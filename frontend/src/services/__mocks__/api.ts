import { AuthTokens, LoginCredentials, RegisterData, User, Player } from '../../types';

const mockApiService = {
  login: jest.fn((credentials: LoginCredentials): Promise<AuthTokens> => 
    Promise.resolve({ access_token: 'test-token', token_type: 'Bearer' })
  ),
  
  register: jest.fn((data: RegisterData): Promise<User> => 
    Promise.resolve({
      id: 1,
      username: data.username,
      email: data.email,
      is_active: true,
      is_superuser: false,
      created_at: '2025-01-01T00:00:00Z'
    })
  ),
  
  getCurrentUser: jest.fn((): Promise<User> => 
    Promise.resolve({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_active: true,
      is_superuser: false,
      created_at: '2025-01-01T00:00:00Z'
    })
  ),
  
  getPlayers: jest.fn((skip = 0, limit = 100): Promise<Player[]> => 
    Promise.resolve([])
  ),
  
  getPlayer: jest.fn((playerId: number): Promise<Player> => 
    Promise.resolve({
      id: playerId,
      name: 'Test Player',
      position: 'PG',
      team: 'Test Team',
      is_active: true,
      created_at: '2025-01-01T00:00:00Z'
    })
  ),
};

export default mockApiService;