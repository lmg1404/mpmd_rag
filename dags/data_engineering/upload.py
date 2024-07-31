"""
    DAG operators to upload data onto a Qdrant server
"""

from dotenv import load_dotenv
import qdrant_client
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')

conn = qdrant_client.QdrantClient(
    url = QDRANT_URL, 
    api_key = QDRANT_API_KEY,
)

def get_embedding_model(model: str):
    embedding_model = None
    tokenizer = None 
    vector_size = None
    return embedding_model, tokenizer, vector_size

def create_collection():
    collections = conn.get_collections()
    if not collections:
        conn.create_collection(
            collection_name="moreplatesmoredates"
            vectors_config = qdrant_client.models.VectorParams()
        )

def vectorize(transcript, model):
    pass

def upload_to_qdrant():
    pass
