"""
common.py — shared loaders for A2 (Reviewer 2, concern C2): binary task validity.

Nothing here touches the benchmark, the scoring code, or any stored model output;
everything is read-only. Two corpora are pooled (original Jan 2024 - Mar 2026 and
the Apr - Aug 2026 extension) because the panel was evaluated on both.

Item conventions (fixed by construction of CUSP, verified in RUN2_RESULTS.md §3):
  positive  = the event's `binary_question`            (ground truth YES)
  negative  = the event's `binary_question_perturbed`  (ground truth NO)
target_date = the "By <Month> <Year>" phrase inside the question text (what the
              models saw); on the extension this can differ from the month-
              normalised `publication_date` by one month.
perturbation type (from `binary_perturbation_detail`, rule-based):
  'constraint' if the detail says a constraint/requirement/condition was added
  'numeric'    otherwise (a reported number, range or threshold was changed)
"""
from __future__ import annotations
import hashlib, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "results" / "A2_binary_validity"
S1 = STUDY / "study1_verification"
S2 = STUDY / "study2_detection"
TABLES = STUDY / "tables"
FIGS = STUDY / "figures"
BENCH_ORIG = ROOT / "archive/data/canonical/merged_validated_cusp_fixed.jsonl"
BENCH_EXT = ROOT / "benchmark_data/CUSP_extension/cusp_extension_apr_aug_2026_monthnorm.jsonl"
FR = ROOT / "run_evaluation" / "frq_results"
EXT_REPORTS = ROOT / "results_extension_run2/reports"

DOMAINS = ["Artificial Intelligence", "Biology", "Chemistry", "Environmental Science",
           "Materials Science", "Medicine", "Neuroscience", "Physics", "Other"]
PTYPES = ["numeric", "constraint"]

# The evaluated panel: same registry (paths, cutoffs) as horizon_study/data.py.
MODELS = {
    "gpt4o":       dict(name="GPT-4o",          cutoff="2023-10", orig=FR / "gpt_4o_reeval.json",       ext="gpt4o_base.json"),
    "llama33":     dict(name="LLaMA 3.3 70B",   cutoff="2023-12", orig=FR / "llama_3_3_full.json",      ext="llama33_base.json"),
    "gptoss20b":   dict(name="GPT-OSS 20B",     cutoff="2024-06", orig=FR / "gpt_oss_20B_reeval.json",  ext="gptoss20b_base.json"),
    "deepseek_r1": dict(name="DeepSeek R1",     cutoff="2024-07", orig=FR / "deepseek_r1.json",         ext=None),
    "claude45":    dict(name="Claude S4.5",     cutoff="2025-01", orig=FR / "claude_sonnet.json",       ext="sonnet45_base.json"),
    "gpt54":       dict(name="GPT-5.4",         cutoff="2025-08", orig=FR / "gpt_5_4_eval.json",        ext="gpt54_base.json"),
    "sonnet5":     dict(name="Claude Sonnet 5", cutoff="2026-01", orig=ROOT / "results_sonnet5_run1/reports/base_medium_run1.json", ext="sonnet5_base_run1.json"),
    "sol":         dict(name="GPT-5.6 Sol",     cutoff="2026-02", orig=ROOT / "results_sol_run1/reports/base_medium_run1.json",     ext="sol_base.json"),
    "dsv4pro":     dict(name="DeepSeek-V4-Pro", cutoff="2026-04", orig=ROOT / "results_dsv4pro_run1/reports/base_run1.json",       ext="deepseekv4pro_base.json"),
}
MODEL_ORDER = list(MODELS)

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
_MON = {m[:3]: i for i, m in enumerate(MONTHS, 1)}
_DATE_RE = re.compile(r"[Bb]y ([A-Z][a-z]+)\.? (\d{4})")


def sha(s: str, n: int = 16) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:n]


def months(ym: str) -> int:
    y, m = str(ym).split("-")[:2]
    return int(y) * 12 + int(m)


