# rag_with_sambanova.py
import os
import re
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sambanova import SambaNova

# -----------------------------
# GLOBALS
# -----------------------------
vectorstore = None
client = None
chat_history = []

CATEGORIES = ["Politics", "Technology", "Sports", "Business", "Health", "Entertainment", "World", "Science"]

# -----------------------------
# INIT FUNCTION
# -----------------------------
def init_rag():
    global vectorstore, client

    print("🔄 Initializing RAG system...")

    # ✅ FIX 1: Proper embeddings initialization
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # ✅ FIX 2: Safe FAISS loading
    if not os.path.exists("./faiss_npr_test"):
        raise FileNotFoundError("❌ FAISS index not found. Run embedding step first.")

    vectorstore = FAISS.load_local(
        "./faiss_npr_test",
        embeddings,
        allow_dangerous_deserialization=True
    )

    # ✅ FIX 3: Use env variable for API key
    client = SambaNova(
            api_key="9178836e-f0bd-4229-bbbe-e295bf1a7f3f",
            base_url="https://api.sambanova.ai/v1",
        )


    print("✅ RAG ready!")

# -----------------------------
# CATEGORY DETECTION
# -----------------------------
def detect_category(query: str):
    query_lower = query.lower()
    for cat in CATEGORIES:
        if re.search(rf"\b{cat.lower()}\b", query_lower):
            return cat
    return None

# -----------------------------
# BUILD MESSAGES WITH MEMORY
# -----------------------------
def build_messages(query, context):
    messages = [
        {
            "role": "system",
            "content": "You are a news assistant. Answer ONLY using provided articles. Cite sources clearly."
        }
    ]

    for chat in chat_history[-3:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})

    messages.append({
        "role": "user",
        "content": f"ARTICLES:\n{context}\n\nQUESTION: {query}"
    })

    return messages

# -----------------------------
# MAIN RAG FUNCTION
# -----------------------------
def query_rag(query: str, max_chars=700):
    global vectorstore, client, chat_history

    if not vectorstore or not client:
        return {
            "answer": "⚠️ RAG system not initialized",
            "sources": []
        }

    try:
        category = detect_category(query)

        # ✅ safer retriever
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5}
        )

        docs = retriever.invoke(query)

        # ✅ manual filtering (more reliable than FAISS filter)
        if category:
            docs = [d for d in docs if d.metadata.get("category") == category]

        if not docs:
            return {
                "answer": "⚠️ No relevant articles found.",
                "sources": []
            }

        def clean(text):
            return text.replace("\n", " ").replace("\r", " ").strip()

        context = "\n\n".join([
            f"[{d.metadata.get('category','General')}] {d.metadata.get('title','N/A')}:\n"
            f"{clean(d.page_content)[:max_chars]}"
            for d in docs
        ])

        messages = build_messages(query, context)

        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=messages,
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()

        if not answer:
            answer = "⚠️ Could not generate a proper answer. Try again."

        # store memory
        chat_history.append({
            "user": query,
            "assistant": answer
        })

        if len(chat_history) > 10:
            chat_history.pop(0)

        return {
            "answer": answer,
            "sources": [
                {
                    "title": d.metadata.get("title", ""),
                    "category": d.metadata.get("category", ""),
                    "date": d.metadata.get("date", "")
                }
                for d in docs
            ]
        }

    except Exception as e:
        return {
            "answer": f"❌ Error: {e}",
            "sources": []
        }