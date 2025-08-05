import streamlit as st
from io import BytesIO
import smtplib
from email.message import EmailMessage
import mimetypes
import os
from utils.sidebar import show_sidebar

if st.session_state.username not in ["admin", "user"]:
    st.warning("Access Denied! Please log in at the home page.")
    st.stop()
show_sidebar()

from dotenv import load_dotenv
load_dotenv()

email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")

# Constants
MAX_WORDS = 500
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'docx']
MAX_FILE_SIZE_MB = 5

# ---- Session State Setup ----
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False
if "email_text" not in st.session_state:
    st.session_state.email_text = ""
if "file_cleared" not in st.session_state:
    st.session_state.file_cleared = False

# ---- Helper Functions ----
def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def word_count(text):
    return len(text.strip().split())

def file_size_in_mb(file_obj):
    file_obj.seek(0, 2)
    size = file_obj.tell() / (1024 * 1024)
    file_obj.seek(0)
    return size

def send_email(message_text, file_obj):
    try:
        msg = EmailMessage()
        msg['Subject'] = "Message to PDPC PET Team from Streamlit App"
        msg['From'] = email_user
        msg['To'] = "kathy_shen@pdpc.com.sg"
        msg.set_content(message_text)

        if file_obj:
            file_data = file_obj.read()
            maintype, subtype = mimetypes.guess_type(file_obj.name)[0].split('/')
            msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_obj.name)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)

        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# ---- UI ----

st.title("📬 Feedback to PETs Team")

st.markdown("""
### Useful Links
- [IMDA's PET Sandbox](https://www.imda.gov.sg/how-we-can-help/data-innovation/privacy-enhancing-technology-sandboxes)
- [PDPC Guidelines and Consultations](https://www.pdpc.gov.sg/guideline-and-consultation-menu)
- [PDPA Overview](https://www.pdpc.gov.sg/overview-of-pdpa/the-legislation/personal-data-protection-act)
""")

# Text area with session state binding
email_text = st.text_area(
    "Write your message to the PETs Team (max 500 words):",
    key="email_text", height=200
)

words = word_count(email_text)
if words > MAX_WORDS:
    st.warning(f"Your message has {words} words, which exceeds the limit of {MAX_WORDS}.")

# Reset file uploader only by rerunning form — Streamlit doesn't support clearing file_uploader directly
uploaded_file = None
if not st.session_state.file_cleared:
    uploaded_file = st.file_uploader("Attach a file (pdf, txt, docx) - Max size 5 MB", type=ALLOWED_EXTENSIONS)

# Button logic
if st.button("Send Email"):
    if not email_text.strip():
        st.error("Please enter a message.")
    elif words > MAX_WORDS:
        st.error("Your message exceeds the word limit.")
    elif uploaded_file:
        size_mb = file_size_in_mb(uploaded_file)
        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File size exceeds {MAX_FILE_SIZE_MB} MB.")
        elif not allowed_file(uploaded_file.name):
            st.error("Invalid file type.")
        else:
            if send_email(email_text, uploaded_file):
                st.session_state.email_sent = True
                st.session_state.email_text = ""
                st.session_state.file_cleared = True
    else:
        if send_email(email_text, None):
            st.session_state.email_sent = True
            st.session_state.email_text = ""
            st.session_state.file_cleared = True

# Show success message
if st.session_state.email_sent:
    st.success("✅ Your message has been sent to the PDPC PET team.")
    st.session_state.email_sent = False  # Reset for next run
