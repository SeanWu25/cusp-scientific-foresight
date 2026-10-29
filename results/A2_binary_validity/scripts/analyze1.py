"""
analyze1.py — Study 1 analysis: confirmation rate, mislabelling rate, corrected accuracy.

Reads only study1_verification/*.jsonl plus the stored panel answers. Writes
tables, figures, flagged_for_review.csv, corrected_accuracy.csv and results.md.
Never touches the benchmark, the scoring code, or any stored model output.
"""
from __future__ import annotations
import csv, json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

ALPHA = 0.05


def rate(items, flag) -> float:
    n = len(items)
    return sum(1 for it in items if flag(it)) / n if n else float("nan")


def wrate(items, flag) -> float:
    """Horvitz-Thompson (design-weighted) rate."""
    W = sum(it["weight"] for it in items)
    return sum(it["weight"] for it in items if flag(it)) / W if W else float("nan")


def fmt(x, d=3):
    return "" if x is None or (isinstance(x, float) and x != x) else f"{x:.{d}f}"


def pct(x, d=1):
    return "" if x is None or (isinstance(x, float) and x != x) else f"{100*x:.{d}f}%"


def write_table(path: Path, header: list, rows: list, title: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    md = ([f"### {title}", ""] if title else []) + \
         ["| " + " | ".join(map(str, header)) + " |",
          "|" + "|".join(["---"] * len(header)) + "|"] + \
         ["| " + " | ".join("" if c is None else str(c) for c in r) + " |" for r in rows]
    path.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")


def load(kind: str) -> list[dict]:
    name = {"positives": "positives_verdicts.jsonl", "negatives": "negatives_verdicts.jsonl",
            "soundness": "negatives_soundness.jsonl"}[kind]
    recs, seen = [], set()
    for r in C.read_jsonl(C.S1 / name):          # keep the last record per id
        seen.add(r["id"])
    by = {}
    for r in C.read_jsonl(C.S1 / name):
        by[r["id"]] = r
    return [r for r in by.values() if r.get("verdict") and r["verdict"] != "REFUSED"]


def load_refused(kind: str) -> list[dict]:
    name = {"positives": "positives_verdicts.jsonl", "negatives": "negatives_verdicts.jsonl",
            "soundness": "negatives_soundness.jsonl"}[kind]
    by = {}
    for r in C.read_jsonl(C.S1 / name):
        by[r["id"]] = r
    return [r for r in by.values()
            if r.get("refused") or r.get("verdict") == "REFUSED"
            or (not r.get("verdict") and r.get("stop_reason") == "refusal")]


def load_adj(kind: str) -> dict:
    """id -> adjudication record from the independent second pass (may be absent)."""
    by = {}
    for r in C.read_jsonl(C.S1 / f"adjudication_{kind}.jsonl"):
        if r.get("verdict"):
            by[r["id"]] = r
    return by


def breakdown(items, flag, key, label, out_rows, seed=1):
    groups = defaultdict(list)
    for it in items:
        groups[key(it)].append(it)
    for g in sorted(groups):
        sub = groups[g]
        k = sum(1 for it in sub if flag(it))
        lo, hi = C.wilson(k, len(sub))
        blo, bhi = C.boot_prop([flag(it) for it in sub])
        out_rows.append([label, g, len(sub), k, fmt(k / len(sub)), fmt(lo), fmt(hi),
                         fmt(blo), fmt(bhi)])


def main() -> None:
    pos, neg, snd = load("positives"), load("negatives"), load("soundness")
    adj_n, adj_p = load_adj("negatives"), load_adj("positives")
    adj_s = load_adj("soundness")
    C.TABLES.mkdir(parents=True, exist_ok=True)
    strat = lambda it: "|".join(it["stratum"])

    # An independent second pass (different provider, different search index) re-examined
    # every flagged item. Strict = both passes agree; permissive = first pass alone.
    ach_strict = lambda it: ((it["verdict"] == "ACHIEVED"
                              or it.get("verdict") in ("REFUSED", None))
                             and adj_n.get(it["id"], {}).get("verdict") == "ACHIEVED")
    conf_after = lambda it: (it["verdict"] == "CONFIRMED"
                             or adj_p.get(it["id"], {}).get("verdict") == "FOUND")

    # The first verifier's safety classifier declined four benign biomedical
    # positives outright, so they carry no first-pass opinion and are absent from
    # the first-pass denominator -- which is right: a refusal is not a judgement.
    # The second provider has a different refusal profile and did decide them, so
    # once its verdicts exist those four rejoin the sample for the
    # after-second-search rate. First pass stays over `pos`; anything that reads a
    # settled verdict reads `pos_after`.
    pos_refused = [r for r in load_refused("positives") if r["id"] in adj_p]
    pos_after = pos + pos_refused

    # Same treatment on the negative half, plus one item nothing could decide.
    # A single sampled negative -- a claim about H5N1 titres in milk -- is blocked
    # by every provider's biological-risk classifier: first verifier, both strict
    # referees, the closed-book soundness pass and the second-provider adjudicator
    # all declined it. We do not model-shop around a safety classifier, so it was
    # replaced by a same-stratum draw (replace.py, seed 20260924, recorded in
    # replacements.json with the item it stands in for); sample.json is untouched.
    _reps, _replaced = C.load_replacements()
    neg_refused = [r for r in load_refused("negatives")
                   if r["id"] in adj_n and r["id"] not in _replaced]
    neg_after = [r for r in neg if r["id"] not in _replaced] + neg_refused

    # ---------- 1. positives ----------
    conf = lambda it: it["verdict"] == "CONFIRMED"
    p_rate, p_w = rate(pos, conf), wrate(pos, conf)
    p_lo, p_hi = C.wilson(sum(1 for it in pos if conf(it)), len(pos))
    p_wlo, p_whi = C.strat_boot_ci(pos, lambda s: wrate(s, conf), strat, seed=101)

    # ---------- 2. negatives ----------
    ach = lambda it: it["verdict"] == "ACHIEVED"
    n_rate, n_w = rate(neg, ach), wrate(neg, ach)
    n_lo, n_hi = C.wilson(sum(1 for it in neg if ach(it)), len(neg))
    n_wlo, n_whi = C.strat_boot_ci(neg, lambda s: wrate(s, ach), strat, seed=202)

    # ---------- 3. soundness (secondary) ----------
    ss = lambda it: it["verdict"] == "SELF_SATISFIED"
    ss_both = lambda it: (it["verdict"] == "SELF_SATISFIED"
                          and adj_s.get(it["id"], {}).get("verdict") == "SELF_SATISFIED")
    s_rate, s_w = rate(snd, ss), wrate(snd, ss)
    s_lo, s_hi = C.wilson(sum(1 for it in snd if ss(it)), len(snd))
    s_wlo, s_whi = C.strat_boot_ci(snd, lambda s: wrate(s, ss), strat, seed=303) if snd else (float("nan"),) * 2

    hdr = ["half", "metric", "n", "k", "rate", "ci_lo", "ci_hi", "weighted_rate", "w_ci_lo", "w_ci_hi"]
    rows = [
        ["positives", "CONFIRMED", len(pos), sum(1 for it in pos if conf(it)),
         fmt(p_rate), fmt(p_lo), fmt(p_hi), fmt(p_w), fmt(p_wlo), fmt(p_whi)],
        ["negatives", "ACHIEVED elsewhere (mislabelled)", len(neg), sum(1 for it in neg if ach(it)),
         fmt(n_rate), fmt(n_lo), fmt(n_hi), fmt(n_w), fmt(n_wlo), fmt(n_whi)],
        ["negatives", "SELF_SATISFIED by source (secondary)", len(snd), sum(1 for it in snd if ss(it)),
         fmt(s_rate), fmt(s_lo), fmt(s_hi), fmt(s_w), fmt(s_wlo), fmt(s_whi)],
    ]
    write_table(C.TABLES / "t1_headline_rates", hdr, rows, "Study 1 headline rates")

    # breakdowns
    br = []
    breakdown(pos, conf, lambda it: it["main_area"] or "Unknown", "positives/domain", br)
    breakdown(pos, conf, lambda it: it["ptype"] or "unpaired", "positives/ptype", br)
    breakdown(neg, ach, lambda it: it["main_area"] or "Unknown", "negatives/domain", br)
    breakdown(neg, ach, lambda it: it["ptype"] or "?", "negatives/ptype", br)
    breakdown(neg, ach, lambda it: it["corpus"], "negatives/corpus", br)
    if snd:
        breakdown(snd, ss, lambda it: it["main_area"] or "Unknown", "soundness/domain", br)
        breakdown(snd, ss, lambda it: it["ptype"] or "?", "soundness/ptype", br)
    write_table(C.TABLES / "t2_breakdowns",
                ["split", "group", "n", "k", "rate", "wilson_lo", "wilson_hi",
                 "boot_lo", "boot_hi"], br,
                "Study 1 rates by domain, perturbation type and corpus")

    # ---------- 4. extrapolation ----------
    sample = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    N_neg = sample["frames"]["negative"]
    ex = [["negatives frame (corpus-wide)", N_neg, "", "", ""],
          ["mislabelled: achieved elsewhere", "", pct(n_w), pct(n_wlo), pct(n_whi)],
          ["  -> expected count corpus-wide", "", f"{n_w*N_neg:.0f}", f"{n_wlo*N_neg:.0f}", f"{n_whi*N_neg:.0f}"]]
    if snd:
        ex += [["mislabelled: perturbation not binding (secondary)", "", pct(s_w), pct(s_wlo), pct(s_whi)],
               ["  -> expected count corpus-wide", "", f"{s_w*N_neg:.0f}", f"{s_wlo*N_neg:.0f}", f"{s_whi*N_neg:.0f}"]]
        union = {it["id"] for it in neg if ach(it)} | {it["id"] for it in snd if ss(it)}
        idx = {it["id"]: it for it in neg}
        uni_items = [idx[i] for i in union if i in idx]
        u_w = sum(it["weight"] for it in uni_items) / sum(it["weight"] for it in neg)
        flagged = {it["id"] for it in neg if ach(it)} | {it["id"] for it in snd if ss(it)}
        u_lo, u_hi = C.strat_boot_ci(neg, lambda s: (sum(it["weight"] for it in s if it["id"] in flagged)
                                                     / max(sum(it["weight"] for it in s), 1e-9)), strat, seed=404)
        ex += [["EITHER route (union, one pass flags it)", "", pct(u_w), pct(u_lo), pct(u_hi)],
               ["  -> expected count corpus-wide", "", f"{u_w*N_neg:.0f}", f"{u_lo*N_neg:.0f}", f"{u_hi*N_neg:.0f}"]]
        if adj_n or adj_s:
            strict_ids = {it["id"] for it in neg if ach_strict(it)} | {it["id"] for it in snd if ss_both(it)}
            sw = (sum(it["weight"] for it in neg if it["id"] in strict_ids)
                  / max(sum(it["weight"] for it in neg), 1e-9))
            slo, shi = C.strat_boot_ci(neg, lambda s2: (sum(it["weight"] for it in s2 if it["id"] in strict_ids)
                                                        / max(sum(it["weight"] for it in s2), 1e-9)),
                                       strat, seed=707)
            ex += [["EITHER route (union, BOTH passes agree)", "", pct(sw), pct(slo), pct(shi)],
                   ["  -> expected count corpus-wide", "",
                    f"{sw*N_neg:.0f}", f"{slo*N_neg:.0f}", f"{shi*N_neg:.0f}"]]
    # ---------- 4b. adjudication ----------
    if adj_n or adj_p:
        ar = []
        if adj_n:
            cnt = defaultdict(int)
            for it in neg:
                if it["verdict"] == "ACHIEVED":
                    cnt[adj_n.get(it["id"], {}).get("verdict") or "NOT_ADJUDICATED"] += 1
            for k in sorted(cnt):
                ar.append(["negatives: ACHIEVED re-decided independently", k, cnt[k]])
            holds = sum(1 for it in neg if it["verdict"] == "ACHIEVED"
                        and adj_n.get(it["id"], {}).get("first_reviewer_evidence_holds") is True)
            nadj = sum(1 for it in neg if it["verdict"] == "ACHIEVED" and it["id"] in adj_n)
            ar.append(["negatives: second pass relied on the SAME evidence as the first",
                       f"{holds}/{nadj}", fmt(holds / nadj) if nadj else ""])
            ks = sum(1 for it in neg if ach_strict(it))
            ks = sum(1 for it in neg_after if ach_strict(it))
            lo, hi = C.wilson(ks, len(neg_after))
            wlo, whi = C.strat_boot_ci(neg_after, lambda s2: wrate(s2, ach_strict),
                                       strat, seed=505)
            ar.append(["negatives: mislabelling rate, BOTH passes agree",
                       f"{ks}/{len(neg_after)}",
                       f"{fmt(ks/len(neg_after))} [{fmt(lo)}, {fmt(hi)}]"])
            ar.append(["negatives: mislabelling rate, first pass only",
                       f"{sum(1 for it in neg if ach(it))}/{len(neg)}",
                       f"{fmt(n_rate)} [{fmt(n_lo)}, {fmt(n_hi)}]"])
            ar.append(["negatives: weighted, BOTH passes agree", "",
                       f"{fmt(wrate(neg_after, ach_strict))} [{fmt(wlo)}, {fmt(whi)}]"])
            if _reps:
                ar.append(["negatives: sampled item replaced (no verifier could decide it)",
                           f"{len(_reps)}",
                           "; ".join(f"{r['replaces'][:8]} -> {r['id'][:8]} "
                                     f"({'|'.join(r['stratum'])})" for r in _reps)])
        if adj_p:
            cnt = defaultdict(int)
            for it in pos:
                if it["verdict"] != "CONFIRMED":
                    cnt[adj_p.get(it["id"], {}).get("verdict") or "NOT_ADJUDICATED"] += 1
            for k in sorted(cnt):
                ar.append(["positives: NOT_CONFIRMED re-searched", k, cnt[k]])
            kc = sum(1 for it in pos_after if conf_after(it))
            lo, hi = C.wilson(kc, len(pos_after))
            ar.append(["positives: confirmation rate after second search",
                       f"{kc}/{len(pos_after)}", f"{fmt(kc/len(pos_after))} [{fmt(lo)}, {fmt(hi)}]"])
            if pos_refused:
                ar.append(["positives: first-pass refusals decided by the second provider",
                           f"{len(pos_refused)} of {len(load_refused('positives'))}",
                           ", ".join(sorted(f"{adj_p[r['id']]['verdict']}"
                                            for r in pos_refused))])
        write_table(C.TABLES / "t11_adjudication",
                    ["quantity", "outcome", "value"], ar,
                    "Independent second pass over every flagged item (GPT-5.5 + OpenAI web search)")

    # ---------- 4c. soundness: two independent judges ----------
    if adj_s and snd:
        both = [it for it in snd if it["id"] in adj_s]
        a = ["SELF_SATISFIED" if it["verdict"] == "SELF_SATISFIED" else "OTHER" for it in both]
        b = ["SELF_SATISFIED" if adj_s[it["id"]]["verdict"] == "SELF_SATISFIED" else "OTHER" for it in both]
        n2 = len(both)
        agree = sum(1 for x, y in zip(a, b) if x == y)
        po = agree / n2 if n2 else float("nan")
        pa1 = sum(1 for x in a if x == "SELF_SATISFIED") / n2 if n2 else 0
        pb1 = sum(1 for y in b if y == "SELF_SATISFIED") / n2 if n2 else 0
        pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
        kappa = (po - pe) / (1 - pe) if (1 - pe) else float("nan")
        kb = sum(1 for it in both if ss_both(it))
        klo, khi = C.wilson(kb, n2)
        wlo2, whi2 = C.strat_boot_ci(both, lambda s2: wrate(s2, ss_both), strat, seed=606)
        eith = sum(1 for it in both
                   if it["verdict"] == "SELF_SATISFIED" or adj_s[it["id"]]["verdict"] == "SELF_SATISFIED")
        elo, ehi = C.wilson(eith, n2)
        sr = [["judge A (Claude Opus 4.8) SELF_SATISFIED", f"{sum(1 for x in a if x=='SELF_SATISFIED')}/{n2}",
               fmt(pa1)],
              ["judge B (GPT-5.5, independent) SELF_SATISFIED",
               f"{sum(1 for y in b if y=='SELF_SATISFIED')}/{n2}", fmt(pb1)],
              ["raw agreement", f"{agree}/{n2}", fmt(po)],
              ["Cohen's kappa", "", fmt(kappa)],
              ["BOTH judges agree SELF_SATISFIED (strict)", f"{kb}/{n2}",
               f"{fmt(kb/n2)} [{fmt(klo)}, {fmt(khi)}]"],
              ["EITHER judge says SELF_SATISFIED (permissive)", f"{eith}/{n2}",
               f"{fmt(eith/n2)} [{fmt(elo)}, {fmt(ehi)}]"],
              ["BOTH, design-weighted", "", f"{fmt(wrate(both, ss_both))} [{fmt(wlo2)}, {fmt(whi2)}]"]]
        write_table(C.TABLES / "t12_soundness_agreement",
                    ["quantity", "count", "value"], sr,
                    "Perturbation soundness judged independently by two models")

    write_table(C.TABLES / "t3_extrapolation",
                ["quantity", "N", "estimate", "ci_lo", "ci_hi"], ex,
                "Extrapolation of the mislabelling rate to the full negative frame")

    # ---------- 5. flagged for review ----------
    ev_rel = "study1_verification/evidence"
    flag_rows = []
    for it in pos:
        if not conf(it):
            flag_rows.append(["positive", "NOT_CONFIRMED", it["id"], it["main_area"], it["ptype"],
                              it["corpus"], it["target_human"], it.get("paper_link") or "",
                              (it.get("justification") or "").replace("\n", " ")[:400],
                              (it.get("supporting_passage") or "").replace("\n", " ")[:300],
                              " ".join(it.get("urls") or [])[:600],
                              f"{ev_rel}/positives/{it['id']}.json", it.get("confidence"),
                              (adj_p.get(it["id"], {}) or {}).get("verdict") or "not adjudicated",
                              ((adj_p.get(it["id"], {}) or {}).get("reason") or "").replace("\n", " ")[:300]])
    for it in neg:
        if ach(it):
            flag_rows.append(["negative", "ACHIEVED_ELSEWHERE", it["id"], it["main_area"], it["ptype"],
                              it["corpus"], it["target_human"], it.get("paper_link") or "",
                              (it.get("justification") or "").replace("\n", " ")[:400],
                              (it.get("supporting_passage") or "").replace("\n", " ")[:300],
                              " ".join(it.get("urls") or [])[:600],
                              f"{ev_rel}/negatives/{it['id']}.json", it.get("confidence"),
                              (adj_n.get(it["id"], {}) or {}).get("verdict") or "not adjudicated",
                              ((adj_n.get(it["id"], {}) or {}).get("reason") or "").replace("\n", " ")[:300]])
    for it in snd:
        if ss(it):
            flag_rows.append(["negative", "PERTURBATION_NOT_BINDING", it["id"], it["main_area"], it["ptype"],
                              it["corpus"], it["target_human"], it.get("paper_link") or "",
                              (it.get("justification") or "").replace("\n", " ")[:400],
                              f"failure_mode={it.get('failure_mode')}", "",
                              f"{ev_rel}/soundness/{it['id']}.json", it.get("confidence"),
                              (adj_s.get(it["id"], {}) or {}).get("verdict") or "not adjudicated",
                              ((adj_s.get(it["id"], {}) or {}).get("reason") or "").replace("\n", " ")[:300]])
    with open(C.S1 / "flagged_for_review.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["half", "flag", "id", "domain", "perturbation_type", "corpus", "target_date",
                    "source_paper", "verifier_justification", "supporting_passage", "urls",
                    "evidence_file", "verifier_confidence",
                    "second_pass_verdict", "second_pass_reason"])
        w.writerows(flag_rows)

    # ---------- 6. corrected accuracy ----------
    pa = C.load_panel_answers()
    bad_neg = {it["id"] for it in neg if (ach_strict(it) if adj_n else ach(it))}
    bad_neg_permissive = {it["id"] for it in neg if ach(it)}
    bad_neg_sound = {it["id"] for it in snd if (ss_both(it) if adj_s else ss(it))}
    unconf_pos = {it["id"] for it in (pos_after if adj_p else pos)
                  if not (conf_after(it) if adj_p else conf(it))}
    pos_ids = [it["id"] for it in pos]
    neg_ids = [it["id"] for it in neg]

    def acc_ci(units, seed):
        """units: list of (correct_bool,) per answered item."""
        if not units:
            return float("nan"), float("nan"), float("nan"), 0
        a = sum(units) / len(units)
        lo, hi = C.wilson(sum(units), len(units))
        return a, lo, hi, len(units)

    rows = []
    for m in C.MODEL_ORDER:
        name = C.MODELS[m]["name"]
        # full corpus, as published
        full = [v["correct"] for (mm, i, t), v in pa.items() if mm == m and t in ("binary", "binary_perturbed")]
        f_a, f_lo, f_hi, f_n = acc_ci(full, 1)

        # verified sample only
        base = []
        for i in pos_ids:
            v = pa.get((m, i, "binary"))
            if v:
                base.append(("pos", i, v["correct"], v["answer"]))
        for i in neg_ids:
            v = pa.get((m, i, "binary_perturbed"))
            if v:
                base.append(("neg", i, v["correct"], v["answer"]))
        pub = [c for _, _, c, _ in base]
        p_a, p_lo2, p_hi2, p_n = acc_ci(pub, 2)

        # (ii) exclude flagged
        keep = [c for k, i, c, _ in base
                if not (k == "neg" and (i in bad_neg or i in bad_neg_sound)) and not (k == "pos" and i in unconf_pos)]
        e_a, e_lo, e_hi, e_n = acc_ci(keep, 3)

        # (iii) relabel flagged negatives to YES; unverifiable positives left as published.
        # On a negative the published ground truth is NO, so "the model answered yes" is
        # exactly "the model was scored wrong" (verified: 0 mismatches over 63,501 stored
        # answers). Deriving it from `correct` therefore also covers the handful of records
        # whose parsed answer string was not retained.
        rel = []
        for k, i, c, ansr in base:
            if k == "neg" and (i in bad_neg or i in bad_neg_sound):
                rel.append((ansr == "yes") if ansr in ("yes", "no") else (not c))
            else:
                rel.append(c)
        r_a, r_lo, r_hi, r_n = acc_ci(rel, 4)

        # sensitivity: relabel on the permissive definition (either pass flags the item)
        bad_perm = bad_neg_permissive | {it["id"] for it in snd if ss(it)}
        relp = []
        for k, i, c, ansr in base:
            if k == "neg" and i in bad_perm:
                relp.append((ansr == "yes") if ansr in ("yes", "no") else (not c))
            else:
                relp.append(c)
        rp_a, rp_lo, rp_hi, rp_n = acc_ci(relp, 5)

        rows.append([name, C.MODELS[m]["cutoff"], f_n, fmt(f_a), fmt(f_lo), fmt(f_hi),
                     p_n, fmt(p_a), fmt(p_lo2), fmt(p_hi2),
                     e_n, fmt(e_a), fmt(e_lo), fmt(e_hi),
                     r_n, fmt(r_a), fmt(r_lo), fmt(r_hi),
                     fmt(r_a - p_a) if p_a == p_a else "",
                     rp_n, fmt(rp_a), fmt(rp_lo), fmt(rp_hi)])
    write_table(C.S1 / "corrected_accuracy",
                ["model", "cutoff",
                 "n_full", "acc_full_published", "full_lo", "full_hi",
                 "n_sample", "acc_sample_published", "samp_lo", "samp_hi",
                 "n_excl", "acc_excluding_flagged", "excl_lo", "excl_hi",
                 "n_relab", "acc_relabelled", "relab_lo", "relab_hi",
                 "delta_relabelled_minus_published",
                 "n_relab_perm", "acc_relabelled_permissive", "relabperm_lo", "relabperm_hi"], rows,
                "Binary accuracy three ways (full corpus reference + verified sample)")
    (C.TABLES / "t4_corrected_accuracy.csv").write_bytes((C.S1 / "corrected_accuracy.csv").read_bytes())
    (C.TABLES / "t4_corrected_accuracy.md").write_bytes((C.S1 / "corrected_accuracy.md").read_bytes())

    summary = dict(
        positives=dict(n=len(pos), confirmed=sum(1 for it in pos if conf(it)), rate=p_rate,
                       ci=[p_lo, p_hi], weighted=p_w, w_ci=[p_wlo, p_whi]),
        negatives=dict(n=len(neg), achieved=sum(1 for it in neg if ach(it)), rate=n_rate,
                       ci=[n_lo, n_hi], weighted=n_w, w_ci=[n_wlo, n_whi]),
        soundness=dict(n=len(snd), self_satisfied=sum(1 for it in snd if ss(it)), rate=s_rate,
                       ci=[s_lo, s_hi], weighted=s_w, w_ci=[s_wlo, s_whi]),
        frame_negative=N_neg, flagged_rows=len(flag_rows),
        refusals={k: len(load_refused(k)) for k in ("positives", "negatives", "soundness")},
        adjudication=dict(
            negatives_examined=len(adj_n), positives_examined=len(adj_p),
            achieved_upheld=sum(1 for it in neg if ach_strict(it)),
            achieved_first_pass=sum(1 for it in neg if ach(it)),
            rate_strict=(rate(neg, ach_strict) if adj_n else None),
            weighted_strict=(wrate(neg, ach_strict) if adj_n else None),
            confirmed_after_second=(rate(pos_after, conf_after) if adj_p else None),
            n_positives_after_second=(len(pos_after) if adj_p else None),
            soundness_replicated=len(adj_s),
            soundness_both=(rate([it for it in snd if it["id"] in adj_s], ss_both) if adj_s else None)),
    )
    (C.S1 / "summary_stats.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
