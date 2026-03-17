from langchain_community.vectorstores import FAISS
from create_embeddings_and_fiass import embeddings
from sambanova import SambaNova

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

retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 3}  # top 3 articles
)

# ───────────────────────────────
# Initialize SambaNova
# ───────────────────────────────
client = SambaNova(
    api_key="6bdd58a3-792a-40fb-af59-9abbc3ca6e4a",
    base_url="https://api.sambanova.ai/v1",
)

# ───────────────────────────────
# RAG response function
# ───────────────────────────────
def generate_qa_response(query: str):
    # Retrieve top 3 relevant articles
    relevant_docs = retriever.invoke(query)

    # Prepare context safely
    context = "\n\n".join([
        f"Article {i+1}:\nTitle: {doc.metadata.get('title', 'N/A')}\nContent: {doc.page_content[:300].replace(chr(10), ' ').replace(chr(13), ' ')}"
        for i, doc in enumerate(relevant_docs)
    ])

    # Build prompt including retrieved articles
    prompt = f"""You are a helpful assistant. Answer the question strictly based on the following news articles.

ARTICLES:
{context}

QUESTION: {query}

ANSWER:"""

    # Call SambaNova
    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant answering questions strictly based on the provided news articles."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        top_p=0.1
    )

    return {
        "result": response.choices[0].message.content,
        "source_documents": relevant_docs
    }

# ───────────────────────────────
# Interactive loop
# ───────────────────────────────
print("=" * 80)
print("RAG Q&A System with SambaNova SDK")
print("=" * 80)
print("Type 'exit' or 'quit' to exit.\n")

while True:
    query = input("\n📝 Ask a question: ").strip()
    if query.lower() in ["exit", "quit"]:
        print("Exiting. Goodbye!")
        break
    if not query:
        continue

    print("\n🔍 Searching and generating answer...\n")
    try:
        result = generate_qa_response(query)
        print("=" * 80)
        print("💡 ANSWER:")
        print("=" * 80)
        print(result["result"])
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your API key, internet connection, or prompt length.")