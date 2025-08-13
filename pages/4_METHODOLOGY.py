import streamlit as st
import streamlit as st


st.set_page_config(
    layout="centered",
    page_title="Methodology & Data Flow"
)

st.title("Methodology: Data & Logic Flow")

st.markdown("""
This page explains the overall methodology, data flow, and logic flow of the PETs Advisor App. The diagrams below illustrate how user input, knowledge bases, and AI models interact to deliver personalized PETs advice and RAG-enhanced Q&A.
""")

    
# Data Flow Chart (Mermaid as code block)
st.markdown("#### **Data Flow Overview**")
st.code('''mermaid
graph TD
    A[User Input: Problem Statement, Objective, PETs] --> B[Streamlit App]
    B --> C[Default PETs Knowledge Base (Chroma DB)]
    B --> D[User Uploaded Documents]
    D --> E[User Vector DB (Chroma, in-memory)]
    C & E --> F[Retriever(s)]
    F --> G[LLM (OpenAI)]
    G --> H[Response: Q&A, PETs Advice, Checklist]
''', language='markdown')

# Logic Flow Chart (Mermaid as code block)
st.markdown("#### **Logic Flow Overview**")
st.code('''mermaid
graph TD
    U[User: Selects Objective, Enters Problem, Chooses PETs] --> S[Streamlit Page]
    S --> V[Build/Load Vector DBs]
    V --> R[Combine Retrievers]
    R --> Q[Run RetrievalQA Chain]
    Q --> LLM[LLM Reasoning]
    LLM --> O[Output: Challenges, Use Cases, PETs, Checklist]
''', language='markdown')

st.markdown("""
**Legend:**
- **Chroma DB**: Vector database for storing and retrieving document embeddings.
- **Retriever(s)**: Logic to fetch relevant context from one or more knowledge bases.
- **LLM**: Large Language Model (OpenAI GPT) for reasoning and answer generation.

---

### Methodology Steps
1. **User Input**: User provides scenario details, objectives, and PETs of interest.
2. **Knowledge Base**: The app uses a default PETs knowledge base and optionally user-uploaded documents.
3. **Vectorization**: Documents are embedded and stored in Chroma vector DBs.
4. **Retrieval**: The app combines retrievers from both default and user knowledge bases.
5. **LLM Reasoning**: The LLM receives the user query and retrieved context, then generates answers, advice, and checklists.
6. **Output**: The app displays results, including relevant use cases, PETs suggestions, and adoption checklists.

---

For more details, see the code and documentation in this repository.
""")



