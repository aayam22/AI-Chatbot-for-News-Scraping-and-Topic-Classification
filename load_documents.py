# part_2_load_documents.py (RAG-ready loader)
import sqlite3
from langchain_core.documents import Document

DB_PATH = "global_news.db"

def load_articles(limit=None, category=None, ignore_loaded=True):
    """
    Load articles from the DB for RAG.
    
    ignore_loaded=True -> load all articles regardless of 'loaded' flag
    category=None -> load all categories
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure `loaded` column exists
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN loaded INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # column exists

    # Base query
    sql = """
        SELECT id, title, teaser, full_text, scraped_at, predicted_category
        FROM articles
        WHERE full_text IS NOT NULL
    """
    params = []

    # Filter loaded if needed
    if not ignore_loaded:
        sql += " AND (loaded IS NULL OR loaded = 0)"

    # Filter by category if specified
    if category:
        sql += " AND predicted_category = ?"
        params.append(category)

    # Order + limit
    sql += " ORDER BY id DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    # Build Document objects
    docs = []
    for article_id, title, teaser, full_text, scraped_at, predicted_category in rows:
        content = (
            f"Title: {title or ''}\n"
            f"Category: {predicted_category or 'General'}\n"
            f"Date: {scraped_at or '—'}\n\n"
            f"{full_text or ''}"
        )
        metadata = {
            "title": title or "",
            "teaser": teaser[:180] if teaser else "",
            "category": predicted_category or "General",
            "date": scraped_at or "unknown",
        }
        docs.append(Document(page_content=content, metadata=metadata))

    conn.close()
    return docs


# ---------------- Test
if __name__ == "__main__":
    docs = load_articles(limit=None, ignore_loaded=True)
    print(f"Total articles loaded: {len(docs)}")
    for i, doc in enumerate(docs[:5], 1):
        print(f"\n--- Document {i} ---")
        print("Title   :", doc.metadata["title"])
        print("Category:", doc.metadata["category"])
        print("Date    :", doc.metadata["date"])
        print("Preview :", doc.page_content[:200].replace('\n', ' ') + "...")