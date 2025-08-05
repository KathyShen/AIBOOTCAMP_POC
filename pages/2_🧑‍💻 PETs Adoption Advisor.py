# For Streamlit Cloud/Chroma sqlite compatibility (Python 3.11)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st

import os
from utils.sidebar import show_sidebar
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings



show_sidebar()

# ...existing login and sidebar logic...

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🧑‍💻 PETs Adoption Advisor")

def get_user_inputs():
    st.markdown("### 1. What are you trying to achieve?")
    objective_options = [
        "Match Common Customers With Different Datasets",
        "Enrich Datasets With Data From Other Organizations",
        "Make More Data Available for AI"
    ]
    key_objective = st.selectbox(
        "Select Key Objective",
        options=objective_options
    )
    st.markdown("### 2. Please elaborate on your problem statement with more details:")
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

        # Use Chroma for default knowledge base
        embedding = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=st.session_state.api_key)
        main_db = Chroma(
            persist_directory="vector_db/default_db",
            embedding_function=embedding
        )
        retrievers = [main_db.as_retriever()]
        # If user uploaded files in page 1, combine with their Chroma DB
        user_db = st.session_state.get("user_db")
        if user_db:
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

       
        # Chain-of-thoughts: each step includes previous outputs as context
        # 1. Summarize privacy challenges
        challenge_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}

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

        step1_output = run_and_store(challenge_prompt, "#### Step 1: Key Data Privacy Challenges", "step1_output")


        # 2. Assess alignment between objective and problem statement, and select relevant use cases
        alignment_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        Key Data Privacy Challenges: {step1_output}

        Step 2a: Assess whether the selected objective aligns with the problem statement described. If not, explain the mismatch and suggest how to clarify or adjust the objective or problem statement.
        """
        alignment_output = run_and_store(alignment_prompt, "#### Step 2a: Objective-Problem Alignment Assessment", "step2_output")

        # 2b. Retrieve and display relevant use cases from the database
        usecase_prompt = f"""
        Based on the user's scenario objective and problem statement below, select the most relevant use cases from the knowledge base:

        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}

        For each relevant use case, provide:
        - The use case name or title
        - What objective or problem it solved that is similar to the user's case
        - What PET was used in that use case
        Present the results as a simple list, one use case per bullet point, with the above details for each.
        """
        def run_and_store_usecases(prompt, section_title, key):
            chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
            output = chain.invoke({"query": prompt})
            answer = output["result"] if isinstance(output, dict) and "result" in output else output
            # Try to format as bullet points for clarity
            import re
            lines = answer.splitlines()
            bullet_lines = []
            for line in lines:
                if re.match(r"^[-*•] ", line.strip()):
                    bullet_lines.append(line)
                elif line.strip():
                    bullet_lines.append(f"- {line.strip()}")
            formatted_answer = "\n".join(bullet_lines)
            st.markdown(section_title)
            st.write(formatted_answer)
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

        run_and_store_usecases(usecase_prompt, "#### Step 2b: Relevant Use Cases from Knowledge Base", "step2b_output")

        # 3. Suggest PETs
        pet_prompt = f"""
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        Key Data Privacy Challenges: {step1_output}
        Objective-Problem Alignment Assessment: {alignment_output}

        Step 3: Based on the above, suggest potential Privacy Enhancing Technologies (PETs) that could address these challenges. List each PET as a bullet point and explain your reasoning for each.
        """
        # Custom post-processing to ensure bullet points for PETs
        def run_and_store_bullets(prompt, section_title, key):
            chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
            output = chain.invoke({"query": prompt})
            answer = output["result"] if isinstance(output, dict) and "result" in output else output
            # Try to format PETs as bullet points if not already
            import re
            lines = answer.splitlines()
            bullet_lines = []
            for line in lines:
                # If line looks like a PET name (heuristic: matches known PETs or starts with PET-like phrase)
                if re.match(r"^(Differential Privacy|Homomorphic Encryption|Synthetic Data|Federated Learning|Secure Multi-Party Computation|Trusted Execution Environments|Zero-knowledge Proof)", line.strip(), re.I):
                    bullet_lines.append(f"- {line.strip()}")
                elif re.match(r"^[-*•] ", line.strip()):
                    bullet_lines.append(line)
                else:
                    bullet_lines.append(line)
            formatted_answer = "\n".join(bullet_lines)
            st.markdown(section_title)
            st.write(formatted_answer)
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

        step3_output = run_and_store_bullets(pet_prompt, "#### Step 3: Suggested PETs", "step3_output")


        # 4. Assess suitability of user-indicated PETs
        if pet_interest:
            suitability_prompt = f"""
            Scenario Objective: {key_objective}
            User Problem Statement: {problem_statement}
            PETs of Interest: {', '.join(pet_interest)}
            Key Data Privacy Challenges: {step1_output}
            Objective-Problem Alignment Assessment: {alignment_output}
            Suggested PETs: {step3_output}

            Step 4: Assess whether the following PETs are suitable for this scenario: {', '.join(pet_interest)}. Justify your assessment using the above context.
            """
            step4_output = run_and_store(suitability_prompt, "#### Step 4: Suitability Assessment of User-Selected PETs", "step4_output")
        else:
            step4_output = None



        # 5. Suggest checklist questions for adopting PETs, logic based on user PETs and suggested PETs
        # Try to extract suggested PETs as a list from step3_output (LLM output, so fallback to string match)
        import re
        def extract_pet_names(text):
            # Try to extract PETs from a bulleted or comma-separated list
            pets = set()
            # Bullet points
            for line in text.splitlines():
                m = re.match(r"[-*•]\s*([A-Za-z0-9\- ]+)", line)
                if m:
                    pets.add(m.group(1).strip())
            # Comma separated
            if not pets:
                for part in re.split(r",|;|\n", text):
                    part = part.strip()
                    if part and part.lower() not in ["potential pets include", "suggested pets:"]:
                        # Heuristic: only add if matches known PETs
                        for known in ["Differential Privacy", "Homomorphic Encryption", "Synthetic Data", "Federated Learning", "Secure Multi-Party Computation", "Trusted Execution Environments", "Zero-knowledge Proof"]:
                            if known.lower() in part.lower():
                                pets.add(known)
            return list(pets)

        suggested_pets = extract_pet_names(step3_output)
        user_pets = set(pet_interest)
        # If user PETs overlap with suggested PETs, use those; else use suggested PETs
        relevant_pets = list(user_pets & set(suggested_pets)) if user_pets & set(suggested_pets) else suggested_pets

        adoption_prompt = f"""
        Industry/Domain: Please infer from the scenario/problem statement if possible.
        Scenario Objective: {key_objective}
        User Problem Statement: {problem_statement}
        Key Data Privacy Challenges: {step1_output}
        Objective-Problem Alignment Assessment: {alignment_output}
        Suggested PETs: {step3_output}
        PETs to focus on: {', '.join(relevant_pets) if relevant_pets else 'None'}

        Step 5: For each PET listed above, generate a checklist of relevant adoption questions for decision makers to consider, tailored to the industry/domain and objective. If no PETs are listed, suggest general adoption questions for privacy-enhancing technologies.
        """
        run_and_store(adoption_prompt, "#### Step 5: Adoption Checklist Questions for PETs", "step5_output")

    except Exception as e:
        st.error(f"An error occurred: {e}")