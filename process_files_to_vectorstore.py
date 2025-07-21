from utils.file_handler import load_files
from utils.vector_store import save_to_chroma

if __name__ == "__main__":
    docs = load_files("uploads")
    save_to_chroma(docs, persist_directory="vector_db")