"""
A4.2 supplement — document-level leakage under WS+Cutoff: how often the evidence a model actually received contains a
document first made public ON OR AFTER the run's date ceiling. Complements the judge-based outcome leakage in
results.md (which catches snippet-level leaks, e.g. ResearchGate "related" abstracts, that URL dating cannot see).

Each stored URL (the exact list the model received) is dated from its identifier, earliest public date:
  arXiv id (YYMM, first submission) · bioRxiv/medRxiv DOI (posting date) · DOI in URL, Nature article id, eLife id,
  ScienceDirect/Cell PII -> Crossref (min of created / posted / published-online / published-print / issued) ·
  PubMed / PMC -> NCBI E-utilities esummary (earliest of epub/pub date). Other URLs are 'undated' and reported as such.
A document leaks if its month >= the ceiling month (the pipeline's own rule: page_age must be < the ceiling date).
Pre/post split as in results.md: --cutoff-month pre (default) = pre-cutoff event if publication month <= ceiling month
(output suffix _cmpre); --cutoff-month post = the original rule, publication month < ceiling month (original file names).
Lookups are cached in A4_2_groundtruth_inclusion/doc_dates_cache.json (no email or key is sent to Crossref / NCBI).

Writes A4_2_groundtruth_inclusion/leakage{SFX}.md, tables/A4_2_leakage{SFX}.json
"""
import json, re, sys, time, collections, urllib.request, urllib.parse, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); from a42_common import *
import argparse as _ap
_p = _ap.ArgumentParser(); _p.add_argument("--cutoff-month", choices=("pre", "post"), default="pre",
    help="pre (default): an event published in the ceiling/cutoff month counts as PRE-cutoff (post iff pub month > ceiling month), the rule used everywhere in the paper; "
         "post: the original rule of this audit (post iff pub month >= ceiling month), which writes the original output files")
_p.add_argument("--add-ext", type=int, default=0, help="add N extension-corpus events (Apr-Aug 2026, drawn from the A4.3 ext500 set, stratified by month, seed 20261026) "
    "using the stored WS+Cutoff URL lists of each model's original-design run on those events (ext500/original/raw); DeepSeek R1 has no such run")
_p.add_argument("--suffix", default=None, help="output-file suffix; default '_cmpre' for --cutoff-month pre and '' for post")
ARGS = _p.parse_args(); CM_PRE = ARGS.cutoff_month == "pre"; SFX = ARGS.suffix if ARGS.suffix is not None else ("_cmpre" if CM_PRE else "") + (f"_ext{ARGS.add_ext}" if ARGS.add_ext else "")
def is_post(pub_m, cut_m): return pub_m > cut_m if CM_PRE else pub_m >= cut_m
D = OUT / "A4_2_groundtruth_inclusion"; CACHE = D / "doc_dates_cache.json"
cache = json.load(open(CACHE)) if CACHE.exists() else {}
UA = {"User-Agent": "CUSP-revision-leakage-audit/1.0"}
ARX = re.compile(r"arxiv\.org/(?:abs|pdf|html)/(\d{2})(\d{2})\.\d{4,5}"); RX = re.compile(r"(?:bio|med)rxiv\.org/content/10\.1101/(\d{4})\.(\d{2})\.\d{2}")
DOI = re.compile(r"(10\.\d{4,9}/[^\s?#&]+)"); NAT = re.compile(r"nature\.com/articles/([A-Za-z0-9.\-]+)")
PII = re.compile(r"(?:pii/|fulltext/|/pii/)(S[\dX\-\(\)]{15,25})", re.I); ELIFE = re.compile(r"elifesciences\.org/articles/(\d{4,6})")
PMID = re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)"); PMC = re.compile(r"PMC(\d+)")


def ym(y, m=1): return f"{int(y):04d}-{int(m):02d}"
def months(s): y, m = str(s)[:7].split("-"); return int(y) * 12 + int(m)


def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(2 * (k + 1))
        except Exception: time.sleep(2 * (k + 1))
    return None


def crossref_earliest(msg):
    ds = []
    for k in ("created", "posted", "published-online", "published-print", "issued", "published"):
        p = (msg.get(k) or {}).get("date-parts") or [[None]]
        if p and p[0] and p[0][0]: ds.append(ym(p[0][0], p[0][1] if len(p[0]) > 1 else 1) if len(p[0]) > 1 else (ym(p[0][0], 1) + "~y"))
    full = [d for d in ds if not d.endswith("~y")]
    return min(full) if full else (min(d[:7] for d in ds) + "~y" if ds else None)


