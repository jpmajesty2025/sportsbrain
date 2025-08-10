"""
Load supplemental data into Milvus to reach 1000+ embeddings
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from load_to_milvus import MilvusDataLoader
import json
import mmh3
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_supplemental_data():
    """Load supplemental strategies and trades"""
    loader = MilvusDataLoader()
    
    # Load supplemental strategies
    strategies_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'data', 'supplemental', 'supplemental_strategies.json'
    )
    
    trades_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'data', 'supplemental', 'supplemental_trades.json'
    )
    
    total_loaded = 0
    
    # Load strategies if file exists
    if os.path.exists(strategies_file):
        logger.info("Loading supplemental strategies...")
        with open(strategies_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strategies = data['strategies']
        logger.info(f"Found {len(strategies)} supplemental strategies")
        
        from pymilvus import Collection
        collection = Collection("sportsbrain_strategies")
        
        # Generate embeddings
        texts = [s['text'] for s in strategies]
        embeddings = loader.generate_embeddings(texts)
        
        # Prepare data
        primary_keys = []
        vectors = []
        texts_list = []
        metadatas = []
        created_ats = []
        strategy_types = []
        
        for i, strategy in enumerate(strategies):
            pk = mmh3.hash64(strategy['strategy_id'] + "_supp")[0]
            if pk < 0:
                pk = pk + 2**63
            
            primary_keys.append(pk)
            vectors.append(embeddings[i])
            texts_list.append(strategy['text'][:65535])
            metadatas.append(strategy['metadata'])
            created_ats.append(int(time.time()))
            strategy_types.append(strategy['strategy_type'])
        
        # Insert with correct field order
        try:
            result = collection.insert([
                primary_keys,
                vectors,
                texts_list,
                metadatas,
                created_ats,
                strategy_types
            ])
            logger.info(f"Inserted {len(result.primary_keys)} strategies")
            total_loaded += len(result.primary_keys)
        except Exception as e:
            logger.error(f"Error inserting strategies: {e}")
        
        collection.flush()
    
    # Load trades if file exists
    if os.path.exists(trades_file):
        logger.info("Loading supplemental trades...")
        with open(trades_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        trades = data['documents']
        logger.info(f"Found {len(trades)} supplemental trades")
        
        from pymilvus import Collection
        from datetime import datetime
        collection = Collection("sportsbrain_trades")
        
        # Generate embeddings
        texts = [t['text'] for t in trades]
        embeddings = loader.generate_embeddings(texts)
        
        # Prepare data
        primary_keys = []
        vectors = []
        texts_list = []
        metadatas = []
        created_ats = []
        sources = []
        dates_posted = []
        
        for i, trade in enumerate(trades):
            pk = mmh3.hash64(trade['doc_id'] + "_supp")[0]
            if pk < 0:
                pk = pk + 2**63
            
            # Convert date
            date_str = trade['date_posted']
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('T', ' '))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            timestamp = int(dt.timestamp())
            
            primary_keys.append(pk)
            vectors.append(embeddings[i])
            texts_list.append(trade['text'][:65535])
            metadatas.append(trade['metadata'])
            created_ats.append(int(time.time()))
            sources.append(trade['source'][:50])
            dates_posted.append(timestamp)
        
        # Insert with correct field order
        try:
            result = collection.insert([
                primary_keys,
                vectors,
                texts_list,
                metadatas,
                created_ats,
                sources,
                dates_posted
            ])
            logger.info(f"Inserted {len(result.primary_keys)} trades")
            total_loaded += len(result.primary_keys)
        except Exception as e:
            logger.error(f"Error inserting trades: {e}")
        
        collection.flush()
    
    # Verify final counts
    logger.info("\nVerifying final counts...")
    loader.verify_collections()
    
    return total_loaded


if __name__ == "__main__":
    print("=" * 60)
    print("Loading Supplemental Data to Milvus")
    print("=" * 60)
    
    loaded = load_supplemental_data()
    
    print(f"\n[OK] Loaded {loaded} supplemental documents")
    print("=" * 60)