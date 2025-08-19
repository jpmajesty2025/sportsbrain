import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Paper,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Fade,
  LinearProgress,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  SwapHoriz as SwapHorizIcon,
  Send as SendIcon,
  Psychology as PsychologyIcon,
  EmojiEvents as TrophyIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import apiService from '../services/api';
import { Player, Game } from '../types';

interface AgentCard {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  examples: string[];
  isBeta?: boolean;
}

const agents: AgentCard[] = [
  {
    id: 'intelligence',
    name: 'Intelligence Agent',
    description: 'Analytics, predictions, sleepers, and breakout candidates',
    icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
    color: '#3B82F6',
    examples: [
      'Find sleeper centers like Alperen Sengun',
      'Which sophomores will break out in 2025-26?',
      'Is Gary Trent Jr. worth drafting?',
      'Compare Scottie Barnes vs Paolo Banchero'
    ]
  },
  {
    id: 'draft_prep',
    name: 'DraftPrep Agent',
    description: 'Keeper decisions, ADP analysis, and punt strategies',
    icon: <TrophyIcon sx={{ fontSize: 40 }} />,
    color: '#10B981',
    examples: [
      'Should I keep Ja Morant in round 3?',
      'Build a punt FT% team around Giannis',
      'Who are the best value picks in rounds 3-5?',
      'Is LaMelo Ball worth keeping in round 4?'
    ]
  },
  {
    id: 'trade_impact',
    name: 'TradeImpact Agent',
    description: 'Analysis of recent NBA trades and their fantasy impact',
    icon: <SwapHorizIcon sx={{ fontSize: 40 }} />,
    color: '#F59E0B',
    examples: [
      'How does Porzingis trade affect Tatum?',
      'Which players benefited from the Lillard to Bucks trade?',
      'What was the fantasy impact of the Porzingis trade?',
      'How did Lillard trade affect Giannis usage rate?'
    ]
  }
];

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [selectedAgent, setSelectedAgent] = useState<string>('intelligence');
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<string | null>(null);

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgent(agentId);
    setResponse(null);
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse(null);
    try {
      // Map agent IDs to backend agent names
      const agentMap: { [key: string]: string } = {
        'intelligence': 'IntelligenceAgent',
        'draft_prep': 'DraftPrepAgent',
        'trade_impact': 'TradeImpactAgent'
      };
      
      const agentName = agentMap[selectedAgent];
      const result = await apiService.querySecureAgent(agentName, query);
      
      // The response has a 'content' field from the AgentQueryResponse model
      if (result && result.content) {
        setResponse(result.content);
      } else if (result && result.response) {
        setResponse(result.response);
      } else if (result && result.message) {
        setResponse(result.message);
      } else {
        setResponse('Received empty response from agent');
      }
    } catch (error: any) {
      console.error('Error querying agent:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to get response from agent';
      setResponse(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedAgentData = agents.find(a => a.id === selectedAgent);


  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h3" gutterBottom fontWeight="bold">
            SportsBrain AI Assistant
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Welcome back, {user?.username || 'User'}! Select an agent to get started.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip 
            label="2025-26 Season" 
            color="primary" 
            variant="outlined"
            icon={<TimelineIcon />}
          />
          <ThemeToggle />
        </Box>
      </Box>
      {/* Agent Selection Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {agents.map((agent) => (
          <Grid item xs={12} md={4} key={agent.id}>
            <Card
              sx={{
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                border: selectedAgent === agent.id ? `3px solid ${agent.color}` : '1px solid',
                borderColor: selectedAgent === agent.id ? agent.color : 'divider',
                transform: selectedAgent === agent.id ? 'scale(1.02)' : 'scale(1)',
                '&:hover': {
                  transform: 'scale(1.02)',
                  boxShadow: 6,
                },
              }}
              onClick={() => handleAgentSelect(agent.id)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar
                    sx={{
                      bgcolor: agent.color,
                      width: 56,
                      height: 56,
                      mr: 2,
                    }}
                  >
                    {agent.icon}
                  </Avatar>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {agent.name}
                      </Typography>
                      {agent.isBeta && (
                        <Chip
                          label="BETA"
                          size="small"
                          sx={{
                            bgcolor: '#f39c12',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '0.7rem'
                          }}
                        />
                      )}
                    </Box>
                    {selectedAgent === agent.id && (
                      <Chip
                        label="Active"
                        size="small"
                        color="success"
                        sx={{ mt: 0.5 }}
                      />
                    )}
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {agent.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Query Interface */}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 2,
          background: (theme) =>
            theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%)'
              : 'linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%)',
        }}
      >
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="h5" fontWeight="bold">
              Ask {selectedAgentData?.name}
            </Typography>
            {selectedAgentData?.isBeta && (
              <Chip
                label="BETA"
                size="small"
                sx={{
                  bgcolor: '#f39c12',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.7rem'
                }}
              />
            )}
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Try one of these examples or ask your own question:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {selectedAgentData?.examples.map((example, index) => (
              <Chip
                key={index}
                label={example}
                onClick={() => handleExampleClick(example)}
                sx={{
                  cursor: 'pointer',
                  '&:hover': {
                    bgcolor: selectedAgentData.color,
                    color: 'white',
                  },
                }}
              />
            ))}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <TextField
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            placeholder="Type your question here..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '&.Mui-focused fieldset': {
                  borderColor: selectedAgentData?.color,
                },
              },
            }}
          />
          <Button
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={!query.trim() || isLoading}
            sx={{
              bgcolor: selectedAgentData?.color,
              '&:hover': {
                bgcolor: selectedAgentData?.color,
                filter: 'brightness(0.9)',
              },
              minWidth: 120,
            }}
            endIcon={<SendIcon />}
          >
            Send
          </Button>
        </Box>

        {/* Loading Indicator */}
        {isLoading && <LinearProgress sx={{ mb: 2 }} />}

        {/* Response Area */}
        {response && (
          <Fade in={true}>
            <Paper
              sx={{
                p: 3,
                bgcolor: (theme) =>
                  theme.palette.mode === 'dark' ? 'background.paper' : 'grey.50',
                borderLeft: `4px solid ${selectedAgentData?.color}`,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar
                  sx={{
                    bgcolor: selectedAgentData?.color,
                    width: 32,
                    height: 32,
                    mr: 1,
                  }}
                >
                  {selectedAgentData?.icon}
                </Avatar>
                <Typography variant="subtitle2" fontWeight="bold">
                  {selectedAgentData?.name} Response
                </Typography>
              </Box>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {response}
              </Typography>
            </Paper>
          </Fade>
        )}
      </Paper>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Queries Today
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                12
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Active League
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                H2H 9-Cat
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Saved Players
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                24
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Days to Draft
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                45
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;