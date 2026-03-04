import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from tqdm import tqdm
from urllib.parse import urljoin

# ---------------- CONFIG ----------------
RSS_URLS = [
    "https://feeds.bbci.co.uk/news/rss.xml",             # Top Stories
    "https://feeds.bbci.co.uk/news/world/rss.xml",       # World
    "https://feeds.bbci.co.uk/news/technology/rss.xml"  # Technology
]
BASE_URL = "https://www.bbc.com"
DB_FILE = "bbc_rss.db"
MAX_ARTICLES_PER_FEED = 50
SLEEP_SEC = 0.2

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            teaser TEXT,
            image_url TEXT,
            full_text TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("[Checkpoint] Database initialized")
    return conn, cursor

# ---------------- FETCH LINKS FROM RSS ----------------
def fetch_links_from_rss(rss_url):
    print(f"[Checkpoint] Fetching RSS feed: {rss_url}")
    try:
        resp = requests.get(rss_url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")
        links = [item.link.text for item in items]
        print(f"[Checkpoint] Found {len(links)} links in feed")
        return links
    except Exception as e:
        print(f"[Error] Failed to fetch RSS feed {rss_url}: {e}")
        return []

# ---------------- FETCH ARTICLE CONTENT ----------------
def fetch_article_content(link):
    try:
        resp = requests.get(link, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Title
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else "[No title]"

        # Teaser / Description
        teaser_tag = soup.find("meta", property="og:description")
        teaser = teaser_tag["content"] if teaser_tag else ""

        # Image
        img_tag = soup.find("meta", property="og:image")
        image_url = img_tag["content"] if img_tag else ""

        # Full text
        text_parts = []
        article = soup.find("article")
        if article:
            for p in article.find_all("p"):
                txt = p.get_text(strip=True)
                if len(txt) > 40:
                    text_parts.append(txt)

        # Fallback: all <p>
        if not text_parts:
            for p in soup.find_all("p"):
                txt = p.get_text(strip=True)
                if 40 < len(txt) < 900:
                    text_parts.append(txt)

        full_text = " ".join(text_parts)
        return title, teaser, image_url, full_text

    except Exception as e:
        print(f"[Error] Failed to fetch article {link}: {e}")
        return "[Error]", "", "", ""

# ---------------- MAIN SCRAPER ----------------
def main():
    conn, cursor = init_db()
    total_new = 0
    total_skipped = 0

    for rss_url in RSS_URLS:
        links = fetch_links_from_rss(rss_url)
        links = links[:MAX_ARTICLES_PER_FEED]

        for link in tqdm(links, desc=f"Scraping articles from {rss_url}"):
            # Skip already scraped
            cursor.execute("SELECT 1 FROM articles WHERE link=?", (link,))
            if cursor.fetchone():
                total_skipped += 1
                continue

            title, teaser, image_url, full_text = fetch_article_content(link)

            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?)
            """, (title, link, teaser, image_url, full_text))

            if cursor.rowcount > 0:
                total_new += 1

            # Polite jittered sleep
            time.sleep(max(0, SLEEP_SEC + random.uniform(-0.1, 0.2)))

    conn.commit()
    conn.close()
    print(f"\n[Summary] Added {total_new} new articles. Skipped {total_skipped} already existing.")

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
