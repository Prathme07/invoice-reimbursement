import streamlit as st
import pandas as pd
from io import BytesIO
from PyPDF2 import PdfReader
import os, zipfile, tempfile

from vector_store.db import add_to_vector_db, query_vector_db
from llm.llm_chat import chat_with_documents
from llm.groq_analyzer import analyze_invoice


USERS = {
    "admin": "admin123",
    "anand": "emp123",
    "shreya": "emp456"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "policy_text" not in st.session_state:
    st.session_state.policy_text = ""


if not st.session_state.logged_in:
    st.set_page_config(layout="centered")
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_role = "admin" if username == "admin" else "employee"
            st.rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()


st.set_page_config(page_title="Invoice Reimbursement", layout="wide")
st.title("💼 Invoice Reimbursement System")

# 🎚️ Tabs
tabs = ["📤 Upload & Analyze Invoices", "💬 Chat with Bot"]
if st.session_state.user_role == "admin":
    tabs.append("📊 Admin Dashboard")
tab1, tab2, *tab3 = st.tabs(tabs)


with st.sidebar:
    st.markdown(f"👤 `{st.session_state.username}` ({st.session_state.user_role})")
    if st.button("🔓 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 📤 Upload & Analyze Invoices Tab
with tab1:
    st.subheader("📤 Upload HR Policy and Invoices")
    policy_pdf = st.file_uploader("📄 HR Policy PDF", type=["pdf"])
    invoice_zip = st.file_uploader("🧾 ZIP of Invoices", type=["zip"])
    employee_name = st.text_input("👤 Employee Name", value=st.session_state.username)

    if st.button("🚀 Analyze Invoices"):
        if not policy_pdf or not invoice_zip or not employee_name:
            st.warning("⚠️ All fields required")
        else:
            reader = PdfReader(policy_pdf)
            st.session_state.policy_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])

            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(invoice_zip, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)
                pdfs = [f for f in os.listdir(tmpdir) if f.endswith(".pdf")]

                results = []
                progress = st.progress(0)
                for i, fname in enumerate(pdfs):
                    file_path = os.path.join(tmpdir, fname)
                    invoice_text = "\n".join([p.extract_text() for p in PdfReader(file_path).pages if p.extract_text()])
                    analysis = analyze_invoice(st.session_state.policy_text, invoice_text)
                    status, reason = analysis.split("Reason:", 1) if "Reason:" in analysis else ("Unknown", analysis)

                    add_to_vector_db(
                        document_id=fname,
                        text=invoice_text,
                        metadata={
                            "employee": employee_name.lower().strip(),
                            "status": status.replace("Status:", "").strip(),
                            "reason": reason.strip(),
                            "invoice_id": fname
                        }
                    )
                    results.append((fname, analysis))
                    progress.progress((i + 1) / len(pdfs))

                st.success("Analysis Complete")
                for fname, result in results:
                    with st.expander(f"📄 {fname}"):
                        st.markdown(f"```\n{result}\n```")

# 💬 Chatbot Tab
with tab2:
    st.subheader("💬 Invoice Chatbot Assistant")

    # 🎯 Filters in Sidebar — only for Chat
    with st.sidebar:
        st.markdown("### 🔍 Chatbot Filters")
        employee_filter = st.text_input("Filter by Employee Name")
        status_filter = st.selectbox("Filter by Status", ["", "Fully Reimbursed", "Partially Reimbursed", "Declined"])
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input("💬 Ask your question")

    filters = {}
    if employee_filter:
        filters["employee"] = employee_filter.strip().lower()
    if status_filter:
        filters["status"] = status_filter.strip()

    if query:
        with st.spinner("🤖 Thinking..."):
            results = query_vector_db(query_text=query, top_k=5, filters=filters)
            docs = results.get("documents", [[]])[0]

            if not docs or all(d.strip() == "" for d in docs):
                st.info("🔎 No matching invoice found. Trying fallback...")
                fallback = query_vector_db("alcohol", top_k=5)
                docs = fallback.get("documents", [[]])[0]

            if docs:
                answer = chat_with_documents(query, docs, st.session_state.policy_text)
                st.session_state.chat_history.append(("🧑‍💼 You", query))
                st.session_state.chat_history.append(("🤖 Bot", answer))
            else:
                st.warning("🤖 No relevant data found.")

    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:**")
        st.markdown(message, unsafe_allow_html=True)
        st.markdown("---")

# 📊 Admin Dashboard
if tab3:
    with tab3[0]:
        st.subheader("📊 Admin Dashboard")
        try:
            res = query_vector_db("invoice", top_k=100)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]

            if docs:
                df = pd.DataFrame([
                    {
                        "Invoice ID": metas[i].get("invoice_id", ""),
                        "Employee": metas[i].get("employee", ""),
                        "Status": metas[i].get("status", ""),
                        "Reason": metas[i].get("reason", ""),
                        "Snippet": docs[i][:200]
                    }
                    for i in range(len(docs))
                ])
                st.dataframe(df, use_container_width=True)

                buffer = BytesIO()
                df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)
                st.download_button(
                    "📥 Download Excel",
                    data=buffer,
                    file_name="invoice_history.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No data yet.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
