import csv
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser


# ================= CONFIG =================
BASE = "https://www.cambridge.org"
START_URL = "https://www.cambridge.org/core/journals/journal-of-global-history/open-access"
OUTPUT_FILE = "cambridge_jgh_open_access_last2years.csv"

YEARS_BACK = 2
REQUEST_DELAY = 1.5  # polite delay
MAX_PAGES = 50  # safety stop

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cambridge.org/"
}

ARTICLE_PATTERN = re.compile(
    r"/core/journals/journal-of-global-history/article/"
)

session = requests.Session()
session.headers.update(HEADERS)


# ================= UTILITIES =================
def get_soup(url):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def find_article_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0].split("#")[0]
        if ARTICLE_PATTERN.search(href):
            full = urljoin(base_url, href)
            links.add(full)
    return links


def extract_title(soup):
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""


def extract_date(soup):
    # First try meta tags
    meta = soup.find("meta", {"name": "citation_online_date"}) \
        or soup.find("meta", {"name": "citation_publication_date"})
    if meta and meta.get("content"):
        try:
            dt = dateparser.parse(meta["content"])
            return dt.date().isoformat()
        except:
            pass

    # Fallback: search visible text
    text = soup.get_text(" ", strip=True)
    match = re.search(r"Published\s+online.*?(\d{1,2}\s+[A-Za-z]+\s+\d{4})", text)
    if match:
        try:
            dt = dateparser.parse(match.group(1))
            return dt.date().isoformat()
        except:
            pass

    return ""


def extract_abstract(soup):
    # Find heading "Abstract"
    for h in soup.find_all(re.compile("^h[1-6]$")):
        if "abstract" in h.get_text(strip=True).lower():
            parts = []
            for sib in h.find_next_siblings():
                if sib.name and re.match("^h[1-6]$", sib.name):
                    break
                text = sib.get_text(" ", strip=True)
                if text:
                    parts.append(text)
            if parts:
                return "\n\n".join(parts)

    # Fallback: look for class containing abstract
    abs_section = soup.find(
        lambda tag: tag.name in ("div", "section")
        and tag.get("class")
        and any("abstract" in c.lower() for c in tag.get("class"))
    )
    if abs_section:
        return abs_section.get_text(" ", strip=True)

    # Last fallback: first long paragraph
    for p in soup.find_all("p"):
        txt = p.get_text(" ", strip=True)
        if len(txt) > 200:
            return txt

    return ""


def is_recent(date_iso):
    if not date_iso:
        return False
    try:
        dt = datetime.fromisoformat(date_iso).date()
    except:
        return False
    cutoff = datetime.utcnow().date() - timedelta(days=365 * YEARS_BACK)
    return dt >= cutoff


# ================= MAIN =================
def main():
    print("Starting Open Access scrape...")
    article_links = set()

    # --- Paginate safely using pageNum ---
    for page in range(MAX_PAGES):
        page_url = f"{START_URL}?pageNum={page}"
        print(f"Visiting listing page {page} -> {page_url}")

        try:
            soup = get_soup(page_url)
        except Exception as e:
            print("Stopping pagination:", e)
            break

        found_links = find_article_links(soup, page_url)

        if not found_links:
            print("No more articles found. Ending pagination.")
            break

        print(f"  Found {len(found_links)} articles on this page")
        article_links.update(found_links)

        time.sleep(REQUEST_DELAY)

    print(f"\nTotal unique article links found: {len(article_links)}")

    rows = []

    # --- Visit each article page ---
    for i, link in enumerate(sorted(article_links), 1):
        print(f"[{i}/{len(article_links)}] Fetching article")

        try:
            soup = get_soup(link)
        except Exception as e:
            print("  Failed:", e)
            continue

        title = extract_title(soup)
        date_iso = extract_date(soup)
        abstract = extract_abstract(soup)

        if is_recent(date_iso):
            print(f"  Included ({date_iso})")
            rows.append({
                "date_published": date_iso,
                "paper_link": link,
                "full_abstract": abstract,
                "title": title
            })
        else:
            print(f"  Skipped (older than {YEARS_BACK} years)")

        time.sleep(REQUEST_DELAY)

    # --- Write CSV ---
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date_published", "paper_link", "full_abstract", "title"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Saved {len(rows)} articles to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
