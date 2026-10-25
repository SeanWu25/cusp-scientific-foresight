#!/usr/bin/env python3
"""
a5_fetch_metadata.py -- one-shot, single-date metadata pass over the ENTIRE
corpus (both halves), so that visibility and latency can be stratified on the
whole dataset instead of the 481 / 708 events the first A5 pass had to use.

Two free APIs, no inference, no cost:

  OpenAlex  (batch of 50 DOIs per request)      -> cited_by_count for every
            linked event (journal DOIs and arXiv via 10.48550/arXiv.<id>)
  Crossref  (one DOI per request, 10 req/s pool) -> for every journal DOI:
            created / published-online / published-print / issued dates,
            received / accepted / first_online assertions (Nature, Science),
            has-preprint relations; then the posted date of each preprint DOI

Everything is cached as JSONL keyed by DOI under metadata/, one record per
line, written incrementally; rerunning resumes and never re-fetches a DOI
already on disk. The snapshot date is recorded in metadata/SNAPSHOT.json.
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date

REPO = "/home/seanwu/FutureScience"
ORIG = f"{REPO}/archive/data/canonical/merged_validated_cusp_fixed.jsonl"
EXT = f"{REPO}/benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"
OUT = f"{REPO}/results/A5_selection_bias/metadata"
MAILTO = "seannwu25@gmail.com"
UA = {"User-Agent": f"CUSP-A5-metadata/1.0 (mailto:{MAILTO})"}
_DOI = re.compile(r"(10\.\d{4,9}/[^\s]+)$")
_ARX = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})")


def get(url, tries=6):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last = e
            time.sleep(2 ** k if e.code == 429 else 1.5 * (k + 1))
        except Exception as e:  # network hiccup
            last = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError(f"gave up on {url}: {last}")


def events():
    for corpus, path in (("original", ORIG), ("extension", EXT)):
        for l in open(path, encoding="utf-8"):
            if not l.strip():
                continue
            d = json.loads(l)
            link = d.get("paper_link") or ""
            doi, kind = None, "none"
            m = _ARX.search(link)
            if m:
                doi, kind = f"10.48550/arXiv.{m.group(1)}", "arxiv"
            else:
                m = _DOI.search(link)
                if m:
                    doi, kind = m.group(1).rstrip("/").rstrip("."), "doi"
            yield dict(id=d["id"], corpus=corpus, source=d["source"], kind=kind,
                       doi=doi, pub=str(d.get("publication_date", ""))[:7])


def load_cache(path):
    out = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                out[r["doi"]] = r
    return out


def dp(x):
    """Crossref date-parts -> 'YYYY-MM' (or 'YYYY-MM-DD' when a day exists)."""
    try:
        p = x["date-parts"][0]
        if len(p) >= 3:
            return f"{p[0]:04d}-{p[1]:02d}-{p[2]:02d}"
        if len(p) == 2:
            return f"{p[0]:04d}-{p[1]:02d}"
        return f"{p[0]:04d}"
    except Exception:
        return None


MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}


def norm_assert(v):
    """'29 March 2024' or '2025-07-18' -> 'YYYY-MM-DD'."""
    if not v:
        return None
    v = v.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", v)
    if m and m.group(2).lower() in MONTHS:
        return f"{int(m.group(3)):04d}-{MONTHS[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return v


def fetch_openalex(ev):
    path = f"{OUT}/openalex_citations.jsonl"
    cache = load_cache(path)
    todo = sorted({e["doi"] for e in ev if e["doi"] and e["doi"] not in cache})
    print(f"OpenAlex: {len(cache)} cached, {len(todo)} to fetch", flush=True)
    with open(path, "a", encoding="utf-8") as fh:
        for i in range(0, len(todo), 50):
            batch = todo[i:i + 50]
            f = "|".join("https://doi.org/" + d for d in batch)
            url = ("https://api.openalex.org/works?filter=doi:" + urllib.parse.quote(f, safe="")
                   + "&select=id,doi,cited_by_count,publication_date,counts_by_year,type"
                   + f"&per-page=50&mailto={MAILTO}")
            res = get(url) or {"results": []}
            found = {}
            for w in res.get("results", []):
                d = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                found[d] = w
            for d in batch:
                w = found.get(d.lower())
                rec = dict(doi=d, found=w is not None,
                           cited_by_count=w["cited_by_count"] if w else None,
                           oa_publication_date=w.get("publication_date") if w else None,
                           counts_by_year=w.get("counts_by_year") if w else None,
                           openalex_id=w.get("id") if w else None)
                fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"  openalex {i + len(batch)}/{len(todo)}  found {len(found)}/{len(batch)}", flush=True)
            time.sleep(0.15)


def crossref_record(doi):
    w = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}")
    if not w:
        return dict(doi=doi, found=False)
    w = w["message"]
    asr = {}
    for a in w.get("assertion", []) or []:
        n = a.get("name")
        if n in ("received", "accepted", "first_online", "published", "revised"):
            asr[n] = norm_assert(a.get("value"))
    rel = w.get("relation") or {}
    return dict(
        doi=doi, found=True, type=w.get("type"),
        container=(w.get("container-title") or [None])[0],
        created=dp(w.get("created") or {}),
        published_online=dp(w.get("published-online") or {}),
        published_print=dp(w.get("published-print") or {}),
        issued=dp(w.get("issued") or {}),
        posted=dp(w.get("posted") or {}),
        accepted_field=dp(w.get("accepted") or {}),
        assertions=asr,
        has_preprint=[x.get("id") for x in rel.get("has-preprint", [])],
        is_preprint_of=[x.get("id") for x in rel.get("is-preprint-of", [])],
    )


def fetch_crossref(ev):
    path = f"{OUT}/crossref_dates.jsonl"
    cache = load_cache(path)
    todo = sorted({e["doi"] for e in ev if e["kind"] == "doi" and e["doi"] not in cache})
    print(f"Crossref journal DOIs: {len(cache)} cached, {len(todo)} to fetch", flush=True)
    t0 = time.time()
    with open(path, "a", encoding="utf-8") as fh:
        for i, d in enumerate(todo, 1):
            rec = crossref_record(d)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            if i % 100 == 0:
                print(f"  crossref {i}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
            time.sleep(0.12)
    cache = load_cache(path)
    # second pass: posted dates of every linked preprint
    ppath = f"{OUT}/crossref_preprints.jsonl"
    pc = load_cache(ppath)
    pre = sorted({p for r in cache.values() for p in (r.get("has_preprint") or []) if p and p not in pc})
    print(f"Crossref preprint DOIs: {len(pc)} cached, {len(pre)} to fetch", flush=True)
    with open(ppath, "a", encoding="utf-8") as fh:
        for i, d in enumerate(pre, 1):
            rec = crossref_record(d)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            if i % 100 == 0:
                print(f"  preprints {i}/{len(pre)}", flush=True)
            time.sleep(0.12)


def main():
    os.makedirs(OUT, exist_ok=True)
    ev = list(events())
    json.dump(ev, open(f"{OUT}/event_ids.json", "w"), indent=0)
    snap = f"{OUT}/SNAPSHOT.json"
    if not os.path.exists(snap):
        json.dump(dict(snapshot_date=date.today().isoformat(),
                       openalex="https://api.openalex.org/works (batched DOI filter)",
                       crossref="https://api.crossref.org/works/<doi> (polite pool)",
                       n_events=len(ev), n_linked=sum(1 for e in ev if e["doi"]),
                       n_journal_doi=sum(1 for e in ev if e["kind"] == "doi"),
                       n_arxiv=sum(1 for e in ev if e["kind"] == "arxiv")),
                  open(snap, "w"), indent=2)
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "openalex"):
        fetch_openalex(ev)
    if what in ("all", "crossref"):
        fetch_crossref(ev)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
