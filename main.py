from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
import os, zipfile
import pandas as pd

from utils.pdf_parser import extract_text_from_pdf
from llm.llm_chat import chat_with_documents
from llm.groq_analyzer import analyze_invoice
from vector_store.db import add_to_vector_db, query_vector_db, search_similar_docs

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze-invoices/")
async def analyze_invoices(
    policy_pdf: UploadFile = File(...),
    invoices_zip: UploadFile = File(...),
    employee_name: str = Form(...)
):
    try:
        # Save the uploaded files
        policy_path = os.path.join(UPLOAD_DIR, policy_pdf.filename)
        with open(policy_path, "wb") as f:
            f.write(await policy_pdf.read())

        zip_path = os.path.join(UPLOAD_DIR, invoices_zip.filename)
        with open(zip_path, "wb") as f:
            f.write(await invoices_zip.read())

        # Extract ZIP contents
        extract_folder = os.path.join(UPLOAD_DIR, "invoices")
        os.makedirs(extract_folder, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        policy_text = extract_text_from_pdf(policy_path)

        invoice_texts = {}
        for filename in os.listdir(extract_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(extract_folder, filename)
                invoice_text = extract_text_from_pdf(file_path)
                result = analyze_invoice(policy_text, invoice_text)

                invoice_texts[filename] = {
                    "analysis": result,
                    "invoice_text_start": invoice_text[:200]
                }

                # Store in vector DB
                add_to_vector_db(
                    document_id=filename,
                    text=invoice_text,
                    metadata={
                        "employee": employee_name,
                        "analysis": result
                    }
                )

        return JSONResponse({
            "message": "AI Analysis completed",
            "employee_name": employee_name,
            "results": invoice_texts
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/search-invoices/")
def search_invoices(query: str = Query(..., description="Search invoices using AI")):
    try:
        docs = search_similar_docs(query, top_k=5)
        text_chunks = [doc['text'] for doc in docs]
        answer = chat_with_documents(query, text_chunks)
        return {
            "query": query,
            "response": answer
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/export-excel/")
def export_excel():
    try:
        chroma_results = query_vector_db("invoice")  

        data = []
        for i in range(len(chroma_results["documents"][0])):
            data.append({
                "Invoice Name": chroma_results["ids"][0][i],
                "Employee": chroma_results["metadatas"][0][i]["employee"],
                "AI Analysis": chroma_results["metadatas"][0][i]["analysis"],
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
        return {"error": str(e)}


@app.get("/")
def read_root():
    return {"message": "Welcome to the Invoice Analyzer API"}
