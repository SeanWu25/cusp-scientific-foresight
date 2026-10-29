"""
sample.py — draw the Study 1 and Study 2 samples (read-only over the corpora).

Study 1 (verification)
  positives : 200 events carrying `binary_question`            (frame N=2951)
  negatives : 200 events carrying `binary_question_perturbed`  (frame N=4305)
Study 2 (detection)
  pairs     : 500 events carrying BOTH questions               (frame N=2289)

Allocation is stratified on main_area x perturbation type, proportional to the
stratum size with largest-remainder rounding and a floor so that every non-empty
cell is represented. Horvitz-Thompson weights (N_h / n_h) are stored per item so
the overall rate can be reported design-weighted as well as unweighted.

Positives have no perturbation type of their own; they inherit the type of the
same event's perturbed twin, and events with no twin form a third stratum level
('unpaired') so that the whole positive frame stays in scope.
"""
from __future__ import annotations
import json, random, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

SEED_POS, SEED_NEG, SEED_PAIR = 20260920, 20260921, 20260922
N_POS, N_NEG, N_PAIR = 200, 200, 500
FLOOR_S1, FLOOR_S2 = 2, 4


def allocate(sizes: dict, total: int, floor: int) -> dict:
    """Largest-remainder proportional allocation with a per-cell floor."""
    cells = {k: v for k, v in sizes.items() if v > 0}
    base = {k: min(floor, cells[k]) for k in cells}
    rest = total - sum(base.values())
    if rest < 0:                                    # floor alone overshoots
        order = sorted(cells, key=lambda k: -cells[k])
        base = {k: 0 for k in cells}
        for k in order[:total]:
            base[k] = 1
        return base
    pool = sum(cells.values()) - sum(base.values())
    quota, out = {}, dict(base)
    if pool > 0:
        for k in cells:
            head = cells[k] - base[k]
            quota[k] = rest * head / pool
        for k in cells:
            add = min(int(quota[k]), cells[k] - out[k])
            out[k] += add
        left = total - sum(out.values())
        frac = sorted(cells, key=lambda k: (-(quota[k] - int(quota[k])), -cells[k], k))
        i = 0
        while left > 0 and i < len(frac) * 40:
            k = frac[i % len(frac)]
            if out[k] < cells[k]:
                out[k] += 1
                left -= 1
            i += 1
    return out


def draw(frame: list, key, total: int, floor: int, seed: int) -> tuple[list, dict]:
    strata = defaultdict(list)
    for r in frame:
        strata[key(r)].append(r)
    for k in strata:
        strata[k].sort(key=lambda r: r["id"])           # deterministic order
    sizes = {k: len(v) for k, v in strata.items()}
    alloc = allocate(sizes, total, floor)
    rng = random.Random(seed)
    picked = []
    for k in sorted(strata):
        n = alloc.get(k, 0)
        if n:
            for r in rng.sample(strata[k], n):
                r = dict(r)
                r["_stratum"] = list(k) if isinstance(k, tuple) else [k]
                r["_stratum_N"] = sizes[k]
                r["_stratum_n"] = n
                r["_weight"] = sizes[k] / n
                picked.append(r)
    picked.sort(key=lambda r: r["id"])
    return picked, {"strata_sizes": {"|".join(map(str, k)): v for k, v in sorted(sizes.items())},
                    "allocation": {"|".join(map(str, k)): v for k, v in sorted(alloc.items())}}


def slim(r: dict, kind: str) -> dict:
    out = dict(
        id=r["id"], corpus=r["corpus"], main_area=r.get("main_area"),
        sub_categories=r.get("sub_categories"), source=r.get("source"),
        publication_date=r.get("publication_date"),
        target_ym=r.get("target_ym"), target_human=r.get("target_human"),
        paper_link=r.get("paper_link"), ptype=r.get("ptype"),
        stratum=r["_stratum"], stratum_N=r["_stratum_N"], stratum_n=r["_stratum_n"],
        weight=r["_weight"], kind=kind,
    )
    if kind in ("positive", "pair"):
        out["binary_question"] = r.get("binary_question")
    if kind in ("negative", "pair"):
        out["binary_question_perturbed"] = r.get("binary_question_perturbed")
        out["binary_perturbation_detail"] = r.get("binary_perturbation_detail")
    if kind == "negative":
        out["problem_statement"] = (r.get("problem_statement") or "")[:600]
    return out


