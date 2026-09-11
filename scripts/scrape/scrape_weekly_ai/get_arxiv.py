#!/usr/bin/env python3

import sys
import re
import time
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote
from tqdm import tqdm

ARXIV_API = "http://export.arxiv.org/api/query?id_list="
HEADERS = {"User-Agent": "arXivAbstractFetcher/1.0"}
TIMEOUT = 15
DELAY = 0.3  # polite delay between API calls


# -----------------------------
# Extract arXiv ID from URL
# -----------------------------
def extract_arxiv_id(url):
    if not isinstance(url, str):
        return None

    url = url.strip()

    # Already just an arXiv ID
    if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', url):
        return url

    parsed = urlparse(url)
    if "arxiv.org" not in (parsed.hostname or "").lower():
        return None

    path = parsed.path

    # /abs/ID
    m = re.search(r'/abs/([^/?#]+)', path)
    if m:
        return unquote(m.group(1))

    # /pdf/ID.pdf
    m = re.search(r'/pdf/([^/?#]+)', path)
    if m:
        return re.sub(r'\.pdf$', '', m.group(1))

    return None


# -----------------------------
# Fetch abstract from API
# -----------------------------
def fetch_abstract(arxiv_id):
    try:
        r = requests.get(ARXIV_API + arxiv_id, headers=HEADERS, timeout=TIMEOUT)
    except Exception:
        return None

    if r.status_code != 200:
        return None

    try:
        root = ET.fromstring(r.text.encode("utf-8"))
        for child in root:
            if child.tag.endswith("entry"):
                for sub in child:
                    if sub.tag.endswith("summary"):
                        return " ".join((sub.text or "").split())
    except Exception:
        return None

    return None


# -----------------------------
# Main
# -----------------------------
def main(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # find paper_link column
    link_col = None
    for c in df.columns:
        if c.strip().lower() == "paper_link":
            link_col = c
            break

    if not link_col:
        print("ERROR: 'paper_link' column not found.")
        sys.exit(1)

    arxiv_rows = []
    abstracts = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        url = row[link_col]
        arxiv_id = extract_arxiv_id(url)

        if not arxiv_id:
            continue  # DROP non-arXiv rows entirely

        abstract = fetch_abstract(arxiv_id)
        abstracts.append(abstract if abstract else "")

        new_row = row.copy()
        new_row["abstract"] = abstract if abstract else ""
        arxiv_rows.append(new_row)

        time.sleep(DELAY)

    if not arxiv_rows:
        print("No arXiv rows found.")
        sys.exit(0)

    new_df = pd.DataFrame(arxiv_rows)
    new_df.to_csv(output_csv, index=False)

    print(f"Done. Wrote {len(new_df)} arXiv rows to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_arxiv_only.py input.csv output.csv")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])

