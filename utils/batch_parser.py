import os
from utils.pdf_parser import extract_text_from_pdf
from utils.shared_invoice_utils import process_invoice_file 

def process_invoice_file_wrapper(file_path: str, policy_text: str, employee_name: str) -> dict:
    """
    Wrapper for compatibility if needed externally, but uses shared logic.
    """
    return process_invoice_file(file_path, policy_text, employee_name)
