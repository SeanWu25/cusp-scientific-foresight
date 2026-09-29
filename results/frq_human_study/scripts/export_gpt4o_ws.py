#!/usr/bin/env python3
"""
export_gpt4o_ws.py -- GPT-4o FRQ answers + rubric evaluations under web search,
in the same shape as export_frq.py, for the human study.

Conditions (all POST-CUTOFF by construction: GPT-4o's cutoff is 2023-10 and the
corpus starts 2024-01, so every event postdates it):

  base        no retrieval (the published base run)
  ws_cutoff   You.com pipeline, one model-written query, date ceiling 2023-10
  ws          unrestricted, OpenAI Responses API native web_search tool

A fourth and fifth condition exist (study A4.3 fixed queries, written by a model
outside the panel) and their ANSWERS are exported too -- but they were never FRQ
graded, so they carry no scores. They are kept in ungraded_fixed_query/.

Read-only.
"""
from __future__ import annotations
import argparse, csv, json, os, re, subprocess, sys
from collections import defaultdict

REPO = "/home/seanwu/FutureScience"
BK = f"/home/seanwu/FutureScience_backup_20260508_013823/benchmark_logs/model_outputs"
FR = f"{REPO}/run_evaluation/frq_results"
A43 = f"{REPO}/results/A4_retrieval/A4_3_fixed_queries/reports"
ORIG = f"{REPO}/archive/data/canonical/merged_validated_cusp_fixed.jsonl"

DIMS = ["alignment", "specificity", "novelty", "feasibility"]
_TRAIL = re.compile(r"[\s*_`#>\-•]+$")


def looks_truncated(a):
    if not a:
        return None
    s = _TRAIL.sub("", a.strip())
    return True if not s else s[-1] not in ".!?\"')]}’”"


# condition -> (raw answers, report with rubric scores)
CONDS = [
    ("base",      f"{BK}/predictions_gpt-4o.jsonl",            f"{FR}/gpt_4o_reeval.json"),
    ("ws_cutoff", f"{BK}/gpt_4o_web_search.jsonl",             f"{FR}/gpt-4o_web_search_with_cutoff.json"),
    ("ws",        f"{BK}/gpt_4o_web_search_no_cutoff.jsonl",   f"{FR}/gpt_4o_web_search_no_cutoff_500.json"),
]
UNGRADED = [
    ("fixed_ws_cutoff", f"{A43}/pred_gpt4o_fixed_ws_cutoff.jsonl"),
    ("fixed_ws",        f"{A43}/pred_gpt4o_fixed_ws.jsonl"),
]


def load_events():
    ev = {}
    for line in open(ORIG, encoding="utf-8"):
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("frq_prompt"):
            ev[d["id"]] = dict(event_id=d["id"],
                               publication_date=str(d.get("publication_date", ""))[:7],
                               main_area=d.get("main_area"), source=d.get("source"),
                               paper_link=d.get("paper_link"),
                               frq_prompt=d.get("frq_prompt"),
                               problem_statement=d.get("problem_statement"),
                               technical_approach=d.get("technical_approach"),
                               results_and_metrics=d.get("results_and_metrics"))
    return ev


def load_answers(path):
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        a = r.get("frq_answer")
        if not a:
            continue
        urls = r.get("web_search_urls") or r.get("frq_web_search_urls") or []
        if urls and isinstance(urls[0], dict):
            urls = [u.get("url") for u in urls if u.get("url")]
        q = r.get("web_search_query")
        if q is None:
            qq = r.get("frq_web_search_queries")
            q = "; ".join(qq) if isinstance(qq, list) else qq
        out[r["id"]] = dict(
            frq_answer=a, answer_chars=len(a),
            truncated=bool(r["frq_truncated"]) if "frq_truncated" in r else None,
            looks_truncated=looks_truncated(a),
            refused=bool(r["frq_refusal"]) if "frq_refusal" in r else None,
            stop_reason=r.get("frq_stop_reason"),
            search_query=q, retrieved_urls=urls, n_retrieved=len(urls),
        )
    return out


