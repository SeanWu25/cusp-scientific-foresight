"""
replace.py — substitute a sampled item that NO verifier can decide.

One negative in the Study 1 sample is a claim about H5N1 titres in milk. Every
provider's biological-risk classifier hard-blocks it: the first verifier
(Claude Opus 4.8) refused, both strict referees refused, the closed-book
soundness pass refused, and the second-provider adjudicator (GPT-5.5) returned a
400 flagged for possible biological risk. That is the classifier working as
intended and we do not try to route around it -- no model-shopping, no
rephrasing to slip past a safety check.

The item therefore cannot be verified by any instrument we have, which is a
different situation from "we searched and found nothing". Leaving it in shrinks
the denominator below the drawn 200 and silently; replacing it keeps the sample
at its designed size and puts the substitution on the record.

What this does NOT do: touch sample.json. The original draw, its seed and its
item list stay exactly as they were, so the sampling story remains auditable.
The substitution lives in its own file, names the item it replaces and why, and
is drawn from the SAME stratum with its own recorded seed, so the stratified
design is preserved.

  python replace.py --dry-run     # show what would be drawn
  python replace.py               # write replacements.json
"""
from __future__ import annotations
import argparse, json, random, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

SEED_REPLACE = 20260924
OUT = C.S1 / "replacements.json"

BLOCKED = "no verifier could decide it: every provider's biological-risk classifier blocks the claim"


def settled_negatives() -> tuple[set, set]:
    """(ids with a usable verdict from any pass, all sampled negative ids)"""
    s = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    ids = {i["id"] for i in s["negatives"]["items"]}
    ok = set()
    for r in C.read_jsonl(C.S1 / "negatives_verdicts.jsonl"):
        if r.get("verdict") in ("ACHIEVED", "NOT_ACHIEVED"):
            ok.add(r["id"])
    for r in C.read_jsonl(C.S1 / "adjudication_negatives.jsonl"):
        if r.get("verdict") in ("ACHIEVED", "NOT_ACHIEVED", "UNCERTAIN"):
            ok.add(r["id"])
    for f in ("strict_binding_sonnet5.jsonl", "strict_binding_opus48.jsonl"):
        for r in C.read_jsonl(C.S1 / f):
            if r.get("verdict"):
                ok.add(r["id"])
    return ok & ids, ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    s = json.loads((C.S1 / "sample.json").read_text(encoding="utf-8"))
    by = {i["id"]: i for i in s["negatives"]["items"]}
    ok, ids = settled_negatives()
    stuck = sorted(ids - ok)
    if not stuck:
        print("every sampled negative has a verdict from some pass; nothing to replace")
        return

    corp = C.load_corpus()
    frame = [r for r in corp.values() if (r.get("binary_question_perturbed") or "").strip()]
    rng = random.Random(SEED_REPLACE)
    out, used = [], set(ids)
    for sid in stuck:
        it = by[sid]
        area, pt = it["stratum"][0], it["stratum"][1]
        pool = sorted((r for r in frame
                       if (r.get("main_area") or "Unknown") == area and r.get("ptype") == pt
                       and r["id"] not in used), key=lambda r: r["id"])
        if not pool:
            print(f"  !! no replacement available in stratum {area}|{pt} for {sid[:8]}")
            continue
        pick = rng.choice(pool)
        used.add(pick["id"])
        out.append(dict(
            replaces=sid, replaces_claim=it["binary_question_perturbed"],
            reason=BLOCKED, stratum=[area, pt],
            id=pick["id"], corpus=pick["corpus"], main_area=pick.get("main_area"),
            publication_date=pick.get("publication_date"),
            target_ym=pick.get("target_ym"), target_human=pick.get("target_human"),
            paper_link=pick.get("paper_link"), ptype=pick.get("ptype"),
            stratum_N=it["stratum_N"], stratum_n=it["stratum_n"], weight=it["weight"],
            kind="negative",
            binary_question_perturbed=pick.get("binary_question_perturbed"),
            binary_perturbation_detail=pick.get("binary_perturbation_detail"),
            problem_statement=(pick.get("problem_statement") or "")[:600],
            pool_size=len(pool)))
        print(f"  {sid[:8]} [{area}|{pt}] -> {pick['id'][:8]}  (drawn from {len(pool)} in stratum)")
        print(f"      out: {it['binary_question_perturbed'][:110]}")
        print(f"      in : {(pick.get('binary_question_perturbed') or '')[:110]}")

    if a.dry_run:
        print("\n--dry-run: nothing written")
        return
    OUT.write_text(json.dumps(dict(
        generated_utc=C.now_utc(), git_sha=C.git_sha(), seed=SEED_REPLACE,
        rule="same main_area x perturbation_type stratum, uniform over items not already "
             "sampled, inheriting the replaced item's Horvitz-Thompson weight so the "
             "design weighting is unchanged",
        note="sample.json is NOT modified; the original draw stays auditable",
        n=len(out), replacements=out), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT} ({len(out)} replacement(s))")


if __name__ == "__main__":
    main()
