import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="PETs Advisor App"
)
# endregion <--------- Streamlit App Configuration --------->

# Disclaimer (collapsible)
with st.expander("IMPORTANT NOTICE: Disclaimer", expanded=False):
    st.markdown("""
    **IMPORTANT NOTICE:** This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

    Always consult with qualified professionals for accurate and personalized advice.
    """)

st.title("About Us")

st.write("We are from the PETs Team at the IMDA. This is a Streamlit App to help organisations who are interested in PETs better understand PETs and how to adopt them. The PETs Knowledge Hub uses a LLM and where relevant, additional data from user, to build a knowledge database and to provide RAG-enhanced Q&A response. The PETs Adoption Advisor provides personalised advice on what PETs the user can adopt based on a specific problem statement, and generates a checklist for the user to consider.")

st.markdown("<u><b>Regarding the Login</b></u>", unsafe_allow_html=True)
st.markdown("""
- **For Admin users:** You will be able to access all features without the need to provide your own OpenAI API key, as the system provides you a key automatically at the backend.  
- **For other users:** You will need to submit your own OpenAI API key before you can use each feature. The key you submitted is only temporarily stored in the session state and will not be saved permanently.
""")

st.markdown("<u><b>How to use this App</b></u>", unsafe_allow_html=True)
with st.expander("**Feature 1 PETs Knowledge Hub:**"):
    st.write("Build Your Own Knowledge Base and Get RAG-enhanced Q&A Response")
    st.write("1. (Optional) Upload your documents to enhance the default PETs Knowledge Base.")
    st.write("2. Once the documents are uploaded, you may generate the enhanced Knowledge Base.")
    st.write("3. Based on the knowledge base, you can ask questions and retrieve relevant context from the knowledge base.")

with st.expander("**Feature 2 PETs Adoption Advisor:**"):
    st.write("Submit Your Own Problem Statement and Get Personalised PETs Adoption Advice")
    st.write("1. Select your key objective from the dropdown list.")
    st.write("2. Write your problem statement in the text area.")
    st.write("3. Select the PETs you are interested to apply from the dropdown list.")
    st.write("4. Click the 'Analyze & Advise' button. The app will generate the relevant advice for your scenario.")
