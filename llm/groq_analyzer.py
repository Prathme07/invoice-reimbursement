import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_invoice(policy_text, invoice_text):
    prompt = f"""
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
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
