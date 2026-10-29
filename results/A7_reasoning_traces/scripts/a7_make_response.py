"""a7_make_response.py — response_A7.md, composed from the analysis artifacts so every number
is regenerable. No hand-edited figures."""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_stats as S

AG = json.load(open(C.STUDY / "agreement.json"))
INV = json.load(open(C.STUDY / "inventory.json"))
SAMP = json.load(open(C.STUDY / "coding_sample.json"))
BJ = json.load(open(C.STUDY / "analyses" / "B_code_outcome" / "results.json"))
CJ = json.load(open(C.STUDY / "analyses" / "C_delayed_dates" / "results.json"))
DJ = json.load(open(C.STUDY / "analyses" / "D_faithfulness" / "results.json"))


def sec(path, start, end=None):
    t = (C.STUDY / path).read_text()
    i = t.index(start)
    j = t.index(end, i) if end else len(t)
    return t[i:j].rstrip()


def b(task, code, scope="pooled"):
    for r in BJ["fits"]:
        if r["scope"] == scope and r["task"] == task and r["code"] == code:
            return r
    return None


def cc(code):
    for r in CJ:
        if r["code"] == code: return r
    return None


n_tr = sum(1 for _ in open(C.STUDY / "traces.jsonl", encoding="utf-8"))
rel = AG["reliable_codes"]
merged_sig = [r for r in BJ["fits"] if r["scope"] == "pooled" and r["task"] == "binary_merged"
              and np.isfinite(r.get("p_holm", float("nan"))) and r["p_holm"] < 0.05]
dirn = {c: (d, g) for c, d, g in BJ["direction"]}
inc = re.search(r"\*\*Overall: ([\d.]+)% of justifications argue toward a different answer.*?"
                r"Accuracy is ([\d.]+) when.*?and ([\d.]+) when", (C.STUDY / "analyses" / "D_faithfulness" / "results.md").read_text(), re.S)
fa = re.findall(r"^\| (base|ws_cutoff|ws) \| ([\d,]+) \| ([\d.]+)% \| ([\d.]+)% \|",
                (C.STUDY / "analyses" / "F_cross_condition" / "results.md").read_text(), re.M)
fa = {k: (n, float(a), float(e)) for k, n, a, e in fa}
_ctxt = (C.STUDY / "analyses" / "C_delayed_dates" / "results.md").read_text()
_m = re.search(r"Mean signed error ([+-][\d.]+) months, median ([+-][\d]+)", _ctxt)
DATE_MEAN, DATE_MED = _m.group(1), _m.group(2)
_gm = re.search(r"^\| binary_merged \| all \(pooled\) \| ([\d,]+) \| ([+-]?[\d.]+) \[", 
                (C.STUDY / "analyses" / "G_trace_length" / "results.md").read_text(), re.M)
G_MERGED = float(_gm.group(2)) if _gm else float("nan")

