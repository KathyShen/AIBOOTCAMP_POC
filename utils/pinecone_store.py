
from pinecone import Pinecone
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone


# Initialize Pinecone client from Streamlit secrets
def init_pinecone():
    api_key = st.secrets["PINECONE_API_KEY"]
    return Pinecone(api_key=api_key)

embedding = OpenAIEmbeddings(model="text-embedding-ada-002")


# Load pre-existing Pinecone index using langchain's Pinecone wrapper
def load_pinecone(index_name, pinecone_client):
    index = pinecone_client.Index(index_name)
    return LangchainPinecone(index, embedding)

# Save documents to Pinecone index using langchain's Pinecone wrapper
def save_to_pinecone(docs, index_name, pinecone_client):
    index = pinecone_client.Index(index_name)
    return LangchainPinecone.from_documents(
        docs,
        embedding,
        index
    )