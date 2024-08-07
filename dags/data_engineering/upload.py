"""
    DAG operators to upload data onto a Qdrant server
"""

# from airflow.decorators import task
from dotenv import load_dotenv
from typing import List, Tuple, Dict
import qdrant_client.models
from transformers import AutoModel, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
import qdrant_client
import torch
import os

load_dotenv()
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "moreplatesmoredates"

conn = qdrant_client.QdrantClient(
    url = QDRANT_URL, 
    api_key = QDRANT_API_KEY,
)

# @task
def get_embedding_model(model: str
                        ) -> Tuple[PreTrainedModel, PreTrainedTokenizer, int]: # place holder
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
        tokenizer = AutoTokenizer.from_pretrained(model) 
        vector_size = embedding_model.config.hidden_size
    except Exception as e:
        print("Unable to retrieve model: ", e)
    return (embedding_model, tokenizer, vector_size)


# @task
def check_collection(vector_size: int, db_conn: qdrant_client.QdrantClient) -> None:
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
    if not names:
        db_conn.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=qdrant_client.models.VectorParams(
                size=vector_size, distance=qdrant_client.models.Distance.COSINE
            )
        )


# FIXME: pool outputs since it's not outputting correctly
# FIXME: this is out putting the pooler and last hidden state outputs, fix
#@task
def vectorize(chunks: List[Dict[str, str]], 
        embedder: PreTrainedModel, 
        tokenizer: PreTrainedTokenizer
        ) -> Tuple[List[torch.Tensor], List[Dict[str, str]]]:
    """ Vectorizes all of our chunks

    Parameters
    ----------
    chunks : List[Dict[str, str]]
        Payloads that we previously created to be vectorized

    Returns
    -------
    Tuple[List[torch.Tensor], List[Dict[str, str]]]
        Returns our vectors which align with the chunks we made
    """
    vectors = []
    for chunk in chunks:
        tokenized_sentence = tokenizer(chunk['chunk'], padding=True, truncation=True, return_tensors="pt")
        vector = embedder(**tokenized_sentence)
        vectors.append(vector)
    return (vectors, chunks)

# @task
def upload_to_qdrant(
        vectors: List[torch.Tensor], 
        chunks: List[Dict[str, str]], 
        db_conn: qdrant_client.QdrantClient
        ) -> None:
    """ Final step in our pipeline which uploads everything to qdrant

    Parameters
    ----------
    vectors: List[torch.Tensor]
        List of vectorized chunks
    chunks: List[Dict[str, str]]
        1-1 index ratio between vectors
    db_conn: qdrant_client.QdrantClient
        Database connection which we load data

    Returns
    -------
    None
    """
    for i, (v, c) in enumerate(zip(vectors, chunks)):
        print(v)
        db_conn.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                qdrant_client.models.PointStruct(
                    id=i,
                    payload=c,
                    vector=v.tolist()
                )
            ]
        )
    return None


if __name__ == "__main__":
    import fetch, chunking
    print("running upload.py")
    print("fetching")
    playlist_id = fetch.get_uploaded_videos_by_channel()
    video_ids = fetch.get_uploaded_videos_raw(playlist_id)
    videos = fetch.filter_out_shorts(video_ids)
    transcripts = fetch.get_video_transcripts(videos)
    
    print("chunking")
    payloads = chunking.chunk(transcripts, chunking.word_chunking)
    
    print("begin upload tasks")
    model, tokenizer, vector = get_embedding_model(MODEL)
    check_collection(vector, conn)
    (vectors, chunks) = vectorize(payloads, model, tokenizer)
    upload_to_qdrant(vectors, chunks, conn)
    