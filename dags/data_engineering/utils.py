import os
import json

def create_data_folder() -> str:
  cur_path = os.getcwd()
  if "dags" != cur_path[-4:]:
    assert os.path.exists(os.path.join(cur_path, "dags")), "DAGs folder does not exist"
    cur_path = os.path.join(cur_path, "dags")
  
  new_path = os.path.join(cur_path, "intermediate_data")
  if not os.path.exists(new_path):
    os.mkdir(new_path)  
  
  return new_path

def open_file(path) -> str:
  with open(path, 'r') as f:
    data = json.load(f)
  return data

def write_file(base_path, file_name,data) -> str:
  dump = os.path.join(base_path, file_name)
  with open(dump, 'w') as f: 
      json.dump(data, f, indent=4)
      
  return dump
