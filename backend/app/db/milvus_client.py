from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from app.core.config import settings

def get_milvus_connection():
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT
    )

def create_collection_if_not_exists(collection_name: str, dimension: int = 768):
    try:
        collection = Collection(collection_name)
        return collection
    except Exception:
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=1000)
        ]
        schema = CollectionSchema(fields, "Sports data collection")
        collection = Collection(collection_name, schema)
        
        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index("vector", index_params)
        return collection