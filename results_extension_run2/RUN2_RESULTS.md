# Run 2 results — April–August 2026 extension

Status: inference complete for the full panel; stage-1 leakage judging in progress.
All numbers below come from stored predictions scored by the frozen `scoring_v1`
graders. Nothing here required re-running any of the six published models.

**This corpus is not prospective.** Every outcome had resolved before the models
ran. What it is: 815 events published April–August 2026, which postdate every
model's knowledge cutoff, so the corpus is uncontaminated by training data. That
addresses contamination, not the absence of a Time Capsule, and every table says so.

---

## 1. Headline

Three tasks, three different stories, and only one of them survives contact with
uncontaminated material.

| Task | Result on the extension | Trivial baseline | Verdict |
|---|---|---|---|
| Merged binary | best 0.673 (DeepSeek-V4-Pro) | always-"no" = **0.768** | 0 of 8 models beat the baseline |
| Date | best 0.506 (GPT-4o) | constant "2026-06" = **0.893** | no model close |
| MCQ | best 0.910 (Claude Sonnet 5) | chance = 0.250 | clearly above chance |

MCQ is the only task showing real skill. Section 6 argues it may not be measuring
foresight.

**The date result is not an artefact of the extension's five-month window.** It
holds on the original 27-month corpus too. Computing the best constant guess on
each model's *own* post-cutoff subset — the subsets differ in size and span, so a
corpus-wide baseline would not be a fair comparison:

| Model | n | model score | best constant | baseline | gap |
|---|---|---|---|---|---|
| GPT-4o | 2,950 | 0.199 | 2025-02 | 0.544 | −0.344 |
| LLaMA 3.3 70B | 2,930 | 0.485 | 2025-02 | 0.544 | −0.059 |
| GPT-OSS 20B | 2,479 | 0.337 | 2025-04 | 0.589 | −0.251 |
| DeepSeek-R1 | 2,143 | 0.328 | 2025-04 | 0.633 | −0.305 |
| Claude S4.5 | 1,624 | 0.275 | 2025-08 | 0.678 | −0.403 |
| GPT-5.4 | 924 | 0.245 | 2026-12 | 0.776 | −0.531 |
| Claude Sonnet 5 | 410 | 0.288 | 2026-02 | 0.827 | −0.538 |
| GPT-5.6 Sol | 327 | 0.233 | 2026-04 | 0.836 | −0.603 |

Every gap is negative, across 327–2,950 items per model. The gap widens with
cutoff recency, but that is an artefact worth naming rather than a finding: a
later cutoff leaves a narrower remaining window, which strengthens the constant
guess. The substantive point is the sign.

So: **two of three closed-form tasks are beaten by trivial constant strategies on
unseen events, and the third has a retrospective ceiling near 1.0.**

## 2. Full panel, extension corpus (100% post-cutoff)

| Model | cutoff | merged binary | MCQ | date score |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 0.566 [0.53, 0.60] | 0.462 [0.42, 0.50] | 0.506 [0.46, 0.56] |
| LLaMA 3.3 70B | 2023-12 | 0.271 [0.24, 0.30] | 0.442 [0.40, 0.48] | 0.288 [0.27, 0.30] |
| GPT-OSS 20B | 2024-06 | 0.567 [0.53, 0.60] | 0.518 [0.48, 0.56] | 0.347 [0.31, 0.39] |
| Claude S4.5 | 2025-01 | 0.558 [0.52, 0.59] | 0.755 [0.71, 0.79] | 0.317 [0.28, 0.36] |
| GPT-5.4 | 2025-08 | 0.421 [0.39, 0.45] | 0.858 [0.83, 0.88] | 0.154 [0.13, 0.18] |
| Claude Sonnet 5 | 2026-01 | 0.655 [0.62, 0.69] | 0.910 [0.88, 0.93] | 0.228 [0.19, 0.27] |
| GPT-5.6 Sol | 2026-02 | 0.472 [0.44, 0.51] | 0.869 [0.84, 0.89] | 0.221 [0.20, 0.24] |
| DeepSeek-V4-Pro | 2026-04 | 0.669 [0.63, 0.70] | 0.665 [0.62, 0.71] | 0.343 [0.28, 0.40] |

n = 845 merged binary, 606 MCQ, 196 date, except where refusals reduce the
denominator (§5). DeepSeek-V4-Pro is May–Aug only (639 events); its April overlap
changes MCC by 0.003, so the choice is immaterial.

DeepSeek-R1 has no extension row: the deployment returns 410 and there is no live
endpoint for the original model.

## 3. Binary accuracy is response bias, not skill

Ground truth on the binary task is **fixed by task type** in both corpora: the
binary question always resolves *yes* (the real finding), its perturbed twin
always *no* (the corrupted finding). Verified for all 6,408 original and 845
extension instances with no exceptions.

