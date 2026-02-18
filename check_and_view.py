"""
Check DB & View Articles
Combines checkdb.py + view.py
"""

import sqlite3
from datetime import datetime

DB_FILE = "npr_news.db"

# --- Step 1: Check Database ---
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    
    print(f"Database connected successfully!")
    print(f"Number of rows in 'articles' table: {count}")
    
    # Column names
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns:", ", ".join(columns))
    
except Exception as e:
    print("Error:", e)
    exit(1)

# --- Step 2: View first N articles ---
def print_articles(limit=12, order_by="DESC"):
    try:
        has_scraped_at = 'scraped_at' in columns
        print(f"\nShowing up to {limit} of {count} articles (newest first)\n")

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
                idx += 1

            print(f"Title    : {title}")
            print(f"Link     : {link}")
            
            if teaser:
                teaser_preview = teaser[:160] + "..." if len(teaser) > 160 else teaser
                print(f"Teaser   : {teaser_preview}")
                
            if img:
                print(f"Image    : {img}")
                
            print(f"Text prev: {preview if preview else '(no text extracted)'}")
            print("─" * 100)

    except Exception as e:
        print(f"Error: {e}")

# Run viewer
print_articles(limit=12)
conn.close()
