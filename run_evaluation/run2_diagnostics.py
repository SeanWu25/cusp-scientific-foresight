#!/usr/bin/env python3
"""
run2_diagnostics.py — reporting diagnostics for the Apr-Aug 2026 extension.

Four blocks the main tables depend on but do not show:

  1. Refusals by model and scientific area. Claude models decline a
     non-trivial share of biology and medicine items; denominators therefore
     differ across the panel and that must be visible.
  2. Sensitivity of every headline metric to the refusal convention
     (excluded, as reported, vs scored wrong). Any ranking that flips between
     the two conventions is not a finding.
  3. Run-to-run variance across repeated passes, which bounds the
     non-determinism from models that reject temperature=0.
  4. Cost and token accounting, summed from per-item records.

Reads stored reports only. No inference.
"""

from __future__ import annotations

import argparse, json, os, statistics, sys
from collections import Counter

R = "results_extension_run2/reports"
SCRATCH_HINT = "build with scripts/build_report.py --score-refusals-as-wrong"

PANEL = [
    ("GPT-4o",          "gpt4o_base"),
    ("LLaMA 3.3 70B",   "llama33_base"),
    ("GPT-OSS 20B",     "gptoss20b_base"),
    ("Claude S4.5",     "sonnet45_base"),
    ("GPT-5.4",         "gpt54_base"),
    ("Claude Sonnet 5", "sonnet5_base_run1"),
    ("GPT-5.6 Sol",     "sol_base"),
    ("DeepSeek-V4-Pro", "deepseekv4pro_base"),
    ("Claude Opus 4.8", "opus48_base_run1"),
]
REPEATS = {"Claude Sonnet 5": ("sonnet5_base_run1", "sonnet5_base_run2", "sonnet5_base_run3"),
           "Claude Opus 4.8": ("opus48_base_run1", "opus48_base_run2", "opus48_base_run3")}
TASKS = ("binary", "binary_perturbed", "mcq", "date")

# Serving mode and list price (USD per input/output token) per model.
# "api"   -> first-party API, list-priced, cost computed from tokens here
#            rather than read back from the runner, so a missing PRICING entry
#            in run_cusp.py cannot silently zero a row.
# "azure" -> customer Azure deployment; billed at negotiated rates, so no
#            dollar figure is reported rather than an invented one.
# "local" -> served on local GPUs (vLLM); no marginal API cost.
SERVING = {
    "GPT-4o":          ("azure", None),
    "LLaMA 3.3 70B":   ("azure", None),
    "GPT-OSS 20B":     ("local", None),
    "Claude S4.5":     ("api",   (3.00e-6, 15.00e-6)),
    "GPT-5.4":         ("api",   (1.25e-6, 10.00e-6)),
    "Claude Sonnet 5": ("api",   (2.00e-6, 10.00e-6)),
    "GPT-5.6 Sol":     ("api",   (4.00e-6, 20.00e-6)),
    "DeepSeek-V4-Pro": ("azure", None),
    "Claude Opus 4.8": ("api",   (5.00e-6, 25.00e-6)),
}


