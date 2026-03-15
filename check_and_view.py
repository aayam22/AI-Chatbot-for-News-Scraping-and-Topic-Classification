"""
Check DB & View Articles
Improved viewer for global_news.db with cleaned titles and text previews
"""

import sqlite3
from datetime import datetime

DB_FILE = "india_news.db"  # Change to "global_news.db" if needed

# --- Step 1: Connect to Database ---
try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    
    print(f"Database connected successfully!")
    print(f"Number of rows in 'articles' table: {count}")
    
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns:", ", ".join(columns))
    
except Exception as e:
    print("Error:", e)
    exit(1)

# --- Step 2: Clean article title ---
def clean_title(title):
    # Remove .html
    title = title.replace(".html", "")
    # Replace hyphens/underscores with spaces
    title = title.replace("-", " ").replace("_", " ")
    # Skip numeric titles
    if title.isnumeric() or len(title.strip()) < 3:
        title = "(eKantipur News)"
    return title.strip()

# --- Step 3: Print articles ---
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
            "full_text"
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
            raw_title = row[idx]; idx += 1
            link = row[idx]; idx += 1
            teaser = row[idx]; idx += 1
            img = row[idx]; idx += 1
            full_text = row[idx]; idx += 1

            if has_scraped_at:
                scraped = row[idx]; idx += 1

            # Clean title for display
            title = clean_title(raw_title)

            print(f"ID       : {id_}")
            if has_scraped_at:
                if scraped:
                    try:
                        dt = datetime.strptime(scraped, "%Y-%m-%d %H:%M:%S")
                        print(f"Date     : {dt.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        print(f"Date     : {scraped[:16]}")
                else:
                    print("Date     : —")

            print(f"Title    : {title}")
            print(f"Link     : {link}")

            # Teaser or fallback to first 200 chars of full_text
            if teaser:
                teaser_preview = teaser[:160] + "..." if len(teaser) > 160 else teaser
                print(f"Teaser   : {teaser_preview}")
            elif full_text:
                teaser_preview = full_text[:160] + "..." if len(full_text) > 160 else full_text
                print(f"Teaser   : {teaser_preview}")

            if img:
                print(f"Image    : {img}")

            # Full text preview
            preview = full_text[:450] + "..." if full_text and len(full_text) > 450 else full_text
            print(f"Text prev: {preview if preview else '(no text extracted)'}")
            print("─" * 100)

    except Exception as e:
        print(f"Error: {e}")

# --- Step 4: Run viewer ---
print_articles(limit=12)
conn.close()