"""
Combined Loader + Embedding + FAISS (INCREMENTAL, NO DUPLICATES)
"""

import os
import sqlite3
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DB_PATH = "global_news.db"
FAISS_PATH = "./faiss_npr_test"


# -------------------------------
# LOAD ARTICLES (WITH TRACKING)
# -------------------------------
def load_articles(limit=None, category=None, ignore_loaded=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure loaded column exists
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN loaded INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    sql = """
        SELECT id, title, teaser, full_text, scraped_at, predicted_category
        FROM articles
        WHERE full_text IS NOT NULL
    """
    params = []

    if not ignore_loaded:
        sql += " AND (loaded IS NULL OR loaded = 0)"

    if category:
        sql += " AND predicted_category = ?"
        params.append(category)

    sql += " ORDER BY id DESC"

    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    docs = []
    for article_id, title, teaser, full_text, scraped_at, predicted_category in rows:
        content = (
            f"Title: {title or ''}\n"
            f"Category: {predicted_category or 'General'}\n"
            f"Date: {scraped_at or '—'}\n\n"
            f"{full_text or ''}"
        )

        metadata = {
            "id": article_id,   # ✅ important for tracking
            "title": title or "",
            "teaser": teaser[:180] if teaser else "",
            "category": predicted_category or "General",
            "date": scraped_at or "unknown",
        }

        docs.append(Document(page_content=content, metadata=metadata))

    conn.close()
    return docs


# -------------------------------
# MARK AS LOADED
# -------------------------------
def mark_as_loaded(ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executemany(
        "UPDATE articles SET loaded = 1 WHERE id = ?",
        [(i,) for i in ids]
    )

    conn.commit()
    conn.close()


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():
    print("🚀 Starting embedding pipeline...")

    # 1. Initialize embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )

    print("✅ Embedding model ready")

    # 2. Load ONLY new articles
    documents = load_articles(ignore_loaded=False)

    if not documents:
        print("⚠️ No new articles to embed")
        return

    print(f"📄 {len(documents)} new articles loaded")

    # 3. Load or create FAISS
    if os.path.exists(FAISS_PATH):
        print("📦 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        vectorstore.add_documents(documents)
        print("➕ Added new documents")

    else:
        print("🆕 Creating new FAISS index...")
        vectorstore = FAISS.from_documents(documents, embeddings)

    # 4. Save FAISS
    vectorstore.save_local(FAISS_PATH)
    print("💾 FAISS index saved")

    # 5. Mark articles as loaded
    ids = [doc.metadata["id"] for doc in documents if "id" in doc.metadata]

    if ids:
        mark_as_loaded(ids)
        print("✅ Articles marked as embedded")

    # 6. Test query
    query = "Technology news"
    results = vectorstore.similarity_search(query, k=3)

    print("\n🔍 Test Results:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.metadata['title']}")
        print(f"   Category: {r.metadata['category']}")
        print(f"   Date: {r.metadata['date']}\n")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    main()