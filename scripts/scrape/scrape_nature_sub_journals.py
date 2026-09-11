#!/usr/bin/env python3
"""
fetch_nature_journal.py

Single CLI wrapper to fetch metadata + abstracts for Nature journals (Physics, Chemistry, Cell Biology, Nature)
Uses Crossref -> OpenAlex -> publisher landing-page fallback (JSON-LD / meta / itemprop) -> Unpaywall.
Be polite: set YOUR_EMAIL below.

Usage:
  python fetch_nature_journal.py --journal nature
  python fetch_nature_journal.py --journal physics --rate 0.3
  python fetch_nature_journal.py --issn 1745-2481 --out-prefix nature_physics
"""

import time
import csv
import json
import re
from html import unescape
import argparse
import requests
from urllib.parse import quote, urlparse
from urllib.robotparser import RobotFileParser
from datetime import date, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---------------- User config ----------------
YOUR_EMAIL = "your.email@example.com"   # <-- REPLACE with your email (Crossref / Unpaywall etiquette)
DEFAULT_RATE_LIMIT = 1.0                # seconds between polite requests (tune as needed)
ROWS_PER_PAGE = 100
MAX_SAFETY_RECORDS = 50000

# Known journals mapping
JOURNALS = {
    "physics": {
        "issn": "1745-2481",
        "prefix": "nature_physics"
    },
    "chemistry": {
        "issn": "1755-4349",
        "prefix": "nature_chemistry"
    },
    "cellbiology": {
        "issn": "1476-4679",
        "prefix": "nature_cell_biology"
    },
    "machineintelligence": {
        "issn": "2522-5839",
        "prefix": "nature_machine_intelligence"
    }
}

# ---------------- End user config ----------------
CROSSREF_BASE = "https://api.crossref.org/works"
OPENALEX_BASE = "https://api.openalex.org/works/doi:"
UNPAYWALL_BASE = "https://api.unpaywall.org/v2"  # /<doi>?email=
USER_AGENT_TEMPLATE = "MetadataFetcher/1.0 (mailto:{email})"

# ---------------- Helper utilities ----------------
def make_user_agent(email):
    return USER_AGENT_TEMPLATE.format(email=email)

def safe_get(url, params=None, timeout=20, max_retries=2, backoff=1.0, headers=None):
    """GET with retries and exponential backoff for common server errors / 429s."""
    attempt = 0
    hdrs = headers or {"User-Agent": make_user_agent(YOUR_EMAIL)}
    while attempt <= max_retries:
        try:
            r = requests.get(url, params=params, headers=hdrs, timeout=timeout, allow_redirects=True)
            if r.status_code in (429, 500, 502, 503, 504):
                attempt += 1
                time.sleep(backoff * (2 ** (attempt - 1)))
                continue
            return r
        except requests.RequestException:
            attempt += 1
            time.sleep(backoff * (2 ** (attempt - 1)))
    return None

# ---------------- Crossref / OpenAlex / Unpaywall ----------------
def query_crossref(issn, offset=0, rows=ROWS_PER_PAGE, from_date=None, until_date=None, headers=None):
    """
    Query Crossref but restrict to journal-article and require an abstract to reduce noise.
    """
    filters = []
    if from_date and until_date:
        filters.append(f"from-pub-date:{from_date}")
        filters.append(f"until-pub-date:{until_date}")

    # Only primary research articles (exclude editorials, corrections, front matter, etc.)
    filters.append("type:journal-article")

    # Require an abstract to avoid many non-research items
    filters.append("has-abstract:true")

    filters.append(f"issn:{issn}")

    params = {
        "filter": ",".join(filters),
        "rows": rows,
        "offset": offset,
        # include 'type' so we can double-check returned items
        "select": "DOI,title,author,container-title,issued,reference,URL,abstract,type"
    }
    r = safe_get(CROSSREF_BASE, params=params, headers=headers)
    if r and r.status_code == 200:
        return r.json()
    raise RuntimeError(f"Crossref request failed (status: {getattr(r,'status_code',None)})")

def get_unpaywall(doi, headers=None):
    safe_doi = quote(doi, safe="")
    url = f"{UNPAYWALL_BASE}/{safe_doi}"
    params = {"email": YOUR_EMAIL}
    r = safe_get(url, params=params, timeout=20, headers=headers)
    if r and r.status_code == 200:
        try:
            return r.json()
        except Exception:
            return None
    return None

