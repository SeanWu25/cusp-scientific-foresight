#!/usr/bin/env python3
"""
hf_hybrid_ranker.py

Ranks the Top 80 Hugging Face papers per month using a hybrid score
of Upvotes (community interest) and Citations (academic impact), 
normalized for paper age.
"""

from __future__ import annotations
import calendar
import csv
import logging
import os
import re
import time
from datetime import datetime, date, timedelta
from typing import Dict, Iterable, List, Tuple

import requests
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs): return iterable

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---- Config ----
HF_DAILY_API = "https://huggingface.co/api/daily_papers?date={date}&page={page}&limit={limit}"
S2_BATCH_API = "https://api.semanticscholar.org/graph/v1/paper/batch"
DEFAULT_OUTPUT_DIR = os.path.join("data", "output")
DEFAULT_OUTPUT_CSV = os.path.join(DEFAULT_OUTPUT_DIR, "hf_top_40_hybrid_monthly.csv")

S2_BATCH_DELAY = 1.1 
PAGE_LIMIT = 100 

# Scoring Weights (Adjust these to tune the "elegance")
W_UPVOTES = 1.0     # Importance of community likes
W_CITATIONS = 5.0   # Citations are rarer, so we give them a higher multiplier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("hf_hybrid_collector")

ARXIV_ANY = re.compile(r"(\d{4}\.\d{4,5}(v\d+)?)")

def build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": "hf-hybrid-ranker/3.0"})
    return s

def month_range(start_ym: str, end_ym: str) -> Iterable[Tuple[int, int]]:
    sy, sm = int(start_ym[:4]), int(start_ym[4:6])
    ey, em = int(end_ym[:4]), int(end_ym[4:6])
    cur, end = date(sy, sm, 1), date(ey, em, 1)
    while cur <= end:
        yield cur.year, cur.month
        cur = (cur + timedelta(days=32)).replace(day=1)

def detect_link(pid: str) -> str:
    m = ARXIV_ANY.search(pid)
    return f"https://arxiv.org/pdf/{m.group(1)}" if m else f"https://huggingface.co/papers/{pid}"

def get_citations_batch(session: requests.Session, paper_ids: List[str]) -> Dict[str, int]:
    if not paper_ids: return {}
    payload = {"ids": [f"arXiv:{pid}" if "." in pid else pid for pid in paper_ids]}
    try:
        resp = session.post(S2_BATCH_API, json=payload, params={"fields": "citationCount"}, timeout=20)
        resp.raise_for_status()
        results = resp.json()
        return {paper_ids[i]: entry.get("citationCount", 0) for i, entry in enumerate(results) if entry}
    except Exception:
        return {}

def calculate_hybrid_score(upvotes: int, citations: int, paper_date: str) -> float:
    """Calculates a score balancing upvotes and age-normalized citations."""
    pub_date = datetime.strptime(paper_date, "%Y-%m-%d").date()
    months_old = (date.today().year - pub_date.year) * 12 + (date.today().month - pub_date.month)
    
    # Normalize citations by age (plus 1 to avoid div by zero)
    # A new paper with 5 citations is as impressive as an old paper with 50.
    citation_velocity = citations / (months_old + 1)
    
    return (upvotes * W_UPVOTES) + (citation_velocity * W_CITATIONS)

def collect_hybrid_monthly(start_ym: str, end_ym: str, out_csv: str):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    session = build_session()
    all_final_rows = []
    months = list(month_range(start_ym, end_ym))

    for year, month in tqdm(months, desc="Processing Months"):
        month_label = f"{year:04d}-{month:02d}"
        month_papers_map = {}
        
        num_days = calendar.monthrange(year, month)[1]
        days = [date(year, month, d) for d in range(1, num_days + 1)]

        for day in tqdm(days, desc=f"  Scraping {month_label}", leave=False):
            date_iso = day.strftime("%Y-%m-%d")
            url = HF_DAILY_API.format(date=date_iso, page=1, limit=PAGE_LIMIT)
            try:
                resp = session.get(url, timeout=12)
                items = resp.json() if isinstance(resp.json(), list) else resp.json().get("results", [])
                for item in items:
                    p = item.get("paper", {})
                    pid = p.get("id")
                    if pid and pid not in month_papers_map:
                        month_papers_map[pid] = {
                            "month": month_label,
                            "date": date_iso,
                            "paper_id": pid,
                            "title": (p.get("title") or "").strip(),
                            "abstract": (p.get("summary") or "").strip(),
                            "link": detect_link(pid),
                            "upvotes": p.get("upvotes", 0)
                        }
            except Exception: continue
            time.sleep(0.05)

        # Batch Citation Lookup
        unique_pids = list(month_papers_map.keys())
        citation_data = get_citations_batch(session, unique_pids)
        time.sleep(S2_BATCH_DELAY)

        # Apply Hybrid Scoring
        month_list = []
        for pid, pdata in month_papers_map.items():
            pdata["citations"] = citation_data.get(pid, 0)
            pdata["hybrid_score"] = round(calculate_hybrid_score(
                pdata["upvotes"], pdata["citations"], pdata["date"]
            ), 2)
            month_list.append(pdata)

        # Rank and Keep Top 80
        month_list.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_80 = month_list[:40]
        all_final_rows.extend(top_80)

    # Output to CSV
    fields = ["month", "hybrid_score", "citations", "upvotes", "title", "paper_id", "date", "link", "abstract"]
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in all_final_rows:
            writer.writerow({k: r.get(k, "") for k in fields})
    
    logger.info(f"Done! Saved {len(all_final_rows)} papers to {out_csv}")

if __name__ == "__main__":
    today = date.today()
    # 2-year range
    start_dt = today - timedelta(days=365 * 2)
    start_str, end_str = f"{start_dt.year}{start_dt.month:02d}", f"{today.year}{today.month:02d}"
    collect_hybrid_monthly(start_str, end_str, DEFAULT_OUTPUT_CSV)