"""
    Contains the DAG that airflow will be working from
"""
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from datetime import datetime
from data_engineering import fetch
from data_engineering import chunking
from data_engineering import upload

default_args = {}


@dag(
    dag_id='extract_and_chunk_youtube_transcripts_v1.0',
    start_date=datetime(2024, 7, 28),
    schedule_interval='@daily'
)
def my_dag():
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    playlist_id = fetch.get_uploaded_videos_by_channel()
    video_ids = fetch.get_uploaded_videos_raw(playlist_id)
    videos = fetch.filter_out_shorts(video_ids)
    transcripts = fetch.get_video_transcripts(videos)
    chunked_transcripts = chunking.chunk(transcripts, chunking.word_chunking)
    model, tokenizer, vector_size = upload.get_embedding_model(upload.MODEL)
    check = upload.check_collection(vector_size, upload.conn)
    vectors, chunks = upload.vectorize(chunked_transcripts, model, tokenizer)
    almost_done = upload.upload_to_qdrant(vectors, chunks, upload.conn)

    start >> playlist_id
    playlist_id >> video_ids >> videos
    videos >> transcripts
    transcripts >> chunked_transcripts
    [check, model, tokenizer, vector_size, chunked_transcripts] >> [vectors, chunks]
    [vectors, chunks] >> almost_done
    almost_done >> end


dag_instance = my_dag()