def load_scores(path):
    out = {}
    if not os.path.exists(path):
        return out
    for x in json.load(open(path, encoding="utf-8")).get("results", []):
        t = (x.get("tasks") or {}).get("frq")
        if not t or t.get("skipped") or t.get("score") is None:
            continue
        out[x["id"]] = dict(frq_score=float(t["score"]),
                            **{d: (float(t[d]) if t.get(d) is not None else None)
                               for d in DIMS},
                            judge_rationale=t.get("rationale") or t.get("frq_rationale"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"{REPO}/results/frq_human_study/export_gpt4o_ws")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(f"{a.out}/ungraded_fixed_query", exist_ok=True)

    ev = load_events()
    rows, per_cond = [], {}
    for cond, raw, rep in CONDS:
        ans, sc = load_answers(raw), load_scores(rep)
        crows = []
        for eid, s in sc.items():
            if eid not in ev or eid not in ans:
                continue
            e = ev[eid]
            r = dict(model="GPT-4o", model_cutoff="2023-10", condition=cond,
                     event_id=eid, corpus="original",
                     publication_date=e["publication_date"], partition="post",
                     main_area=e["main_area"], source=e["source"],
                     paper_link=e["paper_link"], frq_prompt=e["frq_prompt"])
            r.update(ans[eid]); r.update(s)
            r["truncated_any"] = (r["truncated"] if r["truncated"] is not None
                                  else r["looks_truncated"])
            crows.append(r)
        per_cond[cond] = crows
        rows += crows
        print(f"  {cond:10s} answers {len(ans):5,}  scored {len(sc):5,}  joined {len(crows):5,}")

    # paired view: events answered in every graded condition
    shared = set.intersection(*[{r["event_id"] for r in v} for v in per_cond.values()])
    print(f"  events present in all three graded conditions: {len(shared):,}")

    cols = ["model", "model_cutoff", "condition", "event_id", "corpus",
            "publication_date", "partition", "main_area", "source", "paper_link",
            "frq_prompt", "frq_answer", "answer_chars", "truncated",
            "looks_truncated", "truncated_any", "refused", "stop_reason",
            "search_query", "n_retrieved", "frq_score"] + DIMS + ["judge_rationale"]

    def dump(path, rr):
        with open(path + ".jsonl", "w", encoding="utf-8") as fh:
            for r in rr:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(path + ".csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rr:
                w.writerow(r)

    dump(f"{a.out}/gpt4o_frq_all_conditions", rows)
    dump(f"{a.out}/gpt4o_frq_paired", [r for r in rows if r["event_id"] in shared])
    for cond, v in per_cond.items():
        dump(f"{a.out}/gpt4o_frq_{cond}", v)

    # retrieved URLs, separate (long lists bloat the CSV)
    with open(f"{a.out}/retrieved_urls.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            if r.get("retrieved_urls"):
                fh.write(json.dumps(dict(condition=r["condition"],
                                         event_id=r["event_id"],
                                         search_query=r["search_query"],
                                         retrieved_urls=r["retrieved_urls"]),
                                    ensure_ascii=False) + "\n")

    # ungraded fixed-query answers
    ung = 0
    for cond, raw in UNGRADED:
        ans = load_answers(raw)
        with open(f"{a.out}/ungraded_fixed_query/gpt4o_{cond}.jsonl", "w",
                  encoding="utf-8") as fh:
            for eid, v in ans.items():
                if eid not in ev:
                    continue
                fh.write(json.dumps(dict(model="GPT-4o", condition=cond, event_id=eid,
                                         frq_prompt=ev[eid]["frq_prompt"], **v,
                                         frq_score=None, judge_rationale=None),
                                    ensure_ascii=False) + "\n")
                ung += 1
        print(f"  {cond:16s} answers {len(ans):5,}  (NOT graded)")

    with open(f"{a.out}/events.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["event_id", "publication_date", "main_area",
                                           "source", "paper_link", "frq_prompt",
                                           "problem_statement", "technical_approach",
                                           "results_and_metrics"])
        w.writeheader()
        for eid in sorted({r["event_id"] for r in rows}):
            w.writerow(ev[eid])

    json.dump(dict(
        generated=subprocess.run(["date", "-Is"], capture_output=True,
                                 text=True).stdout.strip(),
        git_sha=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                               text=True, cwd=REPO).stdout.strip(),
        model="GPT-4o", cutoff="2023-10",
        partition="post (all events postdate this model's cutoff by construction)",
        graded_conditions={c: len(v) for c, v in per_cond.items()},
        events_in_all_graded=len(shared), ungraded_rows=ung,
        rubric="published judge_frq_combined; 4 dimensions 0-10, score = their mean",
        sources={c: dict(answers=r, report=p) for c, r, p in CONDS},
        ungraded_sources={c: r for c, r in UNGRADED},
    ), open(f"{a.out}/MANIFEST.json", "w"), indent=2)
    print(f"\ntotal graded rows {len(rows):,}  ->  {a.out}")


if __name__ == "__main__":
    main()
