#!/usr/bin/env python3
"""
export_frq.py -- export every FRQ response and its rubric evaluation, for the
human study.

Read-only: reads stored predictions (answer text) and finalized reports (rubric
scores + judge rationale), joins them by event id, writes a self-contained
export. Nothing in the repo is modified.

Per model x event we emit the model's free-response answer, the four published
rubric dimensions, the overall score, the judge's written rationale, and the
generation flags a human rater needs to know about (truncation, refusal).
"""
from __future__ import annotations
import argparse, csv, json, os, random, sys, hashlib
import re
from collections import defaultdict

# Truncation: the newer runs record frq_truncated, the 2026-04 runs do not.
# This heuristic (trailing markdown stripped, then a terminal-punctuation test)
# scores precision 1.000 / recall 0.962 / accuracy 0.984 against the 21,826 rows
# that DO carry the recorded flag, so it is used to fill the gap.
_TRAIL = re.compile(r"[\s*_`#>\-\u2022]+$")


def looks_truncated(a):
    if not a:
        return None
    s = _TRAIL.sub("", a.strip())
    if not s:
        return True
    return s[-1] not in ".!?\"')]}\u2019\u201d"

REPO = "/home/seanwu/FutureScience"
BK = "/home/seanwu/FutureScience_backup_20260508_013823/benchmark_logs/model_outputs"
EXT_RAW = f"{REPO}/results_extension_run2/raw"
FR = f"{REPO}/run_evaluation/frq_results"

ORIG = f"{REPO}/archive/data/canonical/merged_validated_cusp_fixed.jsonl"
EXTB = f"{REPO}/benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"

# display name -> cutoff, (answers, report) for each corpus half
PANEL = [
 ("GPT-4o", "2023-10",
  f"{BK}/predictions_gpt-4o.jsonl",                       f"{FR}/gpt_4o_reeval.json",
  f"{EXT_RAW}/gpt4o_base.jsonl",   f"{REPO}/results_extension_run2/reports/gpt4o_base.json"),
 ("LLaMA 3.3 70B", "2023-12",
  f"{BK}/llama-3.3-70b-full.jsonl.jsonl",                 f"{FR}/llama_3_3_full.json",
  f"{EXT_RAW}/llama33_base.jsonl", f"{REPO}/results_extension_run2/reports/llama33_base.json"),
 ("GPT-OSS 20B", "2024-06",
  f"{BK}/gpt-oss-20b-full.jsonl",                         f"{FR}/gpt_oss_20B_reeval.json",
  f"{EXT_RAW}/gptoss20b_base.jsonl", f"{REPO}/results_extension_run2/reports/gptoss20b_base.json"),
 ("DeepSeek-R1", "2024-07",
  f"{BK}/predictions_DeepSeek-R1.jsonl",                  f"{FR}/deepseek_r1.json",
  None, None),
 ("Claude S4.5", "2025-01",
  f"{BK}/predictions_claude-sonnet-4-5_20260428_092848.jsonl", f"{FR}/claude_sonnet.json",
  f"{EXT_RAW}/sonnet45_base.jsonl", f"{REPO}/results_extension_run2/reports/sonnet45_base.json"),
 ("GPT-5.4", "2025-08",
  f"{BK}/predictions_gpt-5.4.jsonl",                      f"{FR}/gpt_5_4_eval.json",
  f"{EXT_RAW}/gpt54_base.jsonl",   f"{REPO}/results_extension_run2/reports/gpt54_base.json"),
 ("Claude Sonnet 5", "2026-01",
  f"{REPO}/results_sonnet5_run1/raw/base_medium_run1.jsonl",
  f"{REPO}/results_sonnet5_run1/reports/base_medium_run1.json",
  f"{EXT_RAW}/sonnet5_base_run1.jsonl", f"{REPO}/results_extension_run2/reports/sonnet5_base_run1.json"),
 ("GPT-5.6 Sol", "2026-02",
  f"{REPO}/results_sol_run1/raw/base_medium_run1.jsonl",
  f"{REPO}/results_sol_run1/reports/base_medium_run1.json",
  f"{EXT_RAW}/sol_base.jsonl",     f"{REPO}/results_extension_run2/reports/sol_base.json"),
 ("DeepSeek-V4-Pro", "2026-04",
  f"{REPO}/results_dsv4pro_run1/raw/base_run1.jsonl",
  f"{REPO}/results_dsv4pro_run1/reports/base_run1.json",
  f"{EXT_RAW}/deepseekv4pro_base.jsonl", f"{REPO}/results_extension_run2/reports/deepseekv4pro_base.json"),
 ("Claude Opus 4.8", "2026-01",
  f"{REPO}/results_opus48_run1/raw/base_medium_run1.jsonl",
  f"{REPO}/results_opus48_run1/reports/base_medium_run1.json",
  f"{EXT_RAW}/opus48_base_run1.jsonl", f"{REPO}/results_extension_run2/reports/opus48_base_run1.json"),
]

