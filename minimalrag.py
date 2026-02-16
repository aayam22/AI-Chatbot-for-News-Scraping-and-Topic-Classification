# minimalrag_fixed.py
# Modern minimal RAG retrieval test — works with current LangChain + your existing files

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Reuse your existing loader & embeddings
from load_documents import load_articles
from myembeddings import embeddings   # ← your BAAI/bge-small-en-v1.5 instance

# ─── Option A: Load fresh documents from DB (good for testing) ───
print("Loading articles from SQLite...")
documents = load_articles(limit=80)   # adjust limit as needed
print(f"→ Loaded {len(documents)} documents")

# If documents is empty → early exit
if not documents:
    print("No documents loaded. Check DB or load_articles().")
    exit()

# Optional: small chunking if your articles are very long
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=80,
    length_function=len,
    add_start_index=True,
)

print("Splitting documents...")
split_docs = text_splitter.split_documents(documents)
print(f"→ Created {len(split_docs)} chunks")

# ─── Create / Load FAISS ────────────────────────────────────────
INDEX_PATH = "./faiss_npr_minimal"

try:
    print("Trying to load existing FAISS index...")
    vectorstore = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("→ Loaded existing index")
except Exception as e:
    print("No index found or load failed → creating new one...")
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    vectorstore.save_local(INDEX_PATH)
    print(f"→ New index created & saved to {INDEX_PATH}")

# ─── Create retriever ───────────────────────────────────────────
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}          # return top 4 results
)

# ─── Test retrieval ─────────────────────────────────────────────
queries = [
    "climate change Nepal",
    "election 2024 results",
    "Gaza OR Israel ceasefire",
    "artificial intelligence regulation",
]

for q in queries:
    print("\n" + "═" * 70)
    print(f"Query: {q}")
    print("═" * 70)

    # Modern way (LangChain ≥ 0.2)
    docs = retriever.invoke(q)

    # Fallback for older versions (if invoke doesn't exist)
    # docs = retriever.get_relevant_documents(q) if hasattr(retriever, "get_relevant_documents") else retriever._get_relevant_documents(q)

    for i, doc in enumerate(docs, 1):
        print(f"\nResult {i}  (score hint: higher relevance = better match)")
        print(f"Title : {doc.metadata.get('title', '—')[:90]}")
        print(f"Date  : {doc.metadata.get('date', '—')}")
        print(f"Source: {doc.metadata.get('source', '—')}")
        print(f"Text preview:")
        print(doc.page_content[:380].replace("\n", " ").strip() + "...")
        print("─" * 60)

print("\nDone. You can now plug this retriever into a real chain / LLM.")