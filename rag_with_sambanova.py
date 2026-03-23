# rag_with_sambanova.py
import os
import re
from langchain_community.vectorstores import FAISS
from sambanova import SambaNova
from create_embeddings_and_fiass import embeddings

# -----------------------------
# GLOBALS
# -----------------------------
vectorstore = None
client = None
chat_history = []   # ✅ basic memory

CATEGORIES = ["Politics", "Technology", "Sports", "Business", "Health", "Entertainment", "World", "Science"]

# -----------------------------
# INIT FUNCTION
# -----------------------------
def init_rag():
    global vectorstore, client

    print("🔄 Initializing RAG system...")

    # Load FAISS index
    vectorstore = FAISS.load_local(
        "./faiss_npr_test",
        embeddings,
        allow_dangerous_deserialization=True
    )

    client = SambaNova(
        api_key="6bdd58a3-792a-40fb-af59-9abbc3ca6e4a",
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

    # ✅ last 3 conversations
    for chat in chat_history[-3:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})

    # current query
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
        # Category filtering
        category = detect_category(query)

        if category:
            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "filter": {"category": category}}
            )
        else:
            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5}
            )

        docs = retriever.invoke(query)

        if not docs:
            return {
                "answer": "⚠️ No relevant articles found.",
                "sources": []
            }

        # Clean text
        def clean(text):
            return text.replace("\n", " ").replace("\r", " ").strip()

        # Build context
        context = "\n\n".join([
            f"[{d.metadata.get('category','General')}] {d.metadata.get('title','N/A')}:\n"
            f"{clean(d.page_content)[:max_chars]}"
            for d in docs
        ])

        # Build messages with memory
        messages = build_messages(query, context)

        # LLM call
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=messages,
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()
        if not answer:
            answer = "⚠️ Could not generate a proper answer. Try again."

        # ✅ store memory
        chat_history.append({
            "user": query,
            "assistant": answer
        })

        # limit memory
        if len(chat_history) > 10:
            chat_history.pop(0)

        return {
            "answer": answer,
            "sources": [
                {
                    "title": d.metadata.get("title", ""),
                    "category": d.metadata.get("category", ""),
                    "link": d.metadata.get("source", "")
                }
                for d in docs
            ]
        }

    except Exception as e:
        return {
            "answer": f"❌ Error: {e}",
            "sources": []
        }