import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
} from '@mui/material';
import { Sports, TrendingUp, Chat, Analytics } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import { Player, Game } from '../types';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [players, setPlayers] = useState<Player[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [playersData, gamesData] = await Promise.all([
        apiService.getPlayers(0, 5),
        apiService.getGames(0, 5),
      ]);
      setPlayers(playersData);
      setGames(gamesData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const agentCards = [
    {
      title: 'Analytics Agent',
      description: 'Get detailed statistical analysis and insights',
      icon: <Analytics fontSize="large" />,
      color: '#1976d2',
      onClick: () => navigate('/agents/analytics'),
    },
    {
      title: 'Prediction Agent',
      description: 'AI-powered game and performance predictions',
      icon: <TrendingUp fontSize="large" />,
      color: '#388e3c',
      onClick: () => navigate('/agents/prediction'),
    },
    {
      title: 'Chat Agent',
      description: 'Ask questions about sports and get instant answers',
      icon: <Chat fontSize="large" />,
      color: '#f57c00',
      onClick: () => navigate('/agents/chat'),
    },
  ];

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom>
        Welcome back, {user?.full_name || user?.username}!
      </Typography>

      <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 4, mb: 2 }}>
        AI Agents
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {agentCards.map((agent, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              sx={{ 
                cursor: 'pointer', 
                transition: 'transform 0.2s',
                '&:hover': { transform: 'translateY(-4px)' }
              }}
              onClick={agent.onClick}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box sx={{ color: agent.color, mb: 2 }}>
                  {agent.icon}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {agent.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {agent.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                Recent Players
              </Typography>
              {loading ? (
                <Typography>Loading...</Typography>
              ) : players.length > 0 ? (
                <Box>
                  {players.map((player) => (
                    <Box key={player.id} sx={{ mb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body1">{player.name}</Typography>
                      <Chip label={player.team || 'No Team'} size="small" />
                    </Box>
                  ))}
                  <Button 
                    variant="text" 
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/players')}
                  >
                    View All Players
                  </Button>
                </Box>
              ) : (
                <Typography color="text.secondary">No players found</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h3" gutterBottom>
                Recent Games
              </Typography>
              {loading ? (
                <Typography>Loading...</Typography>
              ) : games.length > 0 ? (
                <Box>
                  {games.map((game) => (
                    <Box key={game.id} sx={{ mb: 1 }}>
                      <Typography variant="body1">
                        {game.away_team} @ {game.home_team}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(game.date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  ))}
                  <Button 
                    variant="text" 
                    sx={{ mt: 2 }}
                    onClick={() => navigate('/games')}
                  >
                    View All Games
                  </Button>
                </Box>
              ) : (
                <Typography color="text.secondary">No games found</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;