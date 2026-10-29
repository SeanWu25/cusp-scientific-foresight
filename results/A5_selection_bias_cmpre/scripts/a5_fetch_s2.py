#!/usr/bin/env python3
"""
a5_fetch_s2.py -- Semantic Scholar citation counts for every linked event, in
batches of 500 (POST /graph/v1/paper/batch), cached to metadata/s2_citations.jsonl.

Semantic Scholar is the primary count source because it indexes arXiv papers
as first-class records; OpenAlex attributes most arXiv citations to the later
journal version (or has no record), so its arXiv counts are near zero. This
mirrors the provenance of the original 481-event file (S2, OpenAlex fallback).
"""
import json, os, sys, time, urllib.request
REPO = "."
OUT = f"{REPO}/results/A5_selection_bias/metadata"
URL = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=citationCount,externalIds,publicationDate"
UA = {"User-Agent": "CUSP-A5-metadata/1.0 (mailto:" + os.environ.get("CUSP_MAILTO", "your.email@example.com") + ")", "Content-Type": "application/json"}

ev = json.load(open(f"{OUT}/event_ids.json"))
path = f"{OUT}/s2_citations.jsonl"
cache = {json.loads(l)["doi"] for l in open(path)} if os.path.exists(path) else set()
todo = sorted({e["doi"] for e in ev if e["doi"] and e["doi"] not in cache})
print(f"S2: {len(cache)} cached, {len(todo)} to fetch", flush=True)


def s2id(doi):
    return "ARXIV:" + doi.split("arXiv.")[1] if doi.startswith("10.48550/arXiv.") else "DOI:" + doi


with open(path, "a") as fh:
    for i in range(0, len(todo), 500):
        batch = todo[i:i + 500]
        body = json.dumps({"ids": [s2id(d) for d in batch]}).encode()
        for k in range(8):
            try:
                req = urllib.request.Request(URL, data=body, headers=UA, method="POST")
                with urllib.request.urlopen(req, timeout=120) as r:
                    res = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                print(f"  HTTP {e.code}, retry {k}", flush=True); time.sleep(3 * (k + 1))
            except Exception as e:
                print(f"  {e}, retry {k}", flush=True); time.sleep(3 * (k + 1))
        else:
            sys.exit("S2 batch failed repeatedly")
        found = 0
        for d, w in zip(batch, res):
            rec = dict(doi=d, found=w is not None,
                       citation_count=w.get("citationCount") if w else None,
                       s2_paper_id=w.get("paperId") if w else None,
                       s2_publication_date=w.get("publicationDate") if w else None)
            found += w is not None
            fh.write(json.dumps(rec) + "\n")
        fh.flush()
        print(f"  s2 {i + len(batch)}/{len(todo)} found {found}/{len(batch)}", flush=True)
        time.sleep(1.2)
print("DONE", flush=True)
