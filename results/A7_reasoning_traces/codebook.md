# A7 codebook — stated-justification analysis

**Draft for approval. Nothing has been coded at scale yet.**

## What a trace is

Every CUSP prompt for binary, perturbed binary, MCQ and date ends with a JSON format that
contains `"reasoning": "<1-2 sentence justification>"`. The **trace** is that field. For FRQ
there is no separate field and the trace is the answer itself (a 3-4 sentence method proposal).

Two consequences the coders and the manuscript must both respect:

* The trace is a **post-hoc stated justification emitted in the same call as the answer**, not a
  chain of thought. No provider-native thinking text was stored for any model (Step 0,
  `inventory.md`), so nothing here observes deliberation before the answer was chosen.
* Traces are **short by instruction**: median 25-70 words for the closed-form tasks, 80-140 for
  FRQ. A code must be able to fire on a single clause. Codes that need extended argument
  (HYPOTHESIS_COMPARISON, BASE_RATE) will be rare, and that rarity is itself a finding rather
  than a coding failure.

## Coding unit and general rules

1. One trace = one coding unit. Each code is judged independently, verdict `yes` / `no`
   (HEDGING is ordinal), plus a short **verbatim span** quoted from the trace as justification.
   A `yes` with no quotable span is invalid and is rejected by the pipeline.
2. Code **what the trace says, not whether it is right**. A cited number that is wrong still
   counts as EVIDENCE_CITED. Coders never see the ground truth (enforced in code).
3. Code the **trace only**. The item text is supplied for context because several codes
   (CONSTRAINT_CHECKED, RESTATEMENT_ONLY) are defined relative to the item, but the model's
   answer, its correctness, its identity and the condition are withheld.
4. When a trace is truncated mid-sentence, code what is present.
5. Default to `no`. Weak or inferred instances are `no`.

## The codes

Screen % = share of base-condition traces matching a permissive regex for the code
(`scripts/a7_screen_counts.py`, n = 189,877). It is an order-of-magnitude guide for sizing, not
a prevalence estimate; the coded rates will differ.

---

### 1. BASE_RATE — screen 0.6% (binary 1.0%, FRQ 0.1%)

**Definition.** The trace reasons explicitly about how often this *kind* of result occurs:
a reference class, a historical frequency, a prior, or an explicit probability derived from one.

**Counts:** "most such claims fail"; "historically only a minority of X reach Y"; "such precise
conjunctions rarely all occur as stated"; an explicit probability justified by frequency.

**Does not count:** a bare probability with no frequency reasoning behind it; "unlikely" on its
own; "rapid progress" (that is FIELD_MOMENTUM).

*Positive* (`0565523a4b613bcc`, perturbed binary): "This is a highly specific compound claim
requiring three simultaneous thresholds ... **such precise conjunctions rarely all occur as
stated**." (also CONJUNCTION_BURDEN, SPECIFICITY_AS_IMPLAUSIBLE)

*Negative* (`1d1a04ff78670ab0`, binary): "While 2D materials research is advancing rapidly,
achieving all four exceptional parameters simultaneously ... " — asserts difficulty of a
conjunction but never appeals to how often such results occur. CONJUNCTION_BURDEN yes,
BASE_RATE no.

---

### 2. HYPOTHESIS_COMPARISON — screen 8.7% (FRQ 16.3%, date 2.9%)

**Definition.** The trace weighs **two or more named candidate outcomes, mechanisms or options
against each other**, rather than asserting one. For MCQ, comparing the chosen option to at
least one other named option counts; "option C directly addresses this" alone does not.

**Counts:** "either X or Y, but Y requires ..."; "more likely an incremental gain than a new
architecture"; "A and C both target the pathway, but C acts upstream".

**Does not count:** listing requirements; naming one mechanism and stopping; hedged single
hypotheses ("this may reflect X").

*Positive* (`508e6d1d9d8df6b9`, binary): frames the item as "a fairly demanding **but
incremental** benchmark" and weighs steady catalyst-layer progress against the demanded
threshold before committing.

*Negative* (`a6e6c1964f82ed57`, binary): "This describes a very specific combination ... which
matches a known Nature-published result around 2023-2024." One hypothesis, asserted.
PROVENANCE_INFERRED yes, HYPOTHESIS_COMPARISON no.

---

### 3. EVIDENCE_CITED — screen 18.5% (binary 33%, FRQ 3.4%)

**Definition.** The trace references **specific prior work, a named system, a dataset, a venue,
or a concrete reported number**, rather than reasoning from generalities.

