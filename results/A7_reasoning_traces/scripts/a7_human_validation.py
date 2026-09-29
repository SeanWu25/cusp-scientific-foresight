"""a7_human_validation.py — build human_validation.csv for three annotators.

Design. 300 traces, stratified across model x task x code. A trace contributes one row per code
that is IN SCOPE for it, which keeps the sheet to a size three people can actually complete:
  * every code the two LLM coders disagreed on (the cases most in need of a human ruling),
  * every code at least one coder marked present,
  * two codes neither coder marked, drawn at random, so the sheet contains true negatives and the
    human-vs-LLM comparison is not conditioned on a positive LLM label.
Rows are blind: the annotator sees the question, the passage and the code definition, and not the
answer, the model, the condition, the outcome or either coder's verdict.

Assignment: three annotators. A shared block of 20% of rows goes to all three (inter-rater
reliability); the rest is split evenly. Written as one CSV plus a codebook sheet.
"""
import csv, json, random, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P, a7_stats as S

SEED = 23
N_TRACES = 300
N_NEG = 2
OVERLAP = 0.20
SHORT = {
 "BASE_RATE": "Reasons explicitly about how often this KIND of result occurs (a reference class, a historical frequency, a prior). A bare 'unlikely' does not count.",
 "HYPOTHESIS_COMPARISON": "Weighs TWO OR MORE named candidate outcomes, mechanisms or options against each other. Naming one and stopping does not count.",
 "EVIDENCE_CITED": "References specific prior work: a named system, dataset, venue, or a concrete number that did NOT come from the question.",
 "KNOWLEDGE_GAP_ADMITTED": "States in the FIRST PERSON that it does not know or is not aware of relevant work. A claim that the literature lacks something is not this code.",
 "ABSENCE_AS_EVIDENCE": "INFERS from the absence of known work that the thing has not happened, will not happen, or will happen later. The inference must do work toward the conclusion.",
 "CONSTRAINT_CHECKED": "Names the question's specific figure, date or added condition AND says something about whether it can be met. Delete the figure: if the argument is unchanged, do not code it.",
 "RATE_OF_PROGRESS": "DERIVES a timeline from a stated pace: a rate, an interval, an extrapolation that yields the date or the feasibility.",
 "ROUND_ANCHOR": "Reasons toward a ROUND or decade-level target for the prediction ('late 2020s', 'by 2030'). A year used to date past work does not count.",
 "CUTOFF_REFERENCED": "Mentions ITS OWN knowledge cutoff, training date or training data as a bound on what it can know.",
 "DIFFICULTY_APPEAL": "Offers complexity, difficulty or the scale of what would be required AS A REASON for the conclusion.",
 "SPECIFICITY_AS_IMPLAUSIBLE": "Treats the unusual precision or specificity OF THE QUESTION ITSELF as evidence the claim is unlikely, speculative or not real.",
 "PROVENANCE_INFERRED": "Asserts the question corresponds to a PARTICULAR real piece of work: names it, dates it, places it in a venue, or says it describes a published study.",
 "CONJUNCTION_BURDEN": "Enumerates TWO OR MORE separate requirements and uses that multiplicity in the argument.",
 "FIELD_MOMENTUM": "Generic appeal to the speed or activity of the field, with NO interval and NO derivation.",
 "RESTATEMENT_ONLY": "Paraphrases the question and adds nothing else: no evidence, mechanism, comparison, rate or assessment of the threshold.",
 "HEDGING": "Degree of hedging, 0-3. 0 = flat assertion. 1 = one hedge. 2 = multiple hedges or explicit uncertainty alongside a conclusion. 3 = declines to commit.",
}


def main():
    rows, coders = S.load_labels()
    per = collections.defaultdict(dict)
    for l in open(C.STUDY / "coded_traces.jsonl", encoding="utf-8"):
        d = json.loads(l); per[d["trace_id"]][d["code"]] = per[d["trace_id"]].get(d["code"], []) + [d]
    traces = {r["trace_id"]: r for r in C.iter_traces(lambda r: r["trace_id"] in per)}
    rng = random.Random(SEED)
    # stratify: model x task, then prefer traces that carry at least one positive or one disagreement
    cells = collections.defaultdict(list)
    for tid, codes in per.items():
        t = traces.get(tid)
        if not t: continue
        pos = [c for c, v in codes.items() if any(x["verdict"] == "yes" for x in v)]
        dis = [c for c, v in codes.items() if len({str(x["verdict"]) for x in v}) > 1]
        cells[(t["model"], t["task"])].append((tid, pos, dis))
    picked = []
    keys = sorted(cells)
    per_cell = max(1, N_TRACES // max(1, len(keys)))
    for k in keys:
        pool = sorted(cells[k], key=lambda x: (-len(x[2]), -len(x[1]), x[0]))
        head = pool[:max(per_cell * 3, 12)]
        picked += rng.sample(head, min(per_cell, len(head)))
    rng.shuffle(picked)
    picked = picked[:N_TRACES]
    out = []
    for tid, pos, dis in picked:
        t = traces[tid]
        scope = list(dict.fromkeys(dis + pos))
        negs = [c for c in P.ALL_CODES if c not in scope and c != "HEDGING"]
        scope += rng.sample(negs, min(N_NEG, len(negs)))
        if "HEDGING" not in scope: scope.append("HEDGING")
        for code in scope:
            out.append(dict(row_id=f"{tid[:10]}_{code}", trace_id=tid, code=code,
                            code_definition=SHORT.get(code, ""),
                            question=t["question"], passage=t["trace"],
                            human_label="", human_span="", annotator_notes=""))
    rng.shuffle(out)
    n_share = int(len(out) * OVERLAP)
    for i, r in enumerate(out):
        r["assigned_to"] = "ALL THREE" if i < n_share else f"annotator {1 + (i - n_share) % 3}"
    fields = ["row_id", "assigned_to", "trace_id", "code", "code_definition", "question", "passage",
              "human_label", "human_span", "annotator_notes"]
    with open(C.STUDY / "human_validation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["# A7 human validation. One row = one passage judged against one code."])
        w.writerow(["# human_label: type yes or no. For HEDGING type 0, 1, 2 or 3."])
        w.writerow(["# human_span: if you answer yes, paste the exact words from the PASSAGE that justify it."])
        w.writerow(["# Judge only what the passage says, not whether it is correct, and not whether you agree with its conclusion."])
        w.writerow(["# You are not shown the answer the system gave, which system wrote it, or whether it was right. That is deliberate."])
        w.writerow(["# Rows marked ALL THREE are annotated by every annotator so we can measure agreement between you."])
        w.writerow(fields)
        for r in out:
            w.writerow([r[k] for k in fields])
    counts = collections.Counter(r["assigned_to"] for r in out)
    print(f"human_validation.csv: {len(out):,} rows over {len(picked)} traces, "
          f"{len({r['code'] for r in out})} codes; assignment {dict(counts)}")
    print("rows per annotator including the shared block:",
          {f"annotator {i}": counts["ALL THREE"] + counts[f"annotator {i}"] for i in (1, 2, 3)})


if __name__ == "__main__":
    main()
