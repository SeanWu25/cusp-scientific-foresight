"""
common.py — shared loaders for the A6 calibration-intervention study.

Nothing here modifies base prompts, scoring code, or the pinned subset. Arm A and
arm C are read from the stored, already-scored evaluation reports; arms B/D/E are
read from this study's own raw JSONL (calibration_study/raw/); arm F is derived.

Item record (one per event x task):
  id, task ('binary' | 'binary_perturbed' | 'mcq'), partition ('pre' | 'post'),
  answer (parsed 'yes'/'no'/letter or None), correct (bool or None),
  conf  : reported confidence in the given answer, or the derived answer-framed
          probability for arms D/E (None if not captured)
  p_yes : binary tasks only — probability the event occurs
          (conf if answer==yes, 1-conf if answer==no, or the directly elicited
          probability for arm E, or the Yes-vote fraction for arm D)
  y     : binary tasks only — event outcome, 1 for original questions (ground
          truth Yes), 0 for perturbed questions (ground truth No)
  p_true: MCQ, arms D/E only — probability assigned to the correct option
  dist  : MCQ, arms D/E only — full distribution over A-D
"""
from __future__ import annotations
import json, hashlib, os, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
FR     = ROOT / "run_evaluation" / "frq_results"
ARCH   = ROOT / "archive" / "model_outputs" / "benchmark_logs_model_outputs"
BENCH  = ROOT / "archive" / "data" / "canonical" / "merged_validated_cusp_fixed.jsonl"
SUBSET = ROOT / "results_sonnet5_run1" / "subset500_ids.txt"
STUDY  = ROOT / "calibration_study"
RAW    = STUDY / "raw"
TABLES = STUDY / "tables"
FIGS   = STUDY / "figures"

sys.path.insert(0, str(ROOT / "scripts"))

# Cutoffs are the ones used by the published tables (compare_models.MODEL_REGISTRY).
MODELS = {
    "llama33":     dict(name="LLaMA 3.3 70B",     cutoff="2023-12", base="llama_3_3_full.json",
                        wscut=ROOT / "results_llama33_run1/reports/ws_cutoff_500.json",  # generated 2026-09-20 on the pinned subset (Foundry Llama-3.3-70B-Instruct, T=0)
                        base_raw="llama-3.3-70b-full.jsonl.jsonl",
                        deploy="Llama-3.3-70B-Instruct", n_sc=10, bias_s13=+0.839),
    "deepseek_r1": dict(name="DeepSeek R1",       cutoff="2024-07", base="deepseek_r1.json",
                        wscut="deepseek_r1_500_web_cutoff.json",     base_raw="predictions_DeepSeek-R1.jsonl",
                        deploy="DeepSeek-R1",            n_sc=5,  bias_s13=-0.025),
    "gpt4o":       dict(name="GPT-4o",            cutoff="2023-10", base="gpt_4o_reeval.json",
                        wscut="gpt-4o_web_search_with_cutoff_500.json", base_raw="predictions_gpt-4o.jsonl",
                        deploy="gpt-4o",                 n_sc=5,  bias_s13=-0.576),
    "gptoss20b":   dict(name="GPT-OSS 20B",       cutoff="2024-06", base="gpt_oss_20B_reeval.json",
                        wscut=None,                                  base_raw="gpt-oss-20b-full.jsonl",
                        deploy=None,                     n_sc=10, bias_s13=-0.600),
    "gpt54":       dict(name="GPT-5.4",           cutoff="2025-08", base="gpt_5_4_eval.json",
                        wscut="gpt_5_4_500_web_cutoff.json",         base_raw="predictions_gpt-5.4.jsonl",
                        deploy="gpt-5.4",                n_sc=5,  bias_s13=+0.238),
    "claude45":    dict(name="Claude Sonnet 4.5", cutoff="2025-01", base="claude_sonnet.json",
                        wscut="claude_500_with_cutoff.json",         base_raw="predictions_claude-sonnet-4-5_20260428_092848.jsonl",
                        deploy=None,                     n_sc=5,  bias_s13=-0.434),
}
PANEL = ["llama33", "gpt54", "gpt4o"]          # the study's three models (DeepSeek R1 swapped for GPT-5.4: its deployment is deprecated)
ARMS  = ["A", "B1", "B2", "C", "D", "E"]
ARM_LABEL = {"A": "A base", "B1": "B1 prompt (asym)", "B2": "B2 prompt (sym)",
             "C": "C retrieval (WS+cutoff)", "D": "D self-consistency", "E": "E probabilistic"}