Two consequences follow, and both are load-bearing.

**Merged-binary accuracy is not comparable across corpora.** Class balance is just
the task-type ratio, and it differs: 43.0% yes in the original, 23.2% in the
extension. A no-leaning model gains ~0.20 from that alone. Observed shifts match
response bias in sign for all six models that ran both halves:

| Model | bias | original → extension |
|---|---|---|
| LLaMA 3.3 70B | +0.93 | 0.453 → 0.271 (−0.182) |
| GPT-5.4 | +0.23 | 0.491 → 0.421 (−0.070) |
| GPT-5.6 Sol | +0.32 | 0.485 → 0.472 (−0.013) |
| Claude S4.5 | −0.48 | 0.526 → 0.558 (+0.032) |
| GPT-4o | −0.55 | 0.519 → 0.566 (+0.047) |
| Claude Sonnet 5 | −0.50 | 0.578 → 0.655 (+0.077) |

**Bias-immune metrics tell a different story.** Over the full corpus, post-cutoff:

| Model | n | bias | balanced acc | MCC |
|---|---|---|---|---|
| GPT-5.6 Sol | 1,183 | +0.33 | 0.574 | **+0.141** |
| Claude Sonnet 5 | 1,387 | −0.50 | 0.527 | **+0.057** |
| LLaMA 3.3 70B | 7,204 | +0.85 | 0.511 | +0.040 |
| GPT-5.4 | 2,679 | +0.23 | 0.505 | +0.010 |
| DeepSeek-R1 | 5,149 | +0.03 | 0.482 | −0.036 |
| GPT-OSS 20B | 6,306 | −0.56 | 0.470 | −0.069 |
| Claude S4.5 | 4,270 | −0.48 | 0.472 | −0.062 |
| GPT-4o | 7,253 | −0.55 | 0.472 | −0.067 |
| DeepSeek-V4-Pro | 845 | −0.74 | 0.465 | −0.088 |

**The clearest statement of the binary signal is the paired discrimination gap:**
P(yes | real finding) − P(yes | corrupted finding), computed **within the same
event**, post-cutoff only, CIs bootstrapped over pairs. It asks directly whether
a model can tell a real finding from a plausible fake, and it is immune to both
the class-balance problem (rates conditioned separately) and to response bias (a
uniform shift cancels).

**Pairing is mandatory, not a refinement.** Only 2,289 of 5,575 events carry both
a real and a perturbed binary question. Computing the two rates over all
available items compares different papers in different domains, and the question
forms differ systematically — real questions are long conjunctive claims bundling
many exact numbers, perturbed ones are short single claims. Unpaired, five models
appear significantly *anti*-discriminating. Paired, none do. That entire result
was artifact.

| Model | P(yes \| real) | P(yes \| corrupted) | gap | 95% CI | pairs |
|---|---|---|---|---|---|
| Claude Sonnet 5 | 0.295 | 0.156 | **+0.139** | [+0.086, +0.189] | 339 |
| GPT-5.6 Sol | 0.762 | 0.623 | **+0.139** | [+0.078, +0.203] | 281 |
| GPT-5.4 | 0.629 | 0.561 | **+0.068** | [+0.028, +0.108] | 760 |
| LLaMA 3.3 70B | 0.935 | 0.899 | **+0.036** | [+0.023, +0.050] | 2,274 |
| DeepSeek-R1 | 0.483 | 0.467 | +0.016 | [−0.012, +0.042] | 1,668 |
| GPT-4o | 0.208 | 0.209 | −0.001 | [−0.019, +0.017] | 2,288 |
| GPT-OSS 20B | 0.189 | 0.191 | −0.002 | [−0.023, +0.020] | 1,953 |
| Claude S4.5 | 0.233 | 0.239 | −0.006 | [−0.032, +0.024] | 1,295 |
| DeepSeek-V4-Pro | 0.079 | 0.115 | −0.036 | [−0.097, +0.030] | 165 |

Four models discriminate significantly — Claude Sonnet 5 and GPT-5.6 Sol at
+0.139, GPT-5.4 at +0.068, LLaMA 3.3 at +0.036 — and the remaining five sit at
zero. No model is significantly anti-discriminating. The ranking is sensible:
the newest models lead, the oldest cluster at zero.

Note the cost of pairing: Sonnet 5's estimate rests on 339 pairs and Sol's on
281, not thousands, because pairing plus the post-cutoff filter is restrictive.

**Residual confound, not fixable in analysis.** Even within pairs the real
question runs longer than the perturbed one (median 176 vs 131 chars), so part
of a positive gap may reflect length or specificity rather than truth
discrimination. Testing that requires length-matched perturbations — a dataset
change, recorded here as a limitation.

**Recommendation: report the paired gap as the binary column in Table 1, with
MCC alongside and the pair count stated.** Move raw merged accuracy to the
supplement: it mostly measures which way a model leans.

