"""a7_examples.py — Step 5: curated example boxes spanning the main failure modes.
Selection is programmatic from the coded data (stated rule per box), so the boxes are
reproducible and not hand-picked. Writes examples/boxes.md and examples/boxes.tex."""
from __future__ import annotations
import json, sys, collections, textwrap
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S

SEED = 31
# (box title, failure mode, selector) — selector gets (trace, labels dict) and returns a sort key or None
SPECS = [
 ("Round-year anchoring on the temporal task", "weak extrapolation",
  lambda t, L: (t["task"] == "date" and L.get("ROUND_ANCHOR") == 1 and (t.get("signed_error_months") or 0) >= 24) and -(t["signed_error_months"])),
 ("A derived rate of progress, still far too slow", "weak extrapolation",
  lambda t, L: (t["task"] == "date" and L.get("RATE_OF_PROGRESS") == 1 and (t.get("signed_error_months") or 0) >= 18) and -(t["signed_error_months"])),
 ("Recognising the underlying publication, and dating it correctly", "recognition rather than forecasting",
  lambda t, L: (t["task"] == "date" and L.get("PROVENANCE_INFERRED") == 1 and abs(t.get("signed_error_months") or 99) <= 1) and 0),
 ("Recognising the underlying publication, and answering Yes because of it", "recognition rather than forecasting",
  lambda t, L: (t["task"] == "binary" and L.get("PROVENANCE_INFERRED") == 1 and t.get("correct") is True) and 0),
 ("Absence of known work read as evidence the event did not occur", "missing knowledge",
  lambda t, L: (t["task"] == "binary" and L.get("ABSENCE_AS_EVIDENCE") == 1 and t.get("correct") is False) and 0),
 ("The same move, rewarded on the perturbed variant", "missing knowledge",
  lambda t, L: (t["task"] == "binary_perturbed" and L.get("ABSENCE_AS_EVIDENCE") == 1 and t.get("correct") is True) and 0),
 ("An admitted knowledge gap, followed by a committed answer", "uncertainty representation",
  lambda t, L: (t["task"] in ("binary", "binary_perturbed") and L.get("KNOWLEDGE_GAP_ADMITTED") == 1 and (L.get("HEDGING") or 0) <= 1) and 0),
 ("Field momentum standing in for a forecast", "weak extrapolation",
  lambda t, L: (t["task"] == "binary" and L.get("FIELD_MOMENTUM") == 1 and L.get("RATE_OF_PROGRESS") == 0 and t.get("correct") is False) and 0),
 ("Specific prior evidence cited, and the answer is right", "knowledge used well",
  lambda t, L: (t["task"] == "binary" and L.get("EVIDENCE_CITED") == 1 and t.get("correct") is True) and 0),
 ("Retrieved sources quoted, conclusion unchanged from the base run", "agent setup",
  lambda t, L: (t["condition"] == "ws_cutoff" and L.get("EVIDENCE_CITED") == 1 and t["task"] in ("binary", "binary_perturbed")) and 0),
 ("A justification arguing one way, an answer going the other", "faithfulness",
  None),
 ("A justification that only restates the question", "no reasoning offered",
  lambda t, L: (t["task"] == "date" and t["trace_words"] <= 30 and (t.get("signed_error_months") or 0) >= 12) and 0),
 ("Hedged to the point of no commitment", "uncertainty representation",
  lambda t, L: ((L.get("HEDGING") or 0) >= 2.5 and t["task"] in ("binary", "binary_perturbed")) and 0),
 ("Mechanistic multiple choice answered from recognition", "recognition rather than forecasting",
  lambda t, L: (t["task"] == "mcq" and L.get("PROVENANCE_INFERRED") == 1 and t.get("correct") is True) and 0),
]