# CUTOFF_MONTH_PRE (default on; env CUTOFF_MONTH_PRE=0 restores the old rule):
#   on  -> post iff pub_month > cutoff_month (the cutoff month counts as pre);
#   off -> old main-table rule: pre iff pub_month < cutoff_month (cutoff month counts as post).
# No A2 analysis calls partition(): the audits, corrected accuracy and detection x accuracy
# tables use every sampled item regardless of cutoff, so no A2 output depends on this rule.
CUTOFF_MONTH_PRE = os.environ.get("CUTOFF_MONTH_PRE", "1") != "0"


def partition(pub: str, cutoff: str) -> str:
    if CUTOFF_MONTH_PRE:
        return "post" if months(pub) > months(cutoff) else "pre"
    return "pre" if months(pub) < months(cutoff) else "post"


def target_date(q: str) -> tuple[str, str] | tuple[None, None]:
    """('YYYY-MM', 'Month YYYY') from the last 'By <Month> <Year>' phrase in the question."""
    ms = [(a, b) for a, b in _DATE_RE.findall(q or "") if a[:3] in _MON]
    if not ms:
        return None, None
    a, b = ms[-1]
    return f"{b}-{_MON[a[:3]]:02d}", f"{MONTHS[_MON[a[:3]] - 1]} {b}"


_CONSTRAINT_RE = re.compile(
    r"\b(add(?:ed|ing|s)?|introduc\w*|unmet|additional|new)\b[^.]{0,80}?\b(constraint|requirement|condition|criteri\w*|stipulat\w*|restriction|limitation)"
    r"|\bconstraint\b|\brequir(?:e|ed|es|ing|ement)\b|\bunmet\b", re.I)


def perturbation_type(detail: str) -> str:
    return "constraint" if _CONSTRAINT_RE.search(detail or "") else "numeric"


_NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")


def numbers_differ(a: str, b: str) -> bool:
    return set(_NUM_RE.findall(a or "")) != set(_NUM_RE.findall(b or ""))


