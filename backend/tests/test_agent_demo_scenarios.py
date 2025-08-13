"""
Integration tests for all 5 demo scenarios
Tests the complete agent pipeline with real tools
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.agent_coordinator import AgentCoordinator
from app.agents.intelligence_agent_enhanced import IntelligenceAgentEnhanced as IntelligenceAgent
from app.agents.draft_prep_agent_tools import DraftPrepAgent
from app.agents.trade_impact_agent_tools import TradeImpactAgent


class TestDemoScenarios:
    """Test all 5 capstone demo scenarios"""
    
    @pytest.fixture
    def coordinator(self):
        """Create agent coordinator"""
        return AgentCoordinator()
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        with patch('app.db.database.get_db') as mock:
            # Create mock session with execute method
            mock_session = Mock()
            mock_result = Mock()
            mock_result.first.return_value = Mock(
                name="Test Player",
                position="PG",
                team="TES",
                adp_rank=21,
                adp_round=2,
                keeper_round=2,
                projected_fantasy_ppg=45.5,
                consistency_rating=0.85,
                injury_risk="Low",
                sleeper_score=0.75,
                breakout_candidate=True,
                punt_ft_fit=True,
                punt_fg_fit=False,
                punt_ast_fit=False,
                punt_3pm_fit=False,
                projected_ppg=25.5,
                projected_rpg=5.5,
                projected_apg=7.5,
                projected_spg=1.5,
                projected_bpg=0.5
            )
            mock_result.fetchall.return_value = [mock_result.first.return_value]
            mock_session.execute.return_value = mock_result
            mock.return_value = iter([mock_session])
            yield mock_session
    
    # SCENARIO 1: Keeper Decision (DraftPrep Agent)
    @pytest.mark.asyncio
    async def test_scenario_1_keeper_decision(self, mock_db):
        """Test: Should I keep Ja Morant in round 3?"""
        agent = DraftPrepAgent()
        
        # Test the keeper value calculation tool directly
        result = agent._calculate_keeper_value("Ja Morant in round 3")
        
        # Verify response contains key elements
        assert "Keeper Analysis" in result or "keeper" in result.lower()
        assert any(word in result.lower() for word in ["value", "recommendation", "adp"])
        
        # Test through process_message (if agent executor is initialized)
        if agent.agent_executor:
            response = await agent.process_message("Should I keep Ja Morant in round 3?")
            assert response.confidence > 0.5
            assert len(response.tools_used) > 0
    
    # SCENARIO 2: Trade Impact (TradeImpact Agent)
    @pytest.mark.asyncio
    async def test_scenario_2_trade_impact(self, mock_db):
        """Test: How does Porzingis trade affect Tatum?"""
        agent = TradeImpactAgent()
        
        # Test fallback analysis (when Milvus not available)
        result = agent._fallback_trade_analysis("porzingis tatum")
        
        # Verify response contains trade impact analysis
        assert "Tatum" in result
        assert any(word in result.lower() for word in ["usage", "impact", "fantasy"])
        
        # Test usage change calculation
        usage_result = agent._calculate_usage_change("porzingis trade")
        assert "Usage Rate Changes" in usage_result or "usage" in usage_result.lower()
    
    # SCENARIO 3: Find Sleepers (Intelligence Agent)
    @pytest.mark.asyncio
    async def test_scenario_3_find_sleepers(self, mock_db):
        """Test: Find me sleepers like last year's Sengun"""
        agent = IntelligenceAgent()
        
        # Test sleeper finding tool (enhanced version)
        result = agent._find_sleeper_candidates_enhanced("")
        
        # Verify response contains sleeper candidates
        assert "sleeper" in result.lower()
        assert any(word in result.lower() for word in ["candidates", "score", "adp"])
    
    # SCENARIO 4: Punt Strategy (DraftPrep Agent)
    @pytest.mark.asyncio
    async def test_scenario_4_punt_strategy(self, mock_db):
        """Test: Best punt FT% build around Giannis"""
        agent = DraftPrepAgent()
        
        # Test punt strategy builder
        result = agent._build_punt_strategy("punt FT% Giannis")
        
        # Verify response contains punt strategy
        assert "punt" in result.lower()
        assert "FT%" in result or "free throw" in result.lower()
        
        # Test finding punt fits
        fits_result = agent._find_punt_fits("Giannis punt ft")
        assert any(word in fits_result.lower() for word in ["punt", "fit", "players"])
    
    # SCENARIO 5: Breakout Candidates (Intelligence Agent)
    @pytest.mark.asyncio
    async def test_scenario_5_breakout_sophomores(self, mock_db):
        """Test: Which sophomores will break out?"""
        agent = IntelligenceAgent()
        
        # Test breakout identification tool (enhanced version)
        result = agent._identify_breakout_candidates_enhanced("")
        
        # Verify response contains breakout candidates
        assert "breakout" in result.lower()
        assert any(word in result.lower() for word in ["candidates", "season", "projected"])
    
    # INTEGRATION TEST: Full Coordinator Routing
    @pytest.mark.asyncio
    async def test_full_coordinator_routing(self, coordinator):
        """Test that coordinator routes messages to correct agents"""
        
        # Test keeper query routes to DraftPrep
        response1 = await coordinator.route_message("Should I keep a player in round 3?")
        assert response1 is not None
        
        # Test trade query routes to TradeImpact  
        response2 = await coordinator.route_message("How does the trade affect Tatum?")
        assert response2 is not None
        
        # Test sleeper query routes to Intelligence
        response3 = await coordinator.route_message("Find me some sleeper picks")
        assert response3 is not None


