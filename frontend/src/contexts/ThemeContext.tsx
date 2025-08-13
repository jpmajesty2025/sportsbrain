import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, CssBaseline } from '@mui/material';
import { lightTheme, darkTheme } from '../theme/theme';
import { useAuth } from './AuthContext';
import apiService from '../services/api';
import { UserPreferences } from '../types/preferences';

interface ThemeContextType {
  isDarkMode: boolean;
  toggleTheme: () => void;
  isLoading: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    // Check localStorage first for non-authenticated users
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'dark';
  });
  const [isLoading, setIsLoading] = useState(false);

  // Load theme preference from backend when user logs in
  useEffect(() => {
    if (isAuthenticated && user) {
      setIsLoading(true);
      apiService.getUserPreferences()
        .then((preferences: UserPreferences) => {
          setIsDarkMode(preferences.theme_mode === 'dark');
          localStorage.setItem('theme', preferences.theme_mode);
        })
        .catch((error: Error) => {
          console.error('Failed to load theme preference:', error);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isAuthenticated, user]);

  const toggleTheme = async () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('theme', newMode ? 'dark' : 'light');

    // If authenticated, save to backend
    if (isAuthenticated) {
      try {
        await apiService.updateUserPreferences({
          theme_mode: newMode ? 'dark' : 'light'
        });
      } catch (error) {
        console.error('Failed to save theme preference:', error);
        // Revert on error
        setIsDarkMode(!newMode);
        localStorage.setItem('theme', !newMode ? 'dark' : 'light');
      }
    }
  };

  const theme = isDarkMode ? darkTheme : lightTheme;

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme, isLoading }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};