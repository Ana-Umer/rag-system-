"""
rag_engine.py — Core RAG pipeline
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

FAISS_INDEX_PATH = "./rag_faiss_index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 4
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class RAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        self.db: Optional[FAISS] = self._load_or_create_db()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _load_or_create_db(self) -> Optional[FAISS]:
        if os.path.exists(FAISS_INDEX_PATH):
            print("Loading existing FAISS index…")
            return FAISS.load_local(
                FAISS_INDEX_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        print("No existing index found — starting fresh.")
        return None

    def _save_db(self):
        if self.db is not None:
            self.db.save_local(FAISS_INDEX_PATH)

    # ------------------------------------------------------------------ #
    # Ingestion
    # ------------------------------------------------------------------ #
    def ingest_text(self, text: str, source: str = "user_input") -> int:
        """Chunk and embed plain text. Returns number of chunks added."""
        chunks = self.splitter.split_text(text)
        docs = [
            Document(page_content=chunk, metadata={"source": source})
            for chunk in chunks
        ]
        if self.db is None:
            self.db = FAISS.from_documents(docs, self.embeddings)
        else:
            self.db.add_documents(docs)
        self._save_db()
        return len(chunks)

    def ingest_pdf(self, file_bytes: bytes, filename: str = "uploaded.pdf") -> int:
        """Parse a PDF and ingest its text. Returns number of chunks added."""
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))# io .bytes used to convert bytes file to pdf 
        text = "\n\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()# go through every pages and get text 
        if not text:# if text not extracted raise the error 
            raise ValueError("Could not extract any text from the PDF.")
        return self.ingest_text(text, source=filename)# send to the text_ingestion because it has chunk and embeded instead of rewrite the logic it use the aleady exist logic 

    def reset(self):
        """Wipe the vector store and start fresh."""
        import shutil
        if os.path.exists(FAISS_INDEX_PATH):
            shutil.rmtree(FAISS_INDEX_PATH)# used to remove the folder  or  Removes entire directory
        self.db = None

    # ------------------------------------------------------------------ #
    # Query
    # ------------------------------------------------------------------ #
    def jls_extract_def(self):
        # used for generate the answer  or Sends prompt to AI model
        return 

    def jls_extract_def(self):
        # used for generate the answer  or Sends prompt to AI model = self.jls_extract_def()
        return 

    def jls_extract_def(self):
        # used for generate the answer  or Sends prompt to AI model
        return 

    def ask(self, question: str) -> dict:
        """Retrieve relevant chunks and generate a grounded answer."""
        if self.db is None:
            return {
                "answer": "No documents have been ingested yet. Please add some content first.",
                "sources": [],
                "chunks": [],
            }

        retriever = self.db.as_retriever(search_kwargs={"k": TOP_K})#“searches the database for relevant information
        relevant_docs = retriever.invoke(question)

        if not relevant_docs:
            return {
                "answer": "I couldn't find relevant information in the knowledge base.",
                "sources": [],
                "chunks": [],
            }

        context = "\n\n---\n\n".join(doc.page_content for doc in relevant_docs)# used for combine all pages into   one text 
        sources = list({doc.metadata.get("source", "unknown") for doc in relevant_docs})# here list used for remove the duplicate source name 
        chunks = [doc.page_content for doc in relevant_docs]

        prompt = f"""You are a helpful assistant. Answer the user's question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."
Do NOT make up information.

Context:
{context}

Question: {question} = self.jls_extract_def() = self.jls_extract_def()

Answer:"""

        response = self.llm.invoke(prompt)# used for generate the answer  or Sends prompt to AI model 
        return {
            "answer": response.content.strip(),
            "sources": sources,
            "chunks": chunks,
        }

    def has_documents(self) -> bool:
        return self.db is not None


# Singleton instance shared across requests
_engine: Optional[RAGEngine] = None


def get_engine() -> RAGEngine:
    global _engine
    if _engine is None:
        _engine = RAGEngine()
    return _engine