def main() -> None:
    corp = C.load_corpus()
    recs = list(corp.values())
    pos_frame = [r for r in recs if (r.get("binary_question") or "").strip()]
    neg_frame = [r for r in recs if (r.get("binary_question_perturbed") or "").strip()]
    pair_frame = [r for r in recs if (r.get("binary_question") or "").strip()
                  and (r.get("binary_question_perturbed") or "").strip()]

    pos_key = lambda r: (r.get("main_area") or "Unknown", r.get("ptype") or "unpaired")
    npt_key = lambda r: (r.get("main_area") or "Unknown", r["ptype"])

    pos, pos_meta = draw(pos_frame, pos_key, N_POS, FLOOR_S1, SEED_POS)
    neg, neg_meta = draw(neg_frame, npt_key, N_NEG, FLOOR_S1, SEED_NEG)
    pair, pair_meta = draw(pair_frame, npt_key, N_PAIR, FLOOR_S2, SEED_PAIR)

    rng = random.Random(SEED_PAIR + 1)
    pairs = []
    for r in pair:
        o = C.strip_dates(r["binary_question"])
        p = C.strip_dates(r["binary_question_perturbed"])
        first = rng.choice(["original", "perturbed"])
        pairs.append(dict(
            slim(r, "pair"),
            claim_original=o, claim_perturbed=p,
            len_original=len(o), len_perturbed=len(p),
            canonical_first=first,                       # stored primary presentation order
            numbers_differ=bool(r.get("numbers_differ")),
        ))

    C.S1.mkdir(parents=True, exist_ok=True)
    C.S2.mkdir(parents=True, exist_ok=True)

    s1 = dict(
        study="study1_verification",
        generated_utc=C.now_utc(), git_sha=C.git_sha(),
        frames=dict(positive=len(pos_frame), negative=len(neg_frame), corpus=len(recs)),
        seeds=dict(positives=SEED_POS, negatives=SEED_NEG),
        allocation_rule=f"largest-remainder proportional, floor={FLOOR_S1} per non-empty cell",
        stratifier="main_area x perturbation_type (positives use the twin's type; 'unpaired' if none)",
        positives=dict(n=len(pos), **pos_meta, items=[slim(r, "positive") for r in pos]),
        negatives=dict(n=len(neg), **neg_meta, items=[slim(r, "negative") for r in neg]),
    )
    (C.S1 / "sample.json").write_text(json.dumps(s1, indent=2, ensure_ascii=False), encoding="utf-8")

    s2 = dict(
        study="study2_detection",
        generated_utc=C.now_utc(), git_sha=C.git_sha(),
        frame=len(pair_frame), seed=SEED_PAIR, order_seed=SEED_PAIR + 1,
        allocation_rule=f"largest-remainder proportional, floor={FLOOR_S2} per non-empty cell",
        stratifier="main_area x perturbation_type",
        n=len(pairs), **pair_meta, pairs=pairs,
    )
    (C.S2 / "pairs.json").write_text(json.dumps(s2, indent=2, ensure_ascii=False), encoding="utf-8")

    ids_p, ids_n, ids_pr = {r["id"] for r in pos}, {r["id"] for r in neg}, {r["id"] for r in pairs}
    print(f"positives {len(pos):4d} / frame {len(pos_frame)}   cells {len(pos_meta['allocation'])}")
    print(f"negatives {len(neg):4d} / frame {len(neg_frame)}   cells {len(neg_meta['allocation'])}")
    print(f"pairs     {len(pairs):4d} / frame {len(pair_frame)}  cells {len(pair_meta['allocation'])}")
    print(f"overlap pos/neg {len(ids_p & ids_n)}  pos/pairs {len(ids_p & ids_pr)}  neg/pairs {len(ids_n & ids_pr)}")
    print("\nnegatives by area x ptype:")
    for k, v in sorted(Counter("|".join(map(str, r["_stratum"])) for r in neg).items()):
        print(f"  {k:42s} {v:3d}  (frame {neg_meta['strata_sizes'][k]})")


if __name__ == "__main__":
    main()
