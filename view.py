import sqlite3
from datetime import datetime

DB_FILE = r"D:\rag\AI-Chatbot-for-News-Scraping-and-Topic-Classification\npr_news.db"

def print_articles(limit=20, order_by="DESC"):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]

        if total == 0:
            print("No articles found in the database yet.")
            return

        # Check available columns to handle different schema versions
        cursor.execute("PRAGMA table_info(articles)")
        columns = {col[1] for col in cursor.fetchall()}

        has_scraped_at = 'scraped_at' in columns

        print(f"Showing up to {limit} of {total} articles (newest first)\n")

        # Build query dynamically based on available columns
        select_fields = [
            "id",
            "title",
            "link",
            "teaser",
            "image_url",
            "substr(full_text, 1, 450) || '...' AS preview"
        ]
        if has_scraped_at:
            select_fields.append("scraped_at")

        query = f"""
            SELECT {', '.join(select_fields)}
            FROM articles
            ORDER BY id {order_by}
            LIMIT ?
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

        for row in rows:
            idx = 0
            id_ = row[idx]; idx += 1
            title = row[idx]; idx += 1
            link = row[idx]; idx += 1
            teaser = row[idx]; idx += 1
            img = row[idx]; idx += 1
            preview = row[idx]; idx += 1

            print(f"ID       : {id_}")
            
            if has_scraped_at:
                scraped = row[idx]
                if scraped:
                    try:
                        dt = datetime.strptime(scraped, "%Y-%m-%d %H:%M:%S")
                        print(f"Date     : {dt.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        print(f"Date     : {scraped[:16]}")
                else:
                    print("Date     : —")
                idx += 1  # only increment if we consumed the field

            print(f"Title    : {title}")
            print(f"Link     : {link}")
            
            if teaser:
                teaser_preview = teaser[:160] + "..." if len(teaser) > 160 else teaser
                print(f"Teaser   : {teaser_preview}")
                
            if img:
                print(f"Image    : {img}")
                
            print(f"Text prev: {preview if preview else '(no text extracted)'}")
            print("─" * 100)

        conn.close()

    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            print("Table 'articles' does not exist yet. Run the scraper first.")
        else:
            print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print_articles(limit=12)