import requests
import pandas as pd
import time
import xml.etree.ElementTree as ET
import re

BASE_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

MONTH_MAP = {
    "Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06",
    "Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"
}

def get_full_text(elem):
    """Extract all text from an XML element including tail text of children."""
    if elem is None:
        return ""
    parts = [elem.text or ""]
    for child in elem:
        parts.append(get_full_text(child))
        parts.append(child.tail or "")
    return "".join(parts)

def clean_abstract(text):
    """Remove citation markers like __1__, __1,2__, __1__,__2__ etc."""
    if not text:
        return ""
    # Remove patterns like __1__, __1,2,3__, __1__,__2__ chains
    text = re.sub(r'(__\d+(__,__\d+)*__,?)+', '', text)
    # Remove any leftover double underscores
    text = re.sub(r'__+', '', text)
    # Remove superscript-style numbers left behind e.g. 1,2,3 after inline tags
    text = re.sub(r'(?<=[a-zA-Z])\d+(,\d+)*(?=\s)', '', text)
    # Clean up extra spaces and stray commas before punctuation
    text = re.sub(r',\s*\.', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_date(pub_date_elem):
    """Return YYYY-MM from a PubDate XML element."""
    if pub_date_elem is None:
        return ""
    year  = pub_date_elem.findtext("Year")  or ""
    month = pub_date_elem.findtext("Month") or ""
    month = MONTH_MAP.get(month, month)
    if month.isdigit():
        month = month.zfill(2)
    if year and month:
        return f"{year}-{month}"
    return year

def search_pubmed(journal="Nature", date_from="2023/03/01", date_to="2025/03/01"):
    """Get all PMIDs for Nature original research articles in date range."""
    pmids = []
    retstart = 0
    retmax = 200

    while True:
        params = {
            "db": "pubmed",
            "term": f'"{journal}"[Journal] AND "{date_from}"[PDAT]:"{date_to}"[PDAT] AND Journal Article[PT]',
            "retmax": retmax,
            "retstart": retstart,
            "retmode": "json",
        }
        r = requests.get(BASE_SEARCH, params=params)
        data = r.json()
        ids = data["esearchresult"]["idlist"]
        total = int(data["esearchresult"]["count"])
        pmids.extend(ids)
        print(f"Fetched {len(pmids)} / {total} PMIDs...")

        if retstart + retmax >= total:
            break
        retstart += retmax
        time.sleep(0.4)

    return pmids

def fetch_details(pmids, batch_size=100):
    """Fetch title, abstract, date, DOI for each PMID."""
    articles = []

    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "rettype": "xml",
            "retmode": "xml"
        }
        r = requests.get(BASE_FETCH, params=params)
        root = ET.fromstring(r.text)

        for article in root.findall(".//PubmedArticle"):
            try:
                # Title
                title_elem = article.find(".//ArticleTitle")
                title = get_full_text(title_elem).strip()

                # Abstract — use get_full_text to capture text after inline citation tags
                abstract_parts = article.findall(".//AbstractText")
                raw_abstract = " ".join(
                    (f"{p.get('Label', '')}: {get_full_text(p)}" if p.get('Label') else get_full_text(p))
                    for p in abstract_parts
                ).strip()
                abstract = clean_abstract(raw_abstract)

                # Date → YYYY-MM
                pub_date = article.find(".//PubDate")
                date = format_date(pub_date)

                # DOI
                doi = ""
                for id_elem in article.findall(".//ArticleId"):
                    if id_elem.get("IdType") == "doi":
                        doi = id_elem.text
                        break
                url = f"https://doi.org/{doi}" if doi else ""

                # Skip if no abstract (filters out editorials, news, corrections)
                if not abstract:
                    continue

                articles.append({
                    "title": title,
                    "date_published": date,
                    "abstract": abstract,
                    "doi": doi,
                    "url": url
                })

            except Exception as e:
                print(f"Skipping article: {e}")
                continue

        print(f"Processed {min(i+batch_size, len(pmids))} / {len(pmids)} articles")
        time.sleep(0.4)

    return articles

# --- Run ---
pmids = search_pubmed(
    journal="Nature",
    date_from="2024/03/01",
    date_to="2026/03/02"
)

articles = fetch_details(pmids)

df = pd.DataFrame(articles)
df.to_csv("nature_articles.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ Saved {len(df)} articles to nature_articles.csv")