**Counts:** named methods or models ("SageAttention", "ModernBERT", "Gravity Probe B"); a
reported figure with a value; "reported in recent literature at ~12-15%"; a named venue plus
approximate year.

**Does not count:** "recent literature suggests"; "studies have shown"; restating a number that
came from the item (that is CONSTRAINT_CHECKED); a bare year.

*Positive* (`320fad276259915b`, binary): "This describes a very specific claim (**SageAttention**
or similar 8-bit attention method) with precise numbers on **RTX5090**."

*Negative* (`9c41428c055c9ae8`, binary): "research in ion-photoelectron entanglement and
electronic coherences is active" — a field, not a result.

---

### 4. KNOWLEDGE_GAP_ADMITTED — screen 1.6% (binary 4.6%, MCQ/date/FRQ ~0%)

**Definition.** The trace states **in the first person** that it does not know, is not aware of,
or cannot recall relevant work.

**Counts:** "I am not aware of"; "I don't have specific knowledge of such a study"; "to my
knowledge, no"; "this is not well documented in what I know".

**Does not count:** "no published method exists" stated as a fact about the world — that is
ABSENCE_AS_EVIDENCE. The distinction is whose gap it is: the model's, or the literature's.

*Positive* (Claude Sonnet 4.5, binary): "The timeframe ... is in the past from my training
cutoff, but **I don't have specific knowledge of such a study being published**." (also
CUTOFF_REFERENCED)

*Negative:* "No known system has demonstrated this dual capability yet." — a claim about the
world. ABSENCE_AS_EVIDENCE yes, KNOWLEDGE_GAP_ADMITTED no.

---

### 5. ABSENCE_AS_EVIDENCE — screen 1.8% (binary 5.5%, perturbed 4.3%)

**Definition.** The trace **infers from the absence of known work that the thing has not
happened, will not happen, or will happen later**. The inference must be present: absence must
do argumentative work toward the conclusion or the date.

This is the hypothesised mechanism for the delayed-date finding. Code it conservatively and
keep every hit; analysis C depends on it.

**Counts:** "has not yet been demonstrated, and is unlikely by <date>"; "no published technique
does X by <date>"; "no reports of this, so a first demonstration is plausible around <later
date>".

**Does not count:** a statement of absence with no inference drawn from it; difficulty claims
("this is extremely challenging") without reference to absence; a first-person gap alone
(KNOWLEDGE_GAP_ADMITTED).

*Positive* (GPT-OSS 20B, binary): "**no published technique demonstrates** programmable
repositioning within seconds to minutes **by August 2024**" — absence carries the No.

*Negative* (`abea51d590e6329a`, perturbed binary): "reported results remained below that level or
were theoretical projections" — asserts what the literature *does* show, not what it lacks.
EVIDENCE_CITED yes, ABSENCE_AS_EVIDENCE no.

---

### 6. CONSTRAINT_CHECKED — screen 3.9% (perturbed 10.4%, MCQ 0.5%)

**Definition.** The trace **engages with the specific numeric threshold, quantity, date or added
condition stated in the item** — quoting it, comparing something to it, or reasoning about
whether it is reachable. Relevant to perturbed binary items, where the perturbation inserts or
alters a constraint.

**Counts:** repeating the item's number and assessing it ("95.1% accuracy on V-NIAH-D by
February 2025 ... seems unlikely"); comparing a known value to the item's threshold; naming the
added condition and testing it.

**Does not count:** generic "the requirements are demanding"; mentioning the deadline only as a
date; reproducing the question's numbers with no assessment (that is RESTATEMENT_ONLY).

*Positive* (Claude Sonnet 4.5, perturbed binary): "achieving **95.1% accuracy on V-NIAH-D by
February 2025**, which is only about 2 months away ... seems unlikely without existing evidence
of methods approaching this threshold."

*Negative* (`9ecd112e1f5e60d8`, binary): "Achieving an optical asymmetry g-factor of 1.0 is a
significant challenge ... maintaining such performance at high temperatures like 250 °C adds
further complexity." Borderline: numbers are quoted and assessed, so this is a **yes**. Contrast
with "this specific combination of breakthroughs is unlikely", which quotes nothing — no.

---

### 7. RATE_OF_PROGRESS — screen 6.2% (date 15.6%, MCQ 1.2%)

**Definition.** The trace **derives a timeline from a stated pace**: a rate, a historical
interval, or an extrapolation that yields the predicted date or feasibility.

**Counts:** "such validation typically takes 2-4 years, so mid-2026"; "doubling every ~8 months
implies"; "preclinical studies in rodents typically require 2-4 years".

