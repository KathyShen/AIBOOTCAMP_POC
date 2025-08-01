import streamlit as st
from utils.chroma_vector_store import load_chroma
from utils.rag_pipeline import build_qa_chain
from utils.sidebar import show_sidebar
import os
#from dotenv import load_dotenv

#show_sidebar()

# ...existing login and sidebar logic...

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🔍 PETs Adoption Advisor")

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

# --- User Input ---
problem_statement, pet_interest = get_user_inputs()


if st.button("Analyze & Advise") and problem_statement:
    # Use Pinecone for default knowledge base
    from utils.pinecone_store import init_pinecone, load_pinecone
    pinecone_client = init_pinecone()
    main_db = load_pinecone(index_name="default-knowledge", pinecone_client=pinecone_client)
    retrievers = [main_db.as_retriever()]
    # If user uploaded files in page 1, combine with Chroma in-memory vector DB
    if "temp_db_dir" in st.session_state:
        from utils.chroma_vector_store import load_chroma
        user_db = load_chroma(st.session_state.temp_db_dir)
        retrievers.append(user_db.as_retriever())
    # Combine retrievers if more than one
    if len(retrievers) > 1:
        from langchain.retrievers import EnsembleRetriever
        retriever = EnsembleRetriever(retrievers=retrievers)
    else:
        retriever = retrievers[0]

    # Multi-step Q&A using multiquery
    from langchain.chains import RetrievalQA
    from langchain.chat_models import ChatOpenAI
    llm = ChatOpenAI(openai_api_key=st.session_state.api_key, temperature=0)

    # 1. Summarize privacy challenges
    challenge_prompt = f"Summarize the key data privacy challenges in this scenario: {problem_statement}"
    challenge_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    challenges = challenge_chain.run(challenge_prompt)
    st.markdown("#### Key Data Privacy Challenges")
    st.write(challenges)

    # 2. Suggest PETs
    pet_prompt = f"Based on the scenario, suggest potential Privacy Enhancing Technologies (PETs) that could address these challenges."
    pet_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    suggested_pets = pet_chain.run(pet_prompt)
    st.markdown("#### Suggested PETs")
    st.write(suggested_pets)

    # 3. Assess suitability of user-indicated PETs
    if pet_interest:
        suitability_prompt = f"Assess whether the following PETs are suitable for this scenario: {', '.join(pet_interest)}. Justify your assessment."
        suitability_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        suitability = suitability_chain.run(suitability_prompt)
        st.markdown("#### Suitability Assessment of User-Selected PETs")
        st.write(suitability)

    # 4. Suggest adoption questions
    adoption_prompt = f"Suggest relevant adoption questions for decision makers to explore for this scenario and privacy needs."
    adoption_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    adoption_questions = adoption_chain.run(adoption_prompt)
    st.markdown("#### Adoption Questions for Decision Makers")
    st.write(adoption_questions)