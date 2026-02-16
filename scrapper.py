import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
import random
from urllib.parse import urljoin
from tqdm import tqdm  # pip install tqdm

# --- Config ---
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

BASE_URL = "https://www.npr.org"
DB_FILE = "npr_news.db"

SECTIONS = [
    "/sections/news/",
    "/sections/world/",
    "/sections/climate/",
    "/sections/environment/",
    "/sections/politics/",
    "/sections/national/",
    # Add more sections here if desired
]

# --- Database setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            teaser TEXT,
            image_url TEXT,
            full_text TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, cursor

# --- Extract article links ---
def get_article_links_from_page(url):
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if re.search(r'/\d{4}/\d{2}/\d{2}/[a-z0-9-]+', href):
                full_url = urljoin(BASE_URL, href)
                if 'npr.org' in full_url and '/player/' not in full_url and not full_url.endswith('/'):
                    links.add(full_url)
        return links
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return set()

def collect_article_links(max_pages_per_section=5):
    all_links = set()
    for section in SECTIONS:
        print(f"→ Crawling section: {section}")
        current_url = urljoin(BASE_URL, section)
        page_count = 0

        while current_url and page_count < max_pages_per_section:
            page_links = get_article_links_from_page(current_url)
            new_count = len(page_links - all_links)
            all_links.update(page_links)
            print(f"  Page {page_count+1}: found {len(page_links)} links ({new_count} new)")

            # Find next page link
            try:
                soup = BeautifulSoup(requests.get(current_url, headers=headers, timeout=5).text, 'html.parser')
                next_link = soup.find('a', text=re.compile(r'(Older|More|Next|Load More|→)', re.I))
                if next_link:
                    current_url = urljoin(BASE_URL, next_link['href'])
                else:
                    page_count += 1
                    next_page_num = page_count + 1
                    current_url = f"{current_url.rstrip('/')}?page={next_page_num}"
                    if requests.get(current_url, headers=headers, timeout=5).status_code != 200:
                        current_url = None
            except:
                current_url = None

            page_count += 1
            # Polite delay between pages
            time.sleep(max(0, 0.3 + random.uniform(0, 0.2)))

    return sorted(list(all_links))

# --- Extract full article text ---
def extract_article_text(soup):
    full_text_parts = []

    containers = [
        soup.find('div', class_='storytext'),
        soup.find('div', class_='body-container'),
        soup.find('article'),
        soup.find('div', {'id': re.compile(r'(main|content|story|article-body)')}),
    ]

    for container in filter(None, containers):
        paragraphs = container.find_all(['p', 'li', 'h2', 'h3'], recursive=True)
        for elem in paragraphs:
            text = elem.get_text(strip=True)
            if text and len(text) > 25 and not any(x in text.lower() for x in ['listen ·', 'support npr', 'copyright ©', 'npr thanks our sponsors']):
                full_text_parts.append(text)

    if not full_text_parts:
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if 30 < len(text) < 900 and 'http' not in text and len(text.split()) > 8:
                full_text_parts.append(text)

    return ' '.join(full_text_parts) if full_text_parts else ''

# --- Main scraping ---
def main(max_articles=400, sleep_sec=0.1):
    conn, cursor = init_db()
    
    print("Collecting article links from multiple sections...")
    links = collect_article_links(max_pages_per_section=6)
    print(f"\nTotal unique candidate links found: {len(links)}")

    links = links[:max_articles]
    new_count = 0
    skipped = 0

    for i, link in enumerate(tqdm(links, desc="Scraping articles"), 1):
        cursor.execute("SELECT 1 FROM articles WHERE link = ?", (link,))
        if cursor.fetchone():
            skipped += 1
            continue

        print(f"[{i}/{len(links)}]  {link}")

        for attempt in range(3):
            try:
                resp = requests.get(link, headers=headers, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                title_tag = soup.find('meta', property='og:title')
                title = title_tag['content'] if title_tag else soup.find('h1').get_text(strip=True) if soup.find('h1') else '[No title]'

                teaser_tag = soup.find('meta', property='og:description')
                teaser = teaser_tag['content'] if teaser_tag else ''

                image_tag = soup.find('meta', property='og:image')
                image_url = image_tag['content'] if image_tag else ''

                full_text = extract_article_text(soup)

                cursor.execute('''
                    INSERT OR IGNORE INTO articles
                    (title, link, teaser, image_url, full_text)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, link, teaser, image_url, full_text))

                if cursor.rowcount > 0:
                    new_count += 1
                    print(f"   → Stored: {title[:80]}{'...' if len(title)>80 else ''}")

                break  # success

            except Exception as e:
                print(f"   → Error (attempt {attempt+1}): {type(e).__name__} {e}")
                if attempt < 2:
                    time.sleep(1 + random.random()*2)
                else:
                    print(f"   → Giving up on {link}")

        # Safe jittered sleep
        sleep_time = max(0, sleep_sec + random.uniform(-0.05, 0.15))
        time.sleep(sleep_time)

    conn.commit()
    conn.close()
    print(f"\nDone. Added {new_count} new articles. Skipped {skipped} already existing.")

# --- Run ---
if __name__ == "__main__":
    main(max_articles=400, sleep_sec=0.1)