def load(tag, root=R):
    p = os.path.join(root, f"{tag}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def block_refusals():
    print("=" * 100)
    print("1. REFUSALS BY MODEL AND AREA (extension, 815 events, 2,277 task instances)")
    print("   Refusals are their own outcome category and are excluded from")
    print("   denominators in the reported tables. Block 2 bounds that choice.")
    print("=" * 100)
    print(f"{'model':<17}{'calls':>7}{'refused':>9}{'rate':>8}"
          f"{'Biology':>16}{'Medicine':>16}{'all other':>16}")
    out = {}
    for name, tag in PANEL:
        rep = load(tag)
        if rep is None:
            print(f"{name:<17}{'(missing)':>7}")
            continue
        ref = rep["refusals"]
        pa = ref["per_area"]
        calls = sum(v["calls"] for v in pa.values())
        bio, med = pa.get("Biology", {}), pa.get("Medicine", {})
        oc = sum(v["calls"] for k, v in pa.items() if k not in ("Biology", "Medicine"))
        orf = sum(v.get("refused", 0) for k, v in pa.items()
                  if k not in ("Biology", "Medicine"))

        def cell(d):
            c, r = d.get("calls", 0), d.get("refused", 0)
            return f"{r}/{c} ({100*r/max(c,1):.1f}%)"

        print(f"{name:<17}{calls:>7}{ref['total']:>9}{100*ref['total']/max(calls,1):>7.1f}%"
              f"{cell(bio):>16}{cell(med):>16}"
              f"{f'{orf}/{oc} ({100*orf/max(oc,1):.1f}%)':>16}")
        out[name] = {"calls": calls, "refused": ref["total"],
                     "per_task": ref["per_task"], "per_area": pa}
    return out


def block_sensitivity(alt_root):
    print("\n" + "=" * 100)
    print("2. SENSITIVITY TO THE REFUSAL CONVENTION")
    print("   left  = refusals excluded from the denominator (what the tables report)")
    print("   right = refusals scored as incorrect (worst case)")
    print("   A ranking that changes between the two columns is convention-dependent.")
    print("=" * 100)
    if not alt_root or not os.path.isdir(alt_root):
        print(f"   [skipped: no --refusals-as-wrong-dir given; {SCRATCH_HINT}]")
        return {}
    print(f"{'model':<17}{'task':<19}{'excluded':>20}{'as wrong':>20}{'shift':>9}")
    out = {}
    for name, tag in PANEL:
        a, b = load(tag), load(tag, alt_root)
        if not a or not b:
            continue
        if a["refusals"]["total"] == 0:
            continue
        for t in TASKS:
            if t not in a["task_metrics"]:
                continue
            av, bv = a["task_metrics"][t]["mean_score"], b["task_metrics"][t]["mean_score"]
            an, bn = a["task_metrics"][t]["count"], b["task_metrics"][t]["count"]
            print(f"{name:<17}{t:<19}{f'{av:.3f} (n={an})':>20}"
                  f"{f'{bv:.3f} (n={bn})':>20}{bv-av:>+9.3f}")
            out.setdefault(name, {})[t] = {"excluded": av, "as_wrong": bv,
                                           "n_excluded": an, "n_all": bn}
        print()
    print("   Models not listed refused nothing; their two columns are identical.")
    return out


def block_variance():
    print("=" * 100)
    print("3. RUN-TO-RUN VARIANCE (repeated passes; models that reject temperature=0)")
    print("   These models reject every sampling parameter, so temperature=0 is")
    print("   unavailable. Repeated passes bound the resulting non-determinism.")
    print("=" * 100)
    out = {}
    for model, tags in REPEATS.items():
        reps = [r for r in (load(t) for t in tags) if r]
        if len(reps) < 2:
            print(f"\n{model}: fewer than two passes available")
            continue
        vals = {}
        for rep in reps:
            tm = rep["task_metrics"]
            b, bp = tm["binary"], tm["binary_perturbed"]
            vals.setdefault("merged_binary", []).append(
                (b["correct"] + bp["correct"]) / (b["count"] + bp["count"]))
            for k, src in (("binary", b), ("binary_perturbed", bp), ("mcq", tm["mcq"])):
                vals.setdefault(k, []).append(src["accuracy"])
            vals.setdefault("date_score", []).append(tm["date"]["mean_score"])
            if tm.get("frq", {}).get("mean_score") is not None:
                vals.setdefault("frq_score", []).append(tm["frq"]["mean_score"])
            vals.setdefault("refusals", []).append(rep["refusals"]["total"])
        hdr = "".join(f"{'run'+str(i+1):>10}" for i in range(len(reps)))
        print(f"\n{model}  ({len(reps)} passes)")
        print(f"{'metric':<20}{hdr}{'mean':>10}{'sd':>9}{'range':>9}")
        for k, v in vals.items():
            sd = statistics.stdev(v)
            print(f"{k:<20}" + "".join(f"{x:>10.4f}" for x in v)
                  + f"{statistics.mean(v):>10.4f}{sd:>9.4f}{max(v)-min(v):>9.4f}")
            out.setdefault(model, {})[k] = {"runs": v, "mean": statistics.mean(v), "sd": sd}
    return out


def block_cost():
    print("\n" + "=" * 100)
    print("4. COST AND TOKEN ACCOUNTING (extension, per model, base condition)")
    print("   'API time' is the SUM of per-call latencies, not wall clock: runs")
    print("   were concurrent, so wall clock is far shorter. Cost is computed")
    print("   from token counts at list prices, and is shown only for")
    print("   first-party APIs -- Azure deployments bill at negotiated rates and")
    print("   GPT-OSS 20B ran on local GPUs.")
    print("=" * 100)
    print(f"{'model':<17}{'serving':>9}{'calls':>7}{'input tok':>12}{'output tok':>12}"
          f"{'reasoning':>12}{'API time h':>11}{'cost':>12}")
    out = {}
    tot = 0.0
    for name, tag in PANEL:
        rep = load(tag)
        if not rep:
            continue
        m = rep["run_metadata"]
        mode, price = SERVING.get(name, ("azure", None))
        it, ot = m.get("input_tokens", 0) or 0, m.get("output_tokens", 0) or 0
        if price:
            c = it * price[0] + ot * price[1]
            tot += c
            cost = f"${c:,.2f}"
        else:
            c = None
            cost = "n/a (azure)" if mode == "azure" else "n/a (local)"
        print(f"{name:<17}{mode:>9}{m.get('calls', 0):>7}{it:>12,}{ot:>12,}"
              f"{(m.get('reasoning_tokens') or 0):>12,}"
              f"{(m.get('latency_s') or 0)/3600:>11.1f}{cost:>12}")
        out[name] = {"serving": mode, "calls": m.get("calls"),
                     "input_tokens": it, "output_tokens": ot,
                     "reasoning_tokens": m.get("reasoning_tokens"),
                     "api_time_s": m.get("latency_s"), "cost_usd": c}
    print(f"{'':<17}{'':>9}{'':>7}{'':>12}{'':>12}{'':>12}"
          f"{'first-party total':>23} ${tot:,.2f}")
    return out


def block_baselines():
    """Constant-answer baselines for merged binary, per corpus.

    Ground truth is fixed by task type: the binary question always resolves
    'yes' (the real finding) and its perturbed twin always resolves 'no' (the
    corrupted finding). Merged binary is therefore a two-class problem whose
    class balance is nothing but the ratio of the two task types -- and that
    ratio is not the same in the two corpora. Raw merged-binary accuracy is
    consequently NOT comparable across corpora; MCC and balanced accuracy are.
    """
    print("\n" + "=" * 100)
    print("5. CONSTANT-ANSWER BASELINES FOR MERGED BINARY")
    print("   binary -> ground truth always 'yes'; perturbed -> always 'no'.")
    print("   So the class balance is just the task-type ratio, which differs")
    print("   between corpora. Compare models to these baselines, not to each")
    print("   other across corpora.")
    print("=" * 100)
    corpora = [
        ("original (Jan 24-Mar 26)", "run_evaluation/frq_results/gpt_4o_reeval.json", None),
        ("extension (Apr-Aug 26)",   os.path.join(R, "gpt4o_base.json"), None),
    ]
    base = {}
    for lab, path, _ in corpora:
        if not os.path.exists(path):
            continue
        rep = json.load(open(path, encoding="utf-8"))
        nb = np_ = 0
        for x in rep["results"]:
            t = x.get("tasks", {})
            if t.get("binary") and "correct" in t["binary"]:
                nb += 1
            if t.get("binary_perturbed") and "correct" in t["binary_perturbed"]:
                np_ += 1
        tot = nb + np_
        base[lab] = {"n_yes": nb, "n_no": np_, "n": tot,
                     "always_yes": nb / tot, "always_no": np_ / tot}
        print(f"   {lab:<26} n={tot:<6} always-YES {nb/tot:.3f}   "
              f"always-NO {np_/tot:.3f}")

    ext = base.get("extension (Apr-Aug 26)")
    if not ext:
        return base
    print(f"\n   Panel vs the always-NO baseline on the extension "
          f"({ext['always_no']:.3f}):")
    print(f"   {'model':<17}{'merged binary':>15}{'vs baseline':>14}")
    beat = 0
    for name, tag in PANEL:
        rep = load(tag)
        if not rep:
            continue
        tm = rep["task_metrics"]
        b, bp = tm["binary"], tm["binary_perturbed"]
        acc = (b["correct"] + bp["correct"]) / (b["count"] + bp["count"])
        d = acc - ext["always_no"]
        beat += d > 0
        print(f"   {name:<17}{acc:>15.3f}{d:>+14.3f}")
    print(f"\n   {beat} of {len(PANEL)} models beat a constant 'no' on the extension.")
    base["models_beating_always_no"] = beat
    return base


def block_mcq_permutation():
    """Position of the correct MCQ answer after shuffling, per model.

    The permutation is drawn from a seeded stream in file order, so every model
    must see the SAME shuffle of the same item -- otherwise cross-model MCQ
    comparison is invalid. Both facts are checked here rather than assumed:
    that the correct answer lands uniformly across slots, and that the
    distribution is identical across models.

    Note the field to read is mcq_shuffled_answer_key (a letter).
    mcq_original_answer_key is an integer index, and index 0 is falsy -- a
    truthiness test on it silently drops every row.
    """
    print("\n" + "=" * 100)
    print("6. MCQ PERMUTATION: where does the correct answer land?")
    print("   uniform = 25% per slot; chi-square df=3, critical 7.81 at p=.05")
    print("=" * 100)
    print(f"{'model':<17}{'n':>6}   " + "".join(f"{c:>8}" for c in 'ABCD')
          + f"{'chi2':>8}{'verdict':>10}{'perms':>8}")
    out = {}
    sigs = set()
    for name, tag in PANEL:
        path = f"results_extension_run2/raw/{tag}.jsonl"
        if not os.path.exists(path):
            continue
        key, picks, perms, n = Counter(), Counter(), set(), 0
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            k = r.get("mcq_shuffled_answer_key")
            if not k:
                continue
            n += 1
            key[k] += 1
            p_ = r.get("mcq_permutation")
            if p_:
                perms.add(tuple(p_))
            a = r.get("mcq_answer")
            if a and str(a).upper()[:1] in "ABCD":
                picks[str(a).upper()[:1]] += 1
        if not n:
            continue
        exp = n / 4
        chi = sum((key[c] - exp) ** 2 / exp for c in "ABCD")
        sigs.add(tuple(key[c] for c in "ABCD"))
        print(f"{name:<17}{n:>6}   " + "".join(f"{100*key[c]/n:>7.1f}%" for c in "ABCD")
              + f"{chi:>8.2f}{'uniform' if chi < 7.81 else 'SKEWED':>10}"
              f"{f'{len(perms)}/24':>8}")
        tp = sum(picks.values())
        out[name] = {"n": n, "correct_at": dict(key), "chi2": chi,
                     "uniform": chi < 7.81, "distinct_permutations": len(perms),
                     "model_picks": {c: picks[c] / tp for c in "ABCD"} if tp else {}}
    print(f"\n   identical correct-answer distribution across models: "
          f"{'YES' if len(sigs) == 1 else 'NO -- cross-model MCQ comparison is INVALID'}")
    print(f"\n   model answer distribution (first-option bias shows up here):")
    print(f"   {'model':<17}" + "".join(f"{c:>8}" for c in 'ABCD'))
    for name, v in out.items():
        mp = v.get("model_picks") or {}
        if mp:
            print(f"   {name:<17}" + "".join(f"{100*mp[c]:>7.1f}%" for c in "ABCD"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refusals-as-wrong-dir",
                    help="directory of reports built with --score-refusals-as-wrong")
    ap.add_argument("--out")
    a = ap.parse_args()

    res = {"refusals": block_refusals(),
           "refusal_sensitivity": block_sensitivity(a.refusals_as_wrong_dir),
           "run_to_run_variance": block_variance(),
           "cost": block_cost(),
           "constant_baselines": block_baselines(),
           "mcq_permutation": block_mcq_permutation()}
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
