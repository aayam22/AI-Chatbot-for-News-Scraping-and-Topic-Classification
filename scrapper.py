import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langdetect import detect
from deep_translator import GoogleTranslator
# ---------------- SETTINGS ----------------
DB_FILE = "global_news.db"
translator = GoogleTranslator(source='auto', target='en')

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})


MAX_WORKERS = 20
TRANS_WORKERS = 5  # threads for parallel translation

# ---------------- SOURCES ----------------
BBC_RSS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]

NPR_SECTIONS = [
    "https://www.npr.org/sections/news/",
    "https://www.npr.org/sections/world/",
]

INDIA_RSS = [
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://feeds.feedburner.com/ndtvnews-india-news",
]

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

def get_existing_links(cursor):
    cursor.execute("SELECT link FROM articles")
    return set(x[0] for x in cursor.fetchall())

# ---------------- UTILITIES ----------------
def safe_request(url, retries=3):
    for _ in range(retries):
        try:
            r = session.get(url, timeout=10)
            if r.status_code == 200:
                return r
        except:
            time.sleep(1)
    return None

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


# ---------------- BBC ----------------
def scrape_bbc(existing_links, max_articles=100):
    articles = []
    all_items = []
    for rss in BBC_RSS:
        r = safe_request(rss)
        if not r:
            continue
        soup = BeautifulSoup(r.content, "xml")
        all_items.extend(soup.find_all("item"))
    all_items = all_items[:max_articles]
    with tqdm(total=len(all_items), desc="BBC") as pbar:
        for item in all_items:
            link = item.link.text
            if link in existing_links:
                pbar.update(1)
                continue
            title = item.title.text
            teaser = item.description.text if item.description else ""
            r = safe_request(link)
            if not r:
                pbar.update(1)
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            paragraphs = soup.select("article p")
            full_text = clean_text(" ".join(p.get_text() for p in paragraphs))
            img_tag = soup.find("meta", property="og:image")
            image_url = img_tag["content"] if img_tag else None
            articles.append(
                ("BBC", "General", title, link, teaser, image_url, full_text[:4000])
            )
            pbar.update(1)
    return articles

# ---------------- NPR ----------------
def scrape_npr(existing_links, max_articles=100):
    articles = []
    links = []

    # Collect links and titles from NPR sections
    for section in NPR_SECTIONS:
        r = safe_request(section)
        if not r:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if "/2026/" in href and len(a.get_text(strip=True)) > 20:
                full_link = urljoin("https://www.npr.org", href)
                links.append((full_link, a.get_text(strip=True)))

    links = links[:max_articles]

    with tqdm(total=len(links), desc="NPR") as pbar:
        for link, title in links:

            if link in existing_links:
                pbar.update(1)
                continue

            r = safe_request(link)
            if not r:
                pbar.update(1)
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            # Extract article text
            paragraphs = (
                soup.select("article p") or
                soup.select("div.storytext p") or
                soup.select("div.body-text p") or
                soup.select("div#storytext p")
            )

            full_text = clean_text(
                " ".join(p.get_text() for p in paragraphs)
            ) if paragraphs else ""

            teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""

            # ❌ Image removed completely
            image_url = None

            articles.append(
                ("NPR", "General", title, link, teaser, image_url, full_text[:4000])
            )

            pbar.update(1)

    return articles


# ---------------- INDIA ----------------
def scrape_india(existing_links, max_articles=100):
    articles = []
    all_items = []

    # Collect RSS items
    for rss in INDIA_RSS:
        r = safe_request(rss)
        if not r:
            continue
        soup = BeautifulSoup(r.content, "xml")
        all_items.extend(soup.find_all("item"))

    all_items = all_items[:max_articles]

    with tqdm(total=len(all_items), desc="India") as pbar:
        for item in all_items:
            link = item.link.text
            if link in existing_links:
                pbar.update(1)
                continue

            # Title
            title = item.title.text if item.title else ""

            # Clean teaser from HTML tags, remove images etc.
            if item.description:
                teaser_soup = BeautifulSoup(item.description.text, "html.parser")
                teaser = clean_text(teaser_soup.get_text())
            else:
                teaser = ""

            # Full article
            r = safe_request(link)
            if not r:
                pbar.update(1)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            paragraphs = soup.select("p")
            full_text = clean_text(" ".join(p.get_text() for p in paragraphs))

            # Image
            img_tag = soup.find("meta", property="og:image")
            image_url = img_tag["content"] if img_tag else None

            articles.append(
                ("Indian News", "India", title, link, teaser, image_url, full_text[:2000])
            )

            pbar.update(1)

    return articles

