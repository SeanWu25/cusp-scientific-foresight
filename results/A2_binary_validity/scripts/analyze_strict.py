"""
analyze_strict.py — strict rates, with every certification re-checked in code.

A referee's answer is only a proposal. It becomes a certification only if it also
passes the mechanical gates in gates.py, which run against the text the referee
was actually shown: the evidence quote must be a literal substring of the source,
every number in the claim must appear in the decomposition, and each numeric
element's inequality is recomputed arithmetically rather than taken on trust.
Both referees must pass every gate.

The two routes are reported SEPARATELY, because they are different claims:

  R1  achieved elsewhere      an empirical claim about the world: some other
                              group did this before the target date. This is
                              Reviewer 2's concern, and the route where a judge
                              can be talked into a match.
  R2  perturbation did not    a claim about the item itself: the question text,
      bind                    read literally, is satisfied by the source paper's
                              own published result, so the NO label is wrong
                              regardless of what anyone else did. Provable from
                              the paper in front of you, not from a search.

Also reported: undecidable claims, which carry an element that can be neither
verified nor falsified. Those are not wrong labels; they are unusable items.

Four referees were run. The headline pair is Claude Sonnet 5 + Claude Opus 4.8;
GPT-5.5 and GPT-5.4-mini are reported as a cross-check. Every referee and every
pairing appears in t20/t21, so the headline never rests on an unstated choice.
"""
from __future__ import annotations
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C
import gates as G
from analyze1 import fmt, pct, write_table, load, load_adj

# Primary pair: Sonnet 5 (the cheap referee) with one larger referee that has a
# measured zero verbatim-quote failure rate. GPT-5.4-mini was trialled and is
# reported in t20/t21, but it fails the quote gate on 62% of its own proposals --
# it quotes the claim instead of the source, and stitches fragments -- so making
# it a required co-signer suppresses the count for a model-capability reason
# rather than because the items are sound.
REFS = ("sonnet5", "opus48")             # primary
XREFS = ("gpt55", "gpt54mini")           # cross-check


def load_refused(kind: str) -> list[dict]:
    """Items the first web pass declined outright. A refusal is not a judgement, so
    they carry no first-pass verdict -- but the closed-book strict referees may
    still have decided them, and where they did the item belongs in this table."""
    name = {"negatives": "negatives_verdicts.jsonl"}[kind]
    by = {}
    for r in C.read_jsonl(C.S1 / name):
        by[r["id"]] = r
    return [r for r in by.values()
            if r.get("refused") or r.get("verdict") == "REFUSED"
            or (not r.get("verdict") and r.get("stop_reason") == "refusal")]


def load_strict(mode: str, ref: str) -> dict:
    by = {}
    for r in C.read_jsonl(C.S1 / f"strict_{mode}_{ref}.jsonl"):
        if r.get("verdict"):
            by[r["id"]] = r
    return by