def main():
    rows, _ = S.load_labels()
    L = collections.defaultdict(dict)
    for r in rows: L[r["trace_id"]][r["code"]] = r["label"]
    traces = {t["trace_id"]: t for t in C.iter_traces(lambda t: t["trace_id"] in L)}
    faith = {}
    fp = C.STUDY / "raw" / "haiku45_faith.jsonl"
    if fp.exists():
        for l in open(fp, encoding="utf-8"):
            d = json.loads(l)
            if not d.get("error") and d.get("predicted_answer"): faith[d["trace_id"]] = d
    rng = np.random.default_rng(SEED)
    picked, used = [], set()
    for title, mode, sel in SPECS:
        cands = []
        if sel is None:
            from a7_analyze_d import norm
            for tid, d in faith.items():
                t = traces.get(tid)
                if not t or tid in used: continue
                pj, pm = norm(d["predicted_answer"], t["task"]), norm(t.get("parsed_answer"), t["task"])
                if pj and pm and pj != pm and t.get("correct") is False:
                    cands.append((0, tid))
        else:
            for tid, t in traces.items():
                if tid in used or t["trace_words"] < 15 or t["trace_words"] > 120: continue
                try: k = sel(t, L[tid])
                except Exception: k = False
                if k is not False and k is not None: cands.append((k, tid))
        if not cands: continue
        cands.sort(key=lambda x: (x[0], x[1]))
        tid = cands[0][1] if cands[0][0] != 0 else cands[int(rng.integers(0, min(len(cands), 40)))][1]
        used.add(tid); picked.append((title, mode, traces[tid], L[tid], faith.get(tid)))
    md = ["# A7 curated examples\n",
          "Each box is selected programmatically from the coded data by the stated rule, not hand-picked, so the "
          "selection is reproducible (`scripts/a7_examples.py`, seed 31). Codes shown are the consensus labels of "
          "the two blind coders. Model identity is given here because these boxes are for the reader, not the coder.\n"]
    tex = []
    for i, (title, mode, t, lab, f) in enumerate(picked, 1):
        codes = ", ".join(c for c, v in sorted(lab.items()) if c != "HEDGING" and v == 1) or "none"
        hed = lab.get("HEDGING")
        q = " ".join(t["question"].split())
        q = q[:400] + (" ..." if len(q) > 400 else "")
        tr = " ".join(t["trace"].split())
        ans = t.get("parsed_answer"); gt = t.get("ground_truth")
        extra = ""
        if t["task"] == "date" and t.get("signed_error_months") is not None:
            extra = f"  Signed error: {t['signed_error_months']:+d} months."
        if t["task"] == "frq" and t.get("frq_score") is not None:
            extra = f"  Rubric score: {t['frq_score']:.1f} / 10."
        if f: extra += f"  Judge read the justification as arguing: {f['predicted_answer']}."
        md += [f"\n## Box {i}. {title}\n", f"*Failure mode: {mode}.* {t['model']}, {t['task']} task, {t['condition']} condition, "
               f"event published {t['publication_date']} ({t['partition']}-cutoff for this model).\n",
               f"**Question.** {q}\n", f"**Stated justification.** “{tr}”\n",
               f"**Answer given.** {ans}   **Ground truth.** {gt}.{extra}\n",
               f"**Codes.** {codes}. Hedging level {hed:.1f}." if hed is not None else f"**Codes.** {codes}.\n"]
        tex.append("\\begin{tcolorbox}[title={Box %d. %s}]\n\\textbf{Model:} %s, %s task.\\\\\n\\textbf{Question:} %s\\\\\n"
                   "\\textbf{Stated justification:} ``%s''\\\\\n\\textbf{Answer:} %s \\quad \\textbf{Ground truth:} %s\\\\\n"
                   "\\textbf{Codes:} %s\n\\end{tcolorbox}" % (i, title.replace("&", "\\&"), t["model"], t["task"],
                   q.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_"),
                   tr.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_"), ans, gt, codes))
    (C.STUDY / "examples" / "boxes.md").write_text("\n".join(md) + "\n")
    (C.STUDY / "examples" / "boxes.tex").write_text("\n\n".join(tex) + "\n")
    print(f"{len(picked)} example boxes written")


if __name__ == "__main__":
    main()
