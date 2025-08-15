# Benchmark Agent Questions v1 - SportsBrain Production Testing

## Intelligence Agent Test Questions

### Question 1: "Who are the most undervalued shooting guards for fantasy?"
**Expected Response:**
- List of 5-10 shooting guards with high sleeper scores (>0.7)
- Should include players like Gary Trent Jr. (0.90 sleeper score), Anfernee Simons
- Each player should show:
  - Sleeper score and ADP
  - Shot distribution (3PT%, midrange%, paint%)
  - 2024-25 projections (PPG, RPG, APG)
  - Draft timing recommendations
  - Risk/reward assessment
  - Team fit considerations

### Question 2: "Which third-year players are primed for a breakout season?"
**Expected Response:**
- List of sophomore/third-year players marked as breakout candidates
- Should include players like Paolo Banchero, Chet Holmgren
- For each player:
  - Breakout confidence level (High/Moderate/Speculative)
  - Statistical projections and improvements expected
  - Draft strategy (target 1-2 rounds before ADP)
  - Pairing suggestions (who to draft alongside them)
  - Role-based analysis (primary scorer, playmaker, etc.)

### Question 3: "Find me high-upside centers going late in drafts"
**Expected Response:**
- Centers with ADP > round 8 but high sleeper scores
- Should include players like Daniel Gafford, Isaiah Hartenstein
- Each center should show:
  - Shot distribution heavily weighted to paint (>70%)
  - Rebounding and blocks projections
  - Risk factors (injury history, playing time concerns)
  - Draft window recommendations
  - Team situation analysis

### Question 4: "Show me guards who could surprise like Tyrese Maxey did last year"
**Expected Response:**
- Young guards with breakout potential
- Should identify players like Scoot Henderson, Jalen Suggs
- Include:
  - Comparison to Maxey's pre-breakout profile
  - Usage rate projections
  - Shot distribution and efficiency metrics
  - Team context (opportunity for increased role)
  - Risk/reward scoring

### Question 5: "Which players are sleepers but also consistent performers?"
**Expected Response:**
- Players with high sleeper scores AND high consistency ratings
- Balance of upside and floor
- Should show:
  - Consistency rating alongside sleeper score
  - Historical performance stability
  - Low injury risk players prioritized
  - Draft value analysis
  - Safe but valuable picks

---

## DraftPrep Agent Test Questions

### Question 1: "Is LaMelo Ball worth keeping in the 4th round?"
**Expected Response:**
- Clear KEEP/DON'T KEEP recommendation
- ADP comparison (likely round 2-3 vs keeper round 4)
- Value calculation showing rounds saved
- Strategic insights:
  - Opportunity cost analysis
  - Alternative keeper options to consider
  - Build synergy (punt FG% friendly)
  - Draft capital saved (1-2 rounds)
- Risk assessment (injury history consideration)

### Question 2: "Build me a punt assists team starting with Jayson Tatum"
**Expected Response:**
- Complete punt assists strategy
- Synergistic categories to dominate (PTS, 3PM, REB, FT%)
- Complementary picks by round:
  - Round 2-3: Elite scoring wings (Kawhi, PG13)
  - Round 4-5: Rebounding bigs (Gobert, Allen)
  - Round 6-8: 3PT specialists
  - Late rounds: Defensive specialists
- Position scarcity analysis
- Specific player targets who fit the build
- Categories you'll dominate (6-7 out of 9)

### Question 3: "Who has better keeper value: Scottie Barnes in round 5 or Tyrese Haliburton in round 3?"
**Expected Response:**
- Direct comparison with clear winner
- ADP analysis for both players
- Value saved calculation for each
- Strategic fit considerations:
  - Barnes: Better for punt FT% or balanced builds
  - Haliburton: Elite assists, good for punt FG%
- Long-term outlook (age, team situation)
- Build flexibility analysis
- Recommendation based on league settings

### Question 4: "What's the optimal strategy for pick 11 in a 12-team draft?"
**Expected Response:**
- Turn pick strategy (11th and 14th picks)
- Best available pairs to target:
  - Guard+Big combo
  - Punt strategy anchors
  - Balanced build options
- Position scarcity at the turn
- Players likely available (ADP 9-14 range)
- Build paths from this position
- Reaching vs waiting decisions
- Round 3-4 turn strategy (picks 35 and 38)

