"""
Test retrieval + Interactive RAG query
Combines test_retrieval.py + rag_query.py
"""

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from create_embeddings_and_fiass import embeddings  # optional: reuse embeddings from previous step

# --- Step 1: Load FAISS index ---
vectorstore = FAISS.load_local("./faiss_npr_test", embeddings, allow_dangerous_deserialization=True)
print("FAISS index loaded successfully.\n")

# --- Step 2: Test query ---
query = "news about climate change or environment"
results = vectorstore.similarity_search(query, k=3)
print(f"--- Test Retrieval for query: '{query}' ---\n")
for i, doc in enumerate(results, 1):
    print(f"Result {i}")
    print("Title:", doc.metadata["title"][:80], "...")
    print("Score hint: relevant content below ↓")
    print(doc.page_content[:400], "...\n")

# --- Step 3: Interactive RAG Query ---
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})

while True:
    query = input("\nEnter your query (or type 'exit' to quit): ").strip()
    if query.lower() in ["exit", "quit"]:
        print("Exiting.")
        break

    print(f"\nSearching for: '{query}' ...")

    try:
        results = retriever._get_relevant_documents(query, run_manager=None)
    except AttributeError:
        results = retriever.get_relevant_documents(query)

    if not results:
        print("No relevant articles found.")
        continue

    print(f"\nTop {len(results)} results:\n")
    for i, doc in enumerate(results, 1):
        print(f"Result {i}")
        print(f"Title : {doc.metadata.get('title','N/A')}")
        print(f"Date  : {doc.metadata.get('scraped_at','N/A')}")
        print(f"Source: {doc.metadata.get('source','N/A')}")
        snippet = doc.page_content[:400].replace("\n", " ")
        print(f"Preview: {snippet}...\n")
        print("-" * 80)
