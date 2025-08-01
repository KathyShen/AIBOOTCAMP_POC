# For Streamlit Cloud/Chroma sqlite compatibility (Python 3.11)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from utils.file_handler import load_files_from_uploads
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from utils.sidebar import show_sidebar
import openai
from langchain.prompts import PromptTemplate

show_sidebar()

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()

st.title("🧠 PETs Knowledge Hub")

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


# --- Chroma setup ---
embedding = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=st.session_state.api_key)


# --- User-uploaded file handling and user_db creation ---
user_db = None
if use_user_files:
    uploaded_files = st.file_uploader("Upload 1-10 documents (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    files = st.session_state.get("uploaded_files")
    if files and (1 <= len(files) <= 10):
        if st.button("Generate Vector DB") or st.session_state.get("force_user_db_rebuild"):
            try:
                os.environ["OPENAI_API_KEY"] = st.session_state.api_key
                openai.api_key = st.session_state.api_key
                docs = load_files_from_uploads(files)
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
                chunked_docs = []
                for doc in docs:
                    splits = text_splitter.create_documents([doc.page_content])
                    for split in splits:
                        split.metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
                    chunked_docs.extend(splits)
                user_db = Chroma.from_documents(
                    documents=chunked_docs,
                    embedding=embedding
                )
                st.session_state.user_db = user_db
                st.session_state.vector_db_ready = True
                st.session_state.force_user_db_rebuild = False
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
            user_db = st.session_state.get("user_db")
    elif files and not (1 <= len(files) <= 10):
        st.warning("Please upload between 1 and 10 files.")
    else:
        st.session_state.vector_db_ready = not use_user_files
else:
    st.session_state.vector_db_ready = True


# --- Q&A Section ---
if st.session_state.get("vector_db_ready"):
    # Load the persistent Chroma DB for default knowledge
    main_db = Chroma(
        persist_directory="vector_db/default_db",
        embedding_function=embedding
    )
    retrievers = [main_db.as_retriever()]
    # If user uploaded files, combine with their Chroma DB
    user_db = st.session_state.get("user_db")
    if use_user_files and user_db:
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
    query = st.text_area(
        "What questions do you have about PETs? Enter your query below to search the knowledge base.",
        key="qa_input"
    )
    if st.button("Ask - LLM Powered with RAG") and query:
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
            # Extract and format relevant context
            context_blurbs = []
            if isinstance(output, dict) and "source_documents" in output:
                for i, doc in enumerate(output["source_documents"], 1):
                    # Try to get a snippet or content from the document
                    snippet = doc.page_content if hasattr(doc, "page_content") else str(doc)
                    # Optionally, show source if available
                    source = doc.metadata.get("source") if hasattr(doc, "metadata") and "source" in doc.metadata else None
                    context_blurbs.append(f"**Context {i}:** {snippet[:500]}" + (f"\n_Source: {source}_" if source else ""))
            st.session_state.qa_history.append((query, answer, context_blurbs))
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
        for i, qa in enumerate(st.session_state.qa_history, 1):
            q = qa[0]
            a = qa[1]
            contexts = qa[2] if len(qa) > 2 else []
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")
            if contexts:
                with st.expander(f"Show retrieved context for Q{i}"):
                    for ctx in contexts:
                        st.markdown(ctx)
