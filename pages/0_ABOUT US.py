import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="PETs Advisor App"
)
# endregion <--------- Streamlit App Configuration --------->

st.title("About Us")

st.write("This is a Streamlit App that demonstrates how to use the OpenAI API to build knowledge database and provide RAG enhanced Q&A response, as well as to provide personalised PETs adoption advices based on specific user scenarios.")

st.markdown("<u><b>Regarding the Login</b></u>", unsafe_allow_html=True)
st.markdown("""
- **For Admin users:** You will be able to access all features without the need to provide your own OpenAI API key, as the system provides you a key automatically at the backend.  
- **For Normal users:** You will need to submit your own OpenAI API key to proceed on each page. The key you submitted is only temporarily stored in the session state and will not be saved permanently.
""")

st.markdown("<u><b>How to use this App</b></u>", unsafe_allow_html=True)
with st.expander("**Feature 1 PETs Knowledge Hub:**"):
    st.write("Build Your Own Knowledge Base and Get RAG Enhanced Q&A Response")
    st.write("1. (Optional) Upload your documents to enhance the default PETs Knowledge Base.")
    st.write("2. Once the documents are uploaded, you may generate the enhanced Knowledge Base.")
    st.write("3. Based on the knowledge base, you can ask questions and retrieve relevant context from the knowledge base.")

with st.expander("**Feature 2 PETs Adoption Advisor:**"):
    st.write("Submit Your Own Problem Statement and Get Personalised PETs Adoption Advice")
    st.write("1. Write your problem statement in the text area.")
    st.write("2. Click the 'Submit' button.")
    st.write("3. The app will generate the relevant advice for your scenario.")
