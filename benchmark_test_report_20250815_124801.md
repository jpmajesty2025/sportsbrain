# SportsBrain Agent Benchmark Test Report
Generated: 2025-08-15T12:48:01.956312

## Summary
- Total Tests: 20
- Successful: 20
- Timeouts: 0
- Errors: 0

## Detailed Results

### Intelligence Agent

#### Test 1: Find sleeper candidates

**Status**: success
**Response Time**: 5.91s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 128 chars):
```
The find_sleepers function provided detailed analysis and recommendations for sleeper candidates for the upcoming fantasy draft.
```

**Raw Tool Outputs** (1 calls):

*Tool*: Intelligence.find_sleepers
*Output Length*: 7420 chars
```
======================================================================
**2024-25 FANTASY BASKETBALL SLEEPER CANDIDATES**
Complete Statistical Analysis with Shot Distributions
======================================================================

#1. **Gary Trent Jr.**
----------------------------------------
Position: SG | Team: MIL | Age: N/A
📊 SLEEPER SCORE: 0.90/1.00
📍 ADP: #140 (Round 12)

📈 PROJECTIONS:
  • Points: 10.5 PPG
  • Rebounds: 3.3 RPG
  • Assists: 1.9 APG
  • Fantasy Points: 21.
... [truncated]
```

**Analysis**:
- Tool output total: 7420 chars
- Agent response: 128 chars
- Compression ratio: 1.73%
- [WARN] Significant summarization detected

---

#### Test 2: What are Scoot Henderson's stats?

**Status**: success
**Response Time**: 6.43s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 51 chars):
```
Agent stopped due to iteration limit or time limit.
```

**Raw Tool Outputs** (3 calls):

*Tool*: Intelligence.analyze_player_stats
*Output Length*: 80 chars
```
Error analyzing player: '>' not supported between instances of 'str' and 'float'
```

*Tool*: Intelligence.analyze_player_stats
*Output Length*: 80 chars
```
Error analyzing player: '>' not supported between instances of 'str' and 'float'
```

**Analysis**:
- Tool output total: 240 chars
- Agent response: 51 chars
- Compression ratio: 21.25%
- [WARN] Significant summarization detected

---

#### Test 3: Compare Scottie Barnes and Paolo Banchero

**Status**: success
**Response Time**: 4.42s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 51 chars):
```
Agent stopped due to iteration limit or time limit.
```

**Raw Tool Outputs** (3 calls):

*Tool*: Intelligence.compare_players
*Output Length*: 64 chars
```
Please provide two players to compare (e.g., 'LeBron vs Durant')
```

*Tool*: Intelligence.compare_players
*Output Length*: 64 chars
```
Please provide two players to compare (e.g., 'LeBron vs Durant')
```

**Analysis**:
- Tool output total: 192 chars
- Agent response: 51 chars
- Compression ratio: 26.56%
- [WARN] Significant summarization detected

---

#### Test 4: Is Gary Trent Jr. worth drafting?

**Status**: success
**Response Time**: 0.27s
**Routing**: BYPASS (direct to tool)
**Tools Used**: evaluate_player_draft_value

**Agent Response** (length: 329 chars):
```
**Gary Trent Jr. Draft Analysis**

**Verdict**: EXCELLENT VALUE - Definitely worth drafting!
• **Sleeper Score**: 0.90/1.00
• **ADP**: #140 (Round 12)
• **Projected Fantasy PPG**: 21.2
• **Consistency**: 0.5819156961477759
• **Injury Risk**: Low

**Recommendation**: Target Gary Trent Jr. 1-2 rounds before their ADP of Round 12.
```

---

#### Test 5: Is Paolo Banchero a breakout candidate?

**Status**: success
**Response Time**: 0.28s
**Routing**: BYPASS (direct to tool)
**Tools Used**: identify_breakouts

**Agent Response** (length: 174 chars):
```
Yes, Paolo Banchero is a breakout candidate for 2024-25. They are expected to significantly improve their fantasy production based on age, role expansion, and team situation.
```