def cr_doi(doi):
    key = "doi:" + doi
    if key in cache: return cache[key]
    d = None
    for cand in (doi, re.sub(r"/(full|abstract|pdf|epdf|fulltext|full\.pdf|meta)$", "", doi), doi.rsplit("/", 1)[0] if doi.count("/") > 1 else doi):
        r = get("https://api.crossref.org/works/" + urllib.parse.quote(cand, safe="/"))
        if r and r.get("message"): d = crossref_earliest(r["message"]); break
    cache[key] = d; return d


def cr_pii(pii):
    p = re.sub(r"[\-\(\)]", "", pii).upper(); key = "pii:" + p
    if key in cache: return cache[key]
    r = get("https://api.crossref.org/works?rows=1&filter=alternative-id:" + p)
    items = (r or {}).get("message", {}).get("items") or []
    d = crossref_earliest(items[0]) if items else (ym(2000 + int(p[9:11]) if int(p[9:11]) < 50 else 1900 + int(p[9:11])) + "~y" if p[9:11].isdigit() else None)
    cache[key] = d; return d


def ncbi(db, ids):
    out = {}
    for i in range(0, len(ids), 150):
        chunk = ids[i:i + 150]; r = get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db={db}&retmode=json&id=" + ",".join(chunk)); time.sleep(0.4)
        res = (r or {}).get("result", {})
        for j in chunk:
            x = res.get(j) or {}; ds = []
            for k in ("epubdate", "pubdate", "printpubdate", "sortpubdate"):
                m = re.match(r"(\d{4})(?:[/ -](\w{2,3}))?", str(x.get(k) or ""))
                if m:
                    mon = m.group(2); mm = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}.get(mon, int(mon) if mon and mon.isdigit() else None)
                    ds.append(ym(m.group(1), mm) if mm else ym(m.group(1), 1) + "~y")
            full = [d for d in ds if not d.endswith("~y")]
            out[j] = min(full) if full else (min(d[:7] for d in ds) + "~y" if ds else None)
    return out


def classify(u):
    m = ARX.search(u)
    if m: return ("arxiv", ym(2000 + int(m.group(1)), m.group(2)))
    m = RX.search(u)
    if m: return ("b/medrxiv", ym(m.group(1), m.group(2)))
    m = PMID.search(u)
    if m: return ("pubmed", "pmid:" + m.group(1))
    if "ncbi.nlm.nih.gov" in u and PMC.search(u): return ("pmc", "pmc:" + PMC.search(u).group(1))
    m = NAT.search(u)
    if m: return ("nature", "doi:10.1038/" + m.group(1).lower().split(".pdf")[0])
    m = ELIFE.search(u)
    if m: return ("elife", "doi:10.7554/elife." + m.group(1))
    m = PII.search(u)
    if m and ("sciencedirect" in u or "cell.com" in u or "thelancet" in u): return ("pii", "pii:" + m.group(1))
    m = DOI.search(u)
    if m: return ("doi", "doi:" + m.group(1).rstrip("/.").lower())
    return ("undated", None)


EXT_DIR = OUT / "A4_3_fixed_queries/ext500"
EXT_RUNS = {  # model -> (stored WS+Cutoff run on the ext500 events, ceiling); ceilings as in a43_ext_original.sh / RUNS
    "GPT-4o": ("gpt4o_ws_cutoff.adapted.jsonl", "2023-10-01"), "GPT-5.4": ("gpt54_ws_cutoff.adapted.jsonl", "2025-08-01"),
    "Claude S4.5": ("claude45_ws_cutoff.adapted.jsonl", "2025-01-01"), "LLaMA 3.3 70B": ("llama33_ws_cutoff.jsonl", "2023-12-01"),
    "Claude Sonnet 5": ("sonnet5_ws_cutoff.jsonl", "2026-01-01"), "GPT-5.6 Sol": ("sol_ws_cutoff.jsonl", "2026-02-01")}


