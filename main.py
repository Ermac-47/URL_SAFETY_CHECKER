import streamlit as st
import validators
import re
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="URL Safety Checker | LangChain + Groq",
    page_icon="🛡️",
    layout="wide"
)

# -------------------- CUSTOM DARK THEME CSS --------------------
st.markdown(
    """
    <style>
        body { background-color: #000000; color: #FFFFFF; }
        .stApp { background-color: #000000; color: #FFFFFF; }
        section[data-testid="stSidebar"] { background-color: #111111; color: #FFFFFF; }
        div.stButton > button {
            background-color: #00b894;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            padding: 10px 20px;
        }
        div.stButton > button:hover { background-color: #019875; }
        input, textarea { background-color: #1e1e1e !important; color: #ffffff !important; }
        .result-box {
            background-color: #1a1a1a;
            color: #FFFFFF;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #00b894;
            box-shadow: 0px 0px 10px #00b894;
            text-align: center;
            font-size: 22px;
            margin-bottom: 15px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- HEADER --------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#00b894;'>🛡️ URL Safety Checker</h1>
    <p style='text-align:center; font-size:18px; color:#E0E0E0;'>
        Instantly check if links are <b>Safe</b> or <b>Phishing</b> using <b>LangChain + Groq</b>.
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Enter your Groq API Key", type="password", placeholder="sk-...")
    st.info("💡 Paste one or multiple URLs below (separated by commas, spaces, or new lines).")

# -------------------- MAIN INPUT --------------------
st.markdown("<h3 style='color:#00b894;'>🔗 Enter URLs to Check:</h3>", unsafe_allow_html=True)
user_urls = st.text_area("Paste URLs here", placeholder="https://example.com\nhttps://phishing-site.com")

# -------------------- SETUP MODEL --------------------
if groq_api_key.strip():
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)
else:
    llm = None

# -------------------- CHECK SAFETY BUTTON --------------------
if st.button("🔍 Check Safety", use_container_width=True):
    if not groq_api_key.strip() or not user_urls.strip():
        st.error("⚠️ Please provide both the API key and at least one URL.")
    else:
        # -------------------- EXTRACT ALL VALID URLS --------------------
        urls = re.findall(r'https?://[^\s,]+', user_urls)
        urls = list(set(urls))  # remove duplicates if any

        with st.spinner("🧠 Analyzing links..."):
            for user_url in urls:
                if not validators.url(user_url):
                    st.markdown(
                        f"<div class='result-box' style='border:2px solid orange;'>⚠️ <b>{user_url}</b><br>Invalid URL format.</div>",
                        unsafe_allow_html=True
                    )
                    continue

                # Prepare prompt for the LLM
                prompt = f"Decide if the following URL is safe or a phishing/scam website. Respond only with one of these two words: 'Safe' or 'Phishing'.\n\nURL: {user_url}"
                result = llm.invoke(prompt)
                verdict = result.content.strip().lower()

                # Display results with color coding
                if "phishing" in verdict:
                    st.markdown(
                        f"<div class='result-box' style='border:2px solid red;'>🚨 <b>{user_url}</b><br>This link is likely <b>PHISHING / MALICIOUS</b>.</div>",
                        unsafe_allow_html=True
                    )
                elif "safe" in verdict:
                    st.markdown(
                        f"<div class='result-box' style='border:2px solid #00b894;'>✅ <b>{user_url}</b><br>This link appears to be <b>SAFE</b>.</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div class='result-box'>⚠️ <b>{user_url}</b><br>Unable to classify clearly. Please verify manually.</div>",
                        unsafe_allow_html=True
                    )
