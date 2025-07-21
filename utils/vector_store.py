import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

def save_to_chroma(docs, persist_directory="vector_db"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = splitter.split_documents(docs)
    db = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=persist_directory
    )
    db.persist()

def load_chroma(persist_directory="vector_db"):
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=OpenAIEmbeddings()
    )