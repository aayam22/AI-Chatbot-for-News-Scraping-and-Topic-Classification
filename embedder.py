"""
Incremental Text + Image Metadata Embedding for FAISS
"""

import os
import sqlite3
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DB_PATH = "global_news.db"
FAISS_PATH = "./faiss_npr_test"


# -------------------------------
# LOAD ARTICLES FROM DATABASE
# -------------------------------
def load_articles(limit=None, category=None, ignore_loaded=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure 'loaded' column exists for tracking
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN loaded INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass

    # Fetch articles
    sql = """
        SELECT id, title, teaser, full_text, scraped_at, predicted_category, image_url
        FROM articles
        WHERE full_text IS NOT NULL
    """
    params = []

    if ignore_loaded:
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
    for article_id, title, teaser, full_text, scraped_at, predicted_category, image_url in rows:
        content = (
            f"Title: {title or ''}\n"
            f"Category: {predicted_category or 'General'}\n"
            f"Date: {scraped_at or '—'}\n\n"
            f"{full_text or ''}"
        )

        metadata = {
            "id": article_id,
            "title": title or "",
            "teaser": teaser[:180] if teaser else "",
            "category": predicted_category or "General",
            "date": scraped_at or "unknown",
            "image_url": image_url or ""  # ✅ include image URL in metadata
        }

        docs.append(Document(page_content=content, metadata=metadata))

    conn.close()
    return docs


# -------------------------------
# MARK ARTICLES AS LOADED
# -------------------------------
def mark_as_loaded(ids):
    if not ids:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        "UPDATE articles SET loaded = 1 WHERE id = ?",
        [(i,) for i in ids]
    )
    conn.commit()
    conn.close()


# -------------------------------
# MAIN EMBEDDING PIPELINE
# -------------------------------
def main():
    print("🚀 Starting embedding pipeline...")

    # 1️⃣ Initialize text embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )
    print("✅ Embedding model ready")

    # 2️⃣ Load new articles
    documents = load_articles(ignore_loaded=True)
    if not documents:
        print("⚠️ No new articles to embed")
        return

    print(f"📄 {len(documents)} new articles loaded")

    # 3️⃣ Load or create FAISS index
    if os.path.exists(FAISS_PATH):
        print("📦 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(
            FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(documents)
        print(f"➕ Added {len(documents)} new articles to FAISS")
    else:
        print("🆕 Creating new FAISS index...")
        vectorstore = FAISS.from_documents(documents, embeddings)
        print(f"✅ Created new FAISS index with {len(documents)} articles")

    # 4️⃣ Save FAISS index
    vectorstore.save_local(FAISS_PATH)
    print("💾 FAISS index saved")

    # 5️⃣ Mark articles as embedded
    ids = [doc.metadata["id"] for doc in documents]
    mark_as_loaded(ids)
    print(f"✅ Marked {len(ids)} articles as embedded")


# -------------------------------
# RUN PIPELINE
# -------------------------------
if __name__ == "__main__":
    main()