# python generate_pinecone_index.py --index_name "default-knowledge"
import streamlit as st

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from utils.file_handler import load_files
from langchain.text_splitter import RecursiveCharacterTextSplitter

# New Pinecone SDK imports
from pinecone import Pinecone, ServerlessSpec

# Always load Pinecone API key from streamlit/secrets.toml
def init_pinecone():
    api_key = st.secrets["PINECONE_API_KEY"]
    # Use default free tier region
    region = "us-east-1"
    # Use the new Pinecone client
    pc = Pinecone(api_key=api_key)
    return pc, region

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Pinecone index from documents.")
    parser.add_argument("--input_dir", type=str, default="files to generate default knowledge", help="Folder containing source files.")
    parser.add_argument("--index_name", type=str, required=True, help="Name of the Pinecone index.")
    parser.add_argument("--embedding_model", type=str, default="text-embedding-ada-002", help="Embedding model to use.")
    parser.add_argument("--dimension", type=int, default=1536, help="Dimension of embedding vectors.")
    args = parser.parse_args()

    # Initialize Pinecone client and region
    pc, region = init_pinecone()

    # Create index if not exists (new SDK)
    indexes = pc.list_indexes()
    if args.index_name not in indexes:
        pc.create_index(
            name=args.index_name,
            dimension=args.dimension,
            spec=ServerlessSpec(cloud="aws", region=region)
        )
        print(f"Created Pinecone index: {args.index_name}")
    else:
        print(f"Using existing Pinecone index: {args.index_name}")

    # Load documents
    docs = load_files(args.input_dir)
    print(f"Loaded {len(docs)} documents from {args.input_dir}")

    # Chunk documents for better retrieval granularity
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunked_docs = []
    for doc in docs:
        splits = text_splitter.create_documents([doc.page_content])
        # Attach metadata from original doc
        for split in splits:
            split.metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
        chunked_docs.extend(splits)
    print(f"Split into {len(chunked_docs)} chunks.")

    # Create embeddings
    embedding = OpenAIEmbeddings(model=args.embedding_model)

    # Upload to Pinecone using LangChain (new API)
    vectorstore = LangchainPinecone.from_documents(
        documents=chunked_docs,
        embedding=embedding,
        index_name=args.index_name
    )
    print(f"Chunks uploaded to Pinecone index: {args.index_name}")
