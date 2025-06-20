from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_with_documents(query: str, documents: list) -> str:
    context = "\n\n".join(documents)
    prompt = f"""You are an intelligent assistant. Based on the documents below, answer the user's query clearly.
    
User Query: {query}

Relevant Documents:
{context}

Answer:"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192", 
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
