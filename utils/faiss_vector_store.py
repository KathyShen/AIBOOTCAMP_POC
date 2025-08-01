import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def save_to_faiss(docs, embedding=None, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = []
    for doc in docs:
        meta = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
        if hasattr(doc, 'page_content'):
            chunks = splitter.create_documents([doc.page_content])
            for chunk in chunks:
                chunk.metadata = meta
            splits.extend(chunks)
        else:
            splits.append(doc)
    if embedding is None:
        embedding = OpenAIEmbeddings()
    db = FAISS.from_documents(splits, embedding)
    return db

def load_faiss():
    # In-memory mode: loading from disk is not supported
    raise NotImplementedError("FAISS in-memory mode does not support loading from disk.")