# app_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from rag_with_sambanova import init_rag, query_rag  # ✅ use correct file name

# -----------------------------
# LIFESPAN HANDLER (NEW WAY)
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up...")
    init_rag()   # initialize RAG
    yield
    print("🛑 Shutting down...")

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(
    title="News RAG API",
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
    return {"message": "News RAG API running"}

@app.post("/ask")
def ask(req: QueryRequest):
    return query_rag(req.question)

# Optional: clear memory endpoint
@app.post("/clear-memory")
def clear_memory():
    from rag_with_sambanova import chat_history
    chat_history.clear()
    return {"status": "Memory cleared"}