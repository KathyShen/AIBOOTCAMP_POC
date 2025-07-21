import os
import streamlit as st 
#from dotenv import load_dotenv
#load_dotenv()

USERS = {
    "admin": st.secrets['ADMIN_PASSWORD'],
    "user": st.secrets['USER_PASSWORD']
    #"admin": os.getenv("ADMIN_PASSWORD", "admin123"),
    #"user": os.getenv("USER_PASSWORD", "user123")
}

def authenticate(username, password):
    return USERS.get(username) == password

def get_api_key(username):
    if username == "admin":
        return st.secrets["OPENAI_API_KEY"]
        #return os.getenv("OPENAI_API_KEY")
    return ""