"""
    DAG operator to upload data onto a Qdrant server
"""

from dotenv import load_dotenv
import qdrant_client
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')

qdrant_client = qdrant_client.QdrantClient(
    url=QDRANT_URL, 
    api_key=QDRANT_API_KEY,
)

def get_embedding_model(model: str):
    pass


def vectorize():
    pass
