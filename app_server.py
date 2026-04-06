# app_server_chat.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# ✅ Import the updated ChatGPT-style RAG module
from rag_with_sambanova import init_rag, query_rag, chat_history  

# -----------------------------
# LIFESPAN HANDLER
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up RAG system...")
    # Initialize RAG (blocking startup call)
    init_rag()
    yield
    print("🛑 Shutting down...")

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(
    title="News ChatGPT-style RAG API",
    lifespan=lifespan
)

# -----------------------------
# CORS (for React frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# REQUEST MODEL
# -----------------------------
class QueryRequest(BaseModel):
    question: str

# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def home():
    return {"message": "News ChatGPT-style RAG API running"}

@app.post("/ask")
def ask(req: QueryRequest):
    """
    Handles user query and returns a ChatGPT-style concise answer
    with summarized content and image URLs if present.
    """
    result = query_rag(req.question)
    return result

@app.post("/clear-memory")
def clear_memory():
    """
    Clears chat memory to reset context.
    """
    chat_history.clear()
    return {"status": "Memory cleared"}