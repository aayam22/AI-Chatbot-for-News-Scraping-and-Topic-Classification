import sqlite3

conn = sqlite3.connect('npr_news.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM articles")
rows = cursor.fetchall()

for row in rows:
    print("\nID:", row[0])
    print("Title:", row[1])
    print("Link:", row[2])
    print("Teaser:", row[3])
    print("Image URL:", row[4])
    print("Full Text:", row[5][:500], "...")  # preview first 500 chars
    print("=" * 100)

conn.close()