## 3b. Cross-corpus MCQ comparison, with the domain mix controlled

The two corpora are **not** drawn from the same domain mix (χ²=212.3, df=8): the
AI share falls 24.0% → 16.3% and "Other" grows 1.3% → 6.6%. Biology and Medicine
are stable, so the refusal analysis in §5 is unaffected, but a crude
extension-vs-original MCQ difference confounds performance with item population.

Stratifying within `main_area` and pooling per-area deltas with weights
n_o·n_e/(n_o+n_e) cancels the mix:

| Model | crude | domain-stratified | areas |
|---|---|---|---|
| GPT-4o | −0.068 ± 0.043 | **−0.074 ± 0.042** | 9 |
| LLaMA 3.3 70B | +0.008 ± 0.042 | +0.007 ± 0.042 | 9 |
| GPT-OSS 20B | +0.052 ± 0.043 | +0.040 ± 0.043 | 9 |
| Claude S4.5 | +0.056 ± 0.043 | +0.066 ± 0.042 | 9 |
| GPT-5.4 | +0.066 ± 0.036 | **+0.059 ± 0.036** | 9 |
| Claude Sonnet 5 | +0.027 ± 0.041 | +0.045 ± 0.041 | 7 |
| GPT-5.6 Sol | +0.019 ± 0.055 | +0.025 ± 0.054 | 7 |

The two columns agree: the largest shift is 0.018 against CI half-widths near
0.041. The mix difference does not drive these deltas — but that is a measured
result, not an assumption, and χ²=212.3 was large enough to require checking.

Only GPT-4o and GPT-5.4 have CIs excluding zero, in opposite directions. The rest
are consistent with no change between corpora.

**Report the stratified column; the crude one belongs in the supplement.** This
also settles the GPT-OSS 20B serving-stack question (§9): its stratified delta of
+0.040 is still mid-pack, so the vLLM substitution did not make it an outlier.

## 4. Binary foresight has a short half-life

Pooled, binary looks like chance. Stratified by horizon, with event-clustered
bootstrap CIs (2,000 resamples), it is not:

| Model | 0–2 mo | 3–5 mo | 6–11 mo |
|---|---|---|---|
| GPT-5.6 Sol | **+0.195** [+0.065, +0.316] | **+0.104** [+0.028, +0.175] | −0.047 [−0.200, +0.116] |
| Claude Sonnet 5 | — | +0.088 [−0.002, +0.176] | +0.012 [−0.094, +0.120] |

Sol's MCC excludes zero at 0–2 and 3–5 months and collapses into noise by 6–11.
Sonnet 5 traces the same decay one bin later. Binary foresight is **real but
short-lived — detectable to about five months, gone by six.** This also explains
the pooled near-zero MCCs: older-cutoff models are only ever observed at 24+ month
horizons, where nothing remains.

Report MCC by horizon, never raw accuracy by horizon — accuracy declines across
bins too, but that is base-rate drift interacting with bias, not skill decay.

## 5. Refusals, and what they do to the rankings

| Model | refused | rate | Biology | Medicine | other |
|---|---|---|---|---|---|
| Claude S4.5 | 361 | 15.9% | 35.8% | 28.0% | 5.8% |
| Claude Sonnet 5 | 76 | 3.3% | 7.9% | 8.6% | 0.4% |
| GPT-5.6 Sol | 11 | 0.5% | 1.0% | 1.7% | 0.0% |
| GPT-5.4 | 1 | 0.0% | 0.0% | 0.3% | 0.0% |
| GPT-4o, LLaMA 3.3, GPT-OSS 20B, DeepSeek-V4-Pro | 0 | 0.0% | — | — | — |

Refusals are their own outcome category and excluded from denominators. That
choice moves results, so it must be stated:

| Model | MCQ excluded | MCQ as-wrong |
|---|---|---|
| Claude Sonnet 5 | 0.910 (n=569) | 0.855 (n=606) |
| GPT-5.4 | 0.858 (n=606) | 0.858 (n=606) |
| Claude S4.5 | 0.755 (n=473) | 0.592 (n=606) |

**Sonnet 5's MCQ lead over GPT-5.4 does not survive the worst-case convention** —
0.855 vs 0.858 is a tie. Any claim that Sonnet 5 leads on MCQ must name the
convention and show both columns.

## 6. Open problem: MCQ may not be measuring foresight

The retrospective ceiling on MCQ is ~1.0 for every model:

| Model | MCQ pre-cutoff | MCQ post-cutoff | ratio |
|---|---|---|---|
| GPT-OSS 20B | 0.497 | 0.474 | 0.954 |
| DeepSeek-R1 | 0.619 | 0.589 | 0.950 |
| Claude S4.5 | 0.762 | 0.708 | 0.930 |
| GPT-5.4 | 0.830 | 0.814 | 0.980 |
| Claude Sonnet 5 | 0.912 | 0.900 | 0.987 |
| GPT-5.6 Sol | 0.879 | 0.864 | 0.982 |

