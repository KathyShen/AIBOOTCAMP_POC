from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os
import streamlit as st 

def build_qa_chain(vectorstore, api_key=None):
    if api_key is None: # admin use the KEY from .env
        from dotenv import load_dotenv
        load_dotenv()
        api_key = st.secrets["OPENAI_API_KEY"]
        #api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(openai_api_key=api_key, temperature=0)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
