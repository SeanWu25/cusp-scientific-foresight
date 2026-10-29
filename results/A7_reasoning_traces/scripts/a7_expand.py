"""a7_expand.py — coded_traces.jsonl: one record per trace per code per coder, with the
verbatim justification span. Built from raw/<coder>.jsonl; no API calls."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P

CODERS = ["haiku45", "gpt54mini_low"]
meta = {r["trace_id"]: r for r in C.iter_traces(lambda r: True)}
n = 0
with open(C.STUDY / "coded_traces.jsonl", "w", encoding="utf-8") as out:
    for coder in CODERS:
        p = C.STUDY / "raw" / f"{coder}.jsonl"
        if not p.exists():
            continue
        seen = set()
        for l in open(p, encoding="utf-8"):
            if not l.strip():
                continue
            d = json.loads(l)
            if d.get("error") or "codes" not in d or d["trace_id"] in seen:
                continue
            seen.add(d["trace_id"])
            t = meta[d["trace_id"]]
            for code, v in d["codes"].items():
                out.write(json.dumps(dict(
                    trace_id=d["trace_id"], coder=coder, coder_model=d.get("coder_model"), code=code,
                    verdict=v["verdict"], span=v["span"], span_verbatim=v["span_verbatim"],
                    model=t["model"], condition=t["condition"], half=t["half"], task=t["task"],
                    id=t["id"], partition=t["partition"], correct=t.get("correct"),
                    score=t.get("score"), frq_score=t.get("frq_score"),
                    month_distance=t.get("month_distance"), signed_error_months=t.get("signed_error_months"),
                    trace_words=t["trace_words"], parse_problems=d.get("problems")), ensure_ascii=False) + "\n")
                n += 1
print(f"wrote {n:,} coded records to {C.STUDY / 'coded_traces.jsonl'}")
