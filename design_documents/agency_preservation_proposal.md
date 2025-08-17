# Proposal: Maintaining Maximum Agency in SportsBrain Agents

## Current Situation Analysis

### The Core Problem
LangChain ReAct agents struggle with:
1. **Tool Matching**: Can't reliably map natural language queries to tool descriptions
2. **Output Summarization**: Compresses detailed tool outputs to 1.73% of original
3. **Iteration Limits**: Gets stuck when tool descriptions don't match query patterns

### Current Bypass Levels
- **Intelligence Agent**: 40% bypass (worth drafting, breakout candidates)
- **DraftPrep Agent**: 95% bypass (almost everything except edge cases)
- **TradeImpact Agent**: 20% bypass (benefited, impact, usage queries)

## Proposed Solutions to Maintain Agency

### Option 1: Enhanced Tool Descriptions (RECOMMENDED)
**Goal**: Help agents match queries to tools WITHOUT bypasses

#### Implementation for Intelligence Agent

```python
# BEFORE (current):
Tool(
    name="find_sleeper_candidates",
    description="Find undervalued players with high breakout potential",
    func=self._find_sleeper_candidates
)

# AFTER (enhanced):
Tool(
    name="find_sleeper_candidates",
    description=(
        "Find sleeper candidates, undervalued players, breakout potential, hidden gems. "
        "Answers: who are sleepers, find sleepers like X, sleeper shooting guards, "
        "underrated players, late round targets, value picks, upside plays. "
        "Keywords: sleeper, undervalued, breakout, hidden, gem, upside, value, cheap"
    ),
    func=self._find_sleeper_candidates
)
```

#### Implementation for DraftPrep Agent

```python
# BEFORE:
Tool(
    name="calculate_keeper_value",
    description="Calculate if a player is worth keeping at a specific round",
    func=self._calculate_keeper_value
)

# AFTER:
Tool(
    name="calculate_keeper_value",
    description=(
        "Calculate keeper value, should I keep player X, is player worth keeping, "
        "keeper decision, keep or drop, retention value, keeper round analysis. "
        "Answers: Should I keep Ja Morant in round 3? Is LaMelo worth keeping? "
        "Keywords: keep, keeper, retain, worth keeping, should I keep, round value"
    ),
    func=self._calculate_keeper_value
)
```

#### Implementation for TradeImpact Agent

```python
# BEFORE:
Tool(
    name="find_trade_beneficiaries",
    description="Find players who benefit most from recent trades",
    func=self._find_trade_beneficiaries
)

# AFTER:
Tool(
    name="find_trade_beneficiaries",
    description=(
        "Find trade beneficiaries, who benefited from trade, trade winners, "
        "players helped by trade, fantasy impact winners, role increases. "
        "Answers: Who benefited from Lillard trade? Trade winners? Impact on players? "
        "Keywords: benefited, benefit, winners, gained, helped, improved, boosted"
    ),
    func=self._find_trade_beneficiaries
)
```

### Option 2: Custom Agent Prompts
**Goal**: Guide the agent's reasoning process better

```python
def _initialize_agent(self):
    system_prompt = """You are an expert fantasy basketball analyst with access to specialized tools.

    IMPORTANT Tool Selection Guidelines:
    - For questions about "sleepers" or "undervalued" → use find_sleeper_candidates
    - For questions about "keeping" a player → use calculate_keeper_value  
    - For questions about "worth drafting" → use analyze_player_stats
    - For questions about player comparisons → use compare_players
    - For questions about breakout potential → use identify_breakout_candidates
    
    When you receive a query:
    1. Identify the key action words (sleeper, keep, draft, compare, breakout)
    2. Match to the appropriate tool based on these guidelines
    3. Use the tool and return its COMPLETE output without summarization
    
    DO NOT summarize tool outputs. Return them in full."""
    
    self.agent_executor = initialize_agent(
        tools=self.tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        system_message=system_prompt,
        verbose=True
    )
```

### Option 3: Tool Name Aliasing
**Goal**: Create multiple tool references for the same function

