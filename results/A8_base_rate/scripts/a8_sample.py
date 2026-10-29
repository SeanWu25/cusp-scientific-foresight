"""a8_sample.py — draw and freeze the 500-event sample (seed recorded). Idempotent:
refuses to overwrite an existing sample.json with different ids."""
import json, random, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a8_common as C

cand = C.candidates()
ids = sorted(random.Random(C.SEED).sample(cand, 500))
b = C.load_bench()
ext_ids = {json.loads(l)["id"] for l in open(C.BENCH[1]) if l.strip()}
s = dict(seed=C.SEED, n=500, sampler="random.Random(seed).sample(sorted(candidate_ids), 500); ids then sorted",
         candidate_pool="events of the full CUSP corpus (original 4,760 + extension 815) carrying BOTH binary_question and binary_question_perturbed",
         n_candidates=len(cand), n_from_extension=sum(i in ext_ids for i in ids),
         main_area_counts=dict(collections.Counter(b[i]["main_area"] for i in ids).most_common()),
         source_counts=dict(collections.Counter(b[i].get("source") for i in ids).most_common()),
         publication_month_range=[min(b[i]["publication_date"] for i in ids), max(b[i]["publication_date"] for i in ids)],
         ids=ids,
         events={i: dict(publication_date=b[i]["publication_date"], main_area=b[i]["main_area"], source=b[i].get("source"),
                         half=("extension" if i in ext_ids else "original")) for i in ids})
if C.SAMPLE.exists():
    old = json.load(open(C.SAMPLE))
    assert old["ids"] == ids and old["seed"] == C.SEED, "sample.json exists with different ids — refusing to overwrite"
    print("sample.json unchanged"); sys.exit(0)
json.dump(s, open(C.SAMPLE, "w"), indent=1)
print(f"wrote {C.SAMPLE}: seed={C.SEED} n=500 of {len(cand)} candidates; {s['n_from_extension']} from the extension half")