# ---------------- AL JAZEERA ----------------
def scrape_aljazeera(existing_links, max_articles=120):
    BASE = "https://www.aljazeera.com"
    def collect_links(limit=120):
        visited = set()
        article_links = set()
        queue = [
            f"{BASE}/news/",
            f"{BASE}/economy/",
            f"{BASE}/sports/",
            f"{BASE}/politics/",
            f"{BASE}/middle-east/"
        ]
        with tqdm(total=limit, desc="Al Jazeera Links") as pbar:
            while queue and len(article_links) < limit:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                r = safe_request(url)
                if not r:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("/"):
                        link = BASE + link
                    if "/20" in link and "aljazeera.com" in link:
                        if link not in article_links:
                            article_links.add(link)
                            pbar.update(1)
                    if BASE in link and link not in visited:
                        if any(x in link for x in ["news","economy","sports","politics","middle-east"]):
                            queue.append(link)
                    if len(article_links) >= limit:
                        break
                time.sleep(0.5)
        return list(article_links)

    links = collect_links(max_articles)
    articles = []
    with tqdm(total=len(links), desc="Al Jazeera Articles") as pbar:
        for link in links:
            if link in existing_links:
                pbar.update(1)
                continue
            r = safe_request(link)
            if not r:
                pbar.update(1)
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.find("h1")
            if not title_tag:
                pbar.update(1)
                continue
            title = title_tag.get_text(strip=True)
            paragraphs = soup.select("div.wysiwyg p")
            full_text = clean_text(" ".join(p.get_text() for p in paragraphs))
            teaser = paragraphs[0].get_text(strip=True) if paragraphs else ""
            img_tag = soup.find("meta", property="og:image")
            image_url = img_tag["content"] if img_tag else None
            articles.append(
                ("Al Jazeera", "International", title, link, teaser, image_url, full_text[:4000])
            )
            pbar.update(1)
    return articles

# eKantipur (all-in-one)
# ---------------- eKantipur (Chunk 2000 → Full 4000) ----------------
def scrape_ekantipur(existing_links, max_articles=150):
    r = safe_request("https://ekantipur.com/")
    if not r: return []
    
    soup = BeautifulSoup(r.text, "lxml")
    links = set()
    for a in soup.select('a[href*="/20"]'):
        href = a.get("href")
        if href:
            if not href.startswith("http"):
                href = urljoin("https://ekantipur.com/", href)
            links.add(href)
    links = list(links)[:max_articles]

    articles = []
    def process_link(link):
        if link in existing_links: return None
        r = safe_request(link)
        if not r: return None
        
        s = BeautifulSoup(r.text, "lxml")
        
        # title
        og = s.find("meta", property="og:title")
        title = (og["content"].strip() if og and og.get("content") 
                else s.find("h1").get_text(strip=True) if s.find("h1") else None)
        if not title: return None
        
        # text
        ps = s.select("div.description p, div.story p, article p") or s.select("p")
        if not ps: return None
        full = clean_text(" ".join(p.get_text() for p in ps))
        teaser = ps[0].get_text(strip=True) if ps else ""
        
        # image
        img = s.find("meta", property="og:image")
        img_url = img["content"] if img else None

        # Chunk into 2000 but keep up to 4000 final
        try:
            t_title = translator.translate(title) if title else ""
            t_teaser = translator.translate(teaser) if teaser else ""
            
            # Split into 2000 char chunks
            chunks = [full[i:i+2000] for i in range(0, min(len(full), 4000), 2000)]
            t_chunks = []
            for chunk in chunks:
                if chunk.strip():
                    t_chunks.append(translator.translate(chunk))
                    time.sleep(0.8)          # safe delay
            t_full = " ".join(t_chunks)
            
            return ("eKantipur", "Nepal", t_title, link, t_teaser, img_url, t_full)
        except:
            return ("eKantipur", "Nepal", title, link, teaser, img_url, full[:4000])

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(process_link, lnk) for lnk in links]
        for f in tqdm(as_completed(futures), total=len(futures), desc="eKantipur"):
            res = f.result()
            if res: articles.append(res)
    return articles

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
    existing_links = get_existing_links(cursor)

    all_articles = []

    print("Scraping BBC...")
    all_articles += scrape_bbc(existing_links)

    print("Scraping NPR...")
    all_articles += scrape_npr(existing_links)

    print("Scraping Al Jazeera...")
    all_articles += scrape_aljazeera(existing_links)

    print("Scraping India News...")
    all_articles += scrape_india(existing_links)

    print("Scraping eKantipur...")     
    all_articles += scrape_ekantipur(existing_links)

    print(f"\nSaving {len(all_articles)} articles to database...")
    save_articles(cursor, all_articles)

    conn.commit()
    conn.close()
    print("✅ Done. Global news database updated.")

if __name__ == "__main__":
    main()
