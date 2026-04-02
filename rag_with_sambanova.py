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

CATEGORIES = [
    "Politics", "Technology", "Sports",
    "Business", "Health", "Entertainment",
    "World", "Science"
]

# -----------------------------
# INIT FUNCTION
# -----------------------------
def init_rag():
    global vectorstore, client

    print("🔄 Initializing RAG system...")

    # Initialize embeddings (FIXED)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Check FAISS path (FIXED)
    faiss_path = "./faiss_npr_test"
    if not os.path.exists(faiss_path):
        raise FileNotFoundError("❌ FAISS index not found. Run embedding step first.")

    # Load FAISS index
    vectorstore = FAISS.load_local(
        faiss_path,
        embeddings,
        allow_dangerous_deserialization=True
    )


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
            "content": (
                "You are a news assistant. Answer ONLY using provided articles. "
                "Summarize clearly and cite sources."
            )
        }
    ]

    # Add last 3 chat history
    for chat in chat_history[-3:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})

    # Add current query
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
        # Detect category from query
        category = detect_category(query)

        # Retrieve documents (MMR search)
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5}
        )

        docs = retriever.invoke(query)

        # Manual category filtering (MORE RELIABLE)
        if category:
            docs = [
                d for d in docs
                if d.metadata.get("category") == category
            ]

        if not docs:
            return {
                "answer": "⚠️ No relevant articles found.",
                "sources": []
            }

        # Clean text helper
        def clean(text):
            return text.replace("\n", " ").replace("\r", " ").strip()

        # Build context
        context = "\n\n".join([
            f"[{d.metadata.get('category','General')}] {d.metadata.get('title','N/A')}:\n"
            f"{clean(d.page_content)[:max_chars]}"
            for d in docs
        ])

        # Build messages
        messages = build_messages(query, context)

        # Call LLM
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=messages,
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()

        if not answer:
            answer = "⚠️ Could not generate a proper answer. Try again."

        # Store memory
        chat_history.append({
            "user": query,
            "assistant": answer
        })

        # Limit memory size
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


# -----------------------------
# TEST RUN (optional)
# -----------------------------
if __name__ == "__main__":
    init_rag()

    while True:
        q = input("\nAsk a question (or 'exit'): ")
        if q.lower() == "exit":
            break

        result = query_rag(q)

        print("\n🧠 Answer:\n", result["answer"])
        print("\n📚 Sources:")
        for s in result["sources"]:
            print(f"- {s['title']} ({s['category']}, {s['date']})")