def query_openalex(doi, headers=None):
    safe = quote(doi, safe="")
    url = OPENALEX_BASE + safe
    r = safe_get(url, timeout=20, headers=headers)
    if r and r.status_code == 200:
        try:
            return r.json()
        except Exception:
            return None
    return None

# ---------------- Abstract helpers ----------------
def abstract_from_crossref(raw_abstract):
    if not raw_abstract:
        return ""
    try:
        soup = BeautifulSoup(raw_abstract, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split())
    except Exception:
        return raw_abstract

def abstract_from_openalex(openalex_json):
    if not openalex_json:
        return ""
    inv = openalex_json.get("abstract_inverted_index")
    if not inv:
        return openalex_json.get("abstract", "") or ""
    max_pos = -1
    for positions in inv.values():
        if positions:
            pmax = max(positions)
            if pmax > max_pos:
                max_pos = pmax
    length = max_pos + 1 if max_pos >= 0 else 0
    tokens = [""] * length
    for token, positions in inv.items():
        for pos in positions:
            if 0 <= pos < length:
                tokens[pos] = token
    text = " ".join(t for t in tokens if t)
    text = text.replace(" ,", ",").replace(" .", ".").replace(" ;", ";").replace(" : ", ": ")
    return " ".join(text.split())

# ---------------- Robust HTML extraction + heuristics ----------------
_robot_parsers = {}

MIN_ABSTRACT_CHARS = 120

def can_fetch_url(url, headers=None):
    try:
        u = urlparse(url)
        base = f"{u.scheme}://{u.netloc}"
        if base in _robot_parsers:
            rp = _robot_parsers[base]
        else:
            robots_url = base + "/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception:
                rp = None
            _robot_parsers[base] = rp
        if rp is None:
            return False
        ua = headers.get("User-Agent") if headers else make_user_agent(YOUR_EMAIL)
        return rp.can_fetch(ua, url) or rp.can_fetch("*", url)
    except Exception:
        return False

def looks_like_abstract(text, title=None, journal_name=None):
    if not text:
        return False
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) < MIN_ABSTRACT_CHARS:
        return False
    if title and t.lower() == title.lower():
        return False
    if journal_name and re.search(r"\b" + re.escape(journal_name) + r"\b", t, flags=re.IGNORECASE) and len(t) < 300:
        return False
    # must contain a sentence-like punctuation or be long with commas
    if re.search(r"\.", t) is None:
        if len(t) < 300 or re.search(r"[,:;]", t) is None:
            return False
    return True

