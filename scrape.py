import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DOCS_DIR = "docs"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; startup-rag-scraper/1.0)"}


def fetch(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def url_to_filename(url):
    parsed = urlparse(url)
    slug = parsed.netloc + parsed.path
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug).strip("_")
    return slug[:80] + ".txt"


def scrape(url):
    print(f"Scraping: {url}")
    html = fetch(url)
    text = clean_text(html)
    filename = url_to_filename(url)
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n\n{text}")
    print(f"  Saved → {path} ({len(text)} chars)")
    return path


if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)

    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("Usage: python scrape.py <url1> <url2> ...")
        print("\nExample:")
        print("  python scrape.py https://paulgraham.com/startupfunding.html")
        sys.exit(0)

    success, failed = 0, 0
    for url in urls:
        try:
            scrape(url)
            success += 1
        except Exception as e:
            print(f"  Failed: {e}")
            failed += 1

    print(f"\nDone: {success} scraped, {failed} failed")
    print("Run 'python ingest.py' to rebuild the index.")