---

#### Test 6: Who are the most undervalued shooting guards for fantasy?

**Status**: success
**Response Time**: 2.92s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 161 chars):
```
The most undervalued shooting guards for fantasy in the 2024-25 season are Gary Trent Jr., Kentavious Caldwell-Pope, Austin Reaves, Collin Sexton, and Josh Hart.
```

**Raw Tool Outputs** (1 calls):

*Tool*: Intelligence.find_sleepers
*Output Length*: 3941 chars
```
======================================================================
**2024-25 SHOOTING GUARD SLEEPER CANDIDATES**
Complete Statistical Analysis with Shot Distributions
======================================================================

#1. **Gary Trent Jr.**
----------------------------------------
Position: SG | Team: MIL | Age: N/A
📊 SLEEPER SCORE: 0.90/1.00
📍 ADP: #140 (Round 12)

📈 PROJECTIONS:
  • Points: 10.5 PPG
  • Rebounds: 3.3 RPG
  • Assists: 1.9 APG
  • Fantasy Points: 21.2 pe
... [truncated]
```

**Analysis**:
- Tool output total: 3941 chars
- Agent response: 161 chars
- Compression ratio: 4.09%
- [WARN] Significant summarization detected

---

#### Test 7: Which centers are sleepers?

**Status**: success
**Response Time**: 4.14s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 160 chars):
```
The sleeper candidates for centers in the 2024-25 fantasy draft are Daniel Gafford, Naz Reid, Isaiah Stewart, Jakob Poeltl, Mitchell Robinson, and Jusuf Nurkic.
```

**Raw Tool Outputs** (1 calls):

*Tool*: Intelligence.find_sleepers
*Output Length*: 4607 chars
```
======================================================================
**2024-25 CENTER SLEEPER CANDIDATES**
Complete Statistical Analysis with Shot Distributions
======================================================================

#1. **Daniel Gafford**
----------------------------------------
Position: C | Team: DAL | Age: N/A
📊 SLEEPER SCORE: 0.85/1.00
📍 ADP: #111 (Round 10)

📈 PROJECTIONS:
  • Points: 13.6 PPG
  • Rebounds: 4.2 RPG
  • Assists: 1.4 APG
  • Fantasy Points: 24.2 per game

🏀
... [truncated]
```

**Analysis**:
- Tool output total: 4607 chars
- Agent response: 160 chars
- Compression ratio: 3.47%
- [WARN] Significant summarization detected

---

#### Test 8: Find me high-upside guards going late in drafts

**Status**: success
**Response Time**: 2.96s
**Routing**: Through agent
**Tools Used**: analyze_player_stats, find_sleepers, identify_breakouts, project_performance, compare_players, analyze_consistency, evaluate_player_draft_value

**Agent Response** (length: 350 chars):
```
Based on the detailed analysis and projections, the top high-upside guards going late in drafts for the 2024-25 fantasy season are Gary Trent Jr., Scoot Henderson, Kentavious Caldwell-Pope, Austin Reaves, Amen Thompson, Collin Sexton, Josh Hart, and Cason Wallace. These players provide excellent value and have the potential to outperform their ADP.
```

**Raw Tool Outputs** (1 calls):

*Tool*: Intelligence.find_sleepers
*Output Length*: 6032 chars
```
======================================================================
**2024-25 SHOOTING GUARD SLEEPER CANDIDATES**
Complete Statistical Analysis with Shot Distributions
======================================================================

#1. **Gary Trent Jr.**
----------------------------------------
Position: SG | Team: MIL | Age: N/A
📊 SLEEPER SCORE: 0.90/1.00
📍 ADP: #140 (Round 12)

📈 PROJECTIONS:
  • Points: 10.5 PPG
  • Rebounds: 3.3 RPG
  • Assists: 1.9 APG
  • Fantasy Points: 21.2 pe
... [truncated]
```