**Does not count:** "the field is advancing rapidly, so this is plausible" — no interval, no
derivation. That is FIELD_MOMENTUM. The test is whether a quantity of time is used.

*Positive* (`74c4802f2814e1e6`, date): "requires fundamental advances ... which **typically take
2-4 years** from current state-of-the-art ... mid-2026 is a plausible timeframe."

*Negative* (LLaMA 3.3, date): "relies on the pace of advancements in quantum sensing ... which
have been rapidly evolving, suggesting ... a relatively short timeframe." Invokes pace but
derives no interval. FIELD_MOMENTUM yes, RATE_OF_PROGRESS no.

---

### 8. ROUND_ANCHOR — screen 1.9% (date 12.0%)

**Definition.** The trace reasons toward a **round or decade-level target** rather than a
specific month: "late 2020s", "by 2030", "mid-2030s", "within the decade", "around 2026".

**Counts:** any decade-scale or half-decade-scale phrase used as the temporal target; "around
<year>" with no month.

**Does not count:** a specific month stated in the trace; a year used to date *past* work
("published around 2023-2024") rather than as the prediction target.

*Positive* (GPT-5.4, date): "The complexity of proving causal necessity in vivo suggests a
timeline in the **late 2020s** rather than imminently."

*Negative* (`a6e6c1964f82ed57`, binary): "matches a known Nature-published result **around
2023-2024**" — dates prior work, not the target. PROVENANCE_INFERRED yes, ROUND_ANCHOR no.

---

### 9. CUTOFF_REFERENCED — screen 1.2% (binary 2.4%)

**Definition.** The trace mentions **its own knowledge cutoff, training date or training data**
as a bound on what it can know.

**Counts:** "as of my knowledge cutoff in April 2024"; "my training data ends before"; "as of my
last update".

**Does not count:** "as of 2024" used as a statement about the field; the item's deadline.

*Positive* (Claude Sonnet 4.5, perturbed binary): "The LiveMCP-101 benchmark is not a widely
recognized ... benchmark **as of my knowledge cutoff in April 2024**."

*Negative:* "As of late 2023, no published methods explicitly demonstrate this exact mechanism"
— a claim about the literature at a date, not about the model's training. ABSENCE_AS_EVIDENCE
yes, CUTOFF_REFERENCED no.

---

### 10. DIFFICULTY_APPEAL — screen 13.5% (binary 23%, MCQ 6.8%)

**Definition.** The trace justifies pessimism (or a later date) by appeal to **complexity,
difficulty, or the scale of what would be required**.

**Counts:** "extremely challenging"; "would require multiple breakthroughs"; "non-trivial
engineering"; "formidable barriers".

**Does not count:** difficulty words used about something other than the target claim;
difficulty asserted while still concluding Yes without it doing work. Requires that the
difficulty support the conclusion.

*Positive* (GPT-4o, binary): "Terrestrial frame-dragging measurements are **extremely
challenging** ... reducing this to one-part-in-a-thousand would require significant advancements
in technology and methodology."

*Negative:* "This is a demanding but incremental benchmark, and several recent reports already
approach it" — difficulty is acknowledged and then overridden. No.

---

### 11. HEDGING — ordinal 0-3 — screen 36.1% (date 67%, FRQ 6.4%)

**Definition.** Degree of epistemic hedging in the trace as a whole.

* **0 — none.** Flat assertion. "This matches a known published result."
* **1 — light.** One hedge on an otherwise committed claim. "likely", "plausible", "suggests".
* **2 — moderate.** Multiple hedges, or an explicit statement of uncertainty alongside a
  conclusion. "uncertain and speculative", "may or may not".
* **3 — heavy.** The trace declines to commit, or its hedging dominates. "I cannot reliably
  forecast whether ..."

Code the level, not the count of words. A single "cannot reliably forecast" is 3.

---

## Proposed additions from the inductive pass

The inductive pass drew 300 traces stratified across model x task x correctness (seed 7,
`inductive_sample.jsonl`) and clustered a 6,000-trace background sample
(`scripts/a7_inductive.py`). **Lexical clustering recovered discipline, not reasoning style** —
the six clusters per task separate biology from AI from photonics — which is expected for
one-sentence traces and is why the deductive instrument is the right one. The structural
screens, however, surfaced five recurring moves the deductive codebook misses. Rates below are
from the background sample.

---

### 12. SPECIFICITY_AS_IMPLAUSIBLE — 3.5% overall, 8% binary **(new)**

