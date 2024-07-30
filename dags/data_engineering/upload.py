"""
    DAG operator to upload data onto a Qdrant server
"""

from dotenv import load_dotenv
from qdrant_client import QdrantClient
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')


