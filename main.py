from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import os, zipfile
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial

from utils.pdf_parser import extract_text_from_pdf
from utils.shared_invoice_utils import process_invoice_file
from llm.llm_chat import chat_with_documents
from vector_store.db import query_vector_db
from utils.logger import setup_logger

app = FastAPI()
logger = setup_logger("main_api")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze-invoices/")
async def analyze_invoices(
    policy_pdf: UploadFile = File(...),
    invoices_zip: UploadFile = File(...),
    employee_name: str = Form(...)
):
    try:
        policy_path = os.path.join(UPLOAD_DIR, policy_pdf.filename)
        with open(policy_path, "wb") as f:
            f.write(await policy_pdf.read())

        zip_path = os.path.join(UPLOAD_DIR, invoices_zip.filename)
        with open(zip_path, "wb") as f:
            f.write(await invoices_zip.read())

        extract_folder = os.path.join(UPLOAD_DIR, "invoices")
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        policy_text = extract_text_from_pdf(policy_path)
        invoice_files = [
            os.path.join(extract_folder, f)
            for f in os.listdir(extract_folder)
            if f.endswith(".pdf")
        ]

        results = []
        for f in invoice_files:
            result = process_invoice_file(f, policy_text=policy_text, employee_name=employee_name)
            results.append(result)


        invoice_texts = {
            r["filename"]: {
                "analysis": r["analysis"],
                "invoice_text_start": r["invoice_text_start"]
            }
            for r in results
        }

        return JSONResponse({
            "message": "AI Analysis completed (batch processed)",
            "employee_name": employee_name,
            "results": invoice_texts
        })

    except Exception as e:
        logger.error(f"Error in /analyze-invoices: {str(e)}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/search-invoices/")
def search_invoices(
    query: str = Query(...),
    employee: Optional[str] = None,
    status: Optional[str] = None,
    invoice_id: Optional[str] = None,
    date: Optional[str] = None
):
    try:
        filters = {}
        if employee:
            filters["employee"] = employee
        if status:
            filters["status"] = status
        if invoice_id:
            filters["invoice_id"] = invoice_id
        if date:
            filters["date"] = date

        results = query_vector_db(query_text=query, top_k=5, filters=filters)
        return {
            "query": query,
            "filters": filters,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in /search-invoices: {str(e)}", exc_info=True)
        return {"error": str(e)}


@app.get("/export-excel/")
def export_excel():
    try:
        chroma_results = query_vector_db("invoice", top_k=100)

        data = []
        for i in range(len(chroma_results["documents"][0])):
            data.append({
                "Invoice Name": chroma_results["ids"][0][i],
                "Employee": chroma_results["metadatas"][0][i].get("employee", ""),
                "Status": chroma_results["metadatas"][0][i].get("status", ""),
                "Reason": chroma_results["metadatas"][0][i].get("reason", ""),
                "Date": chroma_results["metadatas"][0][i].get("date", ""),
                "Text Snippet": chroma_results["documents"][0][i][:100]
            })

        df = pd.DataFrame(data)
        file_path = "invoice_analysis_export.xlsx"
        df.to_excel(file_path, index=False)

        return FileResponse(
            path=file_path,
            filename=file_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"Error in /export-excel: {str(e)}", exc_info=True)
        return {"error": str(e)}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Invoice Analyzer API"}
