"""
    DAG operator to upload data onto a Qdrant server
"""

from dotenv import load_dotenv
from qdrant_client import QdrantClient
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')

# qdrant_client = QdrantClient(
#     url="https://2d2808b0-10d5-4c7f-b78f-932b65f1ed14.us-east4-0.gcp.cloud.qdrant.io:6333", 
#     api_key="FoO7loSf4UG11akURYWygXrYrWVlB5gS9sK3SLoN3sSADFsGo_3rPQ",
# )

# print(qdrant_client.get_collections())
