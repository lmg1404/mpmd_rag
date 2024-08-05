"""
    DAG operators to upload data onto a Qdrant server
"""

from dotenv import load_dotenv
from typing import List, Tuple, Dict
from transformers import AutoModel, AutoTokenizer
import qdrant_client
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

conn = qdrant_client.QdrantClient(
    url = QDRANT_URL, 
    api_key = QDRANT_API_KEY,
)

def get_embedding_model(model: str) -> Tuple[int, int, int]: # place holder
    embedding_model = AutoModel.from_pretrained(model)
    tokenizer = AutoTokenizer.from_pretrained(model) 
    vector_size = embedding_model.config.hidden_size
    return (embedding_model, tokenizer, vector_size)

def check_collection() -> None:
    collections = conn.get_collections()
    if not collections:
        conn.create_collection(
            collection_name="moreplatesmoredates",
            vectors_config = qdrant_client.models.VectorParams(
                size=768, distance=qdrant_client.models.Distance.COSINE
                )
        )

def vectorize(transcript: List[Dict[str, str]], model):
    pass

def upload_to_qdrant():
    pass
