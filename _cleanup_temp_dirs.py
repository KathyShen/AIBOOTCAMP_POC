import os
import shutil
import time
from datetime import datetime, timedelta

# Path to the vector_db directory
VECTOR_DB_DIR = os.path.join(os.path.dirname(__file__), "vector_db")
AGE_LIMIT = timedelta(days=1)  # 1 day

def is_older_than(path, age_limit):
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - mtime > age_limit

def cleanup_user_temp_dirs():
    if not os.path.exists(VECTOR_DB_DIR):
        return
    for name in os.listdir(VECTOR_DB_DIR):
        if name.startswith("user_temp_"):
            full_path = os.path.join(VECTOR_DB_DIR, name)
            if os.path.isdir(full_path) and is_older_than(full_path, AGE_LIMIT):
                print(f"Deleting {full_path} (older than 1 day)")
                shutil.rmtree(full_path, ignore_errors=True)

if __name__ == "__main__":
    cleanup_user_temp_dirs()