"""
analyze_neg_strict.py — what the strict re-verification of the negatives changed.

Compares three standards for "this synthetic negative is mislabelled", on the
same 200 sampled items:

  pass 1        verify.py negatives, Claude Opus 4.8, loose prompt: "was this
                claim achieved by someone other than the source paper?"
  pass 1 + 2    the same, upheld by an independent second reviewer on a different
                provider. This is the figure the published write-up used.
  strict        verify_neg_strict.py: the exact claim, the exact value or the
                exact constraint, the same setting, on or before the date, one
                named non-excluded source, with a quoted passage that itself
                contains the figure -- and every one of those checked in code
                (neg_gates.py) rather than taken on the referee's word. Two
                cheap referees run it independently and BOTH must certify.

Every ACHIEVED that the gates rejected is listed with the gate it failed, so the
change in the rate can be attributed rather than asserted.

Outputs
  tables/t23_negatives_strict_rates.{csv,md}      old vs new, with CIs
  tables/t24_negatives_strict_changed.{csv,md}    every verdict that changed
  tables/t25_negatives_strict_gates.{csv,md}      which gate did the rejecting
  tables/t26_negatives_strict_referees.{csv,md}   referee agreement
  tables/t27_corrected_accuracy_negstrict.{csv,md}
  study1_verification/flagged_for_review.csv      surviving ACHIEVED, evidence inline
  study1_verification/neg_strict_summary.json
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import neg_gates as G

REFS = ["haiku45", "gpt54mini"]
PREV_FLAGGED = C.S1 / "flagged_for_review_v1_prestrict.csv"


def fmt(x, pct=True):
    if x is None or x != x:
        return ""
    return f"{100*x:.1f}%" if pct else f"{x:.3f}"


def write_table(stem: Path, header, rows, caption=""):
    stem.parent.mkdir(parents=True, exist_ok=True)
    with open(stem.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    md = [f"**{caption}**", "", "| " + " | ".join(header) + " |",
          "|" + "---|" * len(header)]
    for r in rows:
        md.append("| " + " | ".join("" if c is None else str(c) for c in r) + " |")
    stem.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    sample = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    items = {i["id"]: i for i in sample["negatives"]["items"]}
    reps, replaced = C.load_replacements()
    for r in reps:
        items.pop(r["replaces"], None)
        items[r["id"]] = r
    N = len(items)

    # ---- pass 1 and pass 2 (previous standard) --------------------------------
    p1 = {r["id"]: r for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl") if r["id"] in items}
    adj = {r["id"]: r for r in C.read_jsonl(C.S1 / "adjudication_negatives.jsonl") if r["id"] in items}
    old1 = {i for i, r in p1.items() if r.get("verdict") == "ACHIEVED"}
    old2 = {i for i in old1 if (adj.get(i, {}) or {}).get("verdict") == "ACHIEVED"}

    # ---- strict pass, per referee ---------------------------------------------
    strict = {}
    for k in REFS:
        p = C.S1 / f"negatives_verdicts_strict_{k}.jsonl"
        strict[k] = {r["id"]: r for r in C.read_jsonl(p) if r["id"] in items} if p.exists() else {}

    ran = [k for k in REFS if strict[k]]
    raw_ach = {k: {i for i, r in strict[k].items() if r.get("raw_verdict") == "ACHIEVED"} for k in ran}
    gated_ach = {k: {i for i, r in strict[k].items() if r.get("verdict") == "ACHIEVED"} for k in ran}
    downgraded = {k: {i for i, r in strict[k].items() if r.get("downgraded")} for k in ran}
    undecided = {k: {i for i, r in strict[k].items() if r.get("raw_verdict") in (None, "REFUSED")} for k in ran}

    both = set.intersection(*[gated_ach[k] for k in ran]) if len(ran) > 1 else (gated_ach[ran[0]] if ran else set())
    either = set.union(*[gated_ach[k] for k in ran]) if len(ran) > 1 else (gated_ach[ran[0]] if ran else set())

    strat = lambda it: str(it.get("stratum") or "?")   # sample.json stores it as a list

    def wrate(ids):
        num = sum(items[i].get("weight", 1.0) for i in ids)
        den = sum(it.get("weight", 1.0) for it in items.values())
        return num / den if den else float("nan")

    def boot(ids, seed):
        flags = [dict(items[i], _f=(i in ids)) for i in items]
        return C.strat_boot_ci(flags, lambda s: (sum(x.get("weight", 1.0) for x in s if x["_f"])
                                                 / max(1e-12, sum(x.get("weight", 1.0) for x in s))),
                               strat, seed=seed)

    # ---- table 18: the rates ---------------------------------------------------
    rows = []

    def add(label, ids, seed):
        k = len(ids)
        lo, hi = C.wilson(k, N)
        wlo, whi = boot(ids, seed)
        rows.append([label, f"{k}/{N}", fmt(k / N), f"[{fmt(lo)}, {fmt(hi)}]",
                     fmt(wrate(ids)), f"[{fmt(wlo)}, {fmt(whi)}]"])

    add("PREVIOUS - pass 1 alone (Opus 4.8, loose prompt)", old1, 101)
    add("PREVIOUS - pass 1 upheld by an independent second reviewer", old2, 102)
    for k in ran:
        add(f"STRICT - {k}, referee's own ACHIEVED before the gates", raw_ach[k], 103)
        add(f"STRICT - {k}, after the mechanical evidence gates", gated_ach[k], 104)
    if len(ran) > 1:
        add("STRICT - EITHER referee certifies (permissive)", either, 105)
        add("STRICT - BOTH referees certify (headline)", both, 106)
    write_table(C.TABLES / "t23_negatives_strict_rates",
                ["standard", "count", "rate", "wilson_95ci", "design_weighted", "boot_95ci"],
                rows,
                "Mislabelling rate of the synthetic negatives: previous standard vs the strict "
                f"re-verification, same {N} sampled items")

    # ---- table 19: every verdict that changed ---------------------------------
    changed = []
    for i in sorted(set(old1) | set(either)):
        it = items[i]
        was = "ACHIEVED" if i in old1 else "NOT_ACHIEVED"
        was2 = "ACHIEVED" if i in old2 else ("NOT_ACHIEVED" if i in old1 else "")
        now = "ACHIEVED" if i in both else "NOT_ACHIEVED"
        if was2 == now or (was == "NOT_ACHIEVED" and now == "NOT_ACHIEVED"):
            continue
        why = []
        for k in ran:
            r = strict[k].get(i)
            if not r:
                why.append(f"{k}: not run")
            elif r.get("raw_verdict") in (None, "REFUSED"):
                why.append(f"{k}: {r.get('raw_verdict') or 'unparsed'}")
            elif r.get("downgraded"):
                why.append(f"{k}: ACHIEVED rejected by gate [{', '.join(r['failed_gates'])}]")
            elif r.get("verdict") == "ACHIEVED":
                why.append(f"{k}: ACHIEVED upheld")
            else:
                why.append(f"{k}: NOT_ACHIEVED - {(r.get('reason') or '')[:160]}")
        changed.append([i, it.get("main_area"), it.get("ptype"), it.get("target_human"),
                        was, was2 or "n/a", now, " || ".join(why),
                        (p1.get(i, {}).get("justification") or "").replace("\n", " ")[:220]])
    write_table(C.TABLES / "t24_negatives_strict_changed",
                ["id", "domain", "perturbation_type", "target_date",
                 "pass1_verdict", "pass1plus2_verdict", "strict_verdict", "why_it_changed",
                 "pass1_justification"],
                changed, "Every negative whose mislabelling verdict changed under the strict standard")

    # ---- table 20: which gate did the rejecting -------------------------------
    grows, gate_counts = [], {}
    for k in ran:
        for i in sorted(downgraded[k]):
            r = strict[k][i]
            for f in r["failed_gates"]:
                gate_counts[f] = gate_counts.get(f, 0) + 1
            grows.append([k, i, items[i].get("main_area"), items[i].get("ptype"),
                          ", ".join(r["failed_gates"]),
                          (r.get("claim_requirement") or "")[:120],
                          (r.get("reported_value") or r.get("satisfied_constraint") or "")[:120],
                          (r.get("source_date") or ""), (r.get("source_name") or "")[:80]])
    write_table(C.TABLES / "t25_negatives_strict_gates",
                ["referee", "id", "domain", "perturbation_type", "failed_gates",
                 "claim_requirement", "value_or_constraint_offered", "source_date", "source"],
                grows,
                "Every ACHIEVED the referee proposed and the mechanical gates rejected, with the gate that rejected it")

    # ---- table 21: referee agreement ------------------------------------------
    arows = []
    for k in ran:
        arows.append([k, strict[k] and strict[k][next(iter(strict[k]))]["referee_model"] or "",
                      len(strict[k]), len(raw_ach[k]), len(downgraded[k]), len(gated_ach[k]),
                      len(undecided[k])])
    write_table(C.TABLES / "t26_negatives_strict_referees",
                ["referee", "model", "n_judged", "proposed_achieved", "rejected_by_gates",
                 "certified_achieved", "unparsed_or_refused"], arows,
                "Each referee's own numbers under the strict standard, before the AND-rule")
    if len(ran) > 1 and gate_counts:
        write_table(C.TABLES / "t25b_negatives_strict_gate_counts",
                    ["gate", "rejections"],
                    sorted(((g, n) for g, n in gate_counts.items()), key=lambda x: -x[1]),
                    "Which mechanical gate rejected how many proposed ACHIEVED verdicts")

    # ---- flagged_for_review.csv: the survivors --------------------------------
    old_flag = C.S1 / "flagged_for_review.csv"
    if old_flag.exists() and not PREV_FLAGGED.exists():
        PREV_FLAGGED.write_bytes(old_flag.read_bytes())     # keep the previous run's output

    frows = []
    for i in sorted(both):
        it = items[i]
        for k in ran:
            r = strict[k][i]
            frows.append(["negative", "ACHIEVED_ELSEWHERE_STRICT", i, k, r["referee_model"],
                          it.get("main_area"), it.get("ptype"), it.get("corpus"),
                          it.get("target_human"), it.get("paper_link") or "",
                          it["binary_question_perturbed"].replace("\n", " "),
                          (r.get("claim_requirement") or "").replace("\n", " ")[:300],
                          (r.get("reported_value") or "").replace("\n", " ")[:200],
                          (r.get("satisfied_constraint") or "").replace("\n", " ")[:300],
                          r.get("source_name", "")[:160], r.get("source_url", "")[:300],
                          r.get("source_date", ""),
                          (r.get("quoted_passage") or "").replace("\n", " ")[:600],
                          (r.get("same_setting_note") or "").replace("\n", " ")[:200],
                          "all gates passed",
                          f"study1_verification/evidence/negatives_strict/{i}.json"])
    with open(C.S1 / "flagged_for_review_negatives_strict.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["half", "flag", "id", "referee", "model", "domain", "perturbation_type",
                    "corpus", "target_date", "source_paper", "perturbed_claim",
                    "claim_requirement", "reported_value", "satisfied_constraint",
                    "achieving_source", "source_url", "source_date", "quoted_passage",
                    "same_setting_note", "gate_status", "evidence_file"])
        w.writerows(frows)

    # ---- corrected accuracy -----------------------------------------------------
    # Route 2 ("the perturbation did not bind") is a different claim, settled from
    # the source paper rather than from a search, and this re-verification does not
    # touch it. It is therefore held FIXED at its own element-gated certified set
    # (strict_verdicts.csv, R2_did_not_bind == CERTIFIED) in every column below, so
    # the only thing that moves between columns is the route-1 standard.
    pa = C.load_panel_answers()
    r2_certified, r1_prev_strict = set(), set()
    sv = C.S1 / "strict_verdicts.csv"
    if sv.exists():
        with open(sv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("R2_did_not_bind") == "CERTIFIED":
                    r2_certified.add(row["id"])
                if row.get("R1_achieved") == "CERTIFIED":
                    r1_prev_strict.add(row["id"])
    pos_ids = [i["id"] for i in sample["positives"]["items"]]
    neg_ids = list(items)

    def acc(units):
        if not units:
            return float("nan"), float("nan"), float("nan"), 0
        lo, hi = C.wilson(sum(units), len(units))
        return sum(units) / len(units), lo, hi, len(units)

    STANDARDS = [("web_pass1plus2", old2), ("element_gated", r1_prev_strict), ("strict_rerun", both)]
    crows, means = [], {k: [] for k, _ in STANDARDS}
    pub_mean = []
    for m in C.MODEL_ORDER:
        base = []
        for i in pos_ids:
            v = pa.get((m, i, "binary"))
            if v:
                base.append(("pos", i, v["correct"], v["answer"]))
        for i in neg_ids:
            v = pa.get((m, i, "binary_perturbed"))
            if v:
                base.append(("neg", i, v["correct"], v["answer"]))
        pub, plo, phi, pn = acc([c for _, _, c, _ in base])
        pub_mean.append(pub)

        def relabel(bad):
            out = []
            for k, i, c, a in base:
                if k == "neg" and i in bad:
                    out.append((a == "yes") if a in ("yes", "no") else (not c))
                else:
                    out.append(c)
            return out

        cells = []
        for key, r1 in STANDARDS:
            a, lo, hi, _ = acc(relabel(r1 | r2_certified))
            means[key].append(a)
            cells += [fmt(a), f"[{fmt(lo)}, {fmt(hi)}]", fmt(a - pub)]
        crows.append([C.MODELS[m]["name"], C.MODELS[m]["cutoff"], pn,
                      fmt(pub), f"[{fmt(plo)}, {fmt(phi)}]"] + cells)

    import statistics as _st
    crows.append(["PANEL MEAN", "", "", fmt(_st.mean(pub_mean)), ""]
                 + sum(([fmt(_st.mean(means[k])), "", fmt(_st.mean(means[k]) - _st.mean(pub_mean))]
                        for k, _ in STANDARDS), []))
    write_table(C.TABLES / "t27_corrected_accuracy_negstrict",
                ["model", "cutoff", "n_sample", "acc_published", "published_95ci",
                 "acc_r1_web_pass1plus2", "ci_a", "delta_a",
                 "acc_r1_element_gated", "ci_b", "delta_b",
                 "acc_r1_strict_rerun", "ci_c", "delta_c"], crows,
                f"Binary accuracy on the verified sample. Route 2 held fixed at its certified set "
                f"({len(r2_certified)} items); only the route-1 standard changes across the three "
                f"relabelling columns ({len(old2)}, {len(r1_prev_strict)} and {len(both)} items)")

    summary = dict(
        n_items=N, referees=ran,
        previous_pass1=len(old1), previous_pass1_plus2=len(old2),
        strict_raw={k: len(raw_ach[k]) for k in ran},
        strict_downgraded={k: len(downgraded[k]) for k in ran},
        strict_certified={k: len(gated_ach[k]) for k in ran},
        strict_unparsed={k: len(undecided[k]) for k in ran},
        strict_both=len(both), strict_either=len(either),
        gate_rejection_counts=gate_counts,
        rate_previous=len(old2) / N, rate_strict=len(both) / N,
        ts=C.now_utc(), git=C.git_sha())
    (C.S1 / "neg_strict_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print()
    print((C.TABLES / "t23_negatives_strict_rates.md").read_text())


if __name__ == "__main__":
    main()
