import streamlit as st
from utils.vector_store import load_chroma
from utils.rag_pipeline import build_qa_chain
from utils.sidebar import show_sidebar
from utils.user_input_handler import get_user_inputs
import os
#from dotenv import load_dotenv

#show_sidebar()

# ...existing login and sidebar logic...

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🔍 PETs Adoption Advisor")

# --- User Input ---
problem_statement, pet_interest = get_user_inputs()

if st.button("Analyze & Advise") and problem_statement:
    # Load default and user vector DBs
    default_db_path = os.path.join("vector_db", "default knowledge")
    main_db = load_chroma(default_db_path)
    retrievers = [main_db.as_retriever()]
    if "temp_db_dir" in st.session_state:
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