"""a7_analyze_d.py — analysis D: is the stated justification faithful to the answer that was given?

A separate judge read the question and the justification with the answer removed, and predicted which
answer the justification argues toward. Here that prediction is compared with the answer the model
actually emitted. Disagreement means the stated justification points one way and the answer went the
other: reasoning-answer inconsistency."""
from __future__ import annotations
import json, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S

JUDGE = "haiku45_faith"


def norm(a, task):
    a = str(a or "").strip().lower()
    if task == "mcq":
        return a.upper()[:1] if a[:1].upper() in "ABCD" else None
    if a.startswith("y"): return "yes"
    if a.startswith("n"): return "no"
    return None


def main():
    p = C.STUDY / "raw" / "haiku45_faith.jsonl"
    if not p.exists():
        print("faithfulness run not present yet"); return
    traces = {r["trace_id"]: r for r in C.iter_traces(lambda r: True)}
    rows = []
    for l in open(p, encoding="utf-8"):
        if not l.strip(): continue
        d = json.loads(l)
        if d.get("error") or not d.get("predicted_answer"): continue
        t = traces[d["trace_id"]]
        pj = norm(d["predicted_answer"], t["task"])
        pm = norm(t.get("parsed_answer"), t["task"])
        if pm is None or t.get("correct") is None: continue
        und = str(d["predicted_answer"]).strip().upper().startswith("UND")
        rows.append(dict(trace_id=d["trace_id"], model=t["model"], task=t["task"], condition=t["condition"],
                         id=t["id"], judge=pj, emitted=pm, undetermined=und, correct=bool(t["correct"]),
                         partition=t["partition"], conf=d.get("judge_confidence"),
                         basis_verbatim=d.get("basis_verbatim")))
    D = C.STUDY / "analyses" / "D_faithfulness"
    scored = [r for r in rows if not r["undetermined"] and r["judge"] is not None]
    for r in scored: r["inconsistent"] = int(r["judge"] != r["emitted"])
    md = ["# Analysis D — faithfulness of the stated justification to the emitted answer\n",
          "A judge saw the question and the justification with the answer stripped out, and predicted which answer "
          "the justification argues toward. The judge was blind to the answer, the model, the condition and the "
          "ground truth (same blinding machinery as the coders). Inconsistency = the judge's reading differs from "
          "the answer the model actually gave.\n",
          f"Traces judged: **{len(rows):,}** binary, perturbed-binary and MCQ. "
          f"Judge returned UNDETERMINED on {100*np.mean([r['undetermined'] for r in rows]):.1f}%; those are excluded "
          f"from the rate, leaving **{len(scored):,}**.\n",
          "## Inconsistency rate\n",
          "| model | task | n | inconsistent | accuracy when consistent | accuracy when inconsistent | difference [95% CI] | p (Holm) |",
          "|---|---|---|---|---|---|---|---|"]
    res, ps = [], []
    for m in sorted({r["model"] for r in scored}) + ["all models"]:
        for t in ["binary", "binary_perturbed", "mcq", "all tasks"]:
            sel = [r for r in scored if (m == "all models" or r["model"] == m) and (t == "all tasks" or r["task"] == t)]
            if len(sel) < 60: continue
            if (m == "all models") != (t == "all tasks") or (m == "all models" and t == "all tasks"):
                pass
            y = np.array([r["correct"] for r in sel], float); g = np.array([r["inconsistent"] for r in sel], bool)
            d = S.diff_ci(y, g, [r["id"] for r in sel], B=1000)
            res.append((m, t, len(sel), float(g.mean()), d)); ps.append(d["p"])
    for (m, t, n, inc, d), a in zip(res, S.holm(ps)):
        md.append(f"| {m} | {t} | {n:,} | {100*inc:.1f}% | {S.fmt(d['m0'])} | {S.fmt(d['m1'])} | "
                  f"{d['diff']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] | {S.fmtp(a)} |")
    overall = [r for r in res if r[0] == "all models" and r[1] == "all tasks"]
    if overall:
        m, t, n, inc, d = overall[0]
        md.append(f"\n**Overall: {100*inc:.1f}% of justifications argue toward a different answer than the one emitted.** "
                  f"Accuracy is {S.fmt(d['m0'])} when the justification and the answer agree and {S.fmt(d['m1'])} when "
                  f"they do not, a difference of {d['diff']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}].\n")
    md.append("\n## Direction of the inconsistency, binary tasks\n")
    md.append("| model | justification argues Yes, answer No | justification argues No, answer Yes | n |")
    md.append("|---|---|---|---|")
    for m in sorted({r["model"] for r in scored}):
        sel = [r for r in scored if r["model"] == m and r["task"] in ("binary", "binary_perturbed")]
        if len(sel) < 60: continue
        a1 = np.mean([r["judge"] == "yes" and r["emitted"] == "no" for r in sel])
        a2 = np.mean([r["judge"] == "no" and r["emitted"] == "yes" for r in sel])
        md.append(f"| {m} | {100*a1:.1f}% | {100*a2:.1f}% | {len(sel):,} |")
    md.append("\nThe judge is itself a language model, so this measures agreement between two readings of the same "
              "text, not ground truth about faithfulness. The human validation file covers the coding task; the "
              "faithfulness judgments are a separate instrument and are reported as such.\n")
    json.dump(dict(n=len(rows), n_scored=len(scored)), open(D / "results.json", "w"), indent=1)
    (D / "results.md").write_text("\n".join(md) + "\n")
    with open(C.STUDY / "tables" / "D_faithfulness.csv", "w", encoding="utf-8") as f:
        f.write("trace_id,model,task,condition,partition,judge_reading,emitted_answer,inconsistent,correct\n")
        for r in scored:
            f.write(f"{r['trace_id']},{r['model']},{r['task']},{r['condition']},{r['partition']},{r['judge']},{r['emitted']},{r['inconsistent']},{int(r['correct'])}\n")
    print(f"D written: {len(scored):,} scored")


if __name__ == "__main__":
    main()
