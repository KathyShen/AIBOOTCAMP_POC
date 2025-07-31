# user_input_handler.py
import streamlit as st

def get_user_inputs():
    st.markdown("### 1. Describe your data privacy problem statement")
    problem_statement = st.text_area("Problem Statement", help="Describe your scenario and privacy needs.")
    st.markdown("### 2. Which PET(s) are you interested in?")
    pet_options = [
        "Differential Privacy",
        "Homomorphic Encryption",
        "Synthetic Data",
        "Zero-knowledge Proof"
    ]
    pet_interest = st.multiselect(
        "Select PET(s) of Interest",
        options=pet_options,
        help="You can select one or more privacy-enhancing technologies (PETs)."
    )
    return problem_statement, pet_interest