# small_fiastest.py
"""
Small FAISS test for NPR news articles (fixed for loading all articles).

- Loads all articles from SQLite DB
- Generates embeddings using Hugging Face model
- Creates FAISS vector store
- Saves index locally for reuse
"""

from langchain_community.vectorstores import FAISS
from load_documents import load_articles
from myembeddings import embeddings  # your embeddings object

# ─── Load all articles safely
documents = load_articles(limit=90)  # None = load all
print(f"Loaded {len(documents)} articles. Creating FAISS index...")

# ─── Create FAISS vector store
vectorstore = FAISS.from_documents(documents, embeddings)

# ─── Save locally so you don't recreate every time
vectorstore.save_local("./faiss_npr_test")
print("Small FAISS index created and saved at './faiss_npr_test'")

# ─── Optional: test a similarity search
query = "Climate change impacts in Nepal"
results = vectorstore.similarity_search(query, k=3)

print(f"\nTop {len(results)} results for query: '{query}'\n")
for i, res in enumerate(results, 1):
    print(f"{i}. {res.metadata['title']}")
    print(f"Link: {res.metadata['source']}")
    print(f"Preview: {res.page_content[:200].replace(chr(10),' ')}...\n")
