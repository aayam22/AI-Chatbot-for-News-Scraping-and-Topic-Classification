"""
Create embeddings & FAISS index
Combines myembeddings.py + smallfiastest.py
"""

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from load_documents import load_articles

# --- Step 1: Create embeddings ---
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# Test embedding
text = "NPR reports on climate change impacts in Nepal."
vector = embeddings.embed_query(text)
print("Embedding vector length:", len(vector))
print("First 8 values:", vector[:8])

# --- Step 2: Load articles ---
documents = load_articles(limit=90)
print(f"\nLoaded {len(documents)} articles. Creating FAISS index...")

# --- Step 3: Create FAISS index ---
vectorstore = FAISS.from_documents(documents, embeddings)
vectorstore.save_local("./faiss_npr_test")
print("FAISS index created and saved at './faiss_npr_test'")

# --- Step 4: Optional similarity test ---
query = "Climate change impacts in Nepal"
results = vectorstore.similarity_search(query, k=3)
print(f"\nTop {len(results)} results for query: '{query}'\n")
for i, res in enumerate(results, 1):
    print(f"{i}. {res.metadata['title']}")
    print(f"Link: {res.metadata['source']}")
    print(f"Preview: {res.page_content[:200].replace(chr(10),' ')}...\n")