def strip_dates(q: str) -> str:
    """Remove target-date information from a binary question.

    Bare four-digit years are LEFT IN PLACE on purpose: in this corpus they are
    almost always part of a benchmark name (AIME-2025, IMO-2025, Video-MME,
    LiveCodeBench 06/24-01/25) and are identical in both members of a pair, so
    they carry no signal about which claim was perturbed. Only explicit
    'By/by <Month> <Year>' deadline phrases are removed."""
    s = (q or "").strip()
    # leading deadline: "By March 2026, will ..."
    s = re.sub(r"^[Bb]y [A-Z][a-z]+\.? \d{4}\s*,?\s*", "", s)
    # trailing / embedded deadline: "..., by March 2026?" / "... by March 2026 ..."
    s = re.sub(r"\s*,\s*[Bb]y [A-Z][a-z]+\.? \d{4}\b", "", s)
    s = re.sub(r"\s+[Bb]y [A-Z][a-z]+\.? \d{4}\b", "", s)
    # any survivor in any position
    s = re.sub(r"\s*\b[Bb]y [A-Z][a-z]+\.? \d{4}\b\s*,?\s*", " ", s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    s = re.sub(r"\s+([?.,;:])", r"\1", s)
    if s:
        s = s[0].upper() + s[1:]
    return s


def residual_years(s: str) -> list[str]:
    return sorted(set(re.findall(r"\b(?:19|20)\d\d\b", s)))


def load_corpus() -> dict:
    """id -> record, with corpus tag, target date fields and perturbation type attached."""
    out = {}
    for path, tag in ((BENCH_ORIG, "orig"), (BENCH_EXT, "ext")):
        for l in open(path, encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            r["corpus"] = tag
            q = r.get("binary_question") or r.get("binary_question_perturbed") or ""
            r["target_ym"], r["target_human"] = target_date(q)
            if r.get("binary_question_perturbed"):
                r["ptype"] = perturbation_type(r.get("binary_perturbation_detail") or "")
                r["numbers_differ"] = numbers_differ(r.get("binary_question") or r.get("results_and_metrics") or "",
                                                     r["binary_question_perturbed"])
            assert r["id"] not in out, r["id"]
            out[r["id"]] = r
    return out


def load_panel_answers() -> dict:
    """(model, id, task) -> dict(answer='yes'|'no'|None, correct=bool, conf=float|None)
    task in {'binary','binary_perturbed'}. Refused / skipped / unparsed items are absent
    (the same rule the published tables use: refusals leave the denominator)."""
    out = {}
    for m, cfg in MODELS.items():
        for p in (cfg["orig"], (EXT_REPORTS / cfg["ext"]) if cfg.get("ext") else None):
            if p is None or not Path(p).exists():
                continue
            rep = json.load(open(p, encoding="utf-8"))
            for r in rep["results"]:
                for task in ("binary", "binary_perturbed"):
                    d = (r.get("tasks") or {}).get(task)
                    if d and not d.get("skipped") and not d.get("refused") and "correct" in d:
                        ans = str(d.get("parsed_answer", "")).lower()
                        out[(m, r["id"], task)] = dict(answer=ans if ans in ("yes", "no") else None,
                                                       correct=bool(d["correct"]),
                                                       conf=(float(d["confidence"]) if d.get("confidence") is not None else None))
    return out


def read_jsonl(p: Path) -> list[dict]:
    if not Path(p).exists():
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def append_jsonl(p: Path, rec: dict) -> None:
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()


def now_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_sha() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=15).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def wilson(k: int, n: int, z: float = 1.959963985) -> tuple[float, float]:
    """Wilson score interval; used for simple unweighted proportions."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def boot_ci(values, stat, B: int = 10000, seed: int = 12345, alpha: float = 0.05):
    """Percentile bootstrap over a list of per-item records."""
    import random as _r
    vals = list(values)
    n = len(vals)
    if n == 0:
        return (float("nan"), float("nan"))
    rng = _r.Random(seed)
    out = []
    for _ in range(B):
        samp = [vals[rng.randrange(n)] for _ in range(n)]
        try:
            out.append(stat(samp))
        except Exception:
            pass
    if not out:
        return (float("nan"), float("nan"))
    out.sort()
    lo = out[int((alpha / 2) * len(out))]
    hi = out[min(len(out) - 1, int((1 - alpha / 2) * len(out)))]
    return (lo, hi)


def strat_boot_ci(items, stat, strata_key, B: int = 10000, seed: int = 12345, alpha: float = 0.05):
    """Stratified percentile bootstrap: resample within each stratum."""
    import random as _r
    from collections import defaultdict as _dd
    g = _dd(list)
    for it in items:
        g[strata_key(it)].append(it)
    rng = _r.Random(seed)
    keys = sorted(g)
    out = []
    for _ in range(B):
        samp = []
        for k in keys:
            pool = g[k]
            m = len(pool)
            samp.extend(pool[rng.randrange(m)] for _ in range(m))
        try:
            out.append(stat(samp))
        except Exception:
            pass
    if not out:
        return (float("nan"), float("nan"))
    out.sort()
    lo = out[int((alpha / 2) * len(out))]
    hi = out[min(len(out) - 1, int((1 - alpha / 2) * len(out)))]
    return (lo, hi)


def git_branch() -> str:
    import subprocess
    try:
        return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, timeout=15).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def boot_prop(flags, B: int = 10000, seed: int = 20260920, alpha: float = 0.05):
    """Vectorised percentile bootstrap for a simple proportion over 0/1 flags."""
    import numpy as _np
    v = _np.asarray([1.0 if f else 0.0 for f in flags])
    if v.size == 0:
        return (float("nan"), float("nan"))
    rng = _np.random.default_rng(seed)
    means = v[rng.integers(0, v.size, size=(B, v.size))].mean(1)
    return (float(_np.percentile(means, 100 * alpha / 2)),
            float(_np.percentile(means, 100 * (1 - alpha / 2))))


def load_replacements() -> tuple[list, set]:
    """(replacement items, ids they replace).

    One sampled negative is blocked by every provider's biological-risk
    classifier, so no verifier can decide it. replace.py draws a substitute from
    the same stratum and records it here; sample.json is left untouched so the
    original draw stays auditable. Loaders append the substitutes and drop the
    ids they stand in for.
    """
    p = S1 / "replacements.json"
    if not p.exists():
        return [], set()
    d = json.loads(p.read_text(encoding="utf-8"))
    reps = d.get("replacements") or []
    return reps, {r["replaces"] for r in reps}
