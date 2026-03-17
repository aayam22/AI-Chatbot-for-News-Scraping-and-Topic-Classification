# part_2_load_documents.py
import sqlite3
from langchain_core.documents import Document

DB_PATH = "global_news.db"

def load_articles(limit=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql = """
        SELECT title, link, teaser, full_text, scraped_at
        FROM articles 
        WHERE full_text IS NOT NULL 
        ORDER BY id DESC
    """
    if limit:
        sql += " LIMIT ?"
        cursor.execute(sql, (limit,))
    else:
        cursor.execute(sql)

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
if __name__ == "__main__":
    all_documents = load_articles()  # load all from DB
    print(f"\nTotal articles loaded: {len(all_documents)}\n")

    # print only first 10 for preview
    for i, doc in enumerate(all_documents[:10], 1):
        print(f"--- Document {i} ---")
        print("Title:", doc.metadata["title"][:70], "...")
        print("Date :", doc.metadata["date"])
        print("Text preview:", doc.page_content[:220].replace("\n", " ") + "...")
        print()