### Question 5: "Give me a punt blocks build around Damian Lillard"
**Expected Response:**
- Guard-heavy build strategy
- Categories to dominate (AST, 3PM, PTS, FT%, STL)
- Target player types:
  - Elite guards (Haliburton, Maxey)
  - Wing defenders (OG Anunoby, Mikal Bridges)
  - Versatile forwards who don't block
- Round-by-round targets
- Avoiding traditional centers
- Late-round specialists for steals and 3s
- Expected category wins (6-3 or 7-2 potential)

---

## TradeImpact Agent Test Questions

### Question 1: "How would a hypothetical Donovan Mitchell to Miami trade affect Bam Adebayo's fantasy value?"
**Expected Response:**
- Clear winner/loser analysis
- Usage rate impact for Bam (-2 to -3%)
- Rebounding might increase (+0.5-1 RPG)
- Assists decrease (-0.5 APG)
- Efficiency improvement potential
- Timeline: Immediate impact vs long-term
- Category breakdown:
  - Negative: Touches, assists
  - Positive: Efficiency, defensive stats
  - Neutral: Rebounds
- Alternative scenarios to consider

### Question 2: "If the Lakers trade for Trae Young, what happens to Austin Reaves?"
**Expected Response:**
- Major negative impact on Reaves
- Usage rate drop (-5 to -7%)
- Role change from secondary playmaker to spot-up shooter
- Minutes reduction likely (-5 to -8 MPG)
- Statistical impacts:
  - Points: -4 to -5 PPG
  - Assists: -2 to -3 APG
  - 3PM: Slight increase in attempts
- Winner: Trae (higher usage than current Hawks)
- Loser: Reaves and Russell (if still there)
- Timeline for adjustment period

### Question 3: "What's the fantasy impact if Karl-Anthony Towns gets traded to the Knicks?"
**Expected Response:**
- Winners and losers analysis:
  - Winner: KAT (becomes primary option)
  - Mixed: Brunson (less usage but better efficiency)
  - Loser: Randle (if still there)
- KAT impact:
  - Usage increase (+2-3%)
  - Better spacing in NY system
  - 3PT attempts increase
- Team dynamics:
  - Pace increase benefits KAT
  - Defensive concerns
- Category impacts for KAT:
  - Points: +2-3 PPG
  - 3PM: +0.5 per game
  - Rebounds: Slight decrease
- Alternative trade destinations comparison

### Question 4: "How does adding Bradley Beal affect Devin Booker's production?"
**Expected Response:**
- Based on actual Suns situation
- Usage rate changes for Booker (-3 to -4%)
- Efficiency improvements with better spacing
- Assists slight increase (+0.5 APG)
- Shot attempts decrease (-2 to -3 FGA)
- Timeline analysis:
  - Immediate: Adjustment period
  - Mid-season: Chemistry building
  - Playoffs: Optimized roles
- Category breakdown for Booker:
  - Points: -2 to -3 PPG
  - Efficiency: +1-2% FG%
  - Assists: +0.5 APG
- Comparison to other star pairings

### Question 5: "If Zion gets traded to the Warriors, how does it impact Draymond Green?"
**Expected Response:**
- Complex impact analysis
- Draymond role evolution:
  - Less rebounding (-1 to -2 RPG)
  - More assists (+1 to +1.5 APG)
  - Fewer minutes potentially
- Defensive dynamics change
- Usage remains low (Draymond not a scorer)
- Winner: Zion (Warriors system)
- Mixed: Draymond (role change)
- Timeline: 
  - Immediate confusion
  - Long-term could extend Draymond's career
- Alternative impacts on Kuminga, Wiggins
- Strategic fit analysis

---

## Testing Notes

### What to Look For:
1. **Response Time**: Should be under 30 seconds (timeout is set)
2. **Data Accuracy**: Players mentioned should exist in our database
3. **Strategic Insights**: Day 3 enhancements should be visible
4. **Formatting**: Structured, readable responses
5. **Tool Usage**: Agent should select appropriate tools

### Known Limitations:
- Intelligence Agent may summarize detailed outputs (LangChain ReAct limitation)
- Some responses might be condensed from original tool outputs
- Trade scenarios use mock data for hypothetical trades

### Success Criteria:
- Agent responds without timeout errors
- Provides relevant player recommendations
- Includes statistical backing for recommendations
- Shows strategic insights (draft timing, team fit, etc.)
- Demonstrates understanding of fantasy basketball concepts