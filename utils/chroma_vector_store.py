import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

def save_to_chroma(docs, embedding=None, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # If docs are already split, skip splitting
    if hasattr(docs, '__iter__') and all(isinstance(doc, str) for doc in docs):
        splits = docs
    else:
        splits = splitter.split_documents(docs)
    if embedding is None:
        embedding = OpenAIEmbeddings()
    db = Chroma.from_documents(
        documents=splits,
        embedding=embedding
    )
    return db

def load_chroma():
    # In-memory mode: loading from disk is not supported
    raise NotImplementedError("Chroma in-memory mode does not support loading from disk.")