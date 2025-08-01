import streamlit as st
from utils import auth
from utils.sidebar import show_sidebar

# Ensure all session state keys are initialized
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")

if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_clicked = st.button("Login")
    if login_clicked:
        if username not in ["admin", "user"]:
            st.warning("😕 User Name incorrect")
        elif not auth.authenticate(username, password):
            st.warning("😕 Password incorrect")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.api_key = auth.get_api_key(username)
            st.rerun()
else:
    show_sidebar()
    # Add a background image using markdown and CSS
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://github.com/KathyShen/AIBOOTCAMP_POC/raw/master/assets/AIBOOTCAMP_POC_HOME_background.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .site-map {
            background: rgba(255,255,255,0.85);
            border-radius: 10px;
            padding: 1.5em;
            margin-top: 2em;
        }
        .stApp h1 {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # Funny PETs tagline
    st.markdown(
        """
        <div style='margin: 0 auto; max-width: 700px; background: rgba(255,255,255,0.92); border-radius: 10px; padding: 1.2em 1.5em 1.2em 1.5em; margin-bottom: 1.5em; text-align: center;'>
            <span style='font-size: 1.3em;'>
                🐾 <b>Wait! These PETs don't bark, purr, or fetch sticks...</b> 🐾<br>
                <span style='font-size: 1.1em;'>
                    <b>PETs</b> here means <b>Privacy Enhancing Technologies</b> <span style='font-size:1.2em;'>🔒🤖</span>,<br>
                    not the adorable <span style='font-size:1.2em;'>🐶🐱🐦🐢</span> you might be thinking of!
                </span>
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.title("Welcome to Our Site")
    st.markdown(
        """
        <div class='site-map' style='margin: 0 auto; max-width: 700px;'>
            <h3>Site Map</h3>
            <ul>
                <li><b>🧠 PETs Knowledge Hub</b>: Explore privacy enhancing technologies, based on the default knowledge database and any files uploaded by user</li>
                <li><b>🧑‍💻 PETs Adoption Advisor</b>: Get personalized advice for adopting PETs, based on specific scenarios given by users</li>
                <li><b>📬 Feedback to PETs Team </b>: Provide useful reference links and accept user feedbacks </li>
            </ul>
            <div style='margin-top:2em; text-align:left;'>
                <span style='font-size:22px; font-weight:bold; color:#000;'>
                    <span style='vertical-align:middle;'>
                        <span style='font-size:32px;'>&#8592;</span> Use the sidebar to navigate!
                    </span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

