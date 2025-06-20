cat <<EOF > README.md
# 🧾 AI/ML Invoice Reimbursement System

## 🚀 Project Overview

This project automates the invoice reimbursement workflow using Large Language Models (LLMs) and semantic search. It allows users to upload invoice PDFs and an HR policy document, analyzes the invoices using Groq LLM based on the policy, and classifies them as **Fully Reimbursed**, **Partially Reimbursed**, or **Declined** — with reasons.

The results are stored as vector embeddings in **ChromaDB**, enabling Excel export and chatbot-based querying via **Streamlit**.

---

## 🎯 Objectives

- ✅ Automate invoice validation using LLMs
- ✅ Store invoice metadata in a vector DB (ChromaDB)
- ✅ Provide Excel export functionality
- ✅ Enable chatbot interaction for querying past invoices

---

## ✨ Features

### 🔹 1. `/analyze-invoices/` – Invoice Reimbursement API (FastAPI)
- Upload an **HR Policy PDF**
- Upload a **ZIP file of invoice PDFs**
- Provide **employee name**
- Each invoice is:
  - Analyzed using Groq LLM
  - Classified into: Fully / Partially / Declined
  - Stored in ChromaDB with metadata

### 🔹 2. `/export-excel/` – Export to Excel
- Download all invoice records as `.xlsx`
- Includes: employee, status, reason, and snippet

### 🔹 3. `/search-invoices/` – Metadata-Aware Search API
- Accepts `query`, `employee`, `status`, `invoice_id`
- Returns matching documents based on both:
  - semantic similarity (via vector embedding)
  - metadata filtering (employee, status, etc.)

### 🔹 4. Streamlit Interface (Tabs: Upload + Chatbot)
- Upload HR policy and invoices (Tab 1)
- Chatbot query interface (Tab 2)
- Sidebar filters: employee name, status
- Natural language queries like:
  - “Why was Invoice 3 declined?”
  - “Show fully reimbursed invoices by Anand”

---

## 🧰 Tech Stack

| Component       | Technology             |
|----------------|------------------------|
| Backend         | FastAPI                |
| Frontend        | Streamlit              |
| LLM API         | Groq (Mixtral / LLaMA3)|
| Embeddings      | Sentence-Transformers  |
| Vector DB       | ChromaDB               |
| PDF Parsing     | PyPDF2                 |
| Excel Export    | pandas + openpyxl      |
| File Uploads    | python-multipart       |

---

## 📁 Folder Structure

```
invoice-reimbursement/
├── app.py                    ← Unified Streamlit UI (upload + chatbot)
├── main.py                   ← FastAPI backend
├── requirements.txt
├── README.md
├── utils/
│   ├── pdf_parser.py
│   ├── shared_invoice_utils.py
│   └── logger.py
├── llm/
│   ├── groq_analyzer.py
│   └── llm_chat.py
├── vector_store/
│   ├── db.py
│   └── embedder.py
├── uploads/                  ← temp storage
└── .env                      ← (not committed)
```

---

## ⚙️ Installation

```

git clone https://github.com/Prathme07/invoice-reimbursement.git

```
```
cd invoice-reimbursement
```
```
python -m venv venv
```
```
venv\Scripts\activate     # Windows
```
```
# OR
source venv/bin/activate  # Linux/macOS
```
```
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Create a `.env` file and set your Groq API key:

```env
GROQ_API_KEY=your-groq-key-here
```

Or use:

```
export GROQ_API_KEY=your-groq-key-here  # macOS/Linux
set GROQ_API_KEY=your-groq-key-here     # Windows
```

---

## ▶️ Running the App

### 🔹 FastAPI Backend

```
uvicorn main:app
```

Visit:  
[http://localhost:8000/docs](http://localhost:8000/docs)

---

### 🔹 Streamlit Frontend

```
streamlit run app.py
```

Visit:  
[http://localhost:8501](http://localhost:8501)

---

## 📦 API Guide

### POST `/analyze-invoices/`
- Inputs: `policy_pdf` (PDF), `invoices_zip` (ZIP), `employee_name` (string)
- Output: JSON result per invoice with:
  - `Status`: Fully / Partially / Declined
  - `Reason`: Explanation from LLM

### GET `/export-excel/`
- Downloads `.xlsx` with all analyzed invoices

### GET `/search-invoices/`
- Inputs: `query` + optional `employee`, `status`, `invoice_id`
- Output: matched invoices with metadata

---

## 🤖 Prompt Design

### Invoice Analysis Prompt

```
You are an invoice checker.

Policy:
{policy_text}

Invoice:
{invoice_text}

Task:
Is the invoice valid as per the policy?
Reply in this format:
Status: Fully Reimbursed / Partially Reimbursed / Declined
Reason: <why?>
```

### Chatbot Prompt (RAG Style)

```
You are a smart and helpful assistant trained to analyze and explain employee invoice reimbursements.

Your task is:
1. Understand the user's question.
2. Refer to the documents provided.
3. Respond with clear and structured answers in **Markdown** format.
```

---

## 📚 How Vector DB Works

Each invoice is embedded using `sentence-transformers` and stored in ChromaDB with metadata:

- `employee`
- `status`
- `reason`
- `invoice_id`
- `text`

Then queried using hybrid of vector similarity + metadata filtering.

---

## 🧠 Challenges & Learnings (Optional)

- ✅ Groq API offers extremely fast LLM inference
- ✅ ChromaDB supports fast similarity search — but allows only one metadata filter at a time (fixed via Python-side filtering)
- ✅ Streamlit's layout flexibility allowed clean tab-based UX
- ✅ Windows' multiprocessing limitations were solved by fallback to sequential or `uvicorn` without `--reload`

---

## 📷 Sample Screenshots



### API Response Example

Invoices Analysis:

![Invoices Analysis](images/analyz_invpices.png)

---
Response of Invoices Analysis in JSON:

![Response of API JSON for Invoices Analysis](images/response.png)

---

Search Invoices:

![Response of API JSON for Query](images/query.png)

---

Response of Search Invoices:

![Response of API JSON for Query](images/queryresponses.png)

---
### Web Interface

A single web interface for both upload and analysis of invoices and a chatbot

Upload & Analysis Tab:

![Upload & Analysis](images/Upload_Analyze.png)

---

ChatBot Tab:

![Chat Bot](images/chatbot.png)


### Excel Export Example
Excel Response in FastAPI:

![Excel Export Screenshot](images/excel.png)

### 

---

## ✅ Final Notes

- 🔐 No invoice data is stored permanently
- 💬 Easy to extend with more LLM providers or advanced filtering
- 🧪 Use `uploads/sample.zip` and `sample_policy.pdf` for demo

---

## ✅ Author

> Developed by Prathmesh Chourasiya
