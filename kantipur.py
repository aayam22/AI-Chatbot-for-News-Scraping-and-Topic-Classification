import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from urllib.parse import urljoin
import time
import random

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE_URL = "https://ekantipur.com/"
translator = Translator()

# Helper: translate in chunks to avoid Google Translate size limit
def translate_text(text, dest='en', chunk_size=500):
    translated = []
    for i in range(0, len(text), chunk_size):
        part = text[i:i+chunk_size]
        try:
            translated_part = translator.translate(part, dest=dest).text
        except:
            translated_part = part  # fallback to original if translation fails
        translated.append(translated_part)
    return " ".join(translated)

# Fetch homepage
r = requests.get(BASE_URL, headers=headers, timeout=12)
soup = BeautifulSoup(r.text, "html.parser")

# Collect article links
links = set()
for a in soup.select('a[href*="/2026/"]'):
    href = a.get("href", "")
    if href and not href.startswith("http"):
        href = urljoin(BASE_URL, href)
    links.add(href)

# Visit each link and extract text
for link in links:
    try:
        art_r = requests.get(link, headers=headers, timeout=10)
        art_soup = BeautifulSoup(art_r.text, "html.parser")

        # Try multiple selectors for full text
        paragraphs = (
            art_soup.select("div.detail p") or
            art_soup.select("article p") or
            art_soup.select(".article-detail p") or
            art_soup.select("div.news-content p") or
            art_soup.select("div#article-body p") or
            art_soup.find_all("p")
        )

        # Extract full text
        full_text = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        # Translate full text to English
        translated_text = translate_text(full_text) if full_text else "(no text extracted)"

        # Get headline
        title_np = art_soup.find("h1")
        title_np = title_np.get_text(strip=True) if title_np else link.split("/")[-1].replace("-", " ")
        title_en = translate_text(title_np)

        # Get image
        img_tag = art_soup.find("meta", property="og:image")
        image_url = img_tag["content"] if img_tag else None

        # Print result
        print(f"Title   : {title_en}")
        print(f"Link    : {link}")
        print(f"Image   : {image_url}")
        print(f"Content : {translated_text[:1000]}..." if translated_text else "Content : (no text extracted)")
        print("-"*80)

        # Avoid overloading server
        time.sleep(random.uniform(0.3, 0.8))

    except Exception as e:
        print(f"Failed to scrape {link}: {e}")