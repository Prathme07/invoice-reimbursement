from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_documents(query: str, documents: list) -> str:
    context = "\n\n---\n\n".join(documents)

    prompt = f"""
You are a smart and helpful assistant trained to analyze and explain employee invoice reimbursements.
You have access to historical analysis of invoices processed according to HR policy.

Your task is:
1. Understand the user's question.
2. Refer to the documents provided.
3. Respond with accurate, clear, and structured answers using **Markdown** formatting.
4. If no relevant match is found, say so clearly.

---
### Instructions:
- Use headings, bullet points, or tables if needed.
- Always include **Status** and **Reason** if applicable.
- If the query is ambiguous or incomplete, ask for clarification.
- If no matching invoice is found, return a polite message saying it doesn't exist.
---

🧑‍💼 **User Query**:
{query}

📄 **Relevant Documents**:
{context}

---

🤖 **Your Response in Markdown**:
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"**Error:** {str(e)}"
