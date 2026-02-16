import requests
from bs4 import BeautifulSoup
import sqlite3
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

BASE_URL = "https://www.npr.org"

# ---------------- DATABASE ----------------
conn = sqlite3.connect('npr_news.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        link TEXT UNIQUE,
        teaser TEXT,
        image_url TEXT,
        full_text TEXT
    )
''')

# ---------------- GET HOMEPAGE ----------------
response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# NPR article links usually contain "/202"
article_links = []

for a in soup.find_all('a', href=True):
    href = a['href']
    if "/202" in href and "npr.org" in href:
        article_links.append(href)

# remove duplicates
article_links = list(set(article_links))

print(f"Found {len(article_links)} candidate articles")

count = 0

# ---------------- SCRAPE EACH ARTICLE ----------------
for link in article_links[:15]:  # limit for safety
    cursor.execute("SELECT 1 FROM articles WHERE link = ?", (link,))
    if cursor.fetchone():
        continue

    try:
        art_resp = requests.get(link, headers=headers)
        art_soup = BeautifulSoup(art_resp.text, 'html.parser')

        # title
        title_tag = art_soup.find('meta', property='og:title')
        title = title_tag['content'] if title_tag else ''

        # image
        img_tag = art_soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else ''

        # teaser
        teaser_tag = art_soup.find('meta', property='og:description')
        teaser = teaser_tag['content'] if teaser_tag else ''

        # full text
        story = art_soup.find('div', id='storytext')
        full_text = ''
        if story:
            full_text = ' '.join(p.get_text(strip=True) for p in story.find_all('p'))

        cursor.execute('''
            INSERT INTO articles (title, link, teaser, image_url, full_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, link, teaser, image_url, full_text))

        count += 1
        time.sleep(2)

    except Exception as e:
        print(f"Error {link}: {e}")

conn.commit()
conn.close()

print(f"Stored {count} new articles from website")
