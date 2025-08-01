import os
import streamlit as st

# Load secrets using Streamlit
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]


from utils.pinecone_store import init_pinecone, load_pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone as LangchainPinecone
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


def main():
    # Initialize Pinecone client
    pinecone_client = init_pinecone()
    # Load the default-knowledge index
    main_db = load_pinecone(index_name="default-knowledge", pinecone_client=pinecone_client)
    retriever = main_db.as_retriever()

    # Initialize LLM
    llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"], temperature=0)

    # Build the RetrievalQA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    print("Ask your question about PETs (type 'exit' to quit):")
    while True:
        query = input("Q: ")
        if query.lower() in ["exit", "quit"]:
            break
        output = chain.invoke({"query": query})
        answer = output["result"] if isinstance(output, dict) and "result" in output else output
        print("\nA:", answer)
        # Show context
        if isinstance(output, dict) and "source_documents" in output:
            print("\n--- Retrieved Context ---")
            for i, doc in enumerate(output["source_documents"], 1):
                snippet = doc.page_content if hasattr(doc, "page_content") else str(doc)
                source = doc.metadata.get("source") if hasattr(doc, "metadata") and "source" in doc.metadata else None
                print(f"Context {i}: {snippet[:500]}")
                if source:
                    print(f"Source: {source}")
            print("------------------------\n")

if __name__ == "__main__":
    main()