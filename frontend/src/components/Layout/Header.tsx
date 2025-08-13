import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
} from '@mui/material';
import { AccountCircle, Sports, Brightness4, Brightness7 } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/');
  };

  const handleProfile = () => {
    navigate('/profile');
    handleClose();
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Sports sx={{ mr: 2 }} />
        <Typography
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          SportsBrain
        </Typography>

        <IconButton 
          sx={{ ml: 1 }} 
          onClick={toggleTheme} 
          color="inherit"
          aria-label="toggle theme"
        >
          {isDarkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>

        {isAuthenticated ? (
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleProfile}>Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </div>
        ) : (
          <div>
            <Button color="inherit" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button color="inherit" onClick={() => navigate('/register')}>
              Register
            </Button>
          </div>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;