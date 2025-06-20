import streamlit as st
import os
from vector_store.db import search_similar_docs
from llm.llm_chat import chat_with_documents

st.set_page_config(page_title="Invoice Chatbot", page_icon="💬")

st.title("Invoice Reimbursement Chatbot")
st.markdown("Ask questions about analyzed invoices stored in the system.")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


query = st.text_input("Enter your query:")

if query:
    with st.spinner("Thinking..."):
        docs = search_similar_docs(query)
        chunks = [doc["text"] for doc in docs]
        answer = chat_with_documents(query, chunks)

        st.session_state.chat_history.append(("You", query))
        st.session_state.chat_history.append(("Bot", answer))


for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"**🧑‍💼 You:** {message}")
    else:
        st.markdown(f"**🤖 Bot:** {message}")
