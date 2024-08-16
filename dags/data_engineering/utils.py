import os

def fix_path() -> str:
  cur_path = os.getcwd()
  if "dags" != cur_path[-4:]:
    assert os.path.exists(os.path.join(cur_path, "dags")), "DAGs folder does not exist"
    cur_path = os.path.join(cur_path, "dags")
  return cur_path
