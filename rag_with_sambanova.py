# rag_with_sambanova_final_chat_fixed.py

import os
import re
import torch
import nltk
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sambanova import SambaNova
from nltk.tokenize import sent_tokenize

# -----------------------------
# GLOBALS
# -----------------------------
vectorstore = None
client = None
chat_history = []
llm_model = "Meta-Llama-3.1-8B-Instruct"

CATEGORIES = [
    "Politics", "Technology", "Sports",
    "Business", "Health", "Entertainment",
    "World", "Science", "Wildlife"
]

# -----------------------------
# RAG INITIALIZATION
# -----------------------------
def init_rag(
    faiss_path="./faiss_npr_test",
    embedding_model="BAAI/bge-small-en-v1.5",
    llm_model_param="Meta-Llama-3.1-8B-Instruct",
    sambanova_api_key=os.getenv("SAMBANOVA_API_KEY")
):
    global vectorstore, client, llm_model
    llm_model = llm_model_param

    print("🔄 Initializing RAG system...")

    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model,
        model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    if os.path.exists(faiss_path):
        vectorstore = FAISS.load_local(
            faiss_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Loaded existing FAISS index")
    else:
        vectorstore = FAISS.from_documents([], embeddings)
        print("⚠️ FAISS index not found. Created empty FAISS index")

    client = SambaNova(
        api_key=sambanova_api_key,
        base_url="https://api.sambanova.ai/v1"
    )

    print(f"✅ RAG ready! Using LLM model: {llm_model}")

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
# CONTEXT CLEANING
# -----------------------------
def clean_context(text, max_chars=700):
    sentences = sent_tokenize(text)
    context = ""
    for s in sentences:
        if len(context) + len(s) > max_chars:
            break
        context += s + " "
    return context.strip()

# -----------------------------
# BUILD MESSAGES (ChatGPT-style)
# -----------------------------
def build_messages(query, context):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful news assistant like ChatGPT. "
                "Read the provided articles and answer the user's question concisely in 3-5 sentences. "
                "Use natural, conversational language, summarize key points, and include image URLs only if relevant. "
                "Always cite article titles and categories where appropriate."
            )
        }
    ]

    # Add last 5 chat history
    for chat in chat_history[-5:]:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})

    messages.append({
        "role": "user",
        "content": f"ARTICLES:\n{context}\n\nQUESTION: {query}"
    })

    return messages

# -----------------------------
# MAIN QUERY FUNCTION
# -----------------------------
def query_rag(query: str, max_chars=700, top_k=10):
    global vectorstore, client, chat_history, llm_model

    if not vectorstore or not client:
        return {"answer": "⚠️ RAG system not initialized", "sources": []}

    try:
        category = detect_category(query)

        # -----------------------------
        # RETRIEVE DOCUMENTS
        # -----------------------------
        docs = vectorstore.similarity_search(query, k=top_k)

        # Apply category filter manually
        if category:
            docs = [d for d in docs if d.metadata.get("category", "").lower() == category.lower()]

        if not docs:
            return {"answer": "⚠️ No relevant articles found.", "sources": []}

        # -----------------------------
        # BUILD CONTEXT
        # -----------------------------
        context = "\n\n".join([
            f"[{d.metadata.get('category','General')}] {d.metadata.get('title','N/A')}:\n"
            f"{clean_context(d.page_content, max_chars)}\n"
            f"Image URL: {d.metadata.get('image_url','No Image')}"
            for d in docs
        ])

        # -----------------------------
        # BUILD CHAT MESSAGES
        # -----------------------------
        messages = build_messages(query, context)

        # -----------------------------
        # CALL LLM
        # -----------------------------
        response = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip() or "⚠️ Could not generate an answer."

        # -----------------------------
        # UPDATE CHAT HISTORY
        # -----------------------------
        chat_history.append({"user": query, "assistant": answer})
        if len(chat_history) > 10:
            chat_history.pop(0)

        return {
            "answer": answer,
            "sources": [
                {
                    "title": d.metadata.get("title", ""),
                    "category": d.metadata.get("category", ""),
                    "date": d.metadata.get("date", ""),
                    "image_url": d.metadata.get("image_url", "")
                }
                for d in docs
            ]
        }

    except Exception as e:
        return {"answer": f"❌ Error: {e}", "sources": []}

# -----------------------------
# TEST RUN
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
            print(f"  Image URL: {s['image_url']}\n")