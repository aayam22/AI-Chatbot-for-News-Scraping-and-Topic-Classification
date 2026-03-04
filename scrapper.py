import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from urllib.parse import urljoin
from googletrans import Translator
from tqdm import tqdm  # progress bar

headers = {"User-Agent": "Mozilla/5.0"}
DB_FILE = "global_news.db"

BBC_RSS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

NPR_SECTIONS = [
    "https://www.npr.org/sections/news/",
    "https://www.npr.org/sections/world/",
]

EKANTIPUR_HOME = "https://ekantipur.com/"

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

# ---------------- Helper ----------------
def translate_text(text, dest='en', chunk_size=500):
    translated = []
    for i in range(0, len(text), chunk_size):
        part = text[i:i+chunk_size]
        try:
            translated.append(translator.translate(part, dest=dest).text)
        except:
            translated.append(part)
    return " ".join(translated)

# ---------------- BBC ----------------
def scrape_bbc(cursor, max_articles=100):
    for rss in BBC_RSS:
        r = requests.get(rss, headers=headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")[:max_articles]

        for item in tqdm(items, desc="BBC articles", unit="article"):
            link = item.link.text
            title = item.title.text
            teaser = item.description.text if item.description else ""

            try:
                art_r = requests.get(link, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_r.text, "html.parser")
                paragraphs = art_soup.select("article p")
                full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                img_tag = art_soup.find("meta", property="og:image")
                image_url = img_tag["content"] if img_tag else None
            except:
                full_text = ""
                image_url = None

            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (source, category, title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("BBC", "General", title, link, teaser, image_url, full_text)
            )
            time.sleep(random.uniform(0.3, 0.8))

# ---------------- NPR ----------------
def scrape_npr(cursor, max_articles=100):
    for section in NPR_SECTIONS:
        r = requests.get(section, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/2026/" in href and len(a.get_text(strip=True)) > 20:
                links.append((href, a.get_text(strip=True)))

        for href, title in tqdm(links[:max_articles], desc="NPR articles", unit="article"):
            full_link = urljoin("https://www.npr.org", href)
            try:
                art_r = requests.get(full_link, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_r.text, "html.parser")
                paragraphs = art_soup.select("div[itemprop='articleBody'] p")
                full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""
                img_tag = art_soup.find("meta", property="og:image")
                image_url = img_tag["content"] if img_tag else None
            except:
                full_text = ""
                teaser = ""
                image_url = None

            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (source, category, title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("NPR", "General", title, full_link, teaser, image_url, full_text)
            )
            time.sleep(random.uniform(0.3, 0.8))

# ---------------- eKantipur ----------------
def scrape_ekantipur(cursor, max_articles=100):
    r = requests.get(EKANTIPUR_HOME, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.select('a[href*="/2026/"]'):
        href = a.get("href")
        if href and not href.startswith("http"):
            href = urljoin(EKANTIPUR_HOME, href)
        links.add(href)

    for link in tqdm(list(links)[:max_articles], desc="eKantipur articles", unit="article"):
        try:
            art_r = requests.get(link, headers=headers, timeout=10)
            art_soup = BeautifulSoup(art_r.text, "html.parser")

            # Extract paragraphs using multiple selectors
            paragraphs = (
                art_soup.select("div.detail p") or
                art_soup.select("article p") or
                art_soup.select(".article-detail p") or
                art_soup.select("div.news-content p") or
                art_soup.select("div#article-body p") or
                art_soup.find_all("p")
            )
            full_text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""

            # Extract title from h1 or URL
            title_np = art_soup.find("h1")
            title_np = title_np.get_text(strip=True) if title_np else link.split("/")[-1].replace("-", " ")
            title_en = translate_text(title_np)

            # Translate full text
            translated_text = translate_text(full_text) if full_text else ""

            # Extract image
            img_tag = art_soup.find("meta", property="og:image")
            image_url = img_tag["content"] if img_tag else None

            cursor.execute("""
                INSERT OR IGNORE INTO articles 
                (source, category, title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("eKantipur", "Nepal", title_en, link, teaser, image_url, translated_text)
            )
            time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            print(f"Failed to scrape {link}: {e}")

# ---------------- MAIN ----------------
def main():
    conn, cursor = init_db()
    print("Scraping BBC...")
    scrape_bbc(cursor, max_articles=100)
    print("Scraping NPR...")
    scrape_npr(cursor, max_articles=100)
    print("Scraping eKantipur...")
    scrape_ekantipur(cursor, max_articles=100)
    conn.commit()
    conn.close()
    print("Done. Unified news database updated with latest articles.")

if __name__ == "__main__":
    main()