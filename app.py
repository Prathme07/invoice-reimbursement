import streamlit as st
import requests
from vector_store.db import query_vector_db
from llm.llm_chat import chat_with_documents

st.set_page_config(page_title="Invoice Reimbursement System", page_icon="🤖", layout="wide")

# Use sidebar as navigation
st.sidebar.title("📌 Navigation")
active_tab = st.sidebar.radio("Select a section", ["📤 Upload & Analyze", "💬 Chat with Bot"])
st.session_state.active_tab = active_tab

# 📤 Upload & Analyze Tab
if active_tab == "📤 Upload & Analyze":
    st.title("📤 Upload & Analyze Invoices")
    st.markdown("Use AI to check if uploaded invoices match your HR policy.")

    st.markdown("### 📘 Instructions")
    st.info("""
- 📄 **HR Policy PDF**: Upload one file.
- 🧾 **Invoices ZIP**: Upload a .zip file containing invoice PDFs.
- 👤 **Employee Name**: Used to tag all uploaded invoices.
- 🚀 Click 'Analyze Invoices' to trigger AI-based analysis.
    """)

    with st.container():
        st.markdown("### 📁 Upload Section")
        employee_name = st.text_input("👤 Employee Name", placeholder="e.g. John Doe")
        st.markdown("")  # Spacer

        col1, col2 = st.columns(2)
        with col1:
            policy_pdf = st.file_uploader("📄 Upload HR Policy PDF", type=["pdf"])
        with col2:
            invoices_zip = st.file_uploader("🧾 Upload ZIP of Invoice PDFs", type=["zip"])

        st.markdown("")  # Spacer

        if st.button("🚀 Analyze Invoices", use_container_width=True):
            if not policy_pdf or not invoices_zip or not employee_name:
                st.warning("⚠️ Please fill all fields before submitting.")
            else:
                with st.spinner("Analyzing invoices with AI..."):
                    try:
                        files = {
                            "policy_pdf": (policy_pdf.name, policy_pdf, "application/pdf"),
                            "invoices_zip": (invoices_zip.name, invoices_zip, "application/zip")
                        }
                        data = {
                            "employee_name": employee_name
                        }

                        response = requests.post(
                            "http://localhost:8000/analyze-invoices/",
                            files=files,
                            data=data
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Analysis complete!")
                            st.markdown(f"### 👤 Employee: `{result['employee_name']}`")

                            for filename, analysis in result["results"].items():
                                with st.expander(f"🧾 {filename}"):
                                    st.markdown(f"**Status & Reason:**\n```\n{analysis['analysis']}\n```")
                        else:
                            st.error(f"❌ Server Error: {response.status_code}\n{response.text}")
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")

# 💬 Chat with Bot Tab
elif active_tab == "💬 Chat with Bot":
    st.title("💬 Invoice Chatbot Assistant")
    st.markdown("Ask invoice-related questions using natural language.")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar filters (only shown in this tab)
    st.sidebar.markdown("## 🔍 Chatbot Filters")
    employee_filter = st.sidebar.text_input("Filter by Employee Name")
    status_filter = st.sidebar.selectbox("Filter by Status", ["", "Fully Reimbursed", "Partially Reimbursed", "Declined"])
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

    query = st.text_input("💬 Ask your question", placeholder="e.g. What is the status of Anand’s hotel invoice?")

    filters = {}
    if employee_filter:
        filters["employee"] = employee_filter
    if status_filter:
        filters["status"] = status_filter

    if query:
        with st.spinner("🤖 Thinking..."):
            try:
                results = query_vector_db(query_text=query, top_k=5, filters=filters)
                documents = results.get("documents", [[]])[0]
                answer = chat_with_documents(query, documents)

                st.session_state.chat_history.append(("🧑‍💼 You", query))
                st.session_state.chat_history.append(("🤖 Bot", answer))

            except Exception as e:
                st.error(f"❌ Error: {e}")

    # Display chat history
    st.markdown("---")
    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:**")
        st.markdown(f"{message}", unsafe_allow_html=True)
        st.markdown("---")
