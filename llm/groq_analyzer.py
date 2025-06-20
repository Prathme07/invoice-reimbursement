import time
import os
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_invoice(policy_text, invoice_text, max_retries=3, base_delay=2):
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
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[Attempt {attempt}] LLM call failed: {e}")
            if attempt == max_retries:
                return f"Status: Unknown\nReason: LLM call failed after {max_retries} attempts: {e}"
            else:
                delay = base_delay * attempt
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)