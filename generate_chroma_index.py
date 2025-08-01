# python _generate_chroma_index.py --input_dir "files to generate default knowledge" --db_dir "vector_db/default_db"
"""
Standalone script to generate a Chroma vector DB from documents in a folder.
- Uses advanced embedding (OpenAIEmbeddings, can be swapped for others)
- Splits documents for better retrieval
- Saves DB to disk for Streamlit Cloud compatibility
"""

import os
import argparse
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.file_handler import load_files
from dotenv import load_dotenv

def main():
    # Load OpenAI key from streamlit/secrets.toml if available
    # For Streamlit Cloud, secrets are exposed as environment variables
    # For local dev, you can use a .env file or set env var manually
    # This block ensures compatibility for both
    secrets_path = os.path.join('.streamlit', 'secrets.toml')
    if os.path.exists(secrets_path):
        import toml
        secrets = toml.load(secrets_path)
        openai_key = secrets.get('OPENAI_API_KEY')
        if openai_key:
            os.environ['OPENAI_API_KEY'] = openai_key
    else:
        # fallback: try .env
        load_dotenv()
    parser = argparse.ArgumentParser(description="Generate Chroma vector DB from documents.")
    parser.add_argument("--input_dir", type=str, default="files to generate default knowledge", help="Folder containing source files.")
    parser.add_argument("--db_dir", type=str, default="vector_db/default_db", help="Directory to save Chroma DB.")
    parser.add_argument("--embedding_model", type=str, default="text-embedding-ada-002", help="Embedding model to use.")
    args = parser.parse_args()

    # Load documents
    docs = load_files(args.input_dir)
    print(f"Loaded {len(docs)} documents from {args.input_dir}")

    # Advanced chunking for better retrieval
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunked_docs = []
    for doc in docs:
        splits = text_splitter.create_documents([doc.page_content])
        for split in splits:
            split.metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
        chunked_docs.extend(splits)
    print(f"Split into {len(chunked_docs)} chunks.")

    # Embedding
    embedding = OpenAIEmbeddings(model=args.embedding_model, openai_api_key=os.environ.get('OPENAI_API_KEY'))

    # Create Chroma DB and persist
    if not os.path.exists(args.db_dir):
        os.makedirs(args.db_dir, exist_ok=True)
    db = Chroma.from_documents(
        documents=chunked_docs,
        embedding=embedding,
        persist_directory=args.db_dir
    )
    db.persist()
    print(f"Chroma vector DB saved to {args.db_dir}")

if __name__ == "__main__":
    main()