**Definition.** The trace treats the **unusual precision or specificity of the item itself** as
evidence that the claim is unlikely, speculative, or not real.

Why it matters: this is a benchmark artefact being read as a signal. CUSP items are specific
*because they are derived from real published results*, so a model that discounts specificity is
systematically penalised. It is a candidate mechanism for the No-bias on binary items.

*Positive* (`9c41428c055c9ae8`, binary, answer No, ground truth Yes): "This describes a **highly
specific** experimental achievement ... such a **precise** result by April 2026 is uncertain and
**speculative**."

*Negative:* "The specific 3x memory claim is uncertain" — doubts one number, does not treat
specificity as such as disqualifying. CONSTRAINT_CHECKED yes, this no.

---

### 13. PROVENANCE_INFERRED — 5.1% overall, 14% date **(new)**

**Definition.** The trace treats the item as **describing a real, identifiable piece of work**,
and reasons from that identification — often naming the likely paper, venue or year.

This is the mirror image of code 12: the same surface cue (unusual specificity) read in the
opposite direction. Separating them is the main inductive finding, and the pair should be
analysed together in analysis B and C.

*Positive* (`560373c57ceec778`, binary, answer Yes, ground truth Yes): "**These very specific
values suggest a particular published study**, likely on biodegradable piezoelectric materials
..., which have been reported in recent literature."

*Negative:* "This question describes a composite of hypothetical future record values rather
than an established published milestone" (`b79cde88fbb944a4`) — explicitly denies provenance.
SPECIFICITY_AS_IMPLAUSIBLE yes, this no.

---

### 14. CONJUNCTION_BURDEN — 11.6% overall, 18% FRQ, 14% binary **(new)**

**Definition.** The trace argues that **several requirements must hold simultaneously** and uses
that conjunction to support doubt (or, rarely, to structure a plan).

*Positive* (`1d1a04ff78670ab0`, binary): "achieving **all four** exceptional parameters
**simultaneously** (perfect yield, near-zero hysteresis, near-ideal subthreshold swing, and
ultrahigh on-current) by September 2025 ..."

*Negative:* "This requires a new architecture" — one requirement.

---

### 15. FIELD_MOMENTUM — 4.9% overall, 7-8% binary and date **(new)**

**Definition.** Generic appeal to the **speed or activity of the field** with no interval and no
derivation: "rapid progress", "active research area", "surge of interest".

Defined explicitly as the residual of RATE_OF_PROGRESS so the two partition cleanly: momentum
without a quantity of time is 15, momentum with one is 7.

*Positive* (Claude Sonnet 5, date): "likely published around 2023-2024 **given the surge in
prophage defense system discoveries**."

*Negative:* "typically requiring 2-4 years for validation" — an interval. RATE_OF_PROGRESS.

---

### 16. RESTATEMENT_ONLY — 8.1% overall, 14% date **(new)**

**Definition.** The trace **paraphrases the item and adds nothing**: no evidence, no mechanism,
no comparison, no rate, no constraint assessment. A pure restatement plus a verdict.

Included because it separates "did not reason" from "reasoned and was wrong" and feeds analysis
G directly.

*Positive* (Claude Sonnet 4.5, date): "This query describes highly specific performance metrics
for what appears to be an advanced code navigation or development tool system with graph-based
indexing, vector search optimization, and context-aware localization." — the item, restated.

*Negative:* any trace that adds a number, a named system, a mechanism or a rate.

---

## Considered and dropped

| candidate | rate | why dropped |
|---|---|---|
| VERIFIABILITY_DOUBT ("not publicly documented") | 0.2% | too rare to estimate; overlaps ABSENCE_AS_EVIDENCE |
| MECHANISM_STATED (causal path given) | 24% (FRQ 53%) | too generic to be diagnostic; largely a task artefact |
| NAMES_SYSTEM (any named entity) | 51% | subsumed by EVIDENCE_CITED |
| TIMEFRAME_TOO_SHORT | 1.9% | merged into CONSTRAINT_CHECKED (the deadline is a stated constraint) |
| ALREADY_HAPPENED | 2.0% | kept out of the codebook; recoverable from the answer, not the trace |

## Coding plan once approved

Two independent coder models, blind to ground truth, correctness, model identity and condition
(enforced by `a7_common.FORBIDDEN_FOR_CODER` and asserted per prompt). One structured judgment
per code per trace with verdict and verbatim span. Cohen's kappa per code; any code below the
pre-registered threshold is excluded from the inferential analyses rather than reported.
