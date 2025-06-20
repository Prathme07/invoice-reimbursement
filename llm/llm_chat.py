import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_documents(query: str, documents: list, policy_text: str = "") -> str:
    context = "\n\n---\n\n".join(documents)

    prompt = f"""
You are a smart and accurate assistant trained to analyze and explain employee invoice reimbursements.

You must always refer to the **official HR reimbursement policy** provided below to guide your response.
Do NOT assume anything about alcohol, food, lodging, or limits unless they are specifically mentioned in the policy.

---

📘 **HR Policy**:
{policy_text or "No HR policy provided."}

---

🧑‍💼 **User Query**:
{query}

---

📄 **Relevant Invoice Texts**:
{context}

---

### Your Response (Use Markdown):
- Answer clearly and briefly.
- Always include **Status** and **Reason** (based on policy).
- If no relevant match, say so politely.
- If the query is unclear, ask for clarification.
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"**Error:** {str(e)}"
