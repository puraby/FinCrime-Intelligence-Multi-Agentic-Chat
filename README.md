#  FinCrime Intelligence Chat

**Multi-Agent Financial Crime Investigation & SAR Generation System**

A conversational AI-powered analyst workspace that automates **data querying, alert investigation, analytics, and AUSTRAC-compliant SAR (SMR) generation** using a **multi-agent architecture with ephemeral code execution**.

---

##  Overview

FinCrime Intelligence Chat enables analysts to interact with financial crime data using natural language.
The system routes each query to specialized agents to:

* Query data (SQL)
* Generate charts (Python)
* Investigate alerts (SAR Agent)
* Answer AML/CTF questions (Chat Agent)

All through a **single chat interface**, replacing multiple manual workflows.

---

## Core Features

* 🔍 **End-to-End Alert Investigation**

  * Multi-source data fetch (alerts, customers, transactions)
  * Risk scoring and red flag detection
  * Automated SAR narrative generation

*  **Natural Language → SQL**

  * Query data without writing SQL
  * Clean tabular outputs

* 📈 **Dynamic Chart Generation**

  * On-demand visual analytics

*  **AML Knowledge Assistant**

  * Domain Q&A for analysts

* 🔐 **Ephemeral Execution**

  * Generated code is executed and deleted immediately

---

##  SAR Agent Pipeline

```
Analyst: "Investigate ALT-2024-08821"
        ↓
1. LLM generates Python code to fetch data
2. Execute → collect alert, customer, transactions, etc.
3. Delete data-fetching code (ephemeral)
4. Risk scoring + red flag detection
5. LLM generates SAR narrative code
6. Execute → produce AUSTRAC SMR (5 sections)
7. Delete SAR code (ephemeral)
8. Return SAR to UI
```

---

##  Key Concept: Ephemeral Execution

All LLM-generated code is:

* Created dynamically
* Executed immediately
* Deleted after execution

### Benefits

* 🔐 Security
* 📋 Audit-friendly
* 🧼 Clean runtime
* ⚡ Controlled execution

---

##  Architecture

```
User Input
    ↓
multi_agent_graph.py (Router)
    ↓
-------------------------------------
| SQL Agent     → Data Queries      |
| Python Agent  → Charts            |
| SAR Agent     → Investigation     |
| Chat Agent    → AML Knowledge     |
-------------------------------------
```

---

##  Project Structure

```
.
├── app.py                  # Streamlit UI
├── multi_agent_graph.py    # Agent router
├── agent_sar.py            # SAR agent
├── agent_sql.py
├── agent_python.py
├── agent_chat.py
├── orchestrator.py
├── multi_agent_state.py
└── README.md
```

---

##  Tech Stack

* Python
* Streamlit
* Pandas
* LLM-based agents
* Custom UI (CSS)

---

##  Getting Started

### Clone repo

```
git clone <your-repo-url>
cd fincrime-intelligence-chat
```

### Setup environment

```
python -m venv venv
source venv/bin/activate   # Mac
venv\Scripts\activate      # Windows
```

### Install dependencies

```
pip install -r requirements.txt
```

### Run app

```
streamlit run app.py
```

---

## 💬 Example Prompts

**SQL**

* Which customers have a high risk rating
* Show me all CRITICAL alerts

**Charts**

* Show alert count by month
* Plot alerts by risk tier

**Investigation**

* Investigate ALT-2024-08821

**AML Knowledge**

* What is structuring?
* What is Enhanced Due Diligence?

---

## 📊 Example Output

```
Risk Score: 87/100
Red Flags: Offshore transfers, structuring
Decision: SAR Required
```

Includes:

* Structured SAR narrative
* Editable report
* Investigation summary

---

##  Impact

*  Hours → seconds for SAR generation
*  Faster investigations
*  AI-assisted decisions
*  Consistent reporting
*  Secure execution

---

##  Disclaimer

Prototype system for financial crime workflows.
Production use requires:

* Access control
* Audit logging
* Data security
* Human review

---

##  Author

**Puraby Dev**
Senior Data Engineer | Financial Crime & AI Systems

---

##  Summary

> A multi-agent AI system that automates financial crime investigations and generates SAR reports using secure, ephemeral execution.
