from langchain_community.vectorstores import FAISS
from myembeddings import embeddings

# ─── Load FAISS index
vectorstore = FAISS.load_local(
    "./faiss_npr_minimal",
    embeddings,
    allow_dangerous_deserialization=True
)
print("FAISS index loaded successfully.\n")

# ─── Create retriever
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})

# ─── Interactive query loop
while True:
    query = input("\nEnter your query (or type 'exit' to quit): ").strip()
    if query.lower() in ["exit", "quit"]:
        print("Exiting.")
        break

    print(f"\nSearching for: '{query}' ...")

    # ✅ Pass run_manager=None for your version
    try:
        results = retriever._get_relevant_documents(query, run_manager=None)
    except AttributeError:
        # fallback for older versions
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