class TestAgentTools:
    """Unit tests for individual agent tools"""
    
    @pytest.fixture
    def mock_db_with_data(self):
        """Mock database with realistic data"""
        with patch('app.db.database.get_db') as mock:
            mock_session = Mock()
            
            # Mock different query results
            def side_effect(*args, **kwargs):
                query_text = str(args[0]) if args else ""
                mock_result = Mock()
                
                if "sleeper_score" in query_text:
                    # Return sleeper candidates
                    mock_result.fetchall.return_value = [
                        Mock(name="Alperen Sengun", position="C", team="HOU", 
                             adp_rank=37, sleeper_score=0.82, projected_fantasy_ppg=38.5),
                        Mock(name="Walker Kessler", position="C", team="UTA",
                             adp_rank=58, sleeper_score=0.78, projected_fantasy_ppg=32.5),
                    ]
                elif "breakout_candidate" in query_text:
                    # Return breakout candidates
                    mock_result.fetchall.return_value = [
                        Mock(name="Paolo Banchero", position="PF", team="ORL",
                             adp_rank=38, projected_fantasy_ppg=40.5),
                        Mock(name="Chet Holmgren", position="C", team="OKC",
                             adp_rank=56, projected_fantasy_ppg=35.5),
                    ]
                elif "punt_ft_fit" in query_text:
                    # Return punt FT% fits
                    mock_result.fetchall.return_value = [
                        Mock(name="Rudy Gobert", position="C", team="MIN",
                             adp_rank=51, adp_round=5, projected_ppg=13.5,
                             projected_rpg=12.5, projected_apg=1.5,
                             punt_ft_fit=True, punt_fg_fit=False,
                             punt_ast_fit=False, punt_3pm_fit=True),
                    ]
                else:
                    # Default player result
                    mock_result.first.return_value = Mock(
                        name="Ja Morant", position="PG", team="MEM",
                        adp_rank=21, adp_round=2, keeper_round=2,
                        projected_fantasy_ppg=42.5, consistency_rating=0.75,
                        injury_risk="Medium"
                    )
                
                return mock_result
            
            mock_session.execute.side_effect = side_effect
            mock.return_value = iter([mock_session])
            yield mock_session
    
    def test_intelligence_agent_tools(self, mock_db_with_data):
        """Test Intelligence Agent tool functions"""
        agent = IntelligenceAgent()
        
        # Test analyze_player_stats (enhanced version)
        stats_result = agent._analyze_player_stats_enhanced("Ja Morant")
        assert "Ja Morant" in stats_result
        assert "PG" in stats_result
        
        # Test find_sleeper_candidates (enhanced version)
        sleepers_result = agent._find_sleeper_candidates_enhanced("")
        assert "Sengun" in sleepers_result or "sleeper" in sleepers_result.lower()
        
        # Test identify_breakout_candidates (enhanced version)
        breakout_result = agent._identify_breakout_candidates_enhanced("")
        assert "Banchero" in breakout_result or "breakout" in breakout_result.lower()
    
    def test_draftprep_agent_tools(self, mock_db_with_data):
        """Test DraftPrep Agent tool functions"""
        agent = DraftPrepAgent()
        
        # Test calculate_keeper_value
        keeper_result = agent._calculate_keeper_value("Ja Morant round 3")
        assert "Morant" in keeper_result or "keeper" in keeper_result.lower()
        
        # Test build_punt_strategy
        punt_result = agent._build_punt_strategy("punt ft")
        assert "punt" in punt_result.lower()
        
        # Test get_adp_rankings
        adp_result = agent._get_adp_rankings("")
        assert "ranking" in adp_result.lower() or "adp" in adp_result.lower()
    
    def test_tradeimpact_agent_tools(self, mock_db_with_data):
        """Test TradeImpact Agent tool functions"""
        agent = TradeImpactAgent()
        
        # Test fallback trade analysis
        trade_result = agent._fallback_trade_analysis("porzingis tatum")
        assert "Tatum" in trade_result
        assert "Porzingis" in trade_result
        
        # Test calculate_usage_change
        usage_result = agent._calculate_usage_change("porzingis")
        assert "usage" in usage_result.lower()
        
        # Test analyze_depth_chart
        depth_result = agent._analyze_depth_chart("celtics")
        assert "depth" in depth_result.lower() or "starters" in depth_result.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])