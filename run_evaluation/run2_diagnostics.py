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
]
REPEATS = ("sonnet5_base_run1", "sonnet5_base_run2", "sonnet5_base_run3")
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
    print("3. RUN-TO-RUN VARIANCE (Claude Sonnet 5, extension, repeated passes)")
    print("   Sonnet 5 rejects every sampling parameter, so temperature=0 is")
    print("   unavailable. These passes bound the resulting non-determinism.")
    print("=" * 100)
    reps = [load(t) for t in REPEATS]
    reps = [r for r in reps if r]
    if len(reps) < 2:
        print("   [fewer than two passes available]")
        return {}
    vals = {}
    for rep in reps:
        tm = rep["task_metrics"]
        b, bp = tm["binary"], tm["binary_perturbed"]
        vals.setdefault("merged_binary", []).append(
            (b["correct"] + bp["correct"]) / (b["count"] + bp["count"]))
        for k, src in (("binary", b), ("binary_perturbed", bp),
                       ("mcq", tm["mcq"])):
            vals.setdefault(k, []).append(src["accuracy"])
        vals.setdefault("date_score", []).append(tm["date"]["mean_score"])
        vals.setdefault("refusals", []).append(rep["refusals"]["total"])
    hdr = "".join(f"{'run'+str(i+1):>10}" for i in range(len(reps)))
    print(f"{'metric':<20}{hdr}{'mean':>10}{'sd':>9}{'range':>9}")
    out = {}
    for k, v in vals.items():
        sd = statistics.stdev(v)
        print(f"{k:<20}" + "".join(f"{x:>10.4f}" for x in v)
              + f"{statistics.mean(v):>10.4f}{sd:>9.4f}{max(v)-min(v):>9.4f}")
        out[k] = {"runs": v, "mean": statistics.mean(v), "sd": sd}
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refusals-as-wrong-dir",
                    help="directory of reports built with --score-refusals-as-wrong")
    ap.add_argument("--out")
    a = ap.parse_args()

    res = {"refusals": block_refusals(),
           "refusal_sensitivity": block_sensitivity(a.refusals_as_wrong_dir),
           "run_to_run_variance": block_variance(),
           "cost": block_cost()}
    if a.out:
        json.dump(res, open(a.out, "w", encoding="utf-8"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
