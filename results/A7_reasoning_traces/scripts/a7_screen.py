"""a7_screen.py — keyword screens to surface candidate positive examples per deductive code (for the
codebook's real examples; NOT used for coding). Prints a few random hits per code from base traces."""
import json, re, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C
PAT = {
 "BASE_RATE": r"\b(base rate|historically|most (such|similar) (claims|efforts|attempts)|rarely|typically (take|achieve)|track record|prior probability|the majority of)\b",
 "HYPOTHESIS_COMPARISON": r"\b(alternatively|on the other hand|versus|whereas|either .* or|more likely than|rather than|compared to option|option [A-D] .*(but|while) option)\b",
 "EVIDENCE_CITED": r"\b(20(1|2)\d\)|et al\.|reported (a|an|that)|achieved \d|arxiv|published|benchmark score of|\d{2,3}(\.\d)?%)",
 "KNOWLEDGE_GAP_ADMITTED": r"\b(i am not aware|i'm not aware|not aware of|no (known|published|documented)|unaware|i (do not|don't) (know|have)|no evidence|cannot recall|to my knowledge)\b",
 "ABSENCE_AS_EVIDENCE": r"\b(no (published|known|reported|documented|existing) (work|method|study|result|system|evidence)|has not (yet )?been (demonstrated|achieved|reported|shown)|not yet (achieved|demonstrated|reported)|as of (my|the) (knowledge|training)|no reports? of)\b",
 "CONSTRAINT_CHECKED": r"\b(threshold|at least \d|exceed|the (specific|stated|required) (number|value|level|target)|the bar of|requires? (achieving|reaching)|specific(ally)? \d)\b",
 "RATE_OF_PROGRESS": r"\b(pace|rate of progress|trajectory|trend|every (year|\d+ months)|per year|doubling|extrapolat|typically takes \d|(\d+|several|a few) (years|months) (from|after|to))\b",
 "ROUND_ANCHOR": r"\b(late 20\d0s|early 20\d0s|mid[- ]20\d0s|by 2030|around 2030|within (the|this) decade|next decade|end of the decade|20[23]0\b)",
 "CUTOFF_REFERENCED": r"\b(knowledge cutoff|training (data|cutoff)|my (training|knowledge)|as of (my|20\d\d)|up to (my|20\d\d)|current knowledge)\b",
 "DIFFICULTY_APPEAL": r"\b(challenging|difficult|hard|complex|ambitious|significant (hurdle|barrier|challenge)|non-?trivial|demanding|formidable)\b",
 "HEDGING": r"\b(may|might|could|possibly|perhaps|uncertain|likely|plausible|it is possible|not certain|unclear)\b",
}
rng = random.Random(3)
hits = {k: [] for k in PAT}; n = 0
for r in C.iter_traces(lambda r: r["condition"] == "base" and not r["trace_is_raw_json"]):
    n += 1
    for k, p in PAT.items():
        if re.search(p, r["trace"], re.I):
            if len(hits[k]) < 4000 and rng.random() < 0.05: hits[k].append(r)
            hits.setdefault(k + "__n", 0); hits[k + "__n"] += 1
print("traces screened:", n)
for k in PAT:
    print(f"\n######## {k}: ~{hits[k + '__n']} keyword hits ({100 * hits[k + '__n'] / n:.1f}%)")
    for r in rng.sample(hits[k], min(4, len(hits[k]))):
        print(f"  [{r['task']} | {r['model']} | correct={r['correct']} | ans={r.get('parsed_answer')} gt={r.get('ground_truth')}] {r['trace'][:420]}")
