"""Direct test of Milvus connectivity and reranking"""

import os
import pytest
from dotenv import load_dotenv

# Skip this test file in CI to avoid downloading models
if os.getenv("CI") == "true":
    pytest.skip("Skipping model test in CI environment", allow_module_level=True)

load_dotenv()

@pytest.mark.skipif(
    not os.getenv("MILVUS_HOST") or not os.getenv("MILVUS_TOKEN"),
    reason="Milvus credentials not available"
)
def test_milvus_connection():
    """Test if we can connect to Milvus and search"""
    from pymilvus import connections, Collection, utility
    from sentence_transformers import SentenceTransformer
    
    print("Testing Milvus Connection...")
    
    # Check environment variables
    milvus_host = os.getenv("MILVUS_HOST")
    milvus_token = os.getenv("MILVUS_TOKEN")
    
    print(f"MILVUS_HOST: {milvus_host[:30]}..." if milvus_host else "MILVUS_HOST: Not set")
    print(f"MILVUS_TOKEN: {'*' * 10}" if milvus_token else "MILVUS_TOKEN: Not set")
    
    if not milvus_host or not milvus_token:
        print("ERROR: Milvus credentials not found!")
        return False
    
    try:
        # Connect
        connections.connect(
            alias="default",
            uri=milvus_host,
            token=milvus_token
        )
        print("[OK] Connected to Milvus")
        
        # List collections
        collections = utility.list_collections()
        print(f"[OK] Found {len(collections)} collections: {collections}")
        
        # Test search on trades collection
        collection = Collection("sportsbrain_trades")
        collection.load()
        print("[OK] Loaded sportsbrain_trades collection")
        
        # Create a test embedding
        model = SentenceTransformer('all-mpnet-base-v2')
        test_query = "How does Porzingis trade affect Tatum"
        embedding = model.encode(test_query).tolist()
        print(f"[OK] Created test embedding (dim: {len(embedding)})")
        
        # Search
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }
        
        results = collection.search(
            data=[embedding],
            anns_field="vector",
            param=search_params,
            limit=5,
            output_fields=["text", "metadata"]
        )
        
        if results and results[0]:
            print(f"[OK] Search successful! Found {len(results[0])} results")
            for i, hit in enumerate(results[0][:2], 1):
                print(f"\nResult {i}:")
                print(f"  Score: {hit.score}")
                print(f"  Text preview: {hit.entity.get('text', '')[:100]}...")
        else:
            print("[FAILED] No search results found")
        
        connections.disconnect("default")
        return True
        
    except Exception as e:
        print(f"[FAILED] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reranker():
    """Test if reranker can initialize"""
    print("\nTesting Reranker...")
    
    try:
        from app.services.reranker_service import ReRankerService
        reranker = ReRankerService()
        
        if reranker.model_loaded:
            print("[OK] Reranker model loaded successfully")
            
            # Test reranking
            test_docs = [
                {"content": "Tatum benefits from Porzingis trade", "score": 0.8},
                {"content": "Unrelated basketball news", "score": 0.6}
            ]
            
            reranked = reranker.rerank(
                query="How does Porzingis affect Tatum",
                documents=test_docs,
                top_k=2
            )
            
            print(f"[OK] Reranking works! Reranked {len(reranked)} documents")
            return True
        else:
            print("[FAILED] Reranker model failed to load")
            return False
            
    except Exception as e:
        print(f"[FAILED] Reranker error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("MILVUS & RERANKING TEST")
    print("="*60)
    
    milvus_ok = test_milvus_connection()
    reranker_ok = test_reranker()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"Milvus: {'[OK] Working' if milvus_ok else '[FAILED] Failed'}")
    print(f"Reranker: {'[OK] Working' if reranker_ok else '[FAILED] Failed'}")
    
    if not milvus_ok:
        print("\nMilvus is not working - this explains the fallback to SQL")
        print("Check if Milvus credentials are set in Railway environment")
    
    if not reranker_ok:
        print("\nReranker is not working - check if sentence-transformers is installed")
    
    print("="*60)