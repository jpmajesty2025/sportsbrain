import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from './Login';
import { AuthProvider } from '../contexts/AuthContext';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Mock the auth context
jest.mock('../contexts/AuthContext', () => ({
  ...jest.requireActual('../contexts/AuthContext'),
  useAuth: jest.fn(),
}));

// Mock navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

const mockLogin = jest.fn();

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
};

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      user: null,
      loading: false,
      isAuthenticated: false,
    });
  });

  describe('Rendering', () => {
    it('should render login form', () => {
      renderLogin();
      
      // Use more specific queries to avoid multiple matches
      expect(screen.getByRole('heading', { name: 'Login' })).toBeInTheDocument();
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
    });

    it('should render register link', () => {
      renderLogin();
      
      const registerLink = screen.getByRole('link', { name: /register here/i });
      expect(registerLink).toBeInTheDocument();
      expect(registerLink).toHaveAttribute('href', '/register');
    });
  });

  describe('Form Interaction', () => {
    it('should update username field on input', () => {
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      
      expect(usernameInput.value).toBe('testuser');
    });

    it('should update password field on input', () => {
      renderLogin();
      
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      
      expect(passwordInput.value).toBe('testpass123');
    });

    it('should require both fields to be filled', () => {
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      
      expect(usernameInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
    });
  });

  describe('Form Submission', () => {
    it('should call login with credentials on successful submission', async () => {
      mockLogin.mockResolvedValueOnce(undefined);
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'testpass123',
        });
      });
    });

    it('should navigate to dashboard on successful login', async () => {
      mockLogin.mockResolvedValueOnce(undefined);
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass123' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should display error message on login failure', async () => {
      const errorMessage = 'Invalid credentials';
      mockLogin.mockRejectedValueOnce({
        response: { data: { detail: errorMessage } },
      });
      
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should display generic error message when no detail provided', async () => {
      mockLogin.mockRejectedValueOnce(new Error('Network error'));
      
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Login failed')).toBeInTheDocument();
      });
    });
  });

  describe('Loading State', () => {
    it('should disable inputs during login', async () => {
      let resolveLogin: () => void;
      mockLogin.mockImplementation(() => new Promise(resolve => {
        resolveLogin = () => resolve(undefined);
      }));
      
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(usernameInput).toBeDisabled();
        expect(passwordInput).toBeDisabled();
        expect(submitButton).toBeDisabled();
      });
      
      // Clean up
      await act(async () => {
        resolveLogin!();
      });
    });

    it('should show loading spinner during login', async () => {
      let resolveLogin: () => void;
      mockLogin.mockImplementation(() => new Promise(resolve => {
        resolveLogin = () => resolve(undefined);
      }));
      
      renderLogin();
      
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /login/i });
      
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'testpass' } });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });
      
      await waitFor(() => {
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
      
      // Clean up
      await act(async () => {
        resolveLogin!();
      });
    });
  });
});