**Analysis**:
- Tool output total: 6032 chars
- Agent response: 350 chars
- Compression ratio: 5.80%
- [WARN] Significant summarization detected

---

### DraftPrep Agent

#### Test 1: Should I keep Ja Morant in round 3?

**Status**: success
**Response Time**: 0.28s
**Routing**: Through agent
**Tools Used**: calculate_keeper_value

**Agent Response** (length: 682 chars):
```

**Keeper Analysis for Ja Morant**

[STATS] **Player Info**:
- Position: PG | Team: MEM
- ADP: #21 (Round 2)
- Typical Keeper Round: 1
- Your Keeper Round: 3

[TARGET] **Recommendation**: GOOD VALUE - Worth keeping

[VALUE] **Value Analysis**:
- You'd be getting a Round 2 player in Round 3
- That's a 1 round discount!
- Projected Fantasy PPG: 37.2
- Consistency: 0.87 | Injury Risk: Medium

[STRATEGY] **Strategic Insights**:
- Opportunity Cost: Moderate - standard keeper play
- Alternative Strate
... [truncated]
```

---

#### Test 2: Build a punt FT% team

**Status**: success
**Response Time**: 0.28s
**Routing**: Through agent
**Tools Used**: build_punt_strategy

**Agent Response** (length: 1080 chars):
```
[TARGET] **Punt FT% Strategy Build**:

**Core Targets** (Players who excel despite weak FT%):

**Early Rounds (1-3)**:
- Nikola Jokic (C) - Round 1
  Stats: 29.1 PPG, 6.1 RPG, 2.1 APG
- Karl-Anthony Towns (C) - Round 2
  Stats: 18.7 PPG, 8.2 RPG, 3.0 APG

**Mid Rounds (4-7)**:
- Myles Turner (C) - Round 5
- Nikola Vucevic (C) - Round 5
- Chet Holmgren (C) - Round 5
- Nic Claxton (C) - Round 5
- Clint Capela (C) - Round 6
- Brook Lopez (C) - Round 6

**Late Round Values (8+)**:
- Deandre Ayton (C
... [truncated]
```

---

#### Test 3: What's LaMelo Ball's ADP?

**Status**: success
**Response Time**: 0.28s
**Routing**: Through agent
**Tools Used**: analyze_adp_value

**Agent Response** (length: 815 chars):
```
[TARGET] **Top ADP Value Picks for 2024-25**:

1. **Julius Randle** (PF, MIN)
   - ADP: #24 (Round 2)
   - Projected: 44.7 FP/game
   - Value Score: 152.72

2. **Jimmy Butler** (SF, MIA)
   - ADP: #20 (Round 2)
   - Projected: 36.0 FP/game
   - Value Score: 147.60

3. **Ja Morant** (PG, MEM)
   - ADP: #21 (Round 2)
   - Projected: 37.2 FP/game
   - Value Score: 145.26

4. **Pascal Siakam** (PF, IND)
   - ADP: #25 (Round 3)
   - Projected: 43.4 FP/game
   - Value Score: 142.35

5. **De'Aaron Fox*
... [truncated]
```

---

#### Test 4: Build me a complete draft strategy for pick 12

**Status**: success
**Response Time**: 0.00s
**Routing**: Through agent

**Agent Response** (length: 728 chars):
```
For comprehensive draft strategy, I recommend:

1. **Use the mock draft tool** to see available players at your pick
2. **Check keeper values** for any keeper decisions
3. **Review punt strategies** if you want to build around specific categories

Example queries:
- "Show mock draft for pick 12" - See available players
- "Build punt FT% team" - Get category-specific strategy
- "Should I keep Giannis in round 2?" - Keeper decisions

For pick-specific strategy, consider:
- Picks 1-3: Elite tier (J
... [truncated]
```

---

#### Test 5: What's the best strategy if I keep both Giannis and Embiid?

