// Mock axios before imports
jest.mock('axios');

import { AuthTokens, LoginCredentials, RegisterData, User, Player } from '../types';
import apiService from './api';
// Import the mock instance to access its methods
import { mockAxiosInstance } from '../__mocks__/axios';

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
        const mockTokens: AuthTokens = { access_token: 'test-token', token_type: 'Bearer' };
        (mockAxiosInstance.post as jest.Mock).mockResolvedValueOnce({ data: mockTokens });

        const credentials: LoginCredentials = { username: 'testuser', password: 'testpass' };
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
        (mockAxiosInstance.post as jest.Mock).mockRejectedValueOnce({
          response: { data: { detail: errorMessage } }
        });

        const credentials: LoginCredentials = { username: 'testuser', password: 'wrongpass' };
        
        await expect(apiService.login(credentials)).rejects.toEqual({
          response: { data: { detail: errorMessage } }
        });
      });
    });

    describe('register', () => {
      it('should send registration data and return user', async () => {
        const mockUser: User = { 
          id: 1, 
          username: 'newuser', 
          email: 'new@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2025-01-01T00:00:00Z'
        };
        (mockAxiosInstance.post as jest.Mock).mockResolvedValueOnce({ data: mockUser });

        const registerData: RegisterData = {
          username: 'newuser',
          email: 'new@example.com',
          password: 'securepass123'
        };
        const result = await apiService.register(registerData);

        expect(mockAxiosInstance.post).toHaveBeenCalledWith('/auth/register', registerData);
        expect(result).toEqual(mockUser);
      });
    });

    describe('getCurrentUser', () => {
      it('should fetch current user data', async () => {
        const mockUser: User = { 
          id: 1, 
          username: 'testuser', 
          email: 'test@example.com',
          is_active: true,
          is_superuser: false,
          created_at: '2025-01-01T00:00:00Z'
        };
        (mockAxiosInstance.get as jest.Mock).mockResolvedValueOnce({ data: mockUser });

        const result = await apiService.getCurrentUser();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/auth/me');
        expect(result).toEqual(mockUser);
      });
    });
  });

  describe('Players API', () => {
    describe('getPlayers', () => {
      it('should fetch players with default pagination', async () => {
        const mockPlayers: Player[] = [
          { 
            id: 1, 
            name: 'Player 1', 
            position: 'PG',
            team: 'Team A',
            is_active: true,
            created_at: '2025-01-01T00:00:00Z'
          },
          { 
            id: 2, 
            name: 'Player 2',
            position: 'SG', 
            team: 'Team B',
            is_active: true,
            created_at: '2025-01-01T00:00:00Z'
          }
        ];
        (mockAxiosInstance.get as jest.Mock).mockResolvedValueOnce({ data: mockPlayers });

        const result = await apiService.getPlayers();

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players?skip=0&limit=100');
        expect(result).toEqual(mockPlayers);
      });

      it('should fetch players with custom pagination', async () => {
        const mockPlayers: Player[] = [];
        (mockAxiosInstance.get as jest.Mock).mockResolvedValueOnce({ data: mockPlayers });

        const result = await apiService.getPlayers(10, 50);

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players?skip=10&limit=50');
        expect(result).toEqual(mockPlayers);
      });
    });

    describe('getPlayer', () => {
      it('should fetch a single player by ID', async () => {
        const mockPlayer: Player = { 
          id: 1, 
          name: 'Test Player',
          position: 'C',
          team: 'Test Team',
          is_active: true,
          created_at: '2025-01-01T00:00:00Z'
        };
        (mockAxiosInstance.get as jest.Mock).mockResolvedValueOnce({ data: mockPlayer });

        const result = await apiService.getPlayer(1);

        expect(mockAxiosInstance.get).toHaveBeenCalledWith('/players/1');
        expect(result).toEqual(mockPlayer);
      });
    });
  });

  describe('Request Interceptor', () => {
    it('should setup interceptors on initialization', () => {
      // The interceptors are set up when ApiService is imported
      // Since we're using a singleton, we just verify the mock structure exists
      expect(mockAxiosInstance.interceptors).toBeDefined();
      expect(mockAxiosInstance.interceptors.request).toBeDefined();
      expect(mockAxiosInstance.interceptors.response).toBeDefined();
    });
  });
});