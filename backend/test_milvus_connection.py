"""Test actual Milvus connection with production credentials"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

def test_milvus_connection():
    """Test connection to managed Milvus instance"""
    from pymilvus import connections, utility, Collection
    
    print("TESTING MILVUS CONNECTION")
    print("=" * 60)
    
    # Get credentials from environment
    host = os.getenv("MILVUS_HOST")
    token = os.getenv("MILVUS_TOKEN")
    
    print(f"Host: {host[:50]}...")
    print(f"Token: {token[:20]}..." if token else "No token found")
    
    try:
        # Connect to Milvus
        print("\nConnecting to Milvus...")
        connections.connect(
            alias="default",
            uri=host,
            token=token
        )
        print("[OK] Connected successfully!")
        
        # List collections
        print("\nAvailable collections:")
        collections = utility.list_collections()
        for coll in collections:
            collection = Collection(coll)
            collection.load()
            count = collection.num_entities
            print(f"  - {coll}: {count} entities")
        
        # Test search on each collection
        print("\nTesting searches:")
        
        # Test players collection
        if "sportsbrain_players" in collections:
            collection = Collection("sportsbrain_players")
            collection.load()
            
            # Create a test embedding (768 dimensions for all-mpnet-base-v2)
            test_embedding = [0.1] * 768
            
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[test_embedding],
                anns_field="vector",
                param=search_params,
                limit=3,
                output_fields=["text"]
            )
            
            print(f"\n  Players search returned {len(results[0])} results")
            for i, hit in enumerate(results[0][:2], 1):
                text = hit.entity.get('text') or 'No text'
                print(f"    {i}. Score: {hit.score:.3f}, Text preview: {text[:50]}...")
        
        # Disconnect
        connections.disconnect("default")
        print("\n[OK] All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        return False

def test_draftprep_with_real_milvus():
    """Test DraftPrep agent with real Milvus connection"""
    from app.agents.draft_prep_agent_enhanced import EnhancedDraftPrepAgent
    
    print("\n" + "=" * 60)
    print("TESTING DRAFTPREP WITH REAL MILVUS")
    print("=" * 60)
    
    agent = EnhancedDraftPrepAgent()
    
    # Test a query that should trigger reranking
    query = "Build a punt FT% team around Giannis"
    print(f"\nQuery: {query}")
    
    result = agent._build_punt_strategy(query)
    
    # Check for AI enhancement
    has_ai = "AI-Powered" in result or "Enhanced" in result
    print(f"\n[OK] AI Enhancement Found: {has_ai}")
    
    if has_ai:
        # Find and display the AI section
        if "Enhanced Strategy Insights" in result:
            start = result.find("Enhanced Strategy Insights")
            end = result.find("\n\n", start + 200)  # Get a reasonable chunk
            if end == -1:
                end = start + 500
            print("\nAI Section Preview:")
            print(result[start:end])
    else:
        print("\nNo AI enhancement found - showing first 500 chars:")
        print(result[:500])
    
    return has_ai

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    
    # Test basic connection
    if test_milvus_connection():
        # Test with DraftPrep
        test_draftprep_with_real_milvus()