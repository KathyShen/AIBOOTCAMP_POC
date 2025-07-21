import streamlit as st

def show_sidebar():
    if "username" in st.session_state and st.session_state.username:
        st.sidebar.success(f"Logged in as {st.session_state.username}")
    