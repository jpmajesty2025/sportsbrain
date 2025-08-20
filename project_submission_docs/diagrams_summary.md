# SportsBrain Project Diagrams Summary

## Diagrams Created for Capstone Submission

### 1. Data Model Diagrams

#### PostgreSQL Data Model (`postgres_data_model.mermaid`)
- **Purpose**: Shows the relational database schema for structured data
- **Key Components**:
  - User authentication and preferences
  - 151 players with positions and teams
  - 30 NBA teams with conference/division data
  - 100 synthetic games (20 with stats)
  - ~240 synthetic game statistics records
  - 151 fantasy data records with projections and punt fits
- **Relationships**: Foreign key relationships between players, teams, games, and stats
- **Note**: All game data is synthesized for demonstration

#### Milvus Vector Collections Model (`milvus_collections_model.mermaid`)
- **Purpose**: Illustrates vector database collections for similarity search
- **Key Components**:
  - sportsbrain_players: 572 player embeddings
  - sportsbrain_strategies: 230 strategy documents
  - sportsbrain_trades: 205 trade analyses
  - Total: 1,007 embeddings (exceeds 1,000 requirement)
- **Technical Details**: 
  - 768-dimensional vectors using SentenceTransformer (all-mpnet-base-v2)
  - Field name: "vector" (not "embedding")
  - Metric: IP (Inner Product) for all collections
- **Reranking Integration**:
  - Initial search returns top 20 candidates
  - BGE cross-encoder (BAAI/bge-reranker-large) reranks to top 5
  - Two-stage retrieval process for improved relevance

#### Neo4j Graph Model (`neo4j_graph_model.mermaid`)
- **Purpose**: Shows graph database nodes and relationships
- **Key Components**:
  - Node Types: Player, Team, Injury, Trade, Performance
  - Relationships: PLAYS_FOR, HAD_INJURY, HAD_PERFORMANCE, IMPACTED_BY, SIMILAR_TO
  - Total: 804 nodes and 719 relationships
  - Query patterns for common graph traversals

### 2. System Architecture Diagram (`system_architecture.mermaid`)
- **Purpose**: Comprehensive view of the implemented system
- **Layers**:
  - Client Layer: React frontend with Material-UI
  - API Gateway: FastAPI with authentication
  - Agent Layer: 3 LangChain agents with 17 total tools + Reranking
  - Reranking Service: BGE cross-encoder for two-stage retrieval
  - Security Layer: 5-layer defensive AI implementation
  - Data Layer: PostgreSQL, Redis, Milvus, Neo4j
  - External Services: OpenAI API, NBA Stats API
  - Deployment: Railway, Zilliz Cloud, Neo4j Aura

### 3. Data Flow Diagram (`data_flow_diagram.mermaid`)
- **Purpose**: Shows how data moves through the system
- **Current Implementation**:
  - Data sources: NBA Stats API (572 players), synthesized data, hardcoded values, algorithm-generated projections
  - Data loading via Python scripts (no external API connections)
  - Storage distribution across PostgreSQL, Milvus, and Neo4j
  - Query flow: User → Security → Agent Router → Tools → Direct DB queries → Reranking → Response
  - Reranking stage: Vector search results (top 20) → BGE cross-encoder → Top 5 results
  - No caching implemented (Redis configured but unused)
- **Planned Features** (clearly marked):
  - Daily updates from external sources
  - Incremental data loading
  - Redis caching layer

### 4. Business Problem Statement (`business_problem_statement.md`)
- **Purpose**: Articulates the problem SportsBrain solves
- **Key Points**:
  - Addresses information overload in fantasy basketball
  - Democratizes access to expert-level analysis
  - Serves 10+ million potential users
  - $12-24 million revenue potential at 1% market penetration
  - Clear competitive advantages through AI innovation

## How to View Mermaid Diagrams

The `.mermaid` files can be viewed in several ways:

1. **GitHub**: Automatically renders mermaid diagrams in markdown files
2. **VS Code**: Install "Markdown Preview Mermaid Support" extension
3. **Online**: Use https://mermaid.live/ and paste the diagram code
4. **Export**: Convert to PNG/SVG using mermaid-cli

## Key Updates and Accuracy Notes

### What Changed (August 20, 2025 - Post-Reranking)
- **Reranking Addition**: All diagrams updated to show BGE cross-encoder integration
- **Milvus Schema**: Corrected field names (vector not embedding) and metric (IP not L2/Cosine)
- **Two-Stage Retrieval**: Documented the top-20 → top-5 reranking process
- **Agent Performance**: Updated success rates (75-95% with reranking)
- **Performance Metrics**: Added reranking latency (~1.5s) and total response time (~3.7s)

### Previous Updates
- **Data Sources**: Corrected to show synthesized/generated data instead of live APIs
- **Neo4j Model**: Updated to reflect actual nodes and relationships in the database
- **Cache Layer**: Marked as configured but not implemented
- **Game Data**: Clarified as synthetic (100 games, 20 with stats)
- **Data Flow**: Removed cache checks, shows direct database queries

### Diagram Highlights
- **Comprehensive Coverage**: All three databases are documented
- **Implementation Accuracy**: Shows what was actually built, not aspirational features
- **Technical Precision**: Reflects real data counts and actual relationships
- **Professional Quality**: Industry-standard diagramming notation
- **Clear Distinctions**: Implemented vs planned features are clearly marked

These diagrams fulfill the Capstone Project Spec requirements for system design documentation and provide an honest, clear visual understanding of the SportsBrain MVP architecture.