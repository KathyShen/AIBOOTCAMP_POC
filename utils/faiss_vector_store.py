import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def save_to_faiss(docs, embedding=None, chunk_size=500, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # If docs are already split, skip splitting
    if hasattr(docs, '__iter__') and all(isinstance(doc, str) for doc in docs):
        splits = docs
    else:
        splits = splitter.split_documents(docs)
    if embedding is None:
        embedding = OpenAIEmbeddings()
    db = FAISS.from_documents(splits, embedding)
    return db

def load_faiss():
    # In-memory mode: loading from disk is not supported
    raise NotImplementedError("FAISS in-memory mode does not support loading from disk.")