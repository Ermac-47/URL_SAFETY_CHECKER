# 🛡️ AI-Powered URL Safety Checker

> An intelligent phishing URL detection system that combines **Feature Engineering**, **Rule-Based Risk Analysis**, and **Large Language Models (LLMs)** to provide **real-time explainable security analysis**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)
![LangChain](https://img.shields.io/badge/LLM-LangChain-green)
![Groq](https://img.shields.io/badge/Inference-Groq-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

# 📌 Overview

Phishing attacks remain one of the most common cybersecurity threats, exploiting deceptive URLs to steal sensitive user information.

Traditional URL scanners often rely on blacklists or predefined signatures, making them ineffective against newly generated phishing websites.

To address this challenge, we developed an **AI-powered URL Safety Checker** capable of performing **real-time URL analysis** by combining:

- Intelligent Feature Extraction
- Rule-Based Security Analysis
- LLM-powered Reasoning
- Explainable AI Reports

Instead of simply classifying a website as **Safe** or **Unsafe**, the application explains *why* a URL may be suspicious, helping users better understand potential security risks.

---

# 🎯 Objectives

- Detect suspicious and phishing URLs in real time.
- Generate explainable security reports.
- Combine heuristic analysis with LLM reasoning.
- Provide an intuitive Streamlit interface.
- Demonstrate the practical use of AI in cybersecurity.

---

# ✨ Features

## 🔍 Intelligent URL Analysis

- URL Length Analysis
- HTTPS Verification
- Suspicious Keyword Detection
- IP Address Detection
- Multiple Dot Detection
- Hyphen Detection
- Login Form Detection
- Domain Information Extraction
- SSL Certificate Validation
- Domain Age Verification
- IFrame Detection
- Page Title Analysis

---

## 🤖 AI Security Reasoning

Unlike traditional URL scanners, this project integrates **Large Language Models (LLMs)** to generate contextual explanations.

The AI explains:

- Why a URL appears suspicious
- Which features contribute to the risk
- Possible phishing indicators
- Security recommendations

This makes the system far more transparent than a simple binary prediction.

---

## 📊 Risk Scoring

The application combines multiple approaches:

- Feature Engineering
- Rule-Based Risk Engine
- AI-powered Reasoning

These components work together to produce an overall security assessment.

---

## 🌐 Interactive Dashboard

Built using Streamlit with:

- Real-time URL scanning
- Risk Summary
- AI Security Analysis
- Feature Breakdown
- Clean User Interface

---

# 🏗️ System Architecture

```
                User
                  │
                  ▼
          Enter Website URL
                  │
                  ▼
        Feature Extraction Module
                  │
     ┌────────────┼────────────┐
     │            │            │
 HTTPS Check   Domain Info   URL Analysis
     │            │            │
     └────────────┼────────────┘
                  │
                  ▼
         Rule-Based Risk Engine
                  │
                  ▼
        LLM Security Analysis
                  │
                  ▼
        Final Risk Assessment
                  │
                  ▼
      Streamlit Interactive UI
```

---

# ⚙️ Technology Stack

## Programming Language

- Python

## Frontend

- Streamlit

## Backend

- FastAPI
- Flask

## Artificial Intelligence

- LangChain
- Groq API
- Prompt Engineering

## Machine Learning & NLP

- Scikit-Learn
- Pandas
- NumPy

## Security & Feature Extraction

- BeautifulSoup
- Whois
- tldextract
- SSL
- Socket
- Requests

## Development Tools

- Git
- GitHub
- VS Code

---

# 📂 Project Structure

```
URL_SAFETY_CHECKER/

│── api.py
│── app.py
│── feature_extractor.py
│── risk_engine.py
│── predict.py
│── train_model.py
│── models/
│── templates/
│── static/
│── screenshots/
│── requirements.txt
│── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Ermac-47/URL_SAFETY_CHECKER.git
```

Navigate into the project

```bash
cd URL_SAFETY_CHECKER
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

or

```bash
python api.py
```

---

# 💻 Usage

1. Launch the application.
2. Enter any URL.
3. Click **Analyze**.
4. The system extracts security features.
5. The Rule Engine evaluates the URL.
6. The LLM generates an explainable report.
7. View the final risk assessment.

---

# 📈 Sample Analysis

Example Input

```
https://example-login-security.com
```

Output

```
Risk Level : Suspicious

Reasons:

✔ Suspicious Keywords Detected

✔ Domain appears recently created

✔ URL structure resembles phishing patterns

✔ AI identified possible credential harvesting indicators

Recommendation:

Avoid entering sensitive information until the legitimacy of the website is verified.
```

---

# 🧠 Key Learning Outcomes

Through this project we gained practical experience in:

- Explainable AI
- Prompt Engineering
- Cybersecurity Fundamentals
- URL Feature Engineering
- API Development
- Streamlit Deployment
- FastAPI Development
- LLM Integration
- Rule-Based Expert Systems
- AI-assisted Threat Detection

---

# 🚧 Challenges Faced

Some of the major challenges encountered during development included:

- Designing meaningful URL features for phishing detection.
- Combining rule-based analysis with LLM reasoning.
- Reducing false positives while maintaining detection quality.
- Building explainable outputs instead of simple predictions.
- Integrating multiple AI and backend components into a single workflow.
- Optimizing response time for real-time analysis.

---

# 🔮 Future Improvements

Future enhancements include:

- VirusTotal API Integration
- Google Safe Browsing API
- Browser Extension
- Chrome & Edge Plugin
- QR Code Safety Scanner
- Email Link Scanner
- Threat Intelligence APIs
- OCR-based URL Detection
- Domain Reputation Analysis
- Multi-language Support
- Mobile Application
- AI SOC Dashboard

---

# 👥 Contributors

- **Eshaan Uddin Khan**
- **<Teammate 1>**
- **<Teammate 2>**

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps motivate us to continue building more AI and Cybersecurity projects.

---

# 📬 Contact

For questions, suggestions, or collaboration:

📧 eshaanuddinkhan@gmail.com

🔗 LinkedIn: *(Add your LinkedIn URL)*

🐙 GitHub: https://github.com/Ermac-47

---

## 📄 License

This project is licensed under the MIT License.

