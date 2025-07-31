import pinecone
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

# Initialize Pinecone from Streamlit secrets
def init_pinecone():
    api_key = st.secrets["PINECONE_API_KEY"]
    environment = st.secrets.get("PINECONE_ENVIRONMENT", "us-east-1-aws")  # Change default if needed
    pinecone.init(api_key=api_key, environment=environment)

embedding = OpenAIEmbeddings(model="text-embedding-ada-002")

# Load pre-existing Pinecone index
def load_pinecone(index_name):
    return Pinecone(index_name=index_name, embedding=embedding)

# Save documents to Pinecone index
def save_to_pinecone(docs, index_name):
    return Pinecone.from_documents(
        documents=docs,
        embedding=embedding,
        index_name=index_name
    )