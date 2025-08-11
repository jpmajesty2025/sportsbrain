import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import Login from '../pages/Login';
import apiService from '../services/api';

// Mock the API service
jest.mock('../services/api');
const mockedApiService = apiService as jest.Mocked<typeof apiService>;

// Mock navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Authentication Flow Integration', () => {
  let localStorageMock: { [key: string]: string };
  
  beforeEach(() => {
    // Setup localStorage mocks with proper storage
    localStorageMock = {};
    const mockLocalStorage = {
      getItem: jest.fn((key: string) => localStorageMock[key] || null),
      setItem: jest.fn((key: string, value: string) => {
        localStorageMock[key] = value;
      }),
      removeItem: jest.fn((key: string) => {
        delete localStorageMock[key];
      }),
      clear: jest.fn(() => {
        localStorageMock = {};
      }),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    });
    
    jest.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('should complete full login flow successfully', async () => {
      // Setup mocks
      const mockTokens = { access_token: 'test-token', token_type: 'Bearer' };
      const mockUser = { 
        id: 1, 
        username: 'testuser', 
        email: 'test@example.com',
        is_active: true,
        is_superuser: false,
        created_at: '2025-01-01T00:00:00Z'
      };
      
      mockedApiService.login.mockResolvedValueOnce(mockTokens);
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      // Render login page with auth provider
      render(
        <BrowserRouter>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </BrowserRouter>
      );
      
      // Fill in login form
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      
      // Submit form
      fireEvent.click(loginButton);
      
      // Wait for async operations
      await waitFor(() => {
        // Check that login was called with correct credentials
        expect(mockedApiService.login).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'password123',
        });
        
        // Check that token was stored
        expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-token');
        
        // Check that user data was fetched
        expect(mockedApiService.getCurrentUser).toHaveBeenCalled();
        
        // Check navigation to dashboard
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should handle login failure and show error', async () => {
      const errorMessage = 'Invalid username or password';
      mockedApiService.login.mockRejectedValueOnce({
        response: { data: { detail: errorMessage } }
      });
      
      render(
        <BrowserRouter>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </BrowserRouter>
      );
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'wronguser' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
      fireEvent.click(loginButton);
      
      await waitFor(() => {
        // Check that error message is displayed
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
        
        // Check that no token was stored
        expect(localStorage.setItem).not.toHaveBeenCalledWith('access_token', expect.anything());
        
        // Check that navigation didn't happen
        expect(mockNavigate).not.toHaveBeenCalled();
      });
    });
  });

  describe('Auto-login on Page Load', () => {
    it('should auto-login if valid token exists', async () => {
      const mockUser = { 
        id: 1, 
        username: 'existinguser', 
        email: 'existing@example.com',
        is_active: true,
        is_superuser: false,
        created_at: '2025-01-01T00:00:00Z'
      };
      
      // Set token in localStorage mock before rendering
      localStorageMock['access_token'] = 'existing-token';
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      // Create a test component to check auth state
      const TestComponent = () => {
        const { user, isAuthenticated } = useAuth();
        return (
          <div>
            <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
            <div data-testid="username">{user?.username || 'no-user'}</div>
          </div>
        );
      };
      
      render(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent />
          </AuthProvider>
        </BrowserRouter>
      );
      
      await waitFor(() => {
        expect(mockedApiService.getCurrentUser).toHaveBeenCalled();
        expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
        expect(screen.getByTestId('username').textContent).toBe('existinguser');
      });
    });

    it('should clear invalid token on failed auto-login', async () => {
      // Set invalid token in localStorage mock
      localStorageMock['access_token'] = 'invalid-token';
      mockedApiService.getCurrentUser.mockRejectedValueOnce(new Error('Unauthorized'));
      
      const TestComponent = () => {
        const { isAuthenticated } = useAuth();
        return <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>;
      };
      
      render(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent />
          </AuthProvider>
        </BrowserRouter>
      );
      
      await waitFor(() => {
        expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
        expect(screen.getByTestId('auth-status').textContent).toBe('not-authenticated');
      });
    });
  });

  describe('Logout Flow', () => {
    it('should clear authentication on logout', async () => {
      const mockUser = { 
        id: 1, 
        username: 'testuser', 
        email: 'test@example.com',
        is_active: true,
        is_superuser: false,
        created_at: '2025-01-01T00:00:00Z'
      };
      
      // Set token in localStorage mock
      localStorageMock['access_token'] = 'test-token';
      mockedApiService.getCurrentUser.mockResolvedValueOnce(mockUser);
      
      const TestComponent = () => {
        const { user, logout, isAuthenticated } = useAuth();
        return (
          <div>
            <div data-testid="auth-status">{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
            <div data-testid="username">{user?.username || 'no-user'}</div>
            <button onClick={logout}>Logout</button>
          </div>
        );
      };
      
      render(
        <BrowserRouter>
          <AuthProvider>
            <TestComponent />
          </AuthProvider>
        </BrowserRouter>
      );
      
      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
      });
      
      // Click logout
      const logoutButton = screen.getByText('Logout');
      fireEvent.click(logoutButton);
      
      // Check logout effects
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
      expect(screen.getByTestId('auth-status').textContent).toBe('not-authenticated');
      expect(screen.getByTestId('username').textContent).toBe('no-user');
    });
  });
});