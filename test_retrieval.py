# part_5_test_retrieval.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore = FAISS.load_local("./faiss_npr_test", embeddings, allow_dangerous_deserialization=True)

query = "news about climate change or environment"
results = vectorstore.similarity_search(query, k=3)

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}")
    print("Title:", doc.metadata["title"][:80], "...")
    print("Score hint: relevant content below ↓")
    print(doc.page_content[:400], "...\n")