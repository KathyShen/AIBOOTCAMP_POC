
from pinecone import Pinecone
import streamlit as st
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone


# Initialize Pinecone client from Streamlit secrets
def init_pinecone():
    api_key = st.secrets["PINECONE_API_KEY"]
    return Pinecone(api_key=api_key)

embedding = OpenAIEmbeddings(model="text-embedding-ada-002")


# Load pre-existing Pinecone index using langchain's Pinecone wrapper
def load_pinecone(index_name, pinecone_client):
    return LangchainPinecone(index_name=index_name, embedding=embedding, pinecone_api= pinecone_client)

# Save documents to Pinecone index using langchain's Pinecone wrapper
def save_to_pinecone(docs, index_name, pinecone_client):
    return LangchainPinecone.from_documents(
        documents=docs,
        embedding=embedding,
        index_name=index_name,
        pinecone_api=pinecone_client
    )