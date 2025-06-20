import os
import re
from utils.pdf_parser import extract_text_from_pdf
from llm.groq_analyzer import analyze_invoice
from vector_store.db import add_to_vector_db
from utils.logger import setup_logger

logger = setup_logger()

def extract_date_from_text(text: str) -> str:
    patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b',
        r'\b\d{1,2} \w+ \d{4}\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return "Unknown"

def process_invoice_file(file_path: str, policy_text: str, employee_name: str) -> dict:
    try:
        filename = os.path.basename(file_path)
        invoice_text = extract_text_from_pdf(file_path)

        if not invoice_text:
            raise ValueError("No text extracted from PDF.")

        invoice_date = extract_date_from_text(invoice_text)
        result = analyze_invoice(policy_text, invoice_text)

        if not result:
            raise ValueError("No response from LLM.")

        status, reason = result.split("Reason:", 1) if "Reason:" in result else ("Unknown", result)

        add_to_vector_db(
            document_id=filename,
            text=invoice_text,
            metadata={
                "employee": employee_name,
                "status": status.replace("Status:", "").strip(),
                "reason": reason.strip(),
                "invoice_id": filename,
                "date": invoice_date
            }
        )

        return {
            "filename": filename,
            "analysis": result,
            "invoice_text_start": invoice_text[:200]
        }

    except Exception as e:
        logger.error(f"Error processing invoice '{file_path}': {str(e)}", exc_info=True)
        return {
            "filename": file_path,
            "error": str(e),
            "analysis": "Failed",
            "invoice_text_start": ""
        }
