# user_input_handler.py
import streamlit as st

def get_user_inputs():
    st.markdown("### 1. Describe your data privacy problem statement")
    problem_statement = st.text_area("Problem Statement", help="Describe your scenario and privacy needs.")
    st.markdown("### 2. Which PET(s) are you interested in?")
    pet_interest = st.text_input("PET(s) of Interest (comma separated)", help="E.g. Differential Privacy, Homomorphic Encryption")
    return problem_statement, [pet.strip() for pet in pet_interest.split(",") if pet.strip()]