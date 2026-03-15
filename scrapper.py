import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from urllib.parse import urljoin
from googletrans import Translator
from tqdm import tqdm

headers = {"User-Agent": "Mozilla/5.0"}
DB_FILE = "global_news.db"

# ---------------- SOURCES ----------------
BBC_RSS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

NPR_SECTIONS = [
    "https://www.npr.org/sections/news/",
    "https://www.npr.org/sections/world/",
]

EKANTIPUR_HOME = "https://ekantipur.com/"

ALJAZEERA_RSS = [
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.aljazeera.com/xml/rss/all.xml?section=news",
    "https://www.aljazeera.com/xml/rss/all.xml?section=world",
]

INDIA_RSS = [
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://feeds.feedburner.com/ndtvnews-india-news"
]

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

# ---------------- TRANSLATION ----------------
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
    all_items = []
    for rss in BBC_RSS:
        r = requests.get(rss, headers=headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        all_items.extend(items)
    all_items = all_items[:max_articles]
    with tqdm(total=len(all_items), desc="BBC", unit="article") as pbar:
        for item in all_items:
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
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("BBC", "General", title, link, teaser, image_url, full_text))
            time.sleep(random.uniform(0.3,0.8))
            pbar.update(1)

# ---------------- NPR ----------------
def scrape_npr(cursor, max_articles=100):
    all_links = []
    for section in NPR_SECTIONS:
        r = requests.get(section, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/2026/" in href and len(a.get_text(strip=True)) > 20:
                full_link = urljoin("https://www.npr.org", href)
                all_links.append((full_link, a.get_text(strip=True)))
    all_links = all_links[:max_articles]
    with tqdm(total=len(all_links), desc="NPR", unit="article") as pbar:
        for link, title in all_links:
            try:
                art_r = requests.get(link, headers=headers, timeout=10)
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
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("NPR", "General", title, link, teaser, image_url, full_text))
            time.sleep(random.uniform(0.3,0.8))
            pbar.update(1)

# ---------------- EKANTIPUR ----------------
def scrape_ekantipur(cursor, max_articles=100):
    r = requests.get(EKANTIPUR_HOME, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.select('a[href*="/2026/"]'):
        href = a.get("href")
        if href:
            if not href.startswith("http"):
                href = urljoin(EKANTIPUR_HOME, href)
            links.add(href)
    links = list(links)[:max_articles]
    with tqdm(total=len(links), desc="eKantipur", unit="article") as pbar:
        for link in links:
            try:
                art_r = requests.get(link, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_r.text, "html.parser")
                paragraphs = art_soup.find_all("p")
                full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""
                title_np = art_soup.find("h1")
                title_np = title_np.get_text(strip=True) if title_np else "Nepal News"
                title_en = translate_text(title_np)
                translated_text = translate_text(full_text)
                img_tag = art_soup.find("meta", property="og:image")
                image_url = img_tag["content"] if img_tag else None
                cursor.execute("""
                    INSERT OR IGNORE INTO articles
                    (source, category, title, link, teaser, image_url, full_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("eKantipur", "Nepal", title_en, link, teaser, image_url, translated_text))
            except:
                pass
            time.sleep(random.uniform(0.3,0.8))
            pbar.update(1)

# ---------------- AL JAZEERA ----------------
def scrape_aljazeera(cursor, max_articles=100):
    all_items = []
    for rss in ALJAZEERA_RSS:
        r = requests.get(rss, headers=headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        all_items.extend(items)
    all_items = all_items[:max_articles]
    with tqdm(total=len(all_items), desc="Al Jazeera", unit="article") as pbar:
        for item in all_items:
            link = item.link.text
            title = item.title.text
            teaser = item.description.text if item.description else ""
            try:
                art_r = requests.get(link, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_r.text, "html.parser")
                paragraphs = art_soup.select("div.wysiwyg p")
                full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                img_tag = art_soup.find("meta", property="og:image")
                image_url = img_tag["content"] if img_tag else None
            except:
                full_text = ""
                image_url = None
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (source, category, title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("Al Jazeera", "International", title, link, teaser, image_url, full_text))
            time.sleep(random.uniform(0.3,0.8))
            pbar.update(1)

# ---------------- INDIA ----------------
def scrape_india(cursor, max_articles=100):
    all_items = []
    for rss in INDIA_RSS:
        r = requests.get(rss, headers=headers)
        soup = BeautifulSoup(r.content, "xml")
        items = soup.find_all("item")
        all_items.extend(items)
    all_items = all_items[:max_articles]
    with tqdm(total=len(all_items), desc="India", unit="article") as pbar:
        for item in all_items:
            link = item.link.text
            title = item.title.text
            teaser = item.description.text if item.description else ""
            try:
                art_r = requests.get(link, headers=headers, timeout=10)
                art_soup = BeautifulSoup(art_r.text, "html.parser")
                paragraphs = art_soup.find_all("p")
                full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
                img_tag = art_soup.find("meta", property="og:image")
                image_url = img_tag["content"] if img_tag else None
            except:
                full_text = ""
                image_url = None
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (source, category, title, link, teaser, image_url, full_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("Indian News", "India", title, link, teaser, image_url, full_text))
            time.sleep(random.uniform(0.3,0.8))
            pbar.update(1)

# ---------------- MAIN ----------------
def main():
    conn, cursor = init_db()
    print("Scraping BBC...")
    scrape_bbc(cursor, 100)
    print("Scraping NPR...")
    scrape_npr(cursor, 100)
    print("Scraping eKantipur...")
    scrape_ekantipur(cursor, 100)
    print("Scraping Al Jazeera...")
    scrape_aljazeera(cursor, 100)
    print("Scraping India...")
    scrape_india(cursor, 100)
    conn.commit()
    conn.close()
    print("Done. Global news database updated.")

if __name__ == "__main__":
    main()