"""Test the fixed Hit access pattern"""

import os
from dotenv import load_dotenv
load_dotenv()

def test_fixed_access():
    from pymilvus import connections, Collection
    from sentence_transformers import SentenceTransformer
    
    print("Testing fixed Hit access pattern...")
    
    milvus_host = os.getenv("MILVUS_HOST")
    milvus_token = os.getenv("MILVUS_TOKEN")
    
    connections.connect(
        alias="default",
        uri=milvus_host,
        token=milvus_token
    )
    
    collection = Collection("sportsbrain_trades")
    collection.load()
    
    model = SentenceTransformer('all-mpnet-base-v2')
    embedding = model.encode("Porzingis trade impact").tolist()
    
    results = collection.search(
        data=[embedding],
        anns_field="vector",
        param={"metric_type": "IP", "params": {"nprobe": 10}},
        limit=2,
        output_fields=["text", "metadata"]
    )
    
    print(f"Found {len(results[0])} results")
    
    for hit in results[0]:
        print(f"\nHit type: {type(hit)}")
        print(f"Hit.entity type: {type(hit.entity)}")
        print(f"Hit attributes: {dir(hit)[:5]}...")  # Show first 5 attributes
        
        # The correct pattern - hit.entity IS a dict-like object
        try:
            # Get text field
            text = hit.entity.get('text')
            print(f"Text (first 50 chars): {str(text)[:50]}...")
        except TypeError as e:
            # If get() doesn't accept default, access directly
            text = hit.entity['text'] if 'text' in hit.entity else ''
            print(f"Text via direct access: {str(text)[:50]}...")
        
        try:
            # Get metadata field
            metadata = hit.entity.get('metadata')
            print(f"Metadata type: {type(metadata)}")
        except:
            metadata = hit.entity['metadata'] if 'metadata' in hit.entity else {}
            print(f"Metadata via direct: {type(metadata)}")
        
        break  # Just test first hit
    
    connections.disconnect("default")
    print("\nTest complete!")

if __name__ == "__main__":
    test_fixed_access()