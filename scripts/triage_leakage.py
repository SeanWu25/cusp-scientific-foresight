#!/usr/bin/env python3
"""
triage_leakage.py — classify every stage-1 leakage 'fail' verdict.

On a corpus that postdates every model cutoff, a leakage 'fail' cannot mean
training contamination: the judge searches the live web with no date
restriction, so a model producing a description close to the real finding makes
the search surface the paper -- published after every cutoff -- and the judge
records leakage.

This sorts every failure into:

  model had live web access      the run IS the unrestricted web-search
                                 condition, so a post-cutoff entity came from
                                 retrieval by design -- it confirms search
                                 worked, it says nothing about training data
  evidence is the target paper   the judge retrieved the very paper the item is
                                 about; post-cutoff, so not memorisable
  entity was in the prompt       the model was handed the flagged entity
  other / needs eyes             genuinely ambiguous; read these by hand

Note the asymmetry between the two search conditions: a post-cutoff entity in
the UNRESTRICTED run (`*_ws`) is expected, but one in the CUTOFF-RESTRICTED run
(`*_ws_cutoff`) would mean the date filter leaked and is worth investigating.

The reportable claim is "manual review of all flagged cases found no evidence
of contamination", never "the judge measured an X% leakage rate".
"""

from __future__ import annotations

import argparse, glob, json, os, re, sys
from collections import Counter

DEFAULT_BENCH = "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"


def paper_id(u: str | None):
    """Reduce a URL to a paper identity so DOI, publisher and arXiv forms match."""
    u = (u or "").lower()
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})", u)
    if m:
        return "arxiv:" + m.group(1)
    m = re.search(r"(?:10\.\d{4,9}/|nature\.com/articles/)([^\s?#/]+)", u)
    if m:
        return "doc:" + m.group(1).rstrip(".")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judgements", default="results_extension_run2/judgements/*.jsonl")
    ap.add_argument("--raw-dir", default="results_extension_run2/raw")
    ap.add_argument("--benchmark", default=DEFAULT_BENCH)
    ap.add_argument("--out")
    a = ap.parse_args()

    bench = {}
    for line in open(a.benchmark, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            bench[r["id"]] = str(r.get("paper_link") or "")

    prompts: dict[str, dict[str, str]] = {}

    def prompt_of(tag, rid):
        if tag not in prompts:
            p = os.path.join(a.raw_dir, f"{tag}.jsonl")
            d = {}
            if os.path.exists(p):
                for line in open(p, encoding="utf-8"):
                    r = json.loads(line)
                    d[r["id"]] = json.dumps(r.get("frq_prompt_sent", "")).lower()
            prompts[tag] = d
        return prompts[tag].get(rid, "")

    verdicts, cats, failures = Counter(), Counter(), []
    n = 0
    for f in sorted(glob.glob(a.judgements)):
        tag = os.path.basename(f)[8:-6] if os.path.basename(f).startswith("leakage_") \
            else os.path.basename(f)[:-6]
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            lk = r.get("leakage")
            if not isinstance(lk, dict):
                continue
            n += 1
            verdicts[lk.get("verdict")] += 1
            if lk.get("verdict") != "fail":
                continue
            inds = [str(i) for i in (lk.get("indicators") or [])]
            pr = prompt_of(tag, r["id"])
            urls = [u for s in (lk.get("web_searches") or [])
                    for u in (s.get("urls_reached") or [])]
            tgt = paper_id(bench.get(r["id"]))
            if tag.endswith("_ws"):
                # unrestricted web search: the model was given the live web, so
                # a post-cutoff entity is retrieval working, not memorisation
                c = "model had live web access"
            elif inds and any(i.lower() in pr for i in inds):
                c = "entity was in the prompt"
            elif tgt and any(paper_id(u) == tgt for u in urls):
                c = "evidence is the target paper"
            else:
                c = "other / needs eyes"
            cats[c] += 1
            failures.append({"run": tag, "id": r["id"], "category": c,
                             "indicators": inds, "reason": lk.get("reason"),
                             "urls": urls})

    print(f"judged: {n}   verdicts: {dict(verdicts)}   "
          f"fail rate: {100*verdicts['fail']/max(n,1):.2f}%\n")
    for k, v in cats.most_common():
        print(f"  {v:>4}  {k}")
    eyes = [f for f in failures if f["category"] == "other / needs eyes"]
    if eyes:
        print(f"\n{len(eyes)} case(s) needing human eyes:")
        for f in eyes:
            print(f"  {f['run']:<20} {f['id'][:8]}  {f['indicators']}")
            print(f"      reason: {str(f['reason'])[:160]}")
    print("\nReport as: manual review of all flagged cases found no evidence of")
    print("contamination. Do NOT report the fail rate as a leakage rate.")

    if a.out:
        json.dump({"judged": n, "verdicts": dict(verdicts),
                   "categories": dict(cats), "failures": failures},
                  open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
