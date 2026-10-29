"""a7_build_traces.py — the master trace table: one record per (model, condition, half, task, event),
joining the stored raw prediction (question as shown, in-answer reasoning, answer, confidence) with the
stored graded report (correct / score / month distance / FRQ rubric score). Read-only inputs."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C

LABELS = "ABCDEFGH"


def question_text(task, b, raw):
    if task in ("binary", "binary_perturbed", "date", "frq"):
        return b[C.FIELD[task]]
    sc = C.mcq_choices(raw)
    if sc:
        opts = "\n".join(f"({L}) {sc[L]}" for L in LABELS if L in sc)
    else:  # no stored permutation: show the canonical order and flag it
        opts = "\n".join(f"({LABELS[i]}) {c}" for i, c in enumerate(b["mcq_choices"]))
    return f"{b['mcq_question']}\n\n{opts}"


def main():
    bench, subset = C.load_bench(), C.load_subset()
    n = 0; skipped = {}
    with open(C.TRACES, "w", encoding="utf-8") as out:
        for model, cond, half, rp, repp in C.RUNS:
            rep = {r["id"]: r for r in json.load(open(repp, encoding="utf-8"))["results"]}
            raws = {}
            for l in open(rp, encoding="utf-8"):
                if l.strip():
                    r = json.loads(l); raws[r["id"]] = r
            for i, raw in raws.items():
                b = bench.get(i)
                if b is None:
                    skipped["no_bench"] = skipped.get("no_bench", 0) + 1; continue
                tasks = rep.get(i, {}).get("tasks", {})
                for task in C.TASKS:
                    if not b.get(C.FIELD[task]):
                        continue
                    if task == "frq":
                        trace = raw.get("frq_answer") or raw.get("frq_raw") or ""
                    else:
                        trace = raw.get(f"{task}_reasoning") or ""
                    if not isinstance(trace, str):
                        trace = json.dumps(trace, ensure_ascii=False)
                    trace = trace.strip()
                    if not trace or trace.startswith("Error:"):
                        skipped["no_trace"] = skipped.get("no_trace", 0) + 1; continue
                    t = tasks.get(task) or {}
                    rec = dict(trace_id=C.sha(f"{model}|{cond}|{half}|{task}|{i}")[:16], model=model, model_key=C.MODEL_KEY[model],
                               condition=cond, half=half, task=task, id=i, in_subset500=(i in subset),
                               publication_date=b.get("publication_date"), main_area=b.get("main_area"), source=b.get("source"),
                               cutoff=C.CUTOFF[model], partition=C.partition(b.get("publication_date"), C.CUTOFF[model]),
                               question=question_text(task, b, raw), trace=trace, trace_words=C.words(trace),
                               trace_is_raw_json=trace.lstrip().startswith("{"),
                               answer_raw=(raw.get(f"{task}_answer") if task != "frq" else None),
                               confidence=(raw.get(f"{task}_confidence") if task != "frq" else None),
                               truncated=bool(raw.get(f"{task}_truncated")) or raw.get(f"{task}_stop_reason") in ("length", "max_tokens"),
                               refusal=bool(raw.get(f"{task}_refusal")), graded=bool(t) and not t.get("skipped"),
                               raw_path=str(rp), report_path=str(repp))
                    if task in ("binary", "binary_perturbed", "mcq"):
                        rec.update(parsed_answer=t.get("parsed_answer"), ground_truth=t.get("ground_truth"),
                                   correct=(bool(t["correct"]) if "correct" in t else None), score=t.get("score"))
                    elif task == "date":
                        pm, gm = C.months(t.get("parsed_date")), C.months(t.get("ground_truth"))
                        rec.update(parsed_answer=t.get("parsed_date"), ground_truth=t.get("ground_truth"), score=t.get("score"),
                                   month_distance=t.get("month_distance"), correct=(bool(t["exact_match"]) if "exact_match" in t else None),
                                   signed_error_months=((pm - gm) if pm is not None and gm is not None else None))
                    else:
                        rec.update(frq_score=t.get("score"), correct=((t["score"] >= 5.0) if t.get("score") is not None else None),
                                   ground_truth=None, parsed_answer=None, score=t.get("score"))
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n"); n += 1
    print(f"wrote {n} traces to {C.TRACES}; skipped {skipped}")


if __name__ == "__main__":
    main()
