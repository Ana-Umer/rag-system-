"""
main.py — FastAPI server for the Simple RAG System
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from rag_engine import get_engine

load_dotenv()

app = FastAPI(
    title="LABU  RAG System",
    description="A Retrieval-Augmented Generation system powered by LangChain + FAISS + Groq",
    version="1.0.0",
)

# ------------------------------------------------------------------ #
# Request/Response models
# ------------------------------------------------------------------ #

class IngestTextRequest(BaseModel):
    text: str
    source: str = "user_input"


class AskRequest(BaseModel):
    question: str


# ------------------------------------------------------------------ #
# API endpoints
# ------------------------------------------------------------------ #

@app.get("/health")# Hey! If someone sends a GET request to /health, run the function below. or /health is url endpoint to get the function below 
def health():
    engine = get_engine()
    return {
        "status": "ok",
        "has_documents": engine.has_documents(),
    }


@app.post("/ingest/text")
def ingest_text(body: IngestTextRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    engine = get_engine()
    chunks_added = engine.ingest_text(body.text, source=body.source)
    return {"message": f"Ingested successfully.", "chunks_added": chunks_added}


@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    allowed_types = {"text/plain", "application/pdf"}
    filename = file.filename or "upload"# used to get the of file not the file has no name defualt upload
    ext = Path(filename).suffix.lower()#Extracts the file extension (like .txt or .pdf)

    if ext not in (".txt", ".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .pdf files are supported.",
        )

    contents = await file.read()#Reads the entire content of the uploaded file
    engine = get_engine()# used to get brain system  The engine is what stores and processes the documents

    try:
        if ext == ".pdf":
            chunks_added = engine.ingest_pdf(contents, filename=filename)
        else:
            text = contents.decode("utf-8", errors="ignore")
            chunks_added = engine.ingest_text(text, source=filename)# 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": f"File '{filename}' ingested.", "chunks_added": chunks_added}


@app.post("/ask")
def ask_question(body: AskRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    engine = get_engine()
    result = engine.ask(body.question)
    return result


@app.post("/reset")
def reset_knowledge_base():
    engine = get_engine()
    engine.reset()
    return {"message": "Knowledge base cleared successfully."}


# ------------------------------------------------------------------ #
# Serve frontend
# ------------------------------------------------------------------ #

FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_PATH = FRONTEND_DIR / "index.html"
CSS_PATH = FRONTEND_DIR / "style.css"
JS_PATH = FRONTEND_DIR / "app.js"

from fastapi.responses import FileResponse

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if not FRONTEND_PATH.exists():
        return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
    return HTMLResponse(content=FRONTEND_PATH.read_text(encoding="utf-8"))

@app.get("/style.css")
def serve_css():
    if CSS_PATH.exists():
        return FileResponse(CSS_PATH, media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")

@app.get("/app.js")
def serve_js():
    if JS_PATH.exists():
        return FileResponse(JS_PATH, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")