```python
# Create aliases for commonly mismatched queries
tools = [
    Tool(
        name="find_sleeper_candidates",
        description="Find sleeper candidates and undervalued players",
        func=self._find_sleeper_candidates
    ),
    Tool(
        name="find_undervalued_players",  # Alias
        description="Find sleeper candidates and undervalued players",
        func=self._find_sleeper_candidates  # Same function
    ),
    Tool(
        name="worth_drafting_analysis",
        description="Analyze if a player is worth drafting",
        func=self._analyze_player_stats
    ),
    Tool(
        name="draft_value_check",  # Alias
        description="Check if a player provides good draft value",
        func=self._analyze_player_stats  # Same function
    )
]
```

### Option 4: Semantic Router Layer (MINIMAL BYPASS)
**Goal**: Route only when agent fails, not preemptively

```python
async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
    try:
        # FIRST: Always try the agent
        result = await asyncio.wait_for(
            self.agent_executor.arun(input=message),
            timeout=30.0
        )
        
        # Check if agent actually produced useful output
        if len(result) > 50 and "error" not in result.lower():
            return AgentResponse(content=result, confidence=0.85)
            
    except (asyncio.TimeoutError, Exception) as e:
        # ONLY use semantic routing as fallback
        return self._semantic_fallback(message)
        
def _semantic_fallback(self, message: str) -> AgentResponse:
    """Last resort semantic routing when agent fails"""
    message_lower = message.lower()
    
    # Map query patterns to tools
    patterns = {
        r"sleeper|undervalued|hidden gem": self._find_sleeper_candidates,
        r"worth drafting|draft value": self._analyze_player_stats,
        r"keep|keeper|retain": self._calculate_keeper_value,
        r"breakout|sophomore|second.year": self._identify_breakout_candidates
    }
    
    for pattern, tool_func in patterns.items():
        if re.search(pattern, message_lower):
            result = tool_func(message)
            return AgentResponse(
                content=result,
                metadata={"fallback": True, "reason": "agent_failure"},
                confidence=0.75
            )
```

## Recommendation Priority

1. **IMMEDIATE (Today)**: Implement Option 1 - Enhanced Tool Descriptions
   - Least invasive change
   - Maintains full agency
   - Can be tested immediately
   - No architectural changes

2. **SHORT TERM (Tomorrow)**: Add Option 2 - Custom Agent Prompts
   - Guides agent reasoning
   - Reduces summarization
   - Works with enhanced descriptions

3. **IF NEEDED**: Implement Option 4 - Semantic Router as Fallback Only
   - Use ONLY when agent fails
   - Document as "recovery mode"
   - Maintains agency as primary

4. **AVOID**: Preemptive bypasses that defeat agentic purpose

## Expected Outcomes

### With Enhanced Descriptions + Custom Prompts:
- **Intelligence Agent**: Reduce bypass from 40% to 10%
- **DraftPrep Agent**: Reduce bypass from 95% to 50%
- **TradeImpact Agent**: Reduce bypass from 20% to 5%

### Success Metrics:
1. Agent successfully matches 80%+ of queries to correct tools
2. Timeout/iteration errors reduced by 75%
3. Maintains true agentic behavior for majority of queries
4. Fallbacks clearly documented as recovery mechanisms

## Implementation Plan

### Phase 1: Tool Description Enhancement (30 minutes)
1. Update all tool descriptions with keyword variations
2. Include example questions in descriptions
3. Add common query patterns

### Phase 2: Custom System Prompts (30 minutes)
1. Create detailed system prompts for each agent
2. Include tool selection guidelines
3. Emphasize no summarization

### Phase 3: Testing (1 hour)
1. Run benchmark tests with enhanced descriptions
2. Measure agency percentage
3. Document which queries now work through agent

### Phase 4: Minimal Fallback (If Required)
1. Implement semantic fallback ONLY for failures
2. Log all fallback usage
3. Document as recovery mechanism, not primary path

## Conclusion

The goal is to help the LangChain agent succeed at its job (tool selection) rather than bypassing it. By providing richer tool descriptions and better guidance, we can maintain true agentic behavior while addressing the tool matching issues. This approach:

1. **Preserves the capstone requirement** for agentic AI
2. **Improves user experience** with better responses
3. **Maintains architectural integrity** of the agent system
4. **Documents limitations honestly** without defeating the purpose

The key insight: Don't bypass the agent, help it succeed.