FROM apache/airflow:2.9.3
ADD requirements.txt .
RUN pip install -r requirements.txt