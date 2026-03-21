from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import threading

# --- FastAPI app ---
app = FastAPI(title="News RAG API")

# --- CORS setup (required for React frontend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],   # allow GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# --- Request schema ---
class QueryRequest(BaseModel):
    question: str

# --- Globals ---
vectorstore = None
retriever = None
client = None
services_ready = False

# --- Placeholder response ---
def placeholder_answer(question: str):
    return {
        "answer": f"You asked: {question} (placeholder because services not ready)",
        "sources": [],
        "status": "placeholder"
    }

# --- Initialize FAISS and SambaNova ---
def init_services():
    global vectorstore, retriever, client, services_ready
    try:
        print("Initializing FAISS and SambaNova...")

        from langchain_community.vectorstores import FAISS
        from create_embeddings_and_fiass import embeddings
        from sambanova import SambaNova

        # Load FAISS index
        vectorstore = FAISS.load_local(
            "./faiss_npr_test",
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k":3})

        # Initialize SambaNova client
        client = SambaNova(
            api_key="6bdd58a3-792a-40fb-af59-9abbc3ca6e4a",
            base_url="https://api.sambanova.ai/v1",
        )

        services_ready = True
        print("✓ FAISS and SambaNova are ready!")
    except Exception as e:
        print(f"⚠️ Initialization failed: {e}")
        services_ready = False

threading.Thread(target=init_services, daemon=True).start()

# --- RAG logic ---
def generate_answer(query: str):
    global retriever, client, services_ready

    if not services_ready or not retriever or not client:
        return placeholder_answer(query)

    try:
        docs = retriever.invoke(query)
        context = "\n\n".join([
            f"Title: {doc.metadata.get('title','N/A')}\nContent: {doc.page_content[:600]}"
            for doc in docs
        ])
        prompt = f"""
Answer the question using ONLY the news articles below.

ARTICLES:
{context}

QUESTION:
{query}

ANSWER:
"""
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[
                {"role": "system", "content": "Answer questions using only the provided news articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": [
                {"title": doc.metadata.get("title",""), "link": doc.metadata.get("source","")}
                for doc in docs
            ],
            "status": "real"
        }
    except Exception as e:
        return {"answer": f"Error generating answer: {e}", "sources": [], "status": "error"}

# --- API endpoints ---
@app.get("/")
def home():
    return {"message": "News RAG API is running", "services_ready": services_ready}

@app.post("/ask")
def ask_question(request: QueryRequest):
    return generate_answer(request.question)