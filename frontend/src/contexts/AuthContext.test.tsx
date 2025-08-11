import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import apiService from '../services/api';

// Mock the API service
jest.mock('../services/api');

const mockedApiService = apiService as jest.Mocked<typeof apiService>;

// Test component that uses the auth context
const TestComponent = () => {
  const { user, loading, isAuthenticated, login, logout } = useAuth();
  
  return (
    <div>
      <div data-testid="loading">{loading.toString()}</div>
      <div data-testid="authenticated">{isAuthenticated.toString()}</div>
      <div data-testid="user">{user ? user.username : 'no-user'}</div>
      <button onClick={() => login({ username: 'test', password: 'test' })}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear all mocks
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('useAuth hook', () => {
    it('should throw error when used outside of AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useAuth must be used within an AuthProvider');
      
      consoleSpy.mockRestore();
    });

    it('should provide auth context when used within AuthProvider', () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      expect(screen.getByTestId('loading')).toBeInTheDocument();
      expect(screen.getByTestId('authenticated')).toBeInTheDocument();
      expect(screen.getByTestId('user')).toBeInTheDocument();
    });
  });

  describe('Initial state', () => {
    it('should start with loading true and no user', () => {
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      expect(screen.getByTestId('loading').textContent).toBe('false');
      expect(screen.getByTestId('authenticated').textContent).toBe('false');
      expect(screen.getByTestId('user').textContent).toBe('no-user');
    });

    it('should load user if token exists in localStorage', async () => {
      const mockUser = { id: '1', username: 'testuser', email: 'test@example.com' };
      localStorage.setItem('access_token', 'test-token');
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('user').textContent).toBe('testuser');
        expect(screen.getByTestId('authenticated').textContent).toBe('true');
      });
    });

    it('should remove token if loading user fails', async () => {
      localStorage.setItem('access_token', 'invalid-token');
      mockedApiService.getCurrentUser.mockRejectedValueOnce(new Error('Unauthorized'));
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBeNull();
        expect(screen.getByTestId('user').textContent).toBe('no-user');
      });
    });
  });

  describe('Login', () => {
    it('should login successfully and set user', async () => {
      const mockTokens = { access_token: 'new-token', token_type: 'Bearer' };
      const mockUser = { id: '1', username: 'testuser', email: 'test@example.com' };
      
      mockedApiService.login.mockResolvedValueOnce(mockTokens);
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      const loginButton = screen.getByText('Login');
      
      await act(async () => {
        loginButton.click();
      });
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('new-token');
        expect(screen.getByTestId('user').textContent).toBe('testuser');
        expect(screen.getByTestId('authenticated').textContent).toBe('true');
      });
    });

    it('should handle login error', async () => {
      mockedApiService.login.mockRejectedValueOnce(new Error('Invalid credentials'));
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      const loginButton = screen.getByText('Login');
      
      await act(async () => {
        try {
          await loginButton.click();
        } catch (error) {
          // Expected error
        }
      });
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBeNull();
        expect(screen.getByTestId('user').textContent).toBe('no-user');
      });
    });
  });

  describe('Logout', () => {
    it('should clear user and token on logout', async () => {
      const mockUser = { id: '1', username: 'testuser', email: 'test@example.com' };
      localStorage.setItem('access_token', 'test-token');
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      await waitFor(() => {
        expect(screen.getByTestId('user').textContent).toBe('testuser');
      });
      
      const logoutButton = screen.getByText('Logout');
      
      act(() => {
        logoutButton.click();
      });
      
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(screen.getByTestId('user').textContent).toBe('no-user');
      expect(screen.getByTestId('authenticated').textContent).toBe('false');
    });
  });

  describe('Register', () => {
    it('should register and auto-login', async () => {
      const mockTokens = { access_token: 'new-token', token_type: 'Bearer' };
      const mockUser = { id: '1', username: 'newuser', email: 'new@example.com' };
      
      mockedApiService.register.mockResolvedValueOnce(mockUser);
      mockedApiService.login.mockResolvedValueOnce(mockTokens);
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      const TestRegisterComponent = () => {
        const { register } = useAuth();
        
        return (
          <button 
            onClick={() => register({ 
              username: 'newuser', 
              email: 'new@example.com',
              password: 'password123' 
            })}
          >
            Register
          </button>
        );
      };
      
      render(
        <AuthProvider>
          <TestRegisterComponent />
          <TestComponent />
        </AuthProvider>
      );
      
      const registerButton = screen.getByText('Register');
      
      await act(async () => {
        registerButton.click();
      });
      
      await waitFor(() => {
        expect(mockedApiService.register).toHaveBeenCalled();
        expect(mockedApiService.login).toHaveBeenCalled();
        expect(screen.getByTestId('user').textContent).toBe('newuser');
      });
    });
  });
});