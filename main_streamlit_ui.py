## ---- main_streamlit_ui.py -----##


import streamlit as st
import validators
import re
from langchain_groq import ChatGroq

from backend.utils.feature_extractor import extract_url_features
from backend.utils.risk_engine import compute_risk_score
from backend.models.predict import predict_url

import json
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="URL Safety Checker | Hybrid AI",
    page_icon="🛡️",
    layout="wide"
)

# -------------------- USER STORAGE --------------------
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# -------------------- PAGE STATE --------------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# ===================== LOGIN PAGE =====================
if st.session_state["page"] == "login":

    # 🔥 BACKGROUND + STYLE (from your HTML)
    st.markdown("""
    <style>
    body {
        background: url('https://th.bing.com/th/id/OIP.xopeHwWooaDwXB9JUA6t_gHaEK?w=351') no-repeat center center fixed;
        background-size: cover;
    }

    .login-box {
        width: 400px;
        padding: 40px;
        border-radius: 20px;
        background: rgba(0,0,0,0.7);
        backdrop-filter: brightness(40%);
        box-shadow: 0px 0px 20px rgba(0,0,0,0.75);
        text-align: center;
    }

    .title {
        color: white;
        font-size: 26px;
        margin-bottom: 30px;
    }

    .stTextInput input {
        border-radius: 20px !important;
        padding: 10px !important;
        background: rgba(255,255,255,0.3) !important;
        color: white !important;
        border: none !important;
    }

    .stButton button {
        border-radius: 40px;
        background: rgb(45,126,231);
        color: white;
        width: 100%;
    }

    .stButton button:hover {
        background: linear-gradient(45deg, #4961e9, #6b9dfc);
    }
    </style>
    """, unsafe_allow_html=True)

    users = load_users()

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<div class='title'>LOGIN</div>", unsafe_allow_html=True)

        menu = st.selectbox("", ["Login", "Signup"])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if menu == "Signup":
            if st.button("Create Account"):
                if username in users:
                    st.warning("User already exists")
                else:
                    users[username] = password
                    save_users(users)
                    st.success("Account created!")

        elif menu == "Login":
            if st.button("Submit"):
                if username in users and users[username] == password:
                    st.session_state["page"] = "app"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        st.markdown("</div>", unsafe_allow_html=True)

# ===================== MAIN APP =====================
elif st.session_state["page"] == "app":

    if st.sidebar.button("Logout"):
        st.session_state["page"] = "login"
        st.rerun()

    st.markdown("""
    <style>
        body { background-color: #000000; color: #FFFFFF; }
        .stApp { background-color: #000000; color: #FFFFFF; }
        section[data-testid="stSidebar"] { background-color: #111111; }
        div.stButton > button {
            background-color: #00b894;
            color: white;
            border-radius: 10px;
            font-size: 18px;
            padding: 10px 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h1 style='text-align:center; color:#00b894;'>🛡️ URL Safety Checker</h1>
    <p style='text-align:center; font-size:18px; color:#E0E0E0;'>
        Hybrid Detection using <b>ML + Rules + AI</b>
    </p>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Configuration")
        groq_api_key = st.text_input("Enter Groq API Key", type="password")

    st.markdown("### 🔗 Enter URLs:")
    user_urls = st.text_area("Paste URLs", height=150)

    llm = None
    if groq_api_key.strip():
        llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)

    if st.button("🔍 Check Safety", use_container_width=True):

        urls = re.findall(r'https?://[^\s,]+', user_urls)
        urls = list(set(urls))

        for user_url in urls:

            features = extract_url_features(user_url)
            rule_result = compute_risk_score(features)
            ml_score = predict_url(features)

            final_score = (rule_result["risk_score"] * 0.4) + (ml_score * 0.6)

            verdict = "SAFE" if final_score < 0.3 else "SUSPICIOUS" if final_score < 0.7 else "PHISHING"
            color = "#00b894" if verdict == "SAFE" else "orange" if verdict == "SUSPICIOUS" else "red"

            st.markdown(f"### 🔗 {user_url}")
            st.progress(int(final_score * 100))
            st.write(f"Risk Score: {round(final_score * 100)}%")

            st.markdown(f"""
            <div style="border:2px solid {color};padding:15px;border-radius:10px;text-align:center;">
            Verdict: <b style="color:{color}">{verdict}</b>
            </div>
            """, unsafe_allow_html=True)