DIMS = ["alignment", "specificity", "novelty", "feasibility"]


def mo(s):
    try:
        y, m = str(s).split("-")[:2]
        return int(y) * 12 + int(m)
    except Exception:
        return None


def load_events():
    ev = {}
    for corpus, path in (("original", ORIG), ("extension", EXTB)):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            d = json.loads(line)
            if not d.get("frq_prompt"):
                continue
            ev[d["id"]] = dict(
                event_id=d["id"], corpus=corpus,
                publication_date=str(d.get("publication_date", ""))[:7],
                main_area=d.get("main_area"), source=d.get("source"),
                paper_link=d.get("paper_link"),
                frq_prompt=d.get("frq_prompt"),
                problem_statement=d.get("problem_statement"),
                technical_approach=d.get("technical_approach"),
                results_and_metrics=d.get("results_and_metrics"),
            )
    return ev


def load_answers(path):
    """event id -> dict(answer, truncated, refused, stop_reason)."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        a = r.get("frq_answer")
        if a is None:
            continue
        out[r["id"]] = dict(
            frq_answer=a,
            truncated=bool(r.get("frq_truncated")) if "frq_truncated" in r else None,
            refused=bool(r.get("frq_refusal")) if "frq_refusal" in r else None,
            stop_reason=r.get("frq_stop_reason"),
            answer_chars=len(a),
            looks_truncated=looks_truncated(a),
        )
    return out


def load_scores(path):
    """event id -> dict(score, dims..., rationale)."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    for x in json.load(open(path, encoding="utf-8")).get("results", []):
        t = (x.get("tasks") or {}).get("frq")
        if not t or t.get("skipped") or t.get("score") is None:
            continue
        out[x["id"]] = dict(
            frq_score=float(t["score"]),
            **{d: (float(t[d]) if t.get(d) is not None else None) for d in DIMS},
            judge_rationale=t.get("rationale") or t.get("frq_rationale"),
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=f"{REPO}/results/frq_human_study/export")
    ap.add_argument("--sample", type=int, default=300,
                    help="size of the balanced convenience sample (0 to skip)")
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--partition", choices=["post", "pre", "all"], default="post",
                    help="which side of each model's knowledge cutoff to export "
                         "(default: post -- the forecasting condition)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(f"{a.out}/by_model", exist_ok=True)

    ev = load_events()
    print(f"events with an FRQ prompt: {len(ev):,}")

    rows, per_model = [], {}
    for name, cutoff, o_ans, o_rep, e_ans, e_rep in PANEL:
        ans = {}
        ans.update(load_answers(o_ans))
        ans.update(load_answers(e_ans))
        sc = {}
        sc.update(load_scores(o_rep))
        sc.update(load_scores(e_rep))
        mrows = []
        for eid, s in sc.items():
            if eid not in ev:
                continue
            e = ev[eid]
            pm, cm = mo(e["publication_date"]), mo(cutoff)
            r = dict(model=name, model_cutoff=cutoff, event_id=eid,
                     corpus=e["corpus"], publication_date=e["publication_date"],
                     partition=("post" if (pm is not None and cm is not None and pm >= cm)
                                else "pre"),
                     main_area=e["main_area"], source=e["source"],
                     paper_link=e["paper_link"], frq_prompt=e["frq_prompt"])
            r.update(ans.get(eid, dict(frq_answer=None, truncated=None, refused=None,
                                       stop_reason=None, answer_chars=None,
                                       looks_truncated=None)))
            r["truncated_any"] = (r["truncated"] if r["truncated"] is not None
                                  else r["looks_truncated"])
            if a.partition != "all" and r["partition"] != a.partition:
                continue
            r.update(s)
            mrows.append(r)
        per_model[name] = mrows
        rows += mrows
        n_ans = sum(1 for r in mrows if r["frq_answer"])
        print(f"  {name:18s} {a.partition}-cutoff {len(mrows):5,}   with answer text {n_ans:5,}"
              f"   {'(answers missing!)' if n_ans < len(mrows) else ''}")
        with open(f"{a.out}/by_model/frq_{name.replace(' ', '_').replace('.', '')}.jsonl",
                  "w", encoding="utf-8") as fh:
            for r in mrows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # combined jsonl
    with open(f"{a.out}/frq_responses.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # combined csv (proper quoting handles newlines inside the text fields)
    cols = ["model", "model_cutoff", "event_id", "corpus", "publication_date", "partition",
            "main_area", "source", "paper_link", "frq_prompt", "frq_answer",
            "answer_chars", "truncated", "looks_truncated", "truncated_any",
            "refused", "stop_reason",
            "frq_score"] + DIMS + ["judge_rationale"]
    with open(f"{a.out}/frq_responses.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # events table (prompts once, not repeated per model)
    with open(f"{a.out}/events.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["event_id", "corpus", "publication_date",
                                           "main_area", "source", "paper_link",
                                           "frq_prompt", "problem_statement",
                                           "technical_approach", "results_and_metrics"])
        w.writeheader()
        used = {r["event_id"] for r in rows}
        for eid in sorted(used):
            w.writerow(ev[eid])

    # balanced convenience sample: equal per model, spread over the score range
    if a.sample:
        rng = random.Random(a.seed)
        per = max(1, a.sample // len(per_model))
        samp = []
        for name, mrows in per_model.items():
            ok = [r for r in mrows if r["frq_answer"] and not r["refused"]]
            buckets = defaultdict(list)
            for r in ok:
                buckets[min(9, int(r["frq_score"]))].append(r)
            picks, keys = [], sorted(buckets)
            i = 0
            while len(picks) < min(per, len(ok)) and keys:
                k = keys[i % len(keys)]
                if buckets[k]:
                    picks.append(buckets[k].pop(rng.randrange(len(buckets[k]))))
                else:
                    keys.remove(k)
                    continue
                i += 1
            samp += picks
        rng.shuffle(samp)
        with open(f"{a.out}/sample_balanced.jsonl", "w", encoding="utf-8") as fh:
            for r in samp:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        # blind rating sheet: no model name, no scores
        with open(f"{a.out}/sample_blind_rating_sheet.csv", "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["rating_id", "event_id", "main_area", "frq_prompt", "frq_answer",
                        "alignment_1_10", "specificity_1_10", "novelty_1_10",
                        "feasibility_1_10", "rater_notes"])
            for i, r in enumerate(samp, 1):
                w.writerow([f"R{i:04d}", r["event_id"], r["main_area"],
                            r["frq_prompt"], r["frq_answer"], "", "", "", "", ""])
        with open(f"{a.out}/sample_blind_key.csv", "w", newline="",
                  encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["rating_id", "event_id", "model", "frq_score"] + DIMS)
            for i, r in enumerate(samp, 1):
                w.writerow([f"R{i:04d}", r["event_id"], r["model"], r["frq_score"]]
                           + [r[d] for d in DIMS])
        print(f"  balanced sample: {len(samp)} rows "
              f"({per} per model, spread across the score range)")

    man = dict(
        generated=__import__("subprocess").run(["date", "-Is"], capture_output=True,
                                               text=True).stdout.strip(),
        git_sha=__import__("subprocess").run(["git", "rev-parse", "HEAD"],
                                             capture_output=True, text=True,
                                             cwd=REPO).stdout.strip(),
        partition=a.partition,
        n_rows=len(rows), n_events=len({r["event_id"] for r in rows}),
        n_models=len(per_model), seed=a.seed, sample_size=a.sample,
        rubric="published judge_frq_combined; 4 dimensions 0-10, score = their mean; pass >= 5.0",
        per_model={k: len(v) for k, v in per_model.items()},
        sources={n: dict(orig_answers=o, orig_report=orep, ext_answers=e, ext_report=erep)
                 for n, c, o, orep, e, erep in PANEL},
    )
    json.dump(man, open(f"{a.out}/MANIFEST.json", "w"), indent=2)
    print(f"\nrows {len(rows):,}  events {man['n_events']:,}  models {man['n_models']}")
    print("->", a.out)


if __name__ == "__main__":
    main()
