


import argparse
import os
from utils.file_handler import load_files
from utils.vector_store import save_to_chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    from langchain.embeddings import OpenAIEmbeddings

# Load OpenAI API key from .streamlit/secrets.toml if not set
def load_openai_key():
    if os.environ.get("OPENAI_API_KEY"):
        return
    try:
        import toml
        secrets = toml.load(".streamlit/secrets.toml")
        key = secrets.get("OPENAI_API_KEY")
        if key:
            os.environ["OPENAI_API_KEY"] = key
    except Exception as e:
        print(f"Warning: Could not load OPENAI_API_KEY from secrets.toml: {e}")

def get_embedding_model(model_name):
    # If you have a data privacy-specific embedding, use it here
    # Example: from langchain_privacy.embeddings import PrivacyEmbeddings
    # return PrivacyEmbeddings(model=model_name)
    return OpenAIEmbeddings(model=model_name)

def main(
    input_dir="files to generate default knowledge",
    output_dir="vector_db",
    db_name="default knowledge",
    embedding_model="text-embedding-3-large",
    chunk_size=1000,
    chunk_overlap=200
):
    # Collect all PDF, DOCX, TXT files
    files = []
    for fname in os.listdir(input_dir):
        if fname.lower().endswith((".pdf", ".docx", ".txt")):
            files.append(os.path.join(input_dir, fname))
    if not files:
        print(f"No supported files found in {input_dir}")
        return
    print(f"Found {len(files)} files: {files}")
    # Load documents
    docs = load_files(input_dir)
    # Ensure OpenAI API key is loaded
    load_openai_key()
    # Use advanced embedding model
    embedding = get_embedding_model(embedding_model)
    # Save to Chroma vector DB (let save_to_chroma handle splitting)
    persist_path = os.path.join(output_dir, db_name)
    save_to_chroma(
        docs,
        persist_directory=persist_path,
        embedding=embedding,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    print(f"Vector DB saved to {persist_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate default knowledge vector DB from files.")
    parser.add_argument("--input_dir", type=str, default="files to generate default knowledge", help="Folder containing source files.")
    parser.add_argument("--output_dir", type=str, default="vector_db", help="Folder to save vector DB.")
    parser.add_argument("--db_name", type=str, default="default knowledge", help="Name of the vector DB folder.")
    parser.add_argument("--embedding_model", type=str, default="text-embedding-ada-002", help="Embedding model to use.")
    parser.add_argument("--chunk_size", type=int, default=1000, help="Chunk size for splitting text.")
    parser.add_argument("--chunk_overlap", type=int, default=200, help="Chunk overlap for splitting text.")
    args = parser.parse_args()
    main(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        db_name=args.db_name,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )