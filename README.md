# ScamShield AI 🛡️

**A cybersecurity investigation and scam-awareness platform designed to help users analyze suspicious messages, URLs, investigate indicators of compromise, and manage security incidents.**

ScamShield AI brings scam detection, threat intelligence, investigation management, community reporting, security awareness, and incident reporting into one platform.

---

## 🚀 Features

### 🔍 Message Analyzer
Analyze suspicious messages using rule-based detection techniques to identify potential scam indicators, social engineering patterns, urgency, and suspicious requests.

### 🌐 URL Analyzer
Perform local structural analysis of URLs to identify suspicious characteristics such as embedded credentials, IP-based hosts, URL shorteners, unusual ports, and unencrypted HTTP.

### 🧠 Threat Intelligence
Maintain and search an IOC intelligence workspace for indicators such as URLs, domains, IP addresses, and file hashes.

### 🗂️ Investigation Cases
Create and manage investigation cases, attach evidence, add analyst notes, and maintain investigation activity records.

### 📊 Investigation Reports
Generate reports from investigation records and export report information in supported formats.

### 👥 Community Reports
Submit and review community reports related to suspicious identifiers and scam activity.

### 🎓 Security Awareness
Learn about phishing, online scams, social engineering, account security, and common fraud techniques through educational content and quizzes.

### 🆘 Help & Support
Access help resources, FAQs, troubleshooting guidance, and submit support requests.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Programming Language:** Python
- **Database:** SQLite
- **Testing:** Pytest
- **Version Control:** Git & GitHub

---

## 🏗️ Project Structure

```text
ScamShield/
├── app.py
├── components/
├── core/
├── database/
├── docs/
├── pages/
├── services/
├── tests/
├── .streamlit/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/sasipaidala/Scamsheild.git
```

### 2. Navigate to the project directory

```bash
cd Scamsheild
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure environment variables

Copy `.env.example` to `.env` and configure the variables as required.

Do not commit secrets or API keys.

### 7. Run ScamShield

```bash
streamlit run app.py
```

---

## 🧪 Testing

Run the test suite:

```bash
pytest
```

---

## 🔐 Security & Limitations

- Message detection uses heuristic and rule-based analysis.
- URL analysis is primarily structural and local unless an explicitly configured external service is used.
- A low-risk result does not guarantee that a message or URL is safe.
- Threat intelligence results depend on available data sources.
- Community reports may contain unverified allegations.
- ScamShield should be used as an investigative aid, not as a definitive security verdict.
- Avoid submitting sensitive personal information or confidential evidence.

---

## 🎯 Project Objective

The objective of ScamShield AI is to bring accessible scam analysis, investigation workflows, threat intelligence management, and cybersecurity awareness together in a unified platform.

---

## 👨‍💻 Developer

**Sasi Paidala**

Computer Science & Engineering | Cybersecurity

GitHub: https://github.com/sasipaidala

---

## 📄 License

License information will be added as the project evolves.
