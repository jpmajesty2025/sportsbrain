"""
Load generated data into Milvus collections
Handles strategies and trades collections
"""
import sys
import os
import json
import mmh3
import time
from datetime import datetime
from typing import List, Dict, Any
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymilvus import connections, Collection, utility
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusDataLoader:
    def __init__(self):
        """Initialize connection and model"""
        # Connect to Milvus
        self.connect_to_milvus()
        
        # Initialize embedding model - MUST use same model as original data (768 dimensions)
        logger.info("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-mpnet-base-v2')  # 768 dimensions
        logger.info("Model loaded successfully")
        
    def connect_to_milvus(self):
        """Connect to Milvus instance"""
        try:
            # Load environment variables from backend/.env
            from dotenv import load_dotenv
            env_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                '.env'
            )
            load_dotenv(env_path)
            
            milvus_uri = os.getenv("MILVUS_HOST")
            milvus_token = os.getenv("MILVUS_TOKEN")
            
            if not milvus_uri or not milvus_token:
                raise ValueError("MILVUS_HOST and MILVUS_TOKEN must be set in environment")
            
            logger.info(f"Connecting to Milvus at {milvus_uri[:30]}...")
            connections.connect(
                alias="default",
                uri=milvus_uri,
                token=milvus_token,
                timeout=30
            )
            logger.info("Connected to Milvus successfully")
            
            # List existing collections
            collections = utility.list_collections()
            logger.info(f"Existing collections: {collections}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Normalize embeddings for Inner Product similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / norms
        
        return normalized.tolist()
    
    def load_strategy_documents(self) -> int:
        """Load strategy documents into sportsbrain_strategies collection"""
        logger.info("\n" + "="*60)
        logger.info("Loading Strategy Documents")
        logger.info("="*60)
        
        # Load strategy data
        strategy_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'strategies', 'strategy_documents_2024_25.json'
        )
        
        if not os.path.exists(strategy_file):
            logger.error(f"Strategy file not found: {strategy_file}")
            return 0
        
        with open(strategy_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        strategies = data['strategies']
        logger.info(f"Loaded {len(strategies)} strategy documents from file")
        
        # Connect to collection
        collection = Collection("sportsbrain_strategies")
        
        # Check existing data
        existing_count = collection.num_entities
        logger.info(f"Collection currently has {existing_count} entities")
        
        # Prepare data for insertion
        batch_size = 50
        total_inserted = 0
        
        for i in range(0, len(strategies), batch_size):
            batch = strategies[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} documents)...")
            
            # Prepare batch data
            primary_keys = []
            vectors = []
            texts = []
            strategy_types = []
            metadatas = []
            created_ats = []
            
            # Generate embeddings for batch
            batch_texts = [s['text'] for s in batch]
            batch_embeddings = self.generate_embeddings(batch_texts)
            
            for j, strategy in enumerate(batch):
                # Generate primary key from strategy_id
                pk = mmh3.hash64(strategy['strategy_id'])[0]
                if pk < 0:
                    pk = pk + 2**63  # Ensure positive
                
                primary_keys.append(pk)
                vectors.append(batch_embeddings[j])
                texts.append(strategy['text'][:65535])  # Ensure within VARCHAR limit
                strategy_types.append(strategy['strategy_type'])
                metadatas.append(strategy['metadata'])  # Already a dict, not a string
                created_ats.append(int(time.time()))
            
            # Insert batch - ORDER MATTERS: primary_key, vector, text, metadata, created_at, strategy_type
            try:
                result = collection.insert([
                    primary_keys,
                    vectors,
                    texts,
                    metadatas,
                    created_ats,
                    strategy_types
                ])
                
                inserted_count = len(result.primary_keys)
                total_inserted += inserted_count
                logger.info(f"  Inserted {inserted_count} documents")
                
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
                continue
        
        # Flush to ensure data is persisted
        collection.flush()
        
        final_count = collection.num_entities
        logger.info(f"\nStrategy loading complete:")
        logger.info(f"  - Documents processed: {len(strategies)}")
        logger.info(f"  - Documents inserted: {total_inserted}")
        logger.info(f"  - Final collection count: {final_count}")
        
        return total_inserted
    
    def load_trade_documents(self) -> int:
        """Load trade documents into sportsbrain_trades collection"""
        logger.info("\n" + "="*60)
        logger.info("Loading Trade Documents")
        logger.info("="*60)
        
        # Load trade data
        trade_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'mock_trades', 'trade_documents_2024_25.json'
        )
        
        if not os.path.exists(trade_file):
            logger.error(f"Trade file not found: {trade_file}")
            return 0
        
        with open(trade_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        trades = data['documents']
        logger.info(f"Loaded {len(trades)} trade documents from file")
        
        # Connect to collection
        collection = Collection("sportsbrain_trades")
        
        # Check existing data
        existing_count = collection.num_entities
        logger.info(f"Collection currently has {existing_count} entities")
        
        # Prepare data for insertion
        batch_size = 50
        total_inserted = 0
        
        for i in range(0, len(trades), batch_size):
            batch = trades[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} documents)...")
            
            # Prepare batch data
            primary_keys = []
            vectors = []
            texts = []
            sources = []
            dates_posted = []
            metadatas = []
            created_ats = []
            
            # Generate embeddings for batch
            batch_texts = [t['text'] for t in batch]
            batch_embeddings = self.generate_embeddings(batch_texts)
            
            for j, trade in enumerate(batch):
                # Generate primary key from doc_id
                pk = mmh3.hash64(trade['doc_id'])[0]
                if pk < 0:
                    pk = pk + 2**63  # Ensure positive
                
                # Convert date_posted to Unix timestamp
                date_str = trade['date_posted']
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('T', ' '))
                else:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                timestamp = int(dt.timestamp())
                
                primary_keys.append(pk)
                vectors.append(batch_embeddings[j])
                texts.append(trade['text'][:65535])  # Ensure within VARCHAR limit
                sources.append(trade['source'][:50])  # Ensure within VARCHAR limit
                dates_posted.append(timestamp)
                
                # Enhance metadata with additional fields
                metadata = trade.get('metadata', {})
                metadata['doc_type'] = trade.get('doc_type', '')
                metadata['headline'] = trade.get('headline', '')
                metadata['teams_involved'] = trade.get('teams_involved', [])
                
                metadatas.append(metadata)  # Already a dict, not a string
                created_ats.append(int(time.time()))
            
            # Insert batch - ORDER MATTERS: primary_key, vector, text, metadata, created_at, source, date_posted
            try:
                result = collection.insert([
                    primary_keys,
                    vectors,
                    texts,
                    metadatas,
                    created_ats,
                    sources,
                    dates_posted
                ])
                
                inserted_count = len(result.primary_keys)
                total_inserted += inserted_count
                logger.info(f"  Inserted {inserted_count} documents")
                
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
                continue
        
        # Flush to ensure data is persisted
        collection.flush()
        
        final_count = collection.num_entities
        logger.info(f"\nTrade loading complete:")
        logger.info(f"  - Documents processed: {len(trades)}")
        logger.info(f"  - Documents inserted: {total_inserted}")
        logger.info(f"  - Final collection count: {final_count}")
        
        return total_inserted
    
    def verify_collections(self):
        """Verify all collections and their counts"""
        logger.info("\n" + "="*60)
        logger.info("Collection Verification")
        logger.info("="*60)
        
        collections_to_check = [
            "sportsbrain_players",
            "sportsbrain_strategies", 
            "sportsbrain_trades"
        ]
        
        total_embeddings = 0
        for coll_name in collections_to_check:
            try:
                collection = Collection(coll_name)
                count = collection.num_entities
                total_embeddings += count
                logger.info(f"{coll_name}: {count} entities")
            except Exception as e:
                logger.warning(f"{coll_name}: Not found or error - {e}")
        
        logger.info(f"\nTotal embeddings across all collections: {total_embeddings}")
        
        if total_embeddings >= 1000:
            logger.info("[OK] Target of 1000+ embeddings achieved!")
        else:
            logger.warning(f"Need {1000 - total_embeddings} more embeddings to reach target")
        
        return total_embeddings
    
    def test_similarity_search(self):
        """Test vector similarity search on loaded data"""
        logger.info("\n" + "="*60)
        logger.info("Testing Similarity Search")
        logger.info("="*60)
        
        # Test strategy search
        try:
            collection = Collection("sportsbrain_strategies")
            collection.load()
            
            # Search for punt FT% strategies
            query_text = "I want to punt free throw percentage with Giannis"
            query_embedding = self.generate_embeddings([query_text])[0]
            
            search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
            results = collection.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=3,
                output_fields=["strategy_type", "metadata"]
            )
            
            logger.info(f"\nStrategy search for: '{query_text}'")
            for i, hit in enumerate(results[0]):
                strategy_type = hit.entity.get('strategy_type')
                metadata = hit.entity.get('metadata')
                # Metadata is already a dict, not a JSON string
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                logger.info(f"  {i+1}. Type: {strategy_type}, Score: {hit.score:.3f}")
                logger.info(f"     Key players: {metadata.get('key_players', [])[:3]}")
        
        except Exception as e:
            logger.error(f"Strategy search failed: {e}")
        
        # Test trade search
        try:
            collection = Collection("sportsbrain_trades")
            collection.load()
            
            # Search for Lillard trade impact
            query_text = "How does Damian Lillard trade affect fantasy value"
            query_embedding = self.generate_embeddings([query_text])[0]
            
            search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
            results = collection.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=3,
                output_fields=["source", "metadata"]
            )
            
            logger.info(f"\nTrade search for: '{query_text}'")
            for i, hit in enumerate(results[0]):
                source = hit.entity.get('source')
                metadata = hit.entity.get('metadata')
                # Metadata is already a dict, not a JSON string
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                logger.info(f"  {i+1}. Source: {source}, Score: {hit.score:.3f}")
                logger.info(f"     Type: {metadata.get('doc_type', 'unknown')}")
        
        except Exception as e:
            logger.error(f"Trade search failed: {e}")


def main():
    """Main function to load all data"""
    print("=" * 60)
    print("Milvus Data Loading Script")
    print("=" * 60)
    
    loader = MilvusDataLoader()
    
    # Load strategies
    strategies_count = loader.load_strategy_documents()
    
    # Load trades
    trades_count = loader.load_trade_documents()
    
    # Verify collections
    total_count = loader.verify_collections()
    
    # Test similarity search
    if total_count > 0:
        loader.test_similarity_search()
    
    print("\n" + "=" * 60)
    print("Data Loading Complete!")
    print(f"[OK] Loaded {strategies_count} strategies")
    print(f"[OK] Loaded {trades_count} trades")
    print(f"[OK] Total embeddings: {total_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()