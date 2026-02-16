# part_2_load_documents.py
import sqlite3
from langchain_core.documents import Document

DB_PATH = "npr_news.db"

def load_articles(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, link, teaser, full_text, scraped_at
        FROM articles 
        WHERE full_text IS NOT NULL 
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    docs = []
    for title, link, teaser, full_text, scraped_at in rows:
        content = f"Title: {title}\nLink: {link}\nDate: {scraped_at or '—'}\n\n{full_text}"
        metadata = {
            "title": title,
            "source": link,
            "date": scraped_at or "unknown",
            "teaser": teaser[:180] if teaser else ""
        }
        docs.append(Document(page_content=content, metadata=metadata))
    
    return docs

# ─── Test it ───
documents = load_articles(limit=5)   # just first 5 for testing

print(f"Loaded {len(documents)} documents\n")

for i, doc in enumerate(documents, 1):
    print(f"--- Document {i} ---")
    print("Title:", doc.metadata["title"][:70], "...")
    print("Date :", doc.metadata["date"])
    print("Text preview:", doc.page_content[:220].replace("\n", " ") + "...")
    print()