def ext_rows(n, ev, seed=20261026):
    """n events of the extension corpus (Apr-Aug 2026) from the ext500 set, proportional to month, fixed seed;
    one row per model with stored URLs. The ids are written to ext{n}_leakage_ids.txt."""
    import random
    ids = [l.strip() for l in open(EXT_DIR / "subset_ext500_ids.txt") if l.strip()]
    extc = set(json.loads(l)["id"] for l in open(BENCH_FILES[1]) if l.strip())
    pool = sorted(i for i in ids if i in extc); by = collections.defaultdict(list)
    for i in pool: by[ev[i]["publication_date"][:7]].append(i)
    rng = random.Random(seed); quota = {m: n * len(v) / len(pool) for m, v in by.items()}
    k = {m: int(q) for m, q in quota.items()}
    for m in sorted(quota, key=lambda m: -(quota[m] - k[m]))[: n - sum(k.values())]: k[m] += 1
    pick = sorted(x for m in sorted(by) for x in rng.sample(sorted(by[m]), k[m]))
    (D / f"ext{n}_leakage_ids.txt").write_text("\n".join(pick) + "\n")
    keep = set(pick); out = []
    for model, (fn, ceil) in EXT_RUNS.items():
        key = f"ext:{model}"; RUNS[key] = (model, "ws_cutoff", "ext", EXT_DIR / "original/raw" / fn, "youcom", ceil, None)
        for l in open(EXT_DIR / "original/raw" / fn):
            if not l.strip(): continue
            r = json.loads(l)
            if r["id"] in keep and r.get("web_search_urls"):
                out.append(dict(run=key, model=model, id=r["id"], condition="ws_cutoff", dataset="ext", stored_urls=list(r["web_search_urls"]), judge={}))
    print(f"added {len(pick)} extension events, months {dict(collections.Counter(ev[i]['publication_date'][:7] for i in pick))}, {len(out)} model rows", file=sys.stderr)
    return out