**Status**: success
**Response Time**: 1.24s
**Routing**: Through agent
**Tools Used**: calculate_keeper_value

**Agent Response** (length: 137 chars):
```

**Giannis Antetokounmpo Keeper Info**:
- ADP: #2 (Round 1)
- Recommended Keeper Round: 1 or later
- Projected: 57.4 fantasy points/game

```

---

#### Test 6: Best sleepers in rounds 8-10

**Status**: success
**Response Time**: 4.50s
**Routing**: Through agent
**Tools Used**: calculate_keeper_value, analyze_adp_value, get_adp_rankings, build_punt_strategy, find_punt_fits, simulate_draft_pick

**Agent Response** (length: 132 chars):
```
Shai Gilgeous-Alexander and Damian Lillard are the best sleepers to target in rounds 8-10 for the 2024-25 fantasy basketball season.
```

**Raw Tool Outputs** (1 calls):

*Tool*: DraftPrep.simulate_draft_pick
*Output Length*: 729 chars
```
[DICE] **Mock Draft - Best Available (Picks 1-15)**:

**Pick 1: Nikola Jokic** (C, DEN)
- Projected: 48.2 FP/game
- Consistency: 0.80

**Pick 2: Giannis Antetokounmpo** (PF, MIL)
- Projected: 57.4 FP/game
- Consistency: 0.78

**Pick 3: Luka Doncic** (PG, DAL)
- Projected: 59.5 FP/game
- Consistency: 0.72

**Pick 4: Joel Embiid** (C, PHI)
- Projected: 54.2 FP/game
- Consistency: 0.77

**Pick 5: Jayson Tatum** (SF, BOS)
- Projected: 49.6 FP/game
- Consistency: 0.83

**Pick 6: Stephen Curry** (PG, 
... [truncated]
```

**Analysis**:
- Tool output total: 729 chars
- Agent response: 132 chars
- Compression ratio: 18.11%
- [WARN] Significant summarization detected

---

#### Test 7: Is LaMelo Ball worth keeping in the 4th round?

**Status**: success
**Response Time**: 0.28s
**Routing**: Through agent
**Tools Used**: calculate_keeper_value

**Agent Response** (length: 34 chars):
```
Player Is La not found in database
```

---

### TradeImpact Agent

#### Test 1: How does the Porzingis trade affect Tatum?

**Status**: success
**Response Time**: 3.51s
**Routing**: Through agent
**Tools Used**: search_trade_documents, analyze_trade_impact, calculate_usage_change, find_trade_beneficiaries, analyze_depth_chart

**Agent Response** (length: 106 chars):
```
The Porzingis trade is expected to have a positive impact on Tatum's fantasy value for the 2024-25 season.
```

**Raw Tool Outputs** (1 calls):

*Tool*: TradeImpact.analyze_trade_impact
*Output Length*: 1678 chars
```

**Porzingis Trade Impact on Tatum (2024-25)**:

[UP] **Tatum's Projected Changes**:
- Usage Rate: +2.5% (more offensive responsibility)
- Shot Attempts: +2-3 per game
- Assists: +0.5-1.0 (more playmaking required)
- Fantasy Value: +3-5 points per game

[TIP] **Analysis**: 
With Porzingis providing elite spacing and rim protection, Tatum gets:
- Better driving lanes (Porzingis pulls centers out)
- More open 3PT looks (defensive attention split)
- Reduced defensive burden (can focus on offense)
-
... [truncated]
```

**Analysis**:
- Tool output total: 1678 chars
- Agent response: 106 chars
- Compression ratio: 6.32%
- [WARN] Significant summarization detected

---

#### Test 2: Which players benefit from recent trades?

**Status**: success
**Response Time**: 3.25s
**Routing**: Through agent
**Tools Used**: search_trade_documents, analyze_trade_impact, calculate_usage_change, find_trade_beneficiaries, analyze_depth_chart

