import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';

const ApiConfig: React.FC = () => {
  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const nodeEnv = process.env.NODE_ENV;
  const isProduction = nodeEnv === 'production';
  
  // Only show in development or if there's an issue
  if (isProduction && apiUrl !== 'http://localhost:8000') {
    return null;
  }

  return (
    <Paper 
      sx={{ 
        p: 2, 
        m: 2, 
        backgroundColor: apiUrl.includes('localhost') ? '#fff3cd' : '#d4edda',
        border: '1px solid',
        borderColor: apiUrl.includes('localhost') ? '#ffc107' : '#28a745'
      }}
    >
      <Typography variant="h6" gutterBottom>
        API Configuration Debug
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Box>
          <Typography variant="body2" component="span">
            API URL: 
          </Typography>
          <Chip 
            label={apiUrl} 
            size="small" 
            color={apiUrl.includes('localhost') ? 'warning' : 'success'}
            sx={{ ml: 1 }}
          />
        </Box>
        <Box>
          <Typography variant="body2" component="span">
            Environment: 
          </Typography>
          <Chip 
            label={nodeEnv} 
            size="small" 
            color={isProduction ? 'primary' : 'default'}
            sx={{ ml: 1 }}
          />
        </Box>
        {apiUrl.includes('localhost') && (
          <Typography variant="body2" color="error">
            ⚠️ Using localhost URL - REACT_APP_API_URL not set during build
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ApiConfig;