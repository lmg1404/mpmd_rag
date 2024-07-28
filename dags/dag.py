"""
    Contains the DAG that airflow will be working from
"""
from airflow import DAG
from scripts.data_engineering import fetch
from scripts.data_engineering import chunking
from scripts.data_engineering import upload

default_args = {}

with DAG(dag_id='qdrant_upload_and_chunking_v1.0', default_args, start_date, schedule_interval):
    pass