**Agent Response** (length: 229 chars):
```
Based on the analysis of recent trades, the top five players who are expected to benefit the most for the 2024-25 fantasy basketball season are Jayson Tatum, Kristaps Porzingis, Alperen Sengun, Scottie Barnes, and Ausar Thompson.
```

**Raw Tool Outputs** (1 calls):

*Tool*: TradeImpact.find_trade_beneficiaries
*Output Length*: 786 chars
```
[TARGET] **Top Trade Beneficiaries for 2024-25**:

1. **Jayson Tatum** (SF)
   - Reason: Porzingis spacing
   - Current ADP: #5
   - Projected gain: +4.0 FP/game
   - New projection: 53.6 FP/game

2. **Kristaps Porzingis** (C)
   - Reason: Better system fit
   - Current ADP: #31
   - Projected gain: +3.0 FP/game
   - New projection: 38.8 FP/game

3. **Alperen Sengun** (C)
   - Reason: Increased usage
   - Current ADP: #37
   - Projected gain: +3.5 FP/game
   - New projection: 35.2 FP/game

4. **
... [truncated]
```

**Analysis**:
- Tool output total: 786 chars
- Agent response: 229 chars
- Compression ratio: 29.13%
- [WARN] Significant summarization detected

---

#### Test 3: What's the usage rate change for Brunson after the OG trade?

**Status**: success
**Response Time**: 4.80s
**Routing**: Through agent
**Tools Used**: search_trade_documents, analyze_trade_impact, calculate_usage_change, find_trade_beneficiaries, analyze_depth_chart

**Agent Response** (length: 51 chars):
```
Agent stopped due to iteration limit or time limit.
```

**Raw Tool Outputs** (3 calls):

*Tool*: TradeImpact.calculate_usage_change
*Output Length*: 62 chars
```
Please specify a trade (e.g., Porzingis, Lillard, Towns trade)
```

*Tool*: TradeImpact.search_trade_documents
*Output Length*: 71 chars
```
Trade scenario not found. Please specify player names or trade details.
```

**Analysis**:
- Tool output total: 204 chars
- Agent response: 51 chars
- Compression ratio: 25.00%
- [WARN] Significant summarization detected

---

#### Test 4: How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo?

**Status**: success
**Response Time**: 3.74s
**Routing**: Through agent
**Tools Used**: search_trade_documents, analyze_trade_impact, calculate_usage_change, find_trade_beneficiaries, analyze_depth_chart

**Agent Response** (length: 51 chars):
```
Agent stopped due to iteration limit or time limit.
```

**Raw Tool Outputs** (3 calls):

*Tool*: TradeImpact.analyze_trade_impact
*Output Length*: 71 chars
```
Trade scenario not found. Please specify player names or trade details.
```

*Tool*: TradeImpact.analyze_trade_impact
*Output Length*: 71 chars
```
Trade scenario not found. Please specify player names or trade details.
```

**Analysis**:
- Tool output total: 213 chars
- Agent response: 51 chars
- Compression ratio: 23.94%
- [WARN] Significant summarization detected

---

#### Test 5: If the Lakers trade for Trae Young, what happens to Austin Reaves?

**Status**: success
**Response Time**: 4.68s
**Routing**: Through agent
**Tools Used**: search_trade_documents, analyze_trade_impact, calculate_usage_change, find_trade_beneficiaries, analyze_depth_chart

**Agent Response** (length: 51 chars):
```
Agent stopped due to iteration limit or time limit.
```

**Raw Tool Outputs** (3 calls):

*Tool*: TradeImpact.analyze_trade_impact
*Output Length*: 71 chars
```
Trade scenario not found. Please specify player names or trade details.
```

*Tool*: TradeImpact.analyze_trade_impact
*Output Length*: 71 chars
```
Trade scenario not found. Please specify player names or trade details.
```

**Analysis**:
- Tool output total: 213 chars
- Agent response: 51 chars
- Compression ratio: 23.94%
- [WARN] Significant summarization detected

---