MCQ is the only task clearly above chance, and also the task that least
distinguishes seen from unseen material. Sonnet 5 loses 1.3% crossing its own
cutoff. If MCQ measured foresight, crossing the cutoff should cost far more.

The likely explanation is that MCQ is substantially answerable from the problem
statement in the prompt, without forecasting. That would reconcile all three
results: MCQ scores high and is horizon-insensitive because it is not a
forecasting task; binary and date are genuinely predictive, which is why both fall
below their constant-answer baselines on unseen events.

**Proposed test:** re-run MCQ with the problem statement stripped. If accuracy
holds, the task is reading comprehension; if it falls to chance, the framing
survives. This needs a new prompt variant, which is outside the freeze — not
started.

## 7. Web search isolates the leakage mechanism

Sonnet 5, 83 shared post-cutoff events:

| Metric | n | base | WS + cutoff | WS unrestricted |
|---|---|---|---|---|
| Binary | 23 | 0.391 | **+0.000** (p=1.000) | **+0.435** (p=0.002) |
| Date score | 23 | 0.225 | +0.055 (n.s.) | **+0.313** (p=0.001) |
| Date month error | 23 | 21.3 mo | +1.3 (n.s.) | **−11.0 mo** (p=0.002) |
| MCQ | 59 | 0.966 | −0.085 (p=0.062) | +0.000 (n.s.) |

Δ_know = +0.000, Δ_fore = +0.435. Retrieval restricted to before the cutoff adds
*nothing*; unrestricted retrieval, which reaches the published papers, adds 0.435.
On a 100%-post-cutoff corpus this isolates the mechanism cleanly. Small n — present
as a mechanism demonstration, not a precise effect size.

## 8. Stage-1 leakage: what it can and cannot show here

Judging is in progress. Partial result: 1,320 of 5,184 responses judged, 100%
with web search actually used, **0.7% returning a "fail"** verdict.

That number must not be reported as a contamination rate, because on this corpus
the judge cannot measure contamination. Its evidence search runs against the live
web with no date restriction. When a model produces a description close to the
real finding, the search surfaces the paper — published *after* every model's
cutoff — and the judge records leakage.

Manual review of the first 8 failures:

| Cause | n | Explanation |
|---|---|---|
| Evidence is the target paper itself | 5 | Published post-cutoff; the model cannot have memorised it |
| Flagged entity was in the model's own prompt | 2 | `CASP5`, `R4P`/`SWE-RM` — the model was handed these |
| Other | 1 | Generic phrasing (`Token-Level Credit Assignment`) matching an unrelated paper |

A GPT-OSS 20B model with a 2024-06 cutoff cannot have memorised an August 2026
arXiv paper. Naming something the judge then matches to that paper is a correct
forecast or, more likely given entries like "Token-Level Credit Assignment", a
generic phrase colliding with a real title.

**Correct framing:** "manual review of all flagged cases found no evidence of
contamination" — not "the judge measured a 0.7% leakage rate." At 0.7% of 5,184
that is roughly 35 cases, few enough to review by hand, which is the plan.

The check still earns its place: it would catch a model whose true cutoff is later
than stated, the one contamination route that survives a post-cutoff corpus.

Two judge-side fixes for the methods section, both outside the freeze and **not
made**: the evidence search should be date-restricted to the model's cutoff, and
entities appearing in the prompt should be filtered before flagging.

## 9. Reliability and provenance

- **Run-to-run variance** (Sonnet 5, three passes, temperature unavailable):
  merged binary sd 0.0096, MCQ sd 0.0048, date sd 0.0041, refusals 76/79/78.
  Every cross-model difference reported here is an order of magnitude larger.
- **Judge self-consistency**: 255/266 = 95.9% identical verdicts on independent
  re-judgements. All 11 disagreements were pass↔unclear; none flipped pass↔fail.
- **GPT-OSS 20B serving**: the Azure deployment no longer exists and the published
  checkpoint is not on this host, so its extension row was produced under vLLM
  0.19.0 on local GPUs rather than the HF transformers pipeline behind the
  published row. Empirical check: its extension-vs-original MCQ delta is
  +0.052 ± 0.043, mid-pack against the panel's −0.068 to +0.066, so the change did
  not make it an outlier.
- **Cost**: $44.68 total on first-party APIs. Azure and local rows report tokens
  only; no dollar figure is invented for negotiated or local serving.

## 10. Reproducing

```bash
scripts/make_run2_tables.sh      # every table, from stored outputs, no inference
```

Raw predictions are excluded from git; md5s are recorded in the commit log.