def extract_jsonld_abstract(soup):
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for s in scripts:
        try:
            raw = s.string or s.text
            if not raw:
                continue
            data = json.loads(raw)
            def find_description(obj):
                if isinstance(obj, dict):
                    if "description" in obj and isinstance(obj["description"], str) and obj["description"].strip():
                        return obj["description"].strip()
                    for v in obj.values():
                        res = find_description(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = find_description(item)
                        if res:
                            return res
                return None
            desc = find_description(data)
            if desc:
                return unescape(desc)
        except Exception:
            continue
    return ""

def extract_meta_candidates(soup):
    meta_candidates = [
        "citation_abstract",
        "dc.description",
        "dc.description.abstract",
        "dc.Description",
        "og:description",
        "description",
        "twitter:description"
    ]
    found = []
    for name in meta_candidates:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            found.append(tag["content"].strip())
        tag = soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            found.append(tag["content"].strip())
    return found

def extract_itemprop_or_role_abstracts(soup):
    candidates = []
    for tag in soup.find_all(attrs={"itemprop": "description"}):
        t = tag.get_text(" ", strip=True)
        if t:
            candidates.append(t)
    for tag in soup.find_all(attrs={"role": "abstract"}):
        t = tag.get_text(" ", strip=True)
        if t:
            candidates.append(t)
    selectors = [
        "section#abstract", "section.abstract", "div.abstract", "div[class*='ArticleAbstract']",
        "div[class*='abstract']", "div[class*='article__abstract']", "div[class*='Abstract']",
        "section.article__abstract", "div.c-article-section__content"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(" ", strip=True)
            if t:
                candidates.append(t)
    return candidates

def find_abstract_in_html_robust(soup, title=None, journal_name=None):
    jd = extract_jsonld_abstract(soup)
    if jd and looks_like_abstract(jd, title=title, journal_name=journal_name):
        return " ".join(jd.split())

    metas = extract_meta_candidates(soup)
    for m in metas:
        if looks_like_abstract(m, title=title, journal_name=journal_name):
            return " ".join(m.split())

    items = extract_itemprop_or_role_abstracts(soup)
    for it in items:
        if looks_like_abstract(it, title=title, journal_name=journal_name):
            return " ".join(it.split())

    for tag in soup.find_all(True):
        attrs = " ".join(str(tag.get(attr) or "") for attr in ("id","class","aria-label","title"))
        if "abstract" in attrs.lower():
            text = tag.get_text(" ", strip=True)
            if looks_like_abstract(text, title=title, journal_name=journal_name):
                return " ".join(text.split())

    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if desc_tag and desc_tag.get("content"):
        c = desc_tag["content"].strip()
        if looks_like_abstract(c, title=title, journal_name=journal_name):
            return " ".join(c.split())

    return ""

def fetch_abstract_from_landing_improved(url, doi=None, title=None, journal_name=None, headers=None, rate_limit=1.0):
    if not url:
        return ""
    try:
        r = safe_get(url, timeout=20, headers=headers)
        if not r or r.status_code != 200:
            return ""
        final_url = r.url or url
        if not can_fetch_url(final_url, headers=headers):
            return ""
        r2 = safe_get(final_url, timeout=20, headers=headers)
        if not r2 or r2.status_code != 200 or not r2.text:
            return ""
        soup = BeautifulSoup(r2.text, "html.parser")
        abstr = find_abstract_in_html_robust(soup, title=title, journal_name=journal_name)
        # polite pause
        time.sleep(rate_limit * 0.2)
        return abstr or ""
    except Exception:
        return ""

# ---------------- Utilities ----------------
def author_list(author_field):
    if not author_field:
        return ""
    parts = []
    for a in author_field:
        if a is None:
            continue
        name = " ".join([str(a.get("given","")).strip(), str(a.get("family","")).strip()]).strip()
        if not name:
            name = a.get("name", "")
        parts.append(name)
    return "; ".join(p for p in parts if p)

def doi_safe(doi):
    return doi.replace("/", "_").replace(":", "_")

# ---------------- Main pipeline ----------------
def run_pipeline(issn, out_prefix, rate_limit=DEFAULT_RATE_LIMIT, max_pages=None):
    headers = {"User-Agent": make_user_agent(YOUR_EMAIL)}
    today = date.today()
    two_years_ago = today - timedelta(days=365*2 + 1)
    from_date = two_years_ago.isoformat()
    until_date = today.isoformat()

    print(f"Querying Crossref for ISSN {issn} from {from_date} to {until_date}...")
    first = query_crossref(issn, offset=0, rows=ROWS_PER_PAGE, from_date=from_date, until_date=until_date, headers=headers)
    total = first["message"].get("total-results", 0)
    print(f"Crossref returned total-results: {total}")

    out_csv = f"{out_prefix}_last2y.csv"
    out_jsonl = f"{out_prefix}_last2y.jsonl"

    fieldnames = ["doi","title","authors","pubdate","crossref_url","oa_type","oa_url","abstract"]
    csvfile = open(out_csv, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    jsonlfile = open(out_jsonl, "w", encoding="utf-8")

    offset = 0
    page_count = 0
    processed = 0
    pbar = tqdm(total=total if total and total < 100000 else None, desc="processing")
    try:
        while True:
            if max_pages is not None and page_count >= max_pages:
                break
            data = query_crossref(issn, offset=offset, rows=ROWS_PER_PAGE, from_date=from_date, until_date=until_date, headers=headers)
            items = data["message"].get("items", [])
            if not items:
                break

            # Debug: show types on first page to help diagnose Crossref counts
            if page_count == 0:
                types_seen = {}
                for it in items:
                    t = it.get("type", "unknown")
                    types_seen[t] = types_seen.get(t, 0) + 1
                print("Crossref item types on first page:", types_seen)

            for it in items:
                # Extra safety: only process declared journal-article items
                if it.get("type") != "journal-article":
                    continue

                # Strict container-title check: only accept exact "Nature"
                container_titles = it.get("container-title", [])
                if not any(isinstance(ct, str) and ct.strip().lower() == "nature"
                           for ct in container_titles):
                    # skip items belonging to sub-journals like "Nature Physics" etc.
                    continue

                doi = it.get("DOI")
                title = " / ".join(it.get("title", [])) if it.get("title") else ""
                authors = author_list(it.get("author"))
                issued = it.get("issued", {}).get("date-parts", [[None]])[0]
                pubdate = "-".join(str(x) for x in issued if x) if issued else ""
                crossref_url = it.get("URL", "")

                record = {
                    "doi": doi or "",
                    "title": title or "",
                    "authors": authors or "",
                    "pubdate": pubdate or "",
                    "crossref_url": crossref_url or "",
                    "oa_type": "",
                    "oa_url": "",
                    "abstract": ""
                }

                # 1) Crossref abstract
                raw_abs = it.get("abstract")
                abs_text = abstract_from_crossref(raw_abs) if raw_abs else ""

                # 2) OpenAlex fallback
                if not abs_text and doi:
                    time.sleep(rate_limit * 0.2)
                    oa = query_openalex(doi, headers=headers)
                    abs_text = abstract_from_openalex(oa) if oa else ""

                # 3) landing page robust extraction
                journal_name_guess = None
                # infer journal name from container-title if available
                ct = it.get("container-title")
                if ct:
                    journal_name_guess = ct[0] if isinstance(ct, list) and ct else (ct if isinstance(ct, str) else None)
                if not abs_text and crossref_url:
                    time.sleep(rate_limit * 0.2)
                    abs_text = fetch_abstract_from_landing_improved(crossref_url, doi=doi, title=title, journal_name=journal_name_guess, headers=headers, rate_limit=rate_limit)

                # 4) doi.org resolution if still empty
                if not abs_text and crossref_url and "doi.org" in crossref_url:
                    try:
                        r = safe_get(crossref_url, timeout=20, headers=headers)
                        if r and r.status_code == 200 and r.url and r.url != crossref_url:
                            resolved = r.url
                            time.sleep(rate_limit * 0.2)
                            abs_text = fetch_abstract_from_landing_improved(resolved, doi=doi, title=title, journal_name=journal_name_guess, headers=headers, rate_limit=rate_limit)
                    except Exception:
                        pass

                record["abstract"] = abs_text or ""

                # Unpaywall OA info
                if doi:
                    time.sleep(rate_limit * 0.2)
                    uw = get_unpaywall(doi, headers=headers)
                    if uw:
                        best = uw.get("best_oa_location") or {}
                        record["oa_url"] = best.get("url_for_pdf") or best.get("url") or ""
                        record["oa_type"] = uw.get("oa_status") or ""

                writer.writerow(record)
                jsonlfile.write(json.dumps(record, ensure_ascii=False) + "\n")
                pbar.update(1)
                processed += 1
                time.sleep(rate_limit * 0.1)

                if processed >= MAX_SAFETY_RECORDS:
                    print(f"Reached safety cap of {MAX_SAFETY_RECORDS} records; stopping.")
                    break

            offset += ROWS_PER_PAGE
            page_count += 1
            if offset >= total:
                break
            if processed >= MAX_SAFETY_RECORDS:
                break
            time.sleep(rate_limit)
    finally:
        pbar.close()
        csvfile.close()
        jsonlfile.close()
    print("Done. Outputs:", out_csv, out_jsonl)

# ---------------- CLI ----------------
def parse_args():
    p = argparse.ArgumentParser(description="Fetch Nature journal metadata + abstracts (Crossref -> OpenAlex -> landing page)")
    p.add_argument("--journal", choices=list(JOURNALS.keys()), help=f"Choose journal by name ({' | '.join(JOURNALS.keys())})")
    p.add_argument("--issn", help="Direct ISSN to query (overrides --journal)")
    p.add_argument("--out-prefix", help="Output file prefix (default from journal)", default=None)
    p.add_argument("--rate", type=float, default=DEFAULT_RATE_LIMIT, help="Global rate limit (seconds)")
    p.add_argument("--max-pages", type=int, default=None, help="Optional cap on Crossref pages")
    return p.parse_args()

def main():
    args = parse_args()
    if args.issn:
        issn = args.issn
        out_prefix = args.out_prefix or f"journal_{issn.replace('-', '_')}"
    elif args.journal:
        j = args.journal
        issn = JOURNALS[j]["issn"]
        out_prefix = args.out_prefix or JOURNALS[j]["prefix"]
    else:
        raise SystemExit("Error: provide --journal or --issn. Use -h for help.")

    if YOUR_EMAIL == "your.email@example.com":
        print("Warning: please set YOUR_EMAIL in the script to a contact email (Crossref/Unpaywall etiquette).")

    run_pipeline(issn=issn, out_prefix=out_prefix, rate_limit=args.rate, max_pages=args.max_pages)

if __name__ == "__main__":
    main()