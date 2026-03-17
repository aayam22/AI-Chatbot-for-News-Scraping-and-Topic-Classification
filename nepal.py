import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from urllib.parse import urljoin
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from googletrans import Translator

# ---------------- SETTINGS ----------------
DB_FILE = "nepali_news_no_api.db"
BASE_URL = "https://ekantipur.com/"
MAX_WORKERS = 10       # threads for scraping
TRANS_WORKERS = 5      # threads for translation

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
translator = Translator()

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            category TEXT,
            title TEXT,
            link TEXT UNIQUE,
            teaser TEXT,
            image_url TEXT,
            full_text TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn, cursor

# ---------------- UTIL ----------------
def safe_request(url):
    try:
        r = session.get(url, timeout=10)
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print(f"⚠️ Request failed: {url} | {e}")
        return None

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

# ---------------- TITLE ----------------
def extract_title(soup):
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return None

# ---------------- SCRAPE SINGLE ARTICLE ----------------
def scrape_article(link, existing_links):
    if link in existing_links:
        return None
    r = safe_request(link)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    title = extract_title(soup)
    if not title:
        return None
    paragraphs = soup.select("div.description p, div.story p, article p")
    if not paragraphs:
        paragraphs = soup.select("p")
    full_text = clean_text(" ".join(p.get_text() for p in paragraphs))
    if not full_text:
        return None
    teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""
    img_tag = soup.find("meta", property="og:image")
    image_url = img_tag["content"] if img_tag else None
    return {
        "title": title,
        "link": link,
        "teaser": teaser,
        "image_url": image_url,
        "full_text": full_text
    }

# ---------------- TRANSLATE ARTICLE ----------------
def translate_article(article, retries=3):
    try:
        for _ in range(retries):
            try:
                title_trans = translator.translate(article["title"], dest="en").text
                full_text_trans = translator.translate(article["full_text"], dest="en").text
                return (
                    "eKantipur",
                    "Nepal",
                    title_trans,
                    article["link"],
                    article["teaser"],
                    article["image_url"],
                    full_text_trans
                )
            except Exception:
                continue
    except:
        pass
    return None

# ---------------- MAIN SCRAPER ----------------
def scrape_ekantipur(existing_links, max_articles=150):
    r = safe_request(BASE_URL)
    if not r:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.select('a[href*="/20"]'):
        href = a.get("href")
        if href:
            if not href.startswith("http"):
                href = urljoin(BASE_URL, href)
            links.add(href)

    links = list(links)[:max_articles]

    articles_raw = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(scrape_article, link, existing_links) for link in links]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Scraping"):
            res = f.result()
            if res:
                articles_raw.append(res)

    # ---------------- TRANSLATE ----------------
    final_articles = []
    with ThreadPoolExecutor(max_workers=TRANS_WORKERS) as executor:
        futures = [executor.submit(translate_article, art) for art in articles_raw]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Translating"):
            res = f.result()
            if res:
                final_articles.append(res)

    return final_articles

# ---------------- SAVE ----------------
def save_articles(cursor, articles):
    cursor.executemany("""
        INSERT OR IGNORE INTO articles
        (source, category, title, link, teaser, image_url, full_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, articles)

# ---------------- MAIN ----------------
def main():
    conn, cursor = init_db()
    cursor.execute("SELECT link FROM articles")
    existing_links = set(x[0] for x in cursor.fetchall())

    print("⚡ Fast scraping + translation (no API required)...")
    articles = scrape_ekantipur(existing_links)

    print(f"\nSaving {len(articles)} articles...")
    save_articles(cursor, articles)

    conn.commit()
    conn.close()
    print("✅ Done (ALL ARTICLES TRANSLATED).")

if __name__ == "__main__":
    main()