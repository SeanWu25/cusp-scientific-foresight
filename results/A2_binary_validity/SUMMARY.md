# A2 — binary task validity: summary

Reviewer 2, concern C2. Two validation studies of the CUSP binary task. Both use
unrestricted post-event web search where relevant, because both are questions about the
benchmark, not evaluations of forecasting ability.

Run 2026-09-24T15:21:33Z on git `ed930fc230` (branch
`sonnet5-run1`). Measured cost **$252.04**.

---

### 1. What fraction of positives verified?

**81.1%** of 196 sampled positives were confirmed on the first
post-event web search (95% CI 75.1–86.0%). Searching again with a different model on a different search index recovered a qualifying source for most of the rest, lifting the confirmation rate to **96.5%**. The first-pass misses were largely search coverage, not bad items.

What is left is listed in `study1_verification/flagged_for_review.csv` with its evidence,
for a human to adjudicate. A failed search is not evidence that the advance did not
happen, so nothing here is re-labelled automatically.

### 2. What fraction of synthetic negatives were actually achieved elsewhere?

**Strict answer first, and the two routes are not combined.** Under two independent referees plus mechanical gates that re-check every quote and recompute every inequality in code:

- **Achieved elsewhere by another group: 5 of 200 items (2.5%).** This is the reviewer's own concern, and it does not survive. No pair of referees certifies the same item; at most one referee alone certifies 5.
- **Perturbation never made the claim false: 10 of 200 items (5.0%).** Provable from the source paper alone, without any search.
- **Undecidable claim: 18 (9.0%).** An element such as "high potency" that can be neither verified nor falsified. Not a wrong label, but not a usable item either.

Referee choice moves the second figure (see `tables/t21_referee_pairs.md`): 14 items with Opus 4.8 + GPT-5.5, 9 with Sonnet 5 + either, 2 if GPT-5.4-mini must co-sign. GPT-5.4-mini fails the verbatim-quote gate on 62% of its own proposals against 0% for the two larger models, so it is reported but not relied on.

The looser figures below are what a "is this claim true" reading gives, with no mechanical checking. They are an upper bound only.

**12.1%** of 199 sampled negatives were found to have been achieved by a
group other than the source paper, on or before the target date (95% CI
8.2–17.3%; design-weighted 12.3%).

A separate, closed-book check found that a further **20.5%** of negatives are
already satisfied by their own source paper as literally written — the perturbation did
not bind. That route is invisible to the web check, which is required to exclude the
source paper. Two independent models agree on it at Cohen's kappa 0.855.

Taken together, **23.0%** of synthetic negatives are wrong by at least one of the two routes (95% CI 17.7%–28.5%). Scaled to the 4305 negatives in the corpus that is roughly 991 items (760–1229).

Both routes are flagged for review in `study1_verification/flagged_for_review.csv`, with
the evidence and the second pass's verdict inline.

**Re-run under a deliberately hard standard, the answer is 1 of 200 (0.5%, 95% CI 0.1-2.8%).** The first pass asked whether the claim "was achieved"; that is too easy to say yes to. The re-run requires the *exact* claim: the exact modified value or added constraint, in the same task or system, on or before the target date, by one named non-excluded source, with a quoted passage that itself contains the figure. Two cheap referees (Claude Haiku 4.5 and GPT-5.4-mini) ran it independently and both must certify. Ten mechanical checks then re-verify each certification in code, recomputing the inequality and matching the cited source against the item's own paper; they rejected 5 of the proposals outright, on 11 separate gate failures. The rate falls from 23 of 200 (11.5%) to 1. The panel mean binary accuracy is unchanged at 49.8%. Detail in `study1_verification/results.md` section 4b; the survivor and its evidence in `study1_verification/flagged_for_review_negatives_strict.csv`.

### 3. Does the near-chance binary finding survive correction?

Yes. Across the panel the mean binary accuracy on the verified sample moves from 49.8% as published to 51.5% once every flagged label is corrected — +1.7 points, and still chance. No model is rescued into competent territory: the corrected range is 38.5% to 68.6%.

Individual models move by up to 10.7 points, but in **both** directions — 4 end above chance and 3 below. Which way a model moves is set by how readily it says yes: flipping a negative to YES rewards the yes-biased models and punishes the rest. That is a response-bias effect, not recovered forecasting skill.

### 4. Can models tell original from perturbed claims?

Partly, and not better than a ruler. gpt-5.4 73.1% overall, 59.4% correct under both orders; claude-opus-4-8 74.8% overall, 60.2% correct under both orders. The trivial rule 'pick the shorter statement' scores 82.2% on the same pairs, so most of what the judges detect is a length artifact rather than scientific content.

### 5. Is binary performance explained by that detectability?

No. Taking the pair as the unit, binary accuracy on pairs a judge could tell apart differs from accuracy on pairs it could not by between -6.8 and +4.5 percentage points, and the 95% CI includes zero in 15 of 18 judge x model combinations. In the 3 exceptions the difference is negative, so those models are slightly worse on the detectable pairs. Detectability does not explain binary performance.

---

## What this means for the manuscript

- C2(a) is real but narrower than a loose reading suggests. Quote the demonstrable rate,
  where both referees certify every element against a reported value. The larger share of
  it is perturbations that never made the claim false, not claims achieved elsewhere.
- A second defect sits beside it and is worth naming separately: negatives whose claim
  contains an uncheckable qualifier. Those cannot be scored either way, so they weaken the
  task without being wrong labels.
- C2(b) does not hold as stated for the binary result. The perturbations *are* partly
  detectable, but mostly through a length artifact, and binary accuracy is no better on
  the detectable pairs than on the rest.
- Both kinds of wrong NO label concentrate in the same place: perturbations that add a
  constraint. Numeric modifications are close to sound. Regenerating or dropping the
  constraint-type negatives would fix most of the problem without touching the rest of the
  benchmark.
- The length asymmetry is worth fixing in the dataset regardless of C2: it is a free
  signal that a future model could exploit even though the current panel does not.

## Layout

```
study1_verification/  sample.json, positives_verdicts.jsonl, negatives_verdicts.jsonl,
                      negatives_soundness.jsonl, evidence/, flagged_for_review.csv,
                      corrected_accuracy.csv, results.md
study2_detection/     pairs.json, judgments.jsonl, item_level_join.csv, results.md
tables/               t1..t12, CSV + markdown
scripts/              sample, verify, detect, adjudicate, analyze1/2, figures,
                      manifest, report, run_all.sh
figures/              fig1..fig4, PNG + PDF
MANIFEST.json         models, snapshots, seeds, prompt hashes, usage, cost, git SHA
```
