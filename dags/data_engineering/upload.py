"""
    DAG operators to upload data onto a Qdrant server
"""

# from airflow.decorators import task
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Union
import qdrant_client.models
from transformers import AutoModel, AutoTokenizer
import qdrant_client
import torch
import os
import utils

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "moreplatesmoredates"
DATA_PATH = utils.create_data_folder()

conn = qdrant_client.QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def mean_pooling(model_output, attention_mask) -> torch.Tensor:
    """ Helper function directly from HuggingFace website

    Parameters
    ----------
    model_output
        Basemodel output with pooling output of model
    attention_mask
        Attention mask from the tokenizer of the model

    Returns
    -------
    torch.Tensor
        Mean outputs so that we can properly embed
    """
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1)\
        .expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / \
        torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# @task
def get_embedding_model(model: str) -> int:
    """ Gets the model, tokenizer, and vector sizes

    Parameters
    ----------
    model : str
        Encoder/embedding model we want to use

    Returns
    -------
    Tuple
        Returns the model, tokenizer, and vector size
    """
    try:
        embedding_model = AutoModel.from_pretrained(model)
        vector_size = embedding_model.config.hidden_size
    except Exception as e:
        print("Unable to retrieve model: ", e)
    return vector_size


# @task
def check_collection(
        vector_size: int, db_conn: qdrant_client.QdrantClient) -> None:
    """ Checks if the collection exists, if not it creates it

    Parameters
    ----------
    vector_size : int
        Size of the vectors we want to use

    Returns
    -------
    None
    """
    collections = db_conn.get_collections().collections
    names = [c.name for c in collections]
    if COLLECTION_NAME in names:
        db_conn.delete_collection(collection_name=COLLECTION_NAME)
    db_conn.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qdrant_client.models.VectorParams(
            size=vector_size, distance=qdrant_client.models.Distance.COSINE
        )
    )


# @task
def vectorize(
        chunks_path: str,
        model: str
        ) -> Dict[str, str]:
    """ Vectorizes all of our chunks

    Parameters
    ----------
    chunks_path : str
        Payloads path that we previously created to be vectorized

    Returns
    -------
    Dict[str, str]
        Returns our vector path which align with the chunks we made
    """
    chunks = utils.open_file(chunks_path)
    vectors = []
    embedder = AutoModel.from_pretrained(model)
    tokenizer = AutoTokenizer.from_pretrained(model)
    for chunk in chunks:
        tokenized_sentence = tokenizer(
            chunk['chunk'], padding=True, truncation=True, return_tensors="pt"
            )
        with torch.no_grad():
            vector = embedder(**tokenized_sentence)
            vector = mean_pooling(vector, tokenized_sentence['attention_mask'])
        vector = vector.squeeze().tolist()
        vectors.append(vector)
    vector_name = "vectors"
    return {
            "vectors": utils.write_file(DATA_PATH, vector_name, vectors), 
            "chunks": chunks_path
        }


# @task
def upload_to_qdrant(
        vector_path: str,
        chunk_path: str,
        db_conn: qdrant_client.QdrantClient
        ) -> None:
    """ Final step in our pipeline which uploads everything to qdrant

    Parameters
    ----------
    vector_path: str
        Path of the vectorized chunks
    chunks_path: str
        1-1 index ratio between vectors, the path
    db_conn: qdrant_client.QdrantClient
        Database connection which we load data

    Returns
    -------
    None
    """
    vectors = utils.open_file(vector_path)
    chunks = utils.open_file(chunk_path)
    for i, (v, c) in enumerate(zip(vectors, chunks)):
        db_conn.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                qdrant_client.models.PointStruct(
                    id=i,
                    payload=c,
                    vector=v
                )
            ]
        )
    return None


if __name__ == "__main__":
    import fetch
    import chunking
    print("running upload.py")
    print("fetching")
    playlist_id = fetch.get_uploaded_videos_by_channel() 
    raw_vid_path = fetch.get_uploaded_videos_raw(playlist_id)
    filtered_path = fetch.filter_out_shorts(raw_vid_path)
    transcripts = fetch.get_video_transcripts(filtered_path)

    print("chunking")
    payload_path = chunking.chunk(transcripts, chunking.word_chunking)

    print("begin upload tasks")
    vector_size = get_embedding_model(MODEL)
    check_collection(vector_size, conn)
    print("vectorizing")
    chunk_dict = vectorize(payload_path, MODEL)
    print("begin official upload")
    upload_to_qdrant(chunk_dict["vectors"], chunk_dict["chunks"], conn)