def main() -> None:
    neg = load("negatives")
    # An item the first web pass refused still belongs here if the strict referees
    # -- which are closed-book and see a different prompt -- did decide it. And one
    # item is blocked by every provider's biological-risk classifier, so it was
    # replaced by a same-stratum draw (replace.py); drop the id it stands in for.
    _reps, _replaced = C.load_replacements()
    _bind_ids = set()
    for _r in REFS:
        _bind_ids |= {x["id"] for x in C.read_jsonl(C.S1 / f"strict_binding_{_r}.jsonl")
                      if x.get("verdict")}
    _seen = {it["id"] for it in neg}
    neg = [it for it in neg if it["id"] not in _replaced]
    neg += [r for r in load_refused("negatives")
            if r["id"] in _bind_ids and r["id"] not in _seen and r["id"] not in _replaced]
    by_id = {it["id"]: it for it in neg}
    corp = C.load_corpus()
    # the verdict records carry no question text; take it from the stored sample
    sample0 = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    CLAIM = {i["id"]: i["binary_question_perturbed"] for i in sample0["negatives"]["items"]}
    CLAIM |= {r["id"]: r["binary_question_perturbed"] for r in _reps}
    bind = {r: load_strict("binding", r) for r in REFS + XREFS}
    ach = {r: load_strict("achieved", r) for r in REFS + XREFS}
    C.TABLES.mkdir(parents=True, exist_ok=True)
    strat = lambda it: "|".join(it["stratum"])

    def claim(i):
        return CLAIM.get(i, "")

    def gate_for(rec, mode, i):
        return G.gate_results(rec, mode, claim(i),
                              G.source_text_for(corp[i]) if mode == "binding" else "",
                              by_id[i].get("target_ym"))

    def cert(rec, mode, i):
        return bool(rec) and all(gate_for(rec, mode, i).values())

    def route(mode, refs, i):
        recs = [bind[r].get(i) if mode == "binding" else ach[r].get(i) for r in refs]
        present = [x for x in recs if x]
        if len(present) < 2:
            return "NOT_RUN" if not present else "INCOMPLETE"
        if all(cert(x, mode, i) for x in present):
            return "CERTIFIED"
        if any(cert(x, mode, i) for x in present):
            return "SPLIT"
        if all(x.get("verdict") == "UNDECIDABLE" for x in present):
            return "UNDECIDABLE"
        return "STANDS"

    T = {i: dict(r1=route("achieved", REFS, i), r2=route("binding", REFS, i),
                 x1=route("achieved", XREFS, i), x2=route("binding", XREFS, i))
         for i in by_id}

    def rate_row(label, flag, note=""):
        k = sum(1 for it in neg if flag(it["id"]))
        n = len(neg)
        lo, hi = C.wilson(k, n)
        w = (sum(it["weight"] for it in neg if flag(it["id"]))
             / sum(it["weight"] for it in neg))
        wlo, whi = C.strat_boot_ci(neg, lambda s, f=flag: (
            sum(x["weight"] for x in s if f(x["id"])) / max(sum(x["weight"] for x in s), 1e-9)),
            strat, seed=808)
        return [label, n, k, fmt(k / n), fmt(lo), fmt(hi), fmt(w), fmt(wlo), fmt(whi), note]

    rows = [
        rate_row("R1 achieved elsewhere (certified)", lambda i: T[i]["r1"] == "CERTIFIED",
                 "empirical; Reviewer 2's concern"),
        rate_row("R2 perturbation did not bind (certified)", lambda i: T[i]["r2"] == "CERTIFIED",
                 "provable from the source paper alone"),
        rate_row("Either route (certified)",
                 lambda i: "CERTIFIED" in (T[i]["r1"], T[i]["r2"]), "do not quote without both above"),
        rate_row("One referee only (split)",
                 lambda i: "CERTIFIED" not in (T[i]["r1"], T[i]["r2"])
                 and "SPLIT" in (T[i]["r1"], T[i]["r2"]), "human review"),
        rate_row("Undecidable claim",
                 lambda i: "CERTIFIED" not in (T[i]["r1"], T[i]["r2"])
                 and "SPLIT" not in (T[i]["r1"], T[i]["r2"])
                 and "UNDECIDABLE" in (T[i]["r1"], T[i]["r2"]), "unusable, separate defect"),
        rate_row("Sound", lambda i: T[i]["r1"] in ("STANDS", "NOT_RUN") and T[i]["r2"] == "STANDS"),
    ]
    write_table(C.TABLES / "t13_strict_tiers",
                ["category", "n", "k", "rate", "ci_lo", "ci_hi", "weighted", "w_lo", "w_hi", "note"],
                rows, "Mislabelled synthetic negatives: two routes, reported separately")

    # ---- what each gate rejects -------------------------------------------------
    gr = []
    for mode, refs in (("binding", REFS), ("achieved", REFS)):
        src = bind if mode == "binding" else ach
        for ref in refs:
            prop = [(i, r) for i, r in src[ref].items()
                    if r.get("verdict") == "WRONG_LABEL" and i in by_id]
            fails = Counter()
            passed = 0
            for i, r in prop:
                g = gate_for(r, mode, i)
                if all(g.values()):
                    passed += 1
                for k2, v in g.items():
                    if not v:
                        fails[k2] += 1
            gr.append([mode, ref, len(prop), passed,
                       "; ".join(f"{k2}={v}" for k2, v in fails.most_common()) or "none"])
    write_table(C.TABLES / "t18_gate_attribution",
                ["route", "referee", "proposed_WRONG_LABEL", "survived_all_gates", "gate_failures"],
                gr, "What the mechanical gates reject, per referee")

    # ---- cheap vs expensive referee pair ----------------------------------------
    xr = []
    for name, a, b in (("R1 achieved elsewhere", "r1", "x1"),
                       ("R2 perturbation did not bind", "r2", "x2")):
        ca = sum(1 for i in by_id if T[i][a] == "CERTIFIED")
        cb = sum(1 for i in by_id if T[i][b] == "CERTIFIED")
        both = sum(1 for i in by_id if T[i][a] == "CERTIFIED" and T[i][b] == "CERTIFIED")
        agree = sum(1 for i in by_id
                    if (T[i][a] == "CERTIFIED") == (T[i][b] == "CERTIFIED"))
        xr.append([name, ca, cb, both, f"{agree}/{len(by_id)}", fmt(agree / len(by_id))])
    write_table(C.TABLES / "t19_referee_crosscheck",
                ["route", "cheap_pair_certified", "expensive_pair_certified",
                 "certified_by_both_pairs", "agreement", "agreement_rate"], xr,
                "Primary pair against the cross-check pair, gates applied to both")

    # ---- every referee, and every pair, with nothing hidden ---------------------
    import itertools
    ALL = REFS + XREFS
    certset = {}
    for mode in ("binding", "achieved"):
        src = bind if mode == "binding" else ach
        for r in ALL:
            certset[(mode, r)] = {i for i, rec in src[r].items()
                                  if i in by_id and cert(rec, mode, i)}
    solo = []
    for r in ALL:
        qf = tot = 0
        for i, rec in bind[r].items():
            if i in by_id and rec.get("verdict") == "WRONG_LABEL":
                tot += 1
                qf += not gate_for(rec, "binding", i)["quotes_in_source"]
        solo.append([r, len(certset[("achieved", r)]), len(certset[("binding", r)]),
                     f"{qf}/{tot}", fmt(qf / tot) if tot else ""])
    write_table(C.TABLES / "t20_referee_matrix",
                ["referee", "R1_certified", "R2_certified",
                 "verbatim_quote_failures", "quote_failure_rate"], solo,
                "Each referee alone, after the mechanical gates")
    pr = []
    for a, b in itertools.combinations(ALL, 2):
        pr.append([f"{a} + {b}",
                   len(certset[("achieved", a)] & certset[("achieved", b)]),
                   len(certset[("binding", a)] & certset[("binding", b)])])
    pr.append(["all four referees",
               len(set.intersection(*[certset[("achieved", r)] for r in ALL])),
               len(set.intersection(*[certset[("binding", r)] for r in ALL]))])
    pr.append(["any one referee",
               len(set.union(*[certset[("achieved", r)] for r in ALL])),
               len(set.union(*[certset[("binding", r)] for r in ALL]))])
    write_table(C.TABLES / "t21_referee_pairs",
                ["referee set", "R1_certified", "R2_certified"], pr,
                "Items certified by each pair of referees, out of 198")

    # ---- by perturbation type ---------------------------------------------------
    bt = []
    for name, flag in (("R1 achieved elsewhere", lambda i: T[i]["r1"] == "CERTIFIED"),
                       ("R2 did not bind", lambda i: T[i]["r2"] == "CERTIFIED"),
                       ("undecidable", lambda i: "CERTIFIED" not in (T[i]["r1"], T[i]["r2"])
                        and "SPLIT" not in (T[i]["r1"], T[i]["r2"])
                        and "UNDECIDABLE" in (T[i]["r1"], T[i]["r2"]))):
        g = defaultdict(list)
        for it in neg:
            g[it["ptype"]].append(flag(it["id"]))
        for k2 in sorted(g):
            v = g[k2]
            kk = sum(v)
            lo, hi = C.wilson(kk, len(v))
            bt.append([name, k2, len(v), kk, fmt(kk / len(v)), fmt(lo), fmt(hi)])
    write_table(C.TABLES / "t15_strict_by_ptype",
                ["category", "perturbation_type", "n", "k", "rate", "ci_lo", "ci_hi"], bt,
                "Strict rates by perturbation type")

    # ---- extrapolation ----------------------------------------------------------
    N = sample0["frames"]["negative"]
    ex = []
    for label, flag in (("R1 achieved elsewhere", lambda i: T[i]["r1"] == "CERTIFIED"),
                        ("R2 perturbation did not bind", lambda i: T[i]["r2"] == "CERTIFIED"),
                        ("Either route", lambda i: "CERTIFIED" in (T[i]["r1"], T[i]["r2"])),
                        ("Undecidable", lambda i: "CERTIFIED" not in (T[i]["r1"], T[i]["r2"])
                         and "SPLIT" not in (T[i]["r1"], T[i]["r2"])
                         and "UNDECIDABLE" in (T[i]["r1"], T[i]["r2"]))):
        w = (sum(it["weight"] for it in neg if flag(it["id"])) / sum(it["weight"] for it in neg))
        lo, hi = C.strat_boot_ci(neg, lambda s, f=flag: (
            sum(x["weight"] for x in s if f(x["id"])) / max(sum(x["weight"] for x in s), 1e-9)),
            strat, seed=909)
        ex.append([label, pct(w), pct(lo), pct(hi), f"{w*N:.0f}", f"{lo*N:.0f}", f"{hi*N:.0f}"])
    write_table(C.TABLES / "t16_strict_extrapolation",
                ["quantity", "rate", "ci_lo", "ci_hi", "items", "lo", "hi"], ex,
                f"Strict rates scaled to the {N} negatives in the corpus")

    # ---- corrected accuracy on the certified set --------------------------------
    dem = {i for i in by_id if "CERTIFIED" in (T[i]["r1"], T[i]["r2"])}
    pa = C.load_panel_answers()
    pos = load("positives")
    adj_p = load_adj("positives")
    unconf = {it["id"] for it in pos if it["verdict"] != "CONFIRMED"
              and adj_p.get(it["id"], {}).get("verdict") != "FOUND"}
    ca = []
    for m in C.MODEL_ORDER:
        base = [("pos", it["id"], pa[(m, it["id"], "binary")]["correct"])
                for it in pos if (m, it["id"], "binary") in pa]
        base += [("neg", it["id"], pa[(m, it["id"], "binary_perturbed")]["correct"])
                 for it in neg if (m, it["id"], "binary_perturbed") in pa]
        pub = [c for _, _, c in base]
        rel = [(not c) if (k == "neg" and i in dem) else c for k, i, c in base]
        keep = [c for k, i, c in base
                if not (k == "neg" and i in dem) and not (k == "pos" and i in unconf)]
        a1, a3 = sum(pub) / len(pub), sum(rel) / len(rel)
        l1, h1 = C.wilson(sum(pub), len(pub))
        l3, h3 = C.wilson(sum(rel), len(rel))
        ca.append([C.MODELS[m]["name"], len(pub), fmt(a1), fmt(l1), fmt(h1),
                   len(keep), fmt(sum(keep) / len(keep)),
                   len(rel), fmt(a3), fmt(l3), fmt(h3), fmt(a3 - a1)])
    write_table(C.TABLES / "t17_corrected_accuracy_strict",
                ["model", "n", "acc_published", "pub_lo", "pub_hi", "n_excl",
                 "acc_excluding_certified", "n_relab", "acc_relabelled_strict",
                 "relab_lo", "relab_hi", "delta"], ca,
                "Binary accuracy corrected on the certified set only")

    # ---- per-item sheet ---------------------------------------------------------
    with open(C.S1 / "strict_verdicts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "domain", "perturbation_type", "R1_achieved", "R2_did_not_bind",
                    "R1_expensive_pair", "R2_expensive_pair"]
                   + [f"{r}_{m}_verdict" for m in ("binding", "achieved") for r in REFS]
                   + [f"{r}_binding_failed_gates" for r in REFS] + ["sonnet5_reason"])
        for it in neg:
            i = it["id"]
            fg = []
            for r in REFS:
                rec = bind[r].get(i)
                if rec and rec.get("verdict") == "WRONG_LABEL":
                    g = gate_for(rec, "binding", i)
                    fg.append(";".join(k2 for k2, v in g.items() if not v) or "none")
                else:
                    fg.append("")
            w.writerow([i, it["main_area"], it["ptype"], T[i]["r1"], T[i]["r2"],
                        T[i]["x1"], T[i]["x2"]]
                       + [(bind[r].get(i) or {}).get("verdict", "") for r in REFS]
                       + [(ach[r].get(i) or {}).get("verdict", "") for r in REFS]
                       + fg + [((bind["sonnet5"].get(i) or {}).get("reason", ""))[:300]])

    out = dict(
        n_negatives=len(neg), referees=list(REFS), crosscheck=list(XREFS),
        r1_certified=sum(1 for i in by_id if T[i]["r1"] == "CERTIFIED"),
        r2_certified=sum(1 for i in by_id if T[i]["r2"] == "CERTIFIED"),
        either=len(dem),
        undecidable=sum(1 for i in by_id if "CERTIFIED" not in (T[i]["r1"], T[i]["r2"])
                        and "SPLIT" not in (T[i]["r1"], T[i]["r2"])
                        and "UNDECIDABLE" in (T[i]["r1"], T[i]["r2"])),
        tiers=dict(Counter(("CERTIFIED" if "CERTIFIED" in (T[i]["r1"], T[i]["r2"]) else
                            "SPLIT" if "SPLIT" in (T[i]["r1"], T[i]["r2"]) else
                            "UNDECIDABLE" if "UNDECIDABLE" in (T[i]["r1"], T[i]["r2"]) else "SOUND")
                           for i in by_id)),
        frame_negative=N)
    (C.S1 / "strict_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
