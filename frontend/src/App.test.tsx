import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock react-query
jest.mock('react-query', () => ({
  QueryClient: jest.fn(() => ({})),
  QueryClientProvider: ({ children }: any) => children,
}));

// Mock the API service to prevent real API calls
jest.mock('./services/api', () => ({
  __esModule: true,
  default: {
    getCurrentUser: jest.fn().mockRejectedValue(new Error('No user')),
    login: jest.fn(),
    register: jest.fn(),
  },
}));

describe('App Component', () => {
  it('should render without crashing', () => {
    render(<App />);
    
    // App should render something (either login page or main content)
    expect(document.body).not.toBeEmptyDOMElement();
  });

  it('should show login page when not authenticated', () => {
    render(<App />);
    
    // Should show login form when not authenticated
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });
});