def main():
    rows = [json.loads(l) for l in open(D / "verdicts.jsonl") if l.strip()]
    rows = [r for r in rows if r["condition"] == "ws_cutoff" and r["dataset"] == "orig"]
    ev = load_events()
    if ARGS.add_ext: rows += ext_rows(ARGS.add_ext, ev)
    jobs = collections.defaultdict(set)
    for r in rows:
        for u in r.get("stored_urls") or []:
            kind, ref = classify(u)
            if ref and not re.match(r"\d{4}-\d{2}", ref) and ref not in cache: jobs[ref.split(":")[0]].add(ref.split(":", 1)[1])
    print({k: len(v) for k, v in jobs.items()}, "lookups to do", file=sys.stderr)
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(cr_doi, sorted(jobs.get("doi", []))))
        list(ex.map(cr_pii, sorted(jobs.get("pii", []))))
    for db, k in (("pubmed", "pmid"), ("pmc", "pmc")):
        ids = sorted(jobs.get(k, []))
        if ids:
            for j, d in ncbi(db, ids).items(): cache[f"{k}:{j}"] = d
    json.dump(cache, open(CACHE, "w"))
    # ---- per case: documents dated, leaking
    per = []
    for r in rows:
        ceil = RUNS[r["run"]][5][:7]; pre = not is_post(months(ev[r["id"]]["publication_date"]), months(ceil))
        n = nd = nl = 0; kinds = collections.Counter(); leak_kinds = collections.Counter(); lag = []
        for u in r.get("stored_urls") or []:
            n += 1; kind, ref = classify(u)
            d = ref if (ref and re.match(r"\d{4}-\d{2}$", ref)) else (cache.get(ref) if ref else None)
            if d is None: kinds["undated"] += 1; continue
            if d.endswith("~y"):   # year only: decidable unless same year as the ceiling
                y = int(d[:4]); cy = int(ceil[:4])
                if y == cy: kinds["undated"] += 1; continue
                leak = y > cy
            else: leak = months(d) >= months(ceil)
            nd += 1; kinds[kind] += 1
            if leak: nl += 1; leak_kinds[kind] += 1; lag.append(months(d[:7]) - months(ceil))
        per.append(dict(run=r["run"], model=r["model"], id=r["id"], ceiling=ceil, pre=pre, n_urls=n, n_dated=nd, n_leak=nl, kinds=dict(kinds), leak_kinds=dict(leak_kinds), lag=lag,
                        judge_included=(r["judge"].get("verdict") == "INCLUDED"), has_judge=bool(r["judge"]), dataset=r["dataset"]))
    # ---- tables
    import random
    def boot(xs, f, B=2000, seed=0):
        rng = random.Random(seed); vals = sorted(f([xs[rng.randrange(len(xs))] for _ in xs]) for _ in range(B)); return vals[int(.025 * B)], vals[int(.975 * B) - 1]
    def wilson(k, n, z=1.96):
        if n == 0: return (float("nan"),) * 2
        p = k / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** .5) / (1 + z * z / n); return c - h, c + h
    order = ["GPT-4o", "LLaMA 3.3 70B", "DeepSeek R1", "Claude S4.5", "GPT-5.4", "Claude Sonnet 5", "GPT-5.6 Sol"]
    res = {}; L = ["# Document-level leakage under WS+Cutoff (A4.2 supplement)", "",
        "Share of retrieved evidence first made public on or after the run's date ceiling, using the exact URL list each model received. "
        "Documents are dated from their identifiers (arXiv id, bioRxiv/medRxiv DOI, Crossref for DOIs / Nature / eLife / ScienceDirect and Cell PIIs, NCBI for PubMed / PMC), earliest public date. "
        "**Event leak rate** = events with at least one retrieved document dated on or after the ceiling. **Document leak rate** = share of dated documents on or after the ceiling (event-bootstrap CI). "
        + ("**Cutoff-month rule: an event published in the ceiling month counts as PRE-cutoff (post iff publication month > ceiling month).** " if CM_PRE else "") + (f"**Events: the original 500-event subset plus {ARGS.add_ext} extension-corpus events (Apr-Aug 2026; ids in `ext{ARGS.add_ext}_leakage_ids.txt`), using the stored WS+Cutoff URL lists of each model's original-design run on those events; DeepSeek R1 has original-subset events only. The judge column covers the original subset only.** " if ARGS.add_ext else "") + "URL dating cannot see snippet-level leaks (e.g. a 2022 ResearchGate page whose snippet carries a 2026 abstract); those are measured by the judge-based outcome leakage in `results.md`, repeated in the last column.", ""]
    for part, lab in ((True, "Pre-cutoff events"), (False, "Post-cutoff events"), (None, "All events")):
        L += [f"\n## {lab}\n", "| model | ceiling | events | URLs | dated | event leak rate [95% CI] | document leak rate [95% CI] | median lag of leaking docs (months) | outcome leak by judge (post-cutoff only) |", "|---|---|---|---|---|---|---|---|---|"]
        for m in order:
            sub = [p for p in per if p["model"] == m and (part is None or p["pre"] == part)]
            if not sub: continue
            ne = len(sub); ke = sum(p["n_leak"] > 0 for p in sub); nu = sum(p["n_urls"] for p in sub); nd = sum(p["n_dated"] for p in sub); nl = sum(p["n_leak"] for p in sub)
            elo, ehi = wilson(ke, ne); dl = nl / nd if nd else float("nan")
            dlo, dhi = boot([p for p in sub if p["n_dated"]], lambda xs: sum(p["n_leak"] for p in xs) / max(sum(p["n_dated"] for p in xs), 1)) if nd else (float("nan"),) * 2
            lags = sorted(x for p in sub for x in p["lag"]); med = lags[len(lags) // 2] if lags else None
            js = [p for p in sub if p["has_judge"]]
            jl = f"{sum(p['judge_included'] for p in js) / len(js):.1%} (n={len(js)})" if part is False and js else "—"
            res.setdefault(lab, {})[m] = dict(n_events_ext=sum(p["dataset"] == "ext" for p in sub), ceiling=sub[0]["ceiling"], n_events=ne, n_urls=nu, n_dated=nd, dated_share=nd / nu if nu else None, event_leak=ke / ne, event_leak_ci=[elo, ehi], doc_leak=dl, doc_leak_ci=[dlo, dhi], n_leak_docs=nl, median_lag=med)
            L.append(f"| {m} | {sub[0]['ceiling']} | {ne} | {nu} | {nd} ({nd / nu:.0%}) | {ke / ne:.1%} [{max(elo,0):.1%}, {ehi:.1%}] | {dl:.1%} [{dlo:.1%}, {dhi:.1%}] | {med if med is not None else '—'} | {jl} |")
    # source of leaking docs
    lk = collections.Counter(); dk = collections.Counter()
    for p in per:
        for k, v in p["leak_kinds"].items(): lk[k] += v
        for k, v in p["kinds"].items(): dk[k] += v
    L += ["\n## Which identifiers the dated and leaking documents come from (all models, all events)\n", "| identifier type | URLs | dated | leaking |", "|---|---|---|---|"]
    for k in ("arxiv", "b/medrxiv", "doi", "nature", "pii", "elife", "pubmed", "pmc", "undated"):
        L.append(f"| {k} | {dk.get(k, 0) + (0 if k == 'undated' else 0)} | {'—' if k == 'undated' else dk.get(k, 0)} | {lk.get(k, 0)} |")
    (D / f"leakage{SFX}.md").write_text("\n".join(L) + "\n"); json.dump(dict(per_model=res, leak_by_identifier=dict(lk), dated_by_identifier=dict(dk)), open(OUT / f"tables/A4_2_leakage{SFX}.json", "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__": main()