TASKS = ["binary_merged", "binary", "binary_perturbed", "mcq"]

# Partition rule. CUTOFF_MONTH_PRE (default on, env CUTOFF_MONTH_PRE=0 to switch off):
#   on  -> an event is 'post' iff pub_month > cutoff_month, so the cutoff month itself
#          is 'pre' (the rule the manuscript now uses everywhere, matching the
#          information-access analysis). Outputs go to tables_cmpre/ and figures_cmpre/.
#   off -> the old main-table rule: 'pre' iff pub_month < cutoff_month (cutoff month
#          is 'post'). Outputs go to the original tables/ and figures/.
CUTOFF_MONTH_PRE = os.environ.get("CUTOFF_MONTH_PRE", "1") != "0"
SUFFIX = "_cmpre" if CUTOFF_MONTH_PRE else ""
PARTITION_RULE = ("cutoff-month-pre: post iff pub_month > cutoff_month (cutoff month counts as pre)"
                  if CUTOFF_MONTH_PRE else
                  "main: pre if pub_month < cutoff_month (cutoff month counts as post)")
TABLES = STUDY / f"tables{SUFFIX}"
FIGS   = STUDY / f"figures{SUFFIX}"
TABLES.mkdir(exist_ok=True); FIGS.mkdir(exist_ok=True)


def months(ym: str) -> int:
    y, m = str(ym).split("-")[:2]
    return int(y) * 12 + int(m)


def partition(pub: str, cutoff: str) -> str:
    if CUTOFF_MONTH_PRE:
        return "post" if months(pub) > months(cutoff) else "pre"
    return "pre" if months(pub) < months(cutoff) else "post"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


_bench = None
def load_bench() -> dict:
    global _bench
    if _bench is None:
        _bench = {}
        with open(BENCH, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    r = json.loads(l); _bench[r["id"]] = r
    return _bench


def load_subset() -> list[str]:
    ids = [l.strip() for l in open(SUBSET) if l.strip()]
    assert len(ids) == 500 and len(set(ids)) == 500
    return ids


def load_base_raw(model: str) -> dict:
    """Stored raw predictions of the base run (for the per-item MCQ permutation)."""
    out = {}
    with open(ARCH / MODELS[model]["base_raw"], encoding="utf-8") as f:
        for l in f:
            if l.strip():
                r = json.loads(l); out[r["id"]] = r
    return out


def _answer_to_pyes(ans, conf):
    if conf is None or ans is None:
        return None
    if ans == "yes":
        return float(conf)
    if ans == "no":
        return 1.0 - float(conf)
    return None


def items_from_report(model: str, path: Path, arm: str) -> list[dict]:
    """Arm A / C items from a stored eval.py report, restricted to the pinned subset."""
    rep = json.load(open(path, encoding="utf-8"))
    res = {r["id"]: r for r in rep["results"]}
    bench, cutoff = load_bench(), MODELS[model]["cutoff"]
    items = []
    for i in load_subset():
        b = bench[i]; part = partition(b["publication_date"], cutoff)
        for task, field in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"),
                            ("mcq", "mcq_question")):
            if not b.get(field):
                continue
            t = res.get(i, {}).get("tasks", {}).get(task)
            it = dict(id=i, task=task, partition=part, arm=arm, model=model,
                      answer=None, correct=None, conf=None)
            if t and not t.get("skipped") and "correct" in t:
                ans = str(t.get("parsed_answer", "")).lower()
                if task == "mcq":
                    ans = ans.upper()
                    if ans not in ("A", "B", "C", "D"):
                        ans = None  # semantic-match fallbacks are kept as correct/incorrect but no letter
                elif ans not in ("yes", "no"):
                    ans = None
                it.update(answer=ans, correct=bool(t["correct"]),
                          conf=(float(t["confidence"]) if t.get("confidence") is not None else None))
            if task != "mcq":
                it["y"] = 1 if task == "binary" else 0
                it["p_yes"] = _answer_to_pyes(it["answer"], it["conf"])
            items.append(it)
    return items


