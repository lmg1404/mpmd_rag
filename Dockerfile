FROM apache/airflow:2.9.3
ADD requirements.txt .
RUN pip install -r requirements.txt

# # Use Miniconda as the base image
# FROM continuumio/miniconda3

# # Set the working directory inside the container
# WORKDIR /airflow

# # Copy the environment.yml file into the container
# COPY environment.yml .

# # Install Conda environment from environment.yml
# RUN conda env create -f environment.yml

# RUN conda activate env