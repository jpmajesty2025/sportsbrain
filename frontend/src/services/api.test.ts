// Mock axios before importing apiService
let mockAxiosInstance: any;

jest.mock('axios', () => {
  mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  };
  return {
    create: jest.fn(() => mockAxiosInstance),
  };
});

import axios from 'axios';
import apiService from './api';
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiService', () => {
  let mockLocalStorage: { [key: string]: string };

  beforeEach(() => {
    // Reset localStorage mock
    mockLocalStorage = {};
    Storage.prototype.getItem = jest.fn((key) => mockLocalStorage[key] || null);
    Storage.prototype.setItem = jest.fn((key, value) => {
      mockLocalStorage[key] = value;
    });
    Storage.prototype.removeItem = jest.fn((key) => {
      delete mockLocalStorage[key];
    });

    // Clear mock calls
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication', () => {
    describe('login', () => {
      it('should send login credentials and return tokens', async () => {
        const mockTokens = { access_token: 'test-token', token_type: 'Bearer' };
        mockAxiosInstance.post.mockResolvedValueOnce({ data: mockTokens });

        const credentials = { username: 'testuser', password: 'testpass' };
        const result = await apiService.login(credentials);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/auth/login',
          expect.any(FormData),
          expect.objectContaining({
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          })
        );
        expect(result).toEqual(mockTokens);
      });

      it('should handle login error', async () => {
        const errorMessage = 'Invalid credentials';
        mockAxiosInstance.post.mockRejectedValueOnce({
          response: { data: { detail: errorMessage } }
        });

        const credentials = { username: 'testuser', password: 'wrongpass' };
        
        await expect(apiService.login(credentials)).rejects.toEqual({
          response: { data: { detail: errorMessage } }
        });
      });
    });

    describe('register', () => {
      it('should send registration data and return user', async () => {
        const mockUser = { 
          id: 1, 
          username: 'newuser', 
          email: 'new@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2025-01-01T00:00:00Z'
        };
        mockAxiosInstance.post.mockResolvedValueOnce({ data: mockUser });

        const registerData = {
          username: 'newuser',
          email: 'new@example.com',
          password: 'password123'
        };
        const result = await apiService.register(registerData);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/register', registerData);
        expect(result).toEqual(mockUser);
      });
    });

    describe('getCurrentUser', () => {
      it('should fetch current user data', async () => {
        const mockUser = { 
          id: 1, 
          username: 'testuser', 
          email: 'test@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2025-01-01T00:00:00Z'
        };
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockUser });

        const result = await apiService.getCurrentUser();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me');
        expect(result).toEqual(mockUser);
      });
    });
  });

  describe('Players API', () => {
    describe('getPlayers', () => {
      it('should fetch players with default pagination', async () => {
        const mockPlayers = [
          { id: 1, name: 'Player 1' },
          { id: 2, name: 'Player 2' }
        ];
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockPlayers });

        const result = await apiService.getPlayers();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players?skip=0&limit=100');
        expect(result).toEqual(mockPlayers);
      });

      it('should fetch players with custom pagination', async () => {
        const mockPlayers = [{ id: 3, name: 'Player 3' }];
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockPlayers });

        const result = await apiService.getPlayers(10, 5);

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players?skip=10&limit=5');
        expect(result).toEqual(mockPlayers);
      });
    });

    describe('getPlayer', () => {
      it('should fetch a single player by ID', async () => {
        const mockPlayer = { id: 1, name: 'Player 1' };
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockPlayer });

        const result = await apiService.getPlayer(1);

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players/1');
        expect(result).toEqual(mockPlayer);
      });
    });

    describe('createPlayer', () => {
      it('should create a new player', async () => {
        const newPlayerData = { name: 'New Player', team: 'Lakers' };
        const mockCreatedPlayer = { id: 3, ...newPlayerData };
        mockAxiosInstance.post.mockResolvedValueOnce({ data: mockCreatedPlayer });

        const result = await apiService.createPlayer(newPlayerData);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/players', newPlayerData);
        expect(result).toEqual(mockCreatedPlayer);
      });
    });

    describe('updatePlayer', () => {
      it('should update an existing player', async () => {
        const updateData = { name: 'Updated Player' };
        const mockUpdatedPlayer = { id: 1, ...updateData };
        mockAxiosInstance.put.mockResolvedValueOnce({ data: mockUpdatedPlayer });

        const result = await apiService.updatePlayer(1, updateData);

        expect(mockAxiosInstance.put).toHaveBeenCalledWith('/players/1', updateData);
        expect(result).toEqual(mockUpdatedPlayer);
      });
    });

    describe('getPlayerStats', () => {
      it('should fetch player statistics', async () => {
        const mockStats = [
          { game_id: 1, points: 25, rebounds: 10 },
          { game_id: 2, points: 30, rebounds: 8 }
        ];
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockStats });

        const result = await apiService.getPlayerStats(1);

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players/1/stats');
        expect(result).toEqual(mockStats);
      });
    });
  });

  describe('Agents API', () => {
    describe('createAgentSession', () => {
      it('should create a new agent session', async () => {
        const mockSession = { 
          id: 'session-123', 
          agent_type: 'draft', 
          created_at: '2024-01-01T00:00:00Z' 
        };
        mockAxiosInstance.post.mockResolvedValueOnce({ data: mockSession });

        const result = await apiService.createAgentSession('draft', { round: 1 });

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/agents/sessions', {
          agent_type: 'draft',
          context: { round: 1 }
        });
        expect(result).toEqual(mockSession);
      });
    });

    describe('sendAgentMessage', () => {
      it('should send a message to an agent session', async () => {
        const mockMessage = {
          id: 'msg-123',
          session_id: 'session-123',
          role: 'user',
          content: 'Who should I draft?',
          created_at: '2024-01-01T00:00:00Z'
        };
        mockAxiosInstance.post.mockResolvedValueOnce({ data: mockMessage });

        const result = await apiService.sendAgentMessage(
          'session-123',
          'user',
          'Who should I draft?',
          { round: 1 }
        );

        expect(mockAxiosInstance.post).toHaveBeenCalledWith(
          '/agents/sessions/session-123/messages',
          {
            role: 'user',
            content: 'Who should I draft?',
            message_metadata: { round: 1 }
          }
        );
        expect(result).toEqual(mockMessage);
      });
    });

    describe('getAgentMessages', () => {
      it('should fetch messages for an agent session', async () => {
        const mockMessages = [
          { id: 'msg-1', role: 'user', content: 'Hello' },
          { id: 'msg-2', role: 'assistant', content: 'Hi there!' }
        ];
        mockAxiosInstance.get.mockResolvedValueOnce({ data: mockMessages });

        const result = await apiService.getAgentMessages('session-123');

        expect(mockAxiosInstance.get).toHaveBeenCalledWith(
          '/agents/sessions/session-123/messages?skip=0&limit=100'
        );
        expect(result).toEqual(mockMessages);
      });
    });
  });

  describe('Interceptors', () => {
    it('should add authorization header when token exists', () => {
      // Get the request interceptor function
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      
      mockLocalStorage['access_token'] = 'test-token';
      const config = { headers: {} };
      
      const modifiedConfig = requestInterceptor(config);
      
      expect(modifiedConfig.headers.Authorization).toBe('Bearer test-token');
    });

    it('should not add authorization header when no token', () => {
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0];
      
      const config = { headers: {} };
      
      const modifiedConfig = requestInterceptor(config);
      
      expect(modifiedConfig.headers.Authorization).toBeUndefined();
    });

    it('should handle 401 errors by clearing token and redirecting', () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      
      // Mock window.location
      delete (window as any).location;
      window.location = { href: '' } as any;
      
      mockLocalStorage['access_token'] = 'test-token';
      
      const error = { response: { status: 401 } };
      
      expect(() => responseInterceptor(error)).rejects.toEqual(error);
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
      expect(window.location.href).toBe('/login');
    });

    it('should pass through non-401 errors', () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1];
      
      const error = { response: { status: 500 } };
      
      expect(responseInterceptor(error)).rejects.toEqual(error);
    });
  });
});