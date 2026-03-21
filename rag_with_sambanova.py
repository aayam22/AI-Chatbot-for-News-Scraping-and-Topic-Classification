from langchain_community.vectorstores import FAISS
from create_embeddings_and_fiass import embeddings
from sambanova import SambaNova
import re

# ───────────────────────────────
# Load FAISS index
# ───────────────────────────────
print("Loading FAISS index...")
vectorstore = FAISS.load_local(
    "./faiss_npr_test",
    embeddings,
    allow_dangerous_deserialization=True
)
print("✓ FAISS index loaded successfully.\n")

# ───────────────────────────────
# Initialize SambaNova client
# ───────────────────────────────
client = SambaNova(
    api_key="6bdd58a3-792a-40fb-af59-9abbc3ca6e4a",
    base_url="https://api.sambanova.ai/v1",
)

# ───────────────────────────────
# Chat memory
# ───────────────────────────────
chat_history = []

# ───────────────────────────────
# Known categories
# ───────────────────────────────
CATEGORIES = ["Politics", "Technology", "Sports", "Business", "Health", "Entertainment", "World", "Science"]

# ───────────────────────────────
# Detect category in user query
# ───────────────────────────────
def detect_category(query: str):
    query_lower = query.lower()
    for cat in CATEGORIES:
        if re.search(rf"\b{cat.lower()}\b", query_lower):
            return cat
    return None

# ───────────────────────────────
# RAG response function
# ───────────────────────────────
def generate_qa_response(query: str, max_article_chars=500):
    try:
        # Check if user asked about a specific category
        category = detect_category(query)

        # Create retriever; filter by category if needed
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

        # Retrieve relevant docs
        relevant_docs = retriever.invoke(query)
        if not relevant_docs:
            return "⚠️ No relevant articles found.", []

        # Prepare context: use first N chars per article
        context = "\n\n".join([
            f"[{doc.metadata.get('category', 'General')}] {doc.metadata.get('title', 'N/A')}:\n{doc.page_content[:max_article_chars].replace(chr(10), ' ').replace(chr(13), ' ')}"
            for doc in relevant_docs
        ])

        # Build system + user messages for SambaNova
        system_msg = {
            "role": "system",
            "content": (
                "You are a helpful assistant. Answer the question by summarizing information from the provided news articles. "
                "Do not invent information. Cite sources in brackets with title or category when relevant."
            )
        }
        user_msg = {
            "role": "user",
            "content": f"ARTICLES:\n{context}\n\nQUESTION: {query}\nANSWER:"
        }

        # Call SambaNova
        response = client.chat.completions.create(
            model="Meta-Llama-3.1-8B-Instruct",
            messages=[system_msg, user_msg],
            temperature=0.2,
            top_p=0.95
        )

        answer = response.choices[0].message.content.strip()
        return answer, relevant_docs

    except Exception as e:
        return f"❌ Error generating response: {e}", []

# ───────────────────────────────
# Interactive chat loop
# ───────────────────────────────
def main():
    print("=" * 80)
    print("📰 RAG Chat with SambaNova (Category-aware, ChatGPT-style)")
    print("=" * 80)
    print("Type 'exit' or 'quit' to exit.\n")

    while True:
        query = input("\n📝 You: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        if not query:
            continue

        print("\n🔍 Searching and generating answer...\n")
        answer, docs = generate_qa_response(query)

        print("💡 Assistant:")
        print(answer)

        if docs:
            print("\n📚 Sources:")
            for i, doc in enumerate(docs, 1):
                title = doc.metadata.get("title", "N/A")
                category = doc.metadata.get("category", "General")
                date = doc.metadata.get("date", "Unknown")
                print(f"{i}. [{category}] {title} ({date})")

        chat_history.append({"user": query, "assistant": answer})

if __name__ == "__main__":
    main()