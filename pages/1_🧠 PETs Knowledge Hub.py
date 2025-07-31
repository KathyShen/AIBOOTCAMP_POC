import streamlit as st
from utils.file_handler import load_files
from utils.vector_store import save_to_chroma, load_chroma

import shutil
import os
import uuid
from utils.sidebar import show_sidebar
import openai
from langchain.prompts import PromptTemplate
#from dotenv import load_dotenv

show_sidebar()

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🧠 PETs Knowledge Hub")
st.markdown("<span style='font-size:20px;'>(Q&A Powered by RAG)</span>", unsafe_allow_html=True)

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

is_admin = st.session_state.get("username", "") == "admin"

if is_admin:
    admin_key = st.secrets['OPENAI_API_KEY']
    st.session_state.api_key = admin_key
    st.session_state.api_key_valid = True

def test_openai_api_key(api_key):
    try:
        openai.api_key = api_key
        openai.models.list()
        return True
    except Exception as e:
        return False

if not is_admin and not st.session_state.api_key_valid:
    if st.session_state.get("api_key_error"):
        st.warning("Invalid API Key. Please enter a valid OpenAI API Key.")
        st.session_state.api_key_error = False
    else:
        st.warning("Please enter your OpenAI API Key to continue.")
    api_key_input = st.text_input("Your OpenAI API Key", type="password")
    if st.button("Submit API Key") and api_key_input:
        if test_openai_api_key(api_key_input):
            st.session_state.api_key = api_key_input
            st.session_state.api_key_valid = True
            st.success("API Key validated! You can now proceed.")
            st.rerun()
        else:
            st.session_state.api_key = ""
            st.session_state.api_key_valid = False
            st.session_state.api_key_error = True
            st.rerun()
    st.stop()

# --- Optional file upload logic ---
choice = st.radio(
    "Would you like to upload your own files for Q&A?",
    ("Use default knowledge base", "Upload your own files to enhance the knowledge base")
)

use_user_files = choice == "Upload your own files to enhance the knowledge base"

if use_user_files:
    if "temp_db_dir" not in st.session_state:
        st.session_state.temp_db_dir = f"vector_db/user_temp_{uuid.uuid4().hex}"

    uploaded_files = st.file_uploader("Upload 5-10 documents (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    if st.session_state.get("uploaded_files"):
        files = st.session_state.uploaded_files
        if not (5 <= len(files) <= 10):
            st.warning("Please upload between 5 and 10 files.")
        else:
            if st.button("Generate Vector DB"):
                try:
                    upload_dir = "uploads"
                    shutil.rmtree(upload_dir, ignore_errors=True)
                    os.makedirs(upload_dir, exist_ok=True)
                    for file in files:
                        with open(os.path.join(upload_dir, file.name), "wb") as f:
                            f.write(file.getbuffer())
                    os.environ["OPENAI_API_KEY"] = st.session_state.api_key
                    openai.api_key = st.session_state.api_key
                    docs = load_files(upload_dir)
                    save_to_chroma(docs, persist_directory=st.session_state.temp_db_dir)
                    st.session_state.vector_db_ready = True
                    st.success("Vector DB created. You can now ask questions.")
                except Exception as e:
                    if "401" in str(e) or "invalid_api_key" in str(e):
                        st.session_state.api_key = ""
                        st.session_state.api_key_valid = False
                        st.session_state.api_key_error = True
                        st.rerun()
                    else:
                        st.error(f"Error generating vector DB: {e}")
else:
    # If not using user files, set vector_db_ready to True to enable Q&A
    st.session_state.vector_db_ready = True

# --- Q&A Section ---
if st.session_state.get("vector_db_ready"):
    # Always load the default knowledge DB
    default_db_path = os.path.join("vector_db", "default knowledge")
    main_db = load_chroma(default_db_path)
    retrievers = [main_db.as_retriever()]
    # If user uploaded files, combine with their DB
    if use_user_files and "temp_db_dir" in st.session_state:
        user_db = load_chroma(st.session_state.temp_db_dir)
        retrievers.append(user_db.as_retriever())
    # Combine retrievers if more than one
    if len(retrievers) > 1:
        try:
            from langchain.retrievers import EnsembleRetriever
            retriever = EnsembleRetriever(retrievers=retrievers)
        except ImportError:
            retriever = retrievers[-1]
    else:
        retriever = retrievers[0]

    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []
    query = st.text_area("Enter your question", key="qa_input")
    if st.button("Ask") and query:
        os.environ["OPENAI_API_KEY"] = st.session_state.api_key
        openai.api_key = st.session_state.api_key
        from langchain.chains import RetrievalQA
        from langchain.chat_models import ChatOpenAI
        llm = ChatOpenAI(openai_api_key=st.session_state.api_key, temperature=0)

        template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say \"thanks for asking!\" at the end of the answer.
        {context}
        Question: {question}
        Helpful Answer:"""
        QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

        chain = RetrievalQA.from_chain_type(
            llm=llm, 
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
        )

        try:
            output = chain.invoke({"query": query})
            answer = output["result"] if isinstance(output, dict) and "result" in output else output
            st.session_state.qa_history.append((query, answer))
        except Exception as e:
            if "401" in str(e) or "invalid_api_key" in str(e):
                st.session_state.api_key = ""
                st.session_state.api_key_valid = False
                st.session_state.api_key_error = True
                st.rerun()
            else:
                st.error(f"Error during Q&A: {e}")
    # Show Q&A history
    if st.session_state.get("qa_history"):
        st.markdown("---")
        st.markdown("### Chat History")
        for i, (q, a) in enumerate(st.session_state.qa_history, 1):
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")

import atexit
def cleanup_temp_db():
    temp_db_dir = st.session_state.get("temp_db_dir")
    if temp_db_dir and os.path.exists(temp_db_dir):
        shutil.rmtree(temp_db_dir, ignore_errors=True)
atexit.register(cleanup_temp_db)