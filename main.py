import streamlit as st
import validators
import re
from langchain_groq import ChatGroq

# ✅ Import your modules
from Src.utils.feature_extractor import extract_url_features
from Src.utils.risk_engine import compute_risk_score
from Src.models.predict import predict_url

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

    st.title("🔐 Login")

    users = load_users()

    menu = st.selectbox("Select Option", ["Login", "Signup"])

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
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state["page"] = "app"
                st.rerun()
            else:
                st.error("Invalid credentials")

# ===================== MAIN APP =====================
elif st.session_state["page"] == "app":

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state["page"] = "login"
        st.rerun()

    # -------------------- CUSTOM DARK THEME --------------------
    st.markdown(
        """
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
            div.stButton > button:hover { background-color: #019875; }
            input, textarea { background-color: #1e1e1e !important; color: white !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------- HEADER --------------------
    st.markdown(
        """
        <h1 style='text-align:center; color:#00b894;'>🛡️ URL Safety Checker</h1>
        <p style='text-align:center; font-size:18px; color:#E0E0E0;'>
            Hybrid Detection using <b>ML + Rules + AI</b>
        </p>
        """,
        unsafe_allow_html=True
    )

    # -------------------- SIDEBAR --------------------
    with st.sidebar:
        st.header("⚙️ Configuration")
        groq_api_key = st.text_input("Enter Groq API Key", type="password")
        st.info("Paste one or multiple URLs")

    # -------------------- INPUT --------------------
    st.markdown("### 🔗 Enter URLs:")
    user_urls = st.text_area("Paste URLs", height=150)

    # -------------------- LLM SETUP --------------------
    llm = None
    if groq_api_key.strip():
        llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_api_key)

    # -------------------- BUTTON --------------------
    if st.button("🔍 Check Safety", use_container_width=True):

        if not user_urls.strip():
            st.error("⚠️ Please enter at least one URL")
        else:
            urls = re.findall(r'https?://[^\s,]+', user_urls)
            urls = list(set(urls))

            with st.spinner("🧠 Analyzing..."):

                for user_url in urls:

                    if not validators.url(user_url):
                        st.error(f"Invalid URL: {user_url}")
                        continue

                    features = extract_url_features(user_url)

                    rule_result = compute_risk_score(features)
                    rule_score = rule_result["risk_score"]

                    ml_score = predict_url(features)

                    final_score = (rule_score * 0.4) + (ml_score * 0.6)

                    if final_score < 0.3:
                        verdict = "SAFE"
                        color = "#00b894"
                    elif final_score < 0.7:
                        verdict = "SUSPICIOUS"
                        color = "orange"
                    else:
                        verdict = "PHISHING"
                        color = "red"

                    # -------------------- AI EXPLANATION --------------------
                    if llm:
                        prompt = f"""
                        You are a cybersecurity assistant.

                        Final Verdict: {verdict}
                        Risk Score: {round(final_score, 2)}

                        Reasons:
                        {rule_result['reasons']}

                        Explain this in a natural, human-friendly way.
                        Keep it short (2-3 lines).
                        Do NOT contradict the verdict.
                        """
                        response = llm.invoke(prompt)
                        ai_explanation = response.content
                    else:
                        ai_explanation = "No AI explanation"

                    # -------------------- UI OUTPUT --------------------
                    st.markdown("---")
                    st.markdown(f"### 🔗 {user_url}")

                    st.progress(int(final_score * 100))
                    st.write(f"**Risk Score: {round(final_score * 100)}%**")

                    st.markdown(
                        f"""
                        <div style="
                            border:2px solid {color};
                            padding:15px;
                            border-radius:10px;
                            text-align:center;
                            font-size:22px;
                        ">
                            🔍 Verdict: <b style="color:{color}">{verdict}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("### 📌 Reasons")
                    for reason in rule_result["reasons"]:
                        st.write(f"- {reason}")

                    st.markdown("### 🤖 AI Explanation")
                    st.write(ai_explanation)