
import streamlit as st
import os
from utils.sidebar import show_sidebar
from utils.pinecone_store import init_pinecone, load_pinecone
from utils.faiss_vector_store import save_to_faiss



show_sidebar()

# ...existing login and sidebar logic...

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🧑‍💻 PETs Adoption Advisor")

def get_user_inputs():
    st.markdown("### 1. What are you trying to achieve?")
    objective_options = [
        "Match Common Customers",
        "Enrich Datasets With Data From Other Organizations",
        "Make More Data Available for AI"
    ]
    key_objective = st.selectbox(
        "Select Key Objective",
        options=objective_options
    )
    st.markdown("### 2. Please ellaborate your scenario with more details:")
    problem_statement = st.text_area("Problem Statement", help="Example: We want to collaborate with other banks to detect fraudulent transactions across our combined datasets without exposing sensitive customer information or violating data privacy regulations. What technologies and strategies can enable secure analytics and fraud detection in this scenario?")
    st.markdown("### 3. Which PET(s) are you interested in?")
    pet_options = [
        "Differential Privacy",
        "Homomorphic Encryption",
        "Synthetic Data",
        "Federated Learning",
        "Secure Multi-Party Computation",
        "Trusted Execution Environments",
        "Zero-knowledge Proof"
    ]
    pet_interest = st.multiselect(
        "Select PET(s) of Interest",
        options=pet_options,
        help="You can select one or more privacy-enhancing technologies (PETs)."
    )
    return key_objective,problem_statement, pet_interest


# --- User Input ---
key_objective, problem_statement, pet_interest = get_user_inputs()

# Input validation
if not problem_statement:
    st.info("Please provide a problem statement to proceed.")
    st.stop()



if st.button("Analyze & Advise"):
    try:
        # Set OpenAI API key if needed
        if hasattr(st.session_state, "api_key"):
            os.environ["OPENAI_API_KEY"] = st.session_state.api_key

        # Use Pinecone for default knowledge base
        pinecone_client = init_pinecone()
        main_db = load_pinecone(index_name="default-knowledge", pinecone_client=pinecone_client)
        retrievers = [main_db.as_retriever()]
        # If user uploaded files in page 1, combine with Chroma in-memory vector DB
        if "temp_db_dir" in st.session_state:
            # You may need to reload docs from temp_db_dir, e.g. with load_files
            from utils.file_handler import load_files
            docs = load_files(st.session_state.temp_db_dir)
            user_db = save_to_faiss(docs)
            retrievers.append(user_db.as_retriever())
        # Combine retrievers if more than one
        if len(retrievers) > 1:
            from langchain.retrievers import EnsembleRetriever
            retriever = EnsembleRetriever(retrievers=retrievers)
        else:
            retriever = retrievers[0]

        from langchain.chains import RetrievalQA
        from langchain.chat_models import ChatOpenAI
        llm = ChatOpenAI(openai_api_key=st.session_state.api_key, temperature=0)

        # Helper to run QA and show context
        def run_qa_and_show(prompt, section_title):
            chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
            output = chain.invoke({"query": prompt})
            answer = output["result"] if isinstance(output, dict) and "result" in output else output
            st.markdown(section_title)
            st.write(answer)
            # Show context
            context_blurbs = []
            if isinstance(output, dict) and "source_documents" in output:
                for i, doc in enumerate(output["source_documents"], 1):
                    snippet = doc.page_content if hasattr(doc, "page_content") else str(doc)
                    source = doc.metadata.get("source") if hasattr(doc, "metadata") and "source" in doc.metadata else None
                    context_blurbs.append(f"**Context {i}:** {snippet[:500]}" + (f"\n_Source: {source}_" if source else ""))
            if context_blurbs:
                with st.expander(f"Show retrieved context for {section_title.replace('#### ','')}"):
                    for ctx in context_blurbs:
                        st.markdown(ctx)


        # Chain-of-thoughts: each step includes previous outputs as context
        # 1. Summarize privacy challenges
        challenge_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        PETs of Interest: {', '.join(pet_interest) if pet_interest else 'None provided'}

        Step 1: Summarize the key data privacy challenges in this scenario. Be specific and concise.
        """
        st.session_state.step1_output = None
        def run_and_store(prompt, section_title, key):
            chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
            output = chain.invoke({"query": prompt})
            answer = output["result"] if isinstance(output, dict) and "result" in output else output
            st.markdown(section_title)
            st.write(answer)
            st.session_state[key] = answer
            # Show context
            context_blurbs = []
            if isinstance(output, dict) and "source_documents" in output:
                for i, doc in enumerate(output["source_documents"], 1):
                    snippet = doc.page_content if hasattr(doc, "page_content") else str(doc)
                    source = doc.metadata.get("source") if hasattr(doc, "metadata") and "source" in doc.metadata else None
                    context_blurbs.append(f"**Context {i}:** {snippet[:500]}" + (f"\n_Source: {source}_" if source else ""))
            if context_blurbs:
                with st.expander(f"Show retrieved context for {section_title.replace('#### ','')}"):
                    for ctx in context_blurbs:
                        st.markdown(ctx)
            return answer

        step1_output = run_and_store(challenge_prompt, "#### Key Data Privacy Challenges", "step1_output")

        # 2. Suggest PETs
        pet_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        PETs of Interest: {', '.join(pet_interest) if pet_interest else 'None provided'}
        Key Data Privacy Challenges: {step1_output}

        Step 2: Based on the above, suggest potential Privacy Enhancing Technologies (PETs) that could address these challenges. Explain your reasoning.
        """
        step2_output = run_and_store(pet_prompt, "#### Suggested PETs", "step2_output")

        # 3. Assess suitability of user-indicated PETs
        if pet_interest:
            suitability_prompt = f"""
            Scenario Objective: {key_objective}
            User Problem Statement: {problem_statement}
            PETs of Interest: {', '.join(pet_interest)}
            Key Data Privacy Challenges: {step1_output}
            Suggested PETs: {step2_output}

            Step 3: Assess whether the following PETs are suitable for this scenario: {', '.join(pet_interest)}. Justify your assessment using the above context.
            """
            step3_output = run_and_store(suitability_prompt, "#### Suitability Assessment of User-Selected PETs", "step3_output")
        else:
            step3_output = None

        # 4. Suggest adoption questions
        adoption_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        PETs of Interest: {', '.join(pet_interest) if pet_interest else 'None provided'}
        Key Data Privacy Challenges: {step1_output}
        Suggested PETs: {step2_output}
        Suitability Assessment: {step3_output if step3_output else 'N/A'}

        Step 4: Suggest relevant adoption questions for decision makers to explore for this scenario and privacy needs, using all the above context.
        """
        run_and_store(adoption_prompt, "#### Adoption Questions for Decision Makers", "step4_output")

    except Exception as e:
        st.error(f"An error occurred: {e}")