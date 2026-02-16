# part_1_check_db.py
import sqlite3

DB_PATH = "npr_news.db"   # ← change only if your file is somewhere else

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    
    print(f"Database connected successfully!")
    print(f"Number of rows in 'articles' table: {count}")
    
    # Optional: show column names
    cursor.execute("PRAGMA table_info(articles)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns:", ", ".join(columns))
    
    conn.close()
except Exception as e:
    print("Error:", e)