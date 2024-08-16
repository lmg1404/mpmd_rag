"""
    Contains the DAG that airflow will be working from
"""
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from data_engineering import fetch
from data_engineering import chunking
from data_engineering import upload

default_args = {
    'owner': 'Luis Gallego',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}


@dag(
    dag_id='extract_and_chunk_youtube_transcripts_v1.6',
    default_args=default_args
    # schedule_interval='@daily'
)
def my_dag():
    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    playlist_id = fetch.get_uploaded_videos_by_channel()
    video_ids = fetch.get_uploaded_videos_raw(playlist_id)
    videos = fetch.filter_out_shorts(video_ids)
    transcripts = fetch.get_video_transcripts(videos)
    chunked_transcripts = chunking.chunk(transcripts, chunking.word_chunking)
    vector_size = upload.get_embedding_model(upload.MODEL)
    check = upload.check_collection(vector_size, upload.conn)
    chunk_dict = upload.vectorize(chunked_transcripts, upload.MODEL)
    almost_done = upload.upload_to_qdrant(chunk_dict["vectors"], chunk_dict["chunks"], upload.conn)

    start >> playlist_id
    playlist_id >> video_ids >> videos
    videos >> transcripts
    transcripts >> chunked_transcripts
    [check, vector_size, chunked_transcripts] >> chunk_dict
    chunk_dict >> almost_done
    almost_done >> end


dag_instance = my_dag()
