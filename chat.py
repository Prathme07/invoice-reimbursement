import streamlit as st
from vector_store.db import query_vector_db

st.set_page_config(page_title="Invoice Policy Chat", page_icon="💬")

st.title("🧾 Invoice Policy Chatbot")
st.markdown("Ask questions like:")
st.markdown("- *Why was invoice 5 declined?*")
st.markdown("- *Which invoice has alcohol?*")
st.markdown("- *Show all partially reimbursed invoices*")

query = st.text_input("Ask something about the invoices or policy:")

if query:
    with st.spinner("Searching..."):
        results = query_vector_db(query)
        for i in range(len(results['documents'][0])):
            st.markdown("----")
            st.markdown(f"**📄 Invoice:** {results['ids'][0][i]}")
            st.markdown(f"**💬 Match:** {results['documents'][0][i][:300]}...")
            meta = results['metadatas'][0][i]
            st.markdown(f"**👤 Employee:** {meta['employee']}")
            st.markdown(f"**🧠 AI Analysis:** {meta['analysis']}")
