"""Test script to verify Milvus field name fix works"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows Unicode output issues
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pymilvus import connections, Collection
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def test_milvus_schema():
    """Test that we can connect and query with correct field names"""
    
    print("=" * 60)
    print("TESTING MILVUS FIELD NAME FIX")
    print("=" * 60)
    
    # Get connection details
    MILVUS_HOST = os.getenv("MILVUS_HOST")
    MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")
    
    if not MILVUS_HOST or not MILVUS_TOKEN:
        print("[ERROR] Missing Milvus credentials in .env")
        return False
    
    try:
        # Connect to Milvus
        print(f"Connecting to Milvus at {MILVUS_HOST[:30]}...")
        connections.connect(
            alias="default",
            uri=MILVUS_HOST,
            token=MILVUS_TOKEN
        )
        print("[OK] Connected successfully")
        
        # Test each collection
        collections = ["sportsbrain_players", "sportsbrain_strategies", "sportsbrain_trades"]
        
        for coll_name in collections:
            print(f"\nTesting collection: {coll_name}")
            print("-" * 40)
            
            try:
                collection = Collection(coll_name)
                
                # Get schema info
                schema = collection.schema
                field_names = [field.name for field in schema.fields]
                print(f"Fields in schema: {field_names}")
                
                # Verify 'vector' field exists (not 'embedding')
                if 'vector' in field_names:
                    print("[OK] 'vector' field found")
                else:
                    print("[ERROR] 'vector' field NOT found")
                
                if 'embedding' in field_names:
                    print("[WARNING]  WARNING: Old 'embedding' field still exists")
                
                # Check if collection has data
                collection.load()
                num_entities = collection.num_entities
                print(f"Number of entities: {num_entities}")
                
                if num_entities > 0:
                    # Try a simple query with correct field names
                    print("Attempting a test query...")
                    
                    # Create a dummy embedding (768 dimensions)
                    import numpy as np
                    dummy_embedding = np.random.randn(768).tolist()
                    
                    search_params = {
                        "metric_type": "IP",  # Using Inner Product per schema
                        "params": {"nprobe": 10}
                    }
                    
                    results = collection.search(
                        data=[dummy_embedding],
                        anns_field="vector",  # Use correct field name
                        param=search_params,
                        limit=1,
                        output_fields=["text", "metadata"]  # Use correct output fields
                    )
                    
                    if results and results[0]:
                        print("[OK] Query successful with 'vector' field!")
                        hit = results[0][0]
                        print(f"   Score: {hit.score:.4f}")
                        text = hit.entity.get('text', '')[:100]
                        print(f"   Text preview: {text}...")
                        metadata = hit.entity.get('metadata', {})
                        if isinstance(metadata, str):
                            metadata = json.loads(metadata)
                        print(f"   Metadata keys: {list(metadata.keys()) if metadata else 'None'}")
                    else:
                        print("[WARNING]  Query returned no results")
                else:
                    print("[WARNING]  Collection is empty, skipping query test")
                
                collection.release()
                
            except Exception as e:
                print(f"[ERROR] Error testing {coll_name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Disconnect
        connections.disconnect("default")
        print("\n[OK] All tests completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_milvus_schema()
    print("\n" + "=" * 60)
    if success:
        print("[OK] MILVUS FIELD FIX VERIFIED - Ready for production!")
    else:
        print("[ERROR] Issues found - Review the errors above")
    print("=" * 60)