def items_from_raw(model: str, arm: str) -> list[dict] | None:
    """Arm B1/B2/D/E items from this study's raw JSONL (graded with scripts/eval.py)."""
    path = RAW / f"{model}_{arm}.jsonl"
    if not path.exists():
        return None
    from eval import grade_binary, grade_mcq  # the frozen scoring code, unmodified
    bench, cutoff = load_bench(), MODELS[model]["cutoff"]
    recs = {}
    with open(path, encoding="utf-8") as f:
        for l in f:
            if l.strip():
                r = json.loads(l); recs[(r["id"], r["task"])] = r
    items = []
    for i in load_subset():
        b = bench[i]; part = partition(b["publication_date"], cutoff)
        for task, field in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"),
                            ("mcq", "mcq_question")):
            if not b.get(field):
                continue
            it = dict(id=i, task=task, partition=part, arm=arm, model=model,
                      answer=None, correct=None, conf=None)
            if task != "mcq":
                it["y"] = 1 if task == "binary" else 0; it["p_yes"] = None
            r = recs.get((i, task))
            if r is not None and not r.get("error") and not r.get("refusal"):
                gt = "Yes" if task == "binary" else "No"
                if arm in ("B1", "B2"):
                    ans = r.get("answer")
                    if ans:
                        if task == "mcq":
                            g = grade_mcq(str(ans), r["mcq_answer_key"])
                            it.update(answer=(g["parsed_answer"] if g["parsed_answer"] in "ABCD" else None), correct=g["correct"])
                        else:
                            g = grade_binary(str(ans), gt)
                            it.update(answer=(g["parsed_answer"] if g["parsed_answer"] in ("yes", "no") else None), correct=g["correct"])
                        it["conf"] = r.get("confidence")
                        if task != "mcq":
                            it["p_yes"] = _answer_to_pyes(it["answer"], it["conf"])
                elif arm == "D":
                    votes = r.get("votes") or {}
                    n = r.get("n_valid", 0)
                    if n > 0:
                        maj = max(votes, key=lambda k: (votes[k], k))  # ties -> alphabetical (stated)
                        k = votes[maj]
                        it["n"] = n; it["k"] = k; it["votes"] = votes
                        it["conf"] = k / n                       # raw vote fraction for the majority answer
                        it["conf_laplace"] = (k + 1) / (n + 2)
                        if task == "mcq":
                            g = grade_mcq(maj, r["mcq_answer_key"])
                            it.update(answer=maj, correct=g["correct"])
                            tot = sum(votes.values())
                            it["dist"] = {L: votes.get(L, 0) / tot for L in "ABCD"}
                            it["p_true"] = it["dist"].get(r["mcq_answer_key"], 0.0)
                            it["p_true_laplace"] = (votes.get(r["mcq_answer_key"], 0) + 1) / (tot + 4)
                        else:
                            g = grade_binary(maj, gt)
                            it.update(answer=maj.lower(), correct=g["correct"])
                            ky = votes.get("Yes", 0) + votes.get("yes", 0)
                            it["p_yes"] = ky / n
                            it["p_yes_laplace"] = (ky + 1) / (n + 2)
                elif arm == "E":
                    if task == "mcq":
                        probs = r.get("probs_renorm")
                        if probs:
                            ans = max(probs, key=lambda k: (probs[k], -"ABCD".index(k)))
                            g = grade_mcq(ans, r["mcq_answer_key"])
                            it.update(answer=ans, correct=g["correct"], conf=float(probs[ans]),
                                      dist=probs, p_true=float(probs.get(r["mcq_answer_key"], 0.0)),
                                      probs_raw=r.get("probs_raw"), raw_sum=r.get("raw_sum"))
                    else:
                        p = r.get("probability")
                        if p is not None:
                            p = float(p)
                            ans = "yes" if p >= 0.5 else "no"          # threshold at 0.5, ties -> yes (stated)
                            g = grade_binary(ans, gt)
                            it.update(answer=ans, correct=g["correct"], p_yes=p, conf=(p if ans == "yes" else 1 - p))
            items.append(it)
    return items


def load_arm(model: str, arm: str) -> list[dict] | None:
    m = MODELS[model]
    if arm == "A":
        return items_from_report(model, FR / m["base"], "A")
    if arm == "C":
        return items_from_report(model, Path(m["wscut"]) if Path(m["wscut"]).is_absolute() else FR / m["wscut"], "C") if (m["wscut"] and Path(m["wscut"] if Path(m["wscut"]).is_absolute() else FR / m["wscut"]).exists()) else None
    return items_from_raw(model, arm)


def load_all(models=None, arms=ARMS) -> dict:
    out = {}
    for mdl in (models or list(MODELS)):
        for arm in arms:
            it = load_arm(mdl, arm)
            if it is not None:
                out[(mdl, arm)] = it
    return out