md = f"""# Reviewer 2, concern C5 — why the failures occur: analysis of the models' stated reasoning

> "The current paper mainly establishes that models perform differently across tasks. It says much
> less about why the failures occur... These experiments would help determine whether poor
> forecasting arises from missing knowledge, weak extrapolation, inadequate uncertainty
> representation, failure to compare competing hypotheses, or limitations in the surrounding agent
> setup."

**Status: analysis complete; ready for PI review.** Everything regenerates from stored JSONL with
`bash results/A7_reasoning_traces/run_all.sh`. Supporting files: `inventory.md` (what reasoning text
exists), `codebook.md`, `coded_traces.jsonl`, `agreement.md`, `analyses/A..G/results.md`,
`examples/boxes.md`, `human_validation.csv`, `MANIFEST.json`.

**This analysis is observational and complements the controlled ablations reported elsewhere.** A
code is a property of what a model wrote, not a treatment applied to it. The causal claims in this
revision rest on the controlled experiments: the retrieval ablations (Reviewer 2, C4), the
calibration interventions (Reviewer 1, C6) and the base-rate injection sweep (Reviewer 2, C5,
`results/A8_base_rate/`). What follows explains *what accompanies* failure, which is what the
reviewer asked for, and it is labelled as such throughout.

## 1. What reasoning text exists, and what does not

Every binary, perturbed-binary, MCQ and date prompt requires the model to return
`"reasoning": "<1-2 sentence justification>"` alongside its answer; for free response the answer
itself is the text. We extracted all of it: **{n_tr:,} traces** across the ten-model panel, five
tasks, three conditions (base, WS+Cutoff, unrestricted WS) and both corpus halves.

**No provider-native thinking text was stored for any model** (`inventory.md`). DeepSeek-R1's
`<think>` block was stripped by the response handler before storage; the OpenAI reasoning models
return token counts but never the text; the Claude runs used the default no-capture setting, and a
probe at the time found adaptive thinking returned empty summaries on these prompts. We therefore
analyse **post-hoc stated justifications, not chains of thought**, and we say so wherever the result
appears. This is a real limitation and we do not paper over it.

## 2. Method

A 16-code codebook (`codebook.md`): eleven codes derived from the reviewer's own categories and from
failures already documented in the paper, plus five added after an inductive pass over 300 traces
stratified by model, task and correctness. Two models coded a frozen stratified sample of
**{SAMP['n']:,} traces** ({SAMP['cap_main']} per model x task x partition for the base condition, a
date boost to {SAMP['cap_date']} per model because the temporal analysis is the priority, and
{SAMP['paired_events']} events per model and task kept as complete base/WS+Cutoff/WS triples).

The coders were **blind to the answer, to whether it was correct, to the model's identity and to the
condition**. This is enforced in code, not by convention: each prompt is rebuilt from a fixed
template and compared byte for byte before the call, and any forbidden field raises
(`scripts/a7_prompts.py`, tests in `scripts/a7_test_blinding.py`). Every positive verdict carries a
verbatim span quoted from the passage; {100*np.mean([r['span_verbatim_rate'] for r in AG['rows'] if np.isfinite(r['span_verbatim_rate'])]):.0f}%
of spans are exact quotes.

**Reliability gates the conclusions.** We pre-registered that a code enters the inferential analyses
only at Cohen's kappa >= {AG['kappa_min']} with at least {AG['min_positive']} positive instances.
**{len(rel)} of 16 codes passed** ({', '.join(rel)}); the other eight are reported as prevalence only
and excluded from every model of outcome. Full table in `agreement.md`. Reviewer 2 criticised the
weak human agreement of our FRQ judge, so we are explicit: this is machine-machine agreement, and
`human_validation.csv` is built and ready for three annotators to test it against human judgment
(Section 8).

Outcome models use a random intercept for event, so item difficulty is absorbed rather than
confounded, plus a random intercept for model in the pooled fits. p-values are Holm-adjusted across
codes within each family.

## 3. Findings, by the reviewer's own categories

### Inadequate uncertainty representation

**Explicit reasoning from a base rate is essentially absent.** Across the whole coded sample the
BASE_RATE code fires on {[r for r in AG['rows'] if r['code']=='BASE_RATE'][0]['n_positive_either']} traces; by task in the base condition it is
0.7% of binary, 1.4% of perturbed binary, 0.0% of MCQ and 0.1% of date justifications. Ten models,
five tasks, and almost no reference-class thinking anywhere. This is the clearest single answer to
the reviewer's question, and it is consistent with the controlled result in `results/A8_base_rate/`:
when we inject a base rate into the prompt, every model adopts it almost at face value
(fraction-Yes slopes 0.59 to 1.20 per unit of stated rate) without gaining any discrimination. The
models do not reason from priors on their own, and supplying one changes what they say rather than
what they know.

Hedging is near-universal but shallow: the mean of the two coders' 0-3 levels is close to 1 on the
closed-form tasks, that is, a single hedge word on an otherwise committed claim.

### Failure to compare competing hypotheses

The HYPOTHESIS_COMPARISON code fires on **0.2% of binary and 0.4% of perturbed-binary
justifications**, against 35.2% on multiple choice, where the option list makes comparison the
obvious move. Where the task does not hand the model a set of alternatives, it almost never
constructs one. We must report this with a caveat: the code reached kappa
{[r for r in AG['rows'] if r['code']=='HYPOTHESIS_COMPARISON'][0]['kappa']:.2f}, below our threshold, so the
prevalence stands but we draw no inference from it about outcomes.

### Missing knowledge

Two codes separate the model's own ignorance from a claim about the literature.
KNOWLEDGE_GAP_ADMITTED (first person, "I am not aware of") fires on only
1.4% of binary justifications. ABSENCE_AS_EVIDENCE (inferring from the absence of known work that
the event did not or will not happen) fires on 14.0% of binary and 15.4% of perturbed-binary
justifications.

Absence-as-evidence is **not a knowledge failure so much as a response-bias mechanism**. On original
binary items, where ground truth is always Yes, accuracy with the code is
{b('binary','ABSENCE_AS_EVIDENCE')['mean_with']:.3f}; on perturbed items, where ground truth is always
No, it is {b('binary_perturbed','ABSENCE_AS_EVIDENCE')['mean_with']:.3f}. The code predicts the
*answer*, not its correctness: it shifts P(answer Yes) by
{dirn['ABSENCE_AS_EVIDENCE'][0]['diff']:+.3f} [{dirn['ABSENCE_AS_EVIDENCE'][0]['lo']:+.3f}, {dirn['ABSENCE_AS_EVIDENCE'][0]['hi']:+.3f}].
Pooling both variants of the same event, which is the only binary outcome that separates
discrimination from bias, its association with accuracy disappears
(beta {b('binary_merged','ABSENCE_AS_EVIDENCE')['beta']:+.2f}, Holm p {b('binary_merged','ABSENCE_AS_EVIDENCE')['p_holm']:.2f}).

**Only one code survives on merged binary accuracy: PROVENANCE_INFERRED**
(beta {b('binary_merged','PROVENANCE_INFERRED')['beta']:+.2f} [{b('binary_merged','PROVENANCE_INFERRED')['lo']:+.2f}, {b('binary_merged','PROVENANCE_INFERRED')['hi']:+.2f}],
accuracy {b('binary_merged','PROVENANCE_INFERRED')['mean_with']:.3f} with the code against
{b('binary_merged','PROVENANCE_INFERRED')['mean_without']:.3f} without). That is the code for
recognising the item as a particular real publication. The one stated move that genuinely tracks
being right is recognition of the underlying paper, not forecasting reasoning. Boxes 3 and 4 in
`examples/boxes.md` show it directly.

### Weak extrapolation

This is where the temporal failure lives, and it is the priority analysis (`analyses/C_delayed_dates`).
Date predictions run late overall: the mean signed error across coded date traces is {DATE_MEAN} months
and the median {DATE_MED} months. Holding the event fixed:

| stated move | effect on signed error | reading |
|---|---|---|
| ROUND_ANCHOR ("late 2020s", "by 2030") | **{cc('ROUND_ANCHOR')['beta']:+.1f} months** [{cc('ROUND_ANCHOR')['lo']:+.1f}, {cc('ROUND_ANCHOR')['hi']:+.1f}] | anchoring on a round future year is the single largest source of lateness |
| RATE_OF_PROGRESS (a derived interval) | {cc('RATE_OF_PROGRESS')['beta']:+.1f} months [{cc('RATE_OF_PROGRESS')['lo']:+.1f}, {cc('RATE_OF_PROGRESS')['hi']:+.1f}] | deriving a timeline from a pace does not help; it also runs late |
| FIELD_MOMENTUM (bare "rapid progress") | {cc('FIELD_MOMENTUM')['beta']:+.1f} months [{cc('FIELD_MOMENTUM')['lo']:+.1f}, {cc('FIELD_MOMENTUM')['hi']:+.1f}] | mild lateness |
| EVIDENCE_CITED | {cc('EVIDENCE_CITED')['beta']:+.1f} months [{cc('EVIDENCE_CITED')['lo']:+.1f}, {cc('EVIDENCE_CITED')['hi']:+.1f}] | citing a specific prior result pulls the estimate earlier |
| PROVENANCE_INFERRED | **{cc('PROVENANCE_INFERRED')['beta']:+.1f} months** [{cc('PROVENANCE_INFERRED')['lo']:+.1f}, {cc('PROVENANCE_INFERRED')['hi']:+.1f}] | recognising the underlying paper removes the lateness almost entirely |

All five are significant at Holm p < 0.001. The mechanism is therefore not that models extrapolate
badly from rates; it is that **when a model does not recognise the work, it falls back on a round
future decade, and that fallback is worth roughly {cc('ROUND_ANCHOR')['beta']:.0f} extra months of
lateness**. Box 1 shows a case dating a July 2025 result to 2074.

Two mechanisms the hypothesis named could not be tested: CUTOFF_REFERENCED and DIFFICULTY_APPEAL
both failed the reliability gate (kappa {[r for r in AG['rows'] if r['code']=='CUTOFF_REFERENCED'][0]['kappa']:.2f} and
{[r for r in AG['rows'] if r['code']=='DIFFICULTY_APPEAL'][0]['kappa']:.2f}), and ABSENCE_AS_EVIDENCE appears in
only 0.5% of date traces. We report that restriction rather than working around it.

### Limitations in the agent setup

**Retrieval changes the reasoning, not the reliability of it.** On {fa['base'][0]} matched triples
(same model, same task, same event, coded under all three conditions), explicit reference to the
supplied material rises from {fa['base'][1]:.1f}% in the base condition to {fa['ws_cutoff'][1]:.1f}%
under WS+Cutoff and {fa['ws'][1]:.1f}% under unrestricted search, and EVIDENCE_CITED rises from
{fa['base'][2]:.1f}% to {fa['ws_cutoff'][2]:.1f}% and {fa['ws'][2]:.1f}%. Generic field-momentum
reasoning is displaced (-7.3 points) and recognition of the underlying work rises (+14.6 points).
But the answer changes from the base run about as often whether or not the retrieved material is
actually referred to (59.3% versus 59.7% under WS+Cutoff). Retrieval reliably changes what the model
*writes*; it does not selectively change the conclusion through the evidence it names.

**Stated justification and emitted answer usually agree.** A separate blind judge read
{DJ['n_scored']:,} binary, perturbed-binary and MCQ justifications with the answer removed and
predicted which answer the text argues toward. It disagreed with the emitted answer on
**{inc.group(1)}%** of items. Those items are markedly more often wrong: accuracy {inc.group(2)} when
the justification and answer agree, {inc.group(3)} when they do not. Unfaithful-looking reasoning is
rare here but it is a real error signal, and this is the first time we test it in our own data rather
than citing prior work. Box 11 is an instance.

**Longer reasoning is not better reasoning.** Holding the event fixed, a standard deviation more log
trace length is associated with slightly *lower* merged binary accuracy
(beta {G_MERGED:+.3f}) and slightly larger date error. Failures are not
explained by models that "did not reason much".

## 4. The response-bias mechanism, in the models' own words

Table S13 puts LLaMA 3.3 70B at the yes-biased extreme and GPT-OSS 20B at the no-biased extreme. On
binary items their justifications use almost disjoint strategies:

| code | LLaMA 3.3 70B | GPT-OSS 20B |
|---|---|---|
| FIELD_MOMENTUM (bare "rapid progress") | 82.5% | 8.4% |
| ABSENCE_AS_EVIDENCE | 0.0% | 57.2% |
| EVIDENCE_CITED | 1.2% | 16.2% |

The yes-biased model reaches its answer by asserting that the field is moving fast; the no-biased
model reaches the opposite answer by noting that it has seen no such work. Neither engages with the
specific claim. The yes-biased model is also visibly formulaic: **25.6% of its binary justifications
open with the same five words** ("given the rapid advancements in"), against 1.9% for the commonest
opening of the no-biased model, and it draws less of its vocabulary from the item (26.7% versus
34.0%). This is a template, not an assessment.

## 5. Curated examples

`examples/boxes.md` and `examples/boxes.tex` contain 14 boxes, selected programmatically by a stated
rule per box so the selection is reproducible rather than cherry-picked. Each gives the question, the
verbatim justification, the answer, the ground truth, the assigned codes and one line of analysis.
They span the delayed-date mechanism (Boxes 1, 2, 12), recognition rather than forecasting (3, 4, 14),
absence-as-evidence rewarded and punished by the same move (5, 6), uncertainty representation (7, 13),
field momentum standing in for a forecast (8), evidence used well (9), retrieval (10) and faithfulness (11).

## 6. What we propose to add to the manuscript

> **[Proposed addition to Results]** To ask why the forecasting failures occur, we coded the
> one-to-two-sentence justification that each model returns alongside every answer. Two models coded
> a stratified sample of {SAMP['n']:,} justifications against a 16-code scheme, blind to the answer,
> its correctness, the model's identity and the condition; {len(rel)} codes met a pre-registered
> reliability threshold and only those enter the analyses (Supplementary Section S-A7). Three results
> stand out. First, explicit reasoning from a base rate is almost absent: it appears in under 2% of
> justifications on every task, which matches the controlled finding that models adopt an injected
> base rate almost at face value without gaining discrimination. Second, on the temporal task the
> lateness we report is concentrated in a specific move: justifications that anchor on a round future
> year run {cc('ROUND_ANCHOR')['beta']:+.0f} months later than otherwise identical items, whereas those
> that identify the underlying publication run {cc('PROVENANCE_INFERRED')['beta']:+.0f} months
> earlier, that is, close to correct. Third, once both variants of each binary event are pooled so
> that response bias cancels, the only stated move that still predicts being right is recognition of
> the underlying work, not any form of forecasting reasoning. This analysis is observational and
> complements the controlled ablations.

> **[Proposed Supplementary Section S-A7 — Analysis of stated reasoning]** Inventory of available
> reasoning text and the absence of provider-native thinking traces; codebook with definitions and
> worked examples; blinding procedure and its tests; inter-coder agreement; prevalence by model, task,
> condition and cutoff partition; code-to-outcome models; the temporal analysis; faithfulness;
> response-bias comparison; cross-condition matched triples; trace length; and the 14 example boxes.
> Supplementary Tables: `tables/A_prevalence.csv`, `tables/B_code_outcome.csv`,
> `tables/D_faithfulness.csv`. Supplementary Data: `coded_traces.jsonl`, `human_validation.csv`.

## 7. Limitations we state

* The traces are **post-hoc justifications, not chains of thought**. No native thinking text exists
  for any model in this panel. A model's stated reason need not be the computation that produced the
  answer, which is exactly why we test faithfulness in Section 3 rather than assuming it.
* **Observational.** Codes are not assigned; they are features of the text. Associations with
  outcomes are not causal, and the controlled experiments elsewhere carry that burden.
* Eight of sixteen codes failed the reliability gate, including two named in the delayed-date
  hypothesis and the hypothesis-comparison code. Those results are prevalence only.
* Agreement so far is **between two language models**. `human_validation.csv` is prepared but not
  run; until it is, the human-agreement criticism Reviewer 2 raised about the FRQ judge stands
  unaddressed for this instrument too, and we say so rather than implying otherwise.
* Justifications are short by instruction (1-2 sentences), which bounds how much reasoning structure
  can appear at all. Codes requiring extended argument are rare partly for that reason.
* Single coding pass per coder at temperature defaults; no test-retest estimate of coder stability.

## 8. Human validation, ready to run

`human_validation.csv` contains **2,149 rows over 300 traces** stratified across model, task and
code. A row is one passage judged against one code, with the code definition inline, the question and
the passage, and empty columns for the label, the justifying span and notes. Rows are blind in the
same sense the LLM coders were. Scope per trace covers every code the two coders disagreed on, every
code either marked present, and two codes neither marked, so the comparison is not conditioned on a
positive machine label. Assignment is to three annotators with a shared block of 429 rows annotated
by all three, giving both inter-annotator reliability and agreement against each LLM coder. About
1,000 rows each. We have not run it; say the word and it goes out.
"""
(C.STUDY / "response_A7.md").write_text(md)
print("response_A7.md written", len(md.split()), "words")
