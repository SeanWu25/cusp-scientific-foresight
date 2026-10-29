# Run 2 results — extension corpus and full-dataset panel

Status: COMPLETE. Every model, both corpora, every task — closed-form, stage-1
leakage, and stage-2 FRQ quality under the unchanged published rubric. Finalized
2026-09-21 03:52; regenerate with `scripts/finalize_run2.sh` (no inference).
All numbers below come from stored predictions scored by the frozen `scoring_v1`
graders. Nothing here required re-running any of the six published models. Panel:
ten models — the six in the paper plus Claude Sonnet 5, GPT-5.6 Sol,
DeepSeek-V4-Pro and Claude Opus 4.8 (added 2026-09-22, §9) — on the entire
dataset (5,575 events; DeepSeek-R1 original only).
§10 gives the pre/post-cutoff split for every task; §11 the relationships among
the four tasks (A1.2).

**This corpus is not prospective.** Every outcome had resolved before the models
ran. What it is: 815 events published April–August 2026, which postdate every
model's knowledge cutoff, so the corpus is uncontaminated by training data. That
addresses contamination, not the absence of a Time Capsule, and every table says so.

---

## 1. Headline

Four tasks, and only two of them show skill on uncontaminated material — and those
two barely distinguish seen from unseen material (§6, §10).

| Task | Result on the extension | Trivial baseline | Verdict |
|---|---|---|---|
| Merged binary | best 0.673 (DeepSeek-V4-Pro) | always-"no" = **0.768** | 0 of 9 models beat the baseline |
| Date | best 0.506 (GPT-4o) | constant "2026-06" = **0.893** | no model close |
| MCQ | best 0.928 (Claude Opus 4.8), 0.910 (Sonnet 5) | chance = 0.250 | clearly above chance |
| FRQ (0–10) | best 4.84 (Sol) ≈ 4.83 (GPT-5.4) | no trivial baseline | real spread across models; retrospective ceiling ~1.0 |

MCQ and FRQ are the tasks showing skill. Section 6 argues MCQ may not be measuring
foresight; §10 shows FRQ has the same near-1.0 retrospective ceiling.

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
| DeepSeek-V4-Pro | 196 | 0.346 | 2026-06 | 0.893 | −0.547 |
| Claude Opus 4.8 | 407 | 0.249 | 2026-02 | 0.827 | −0.578 |

Every gap is negative, across 196–2,950 items per model. The gap widens with
cutoff recency, but that is an artefact worth naming rather than a finding: a
later cutoff leaves a narrower remaining window, which strengthens the constant
guess. The substantive point is the sign.

So: **two of the four tasks are beaten by trivial constant strategies on unseen
events, and the other two have retrospective ceilings near 1.0** (§10).

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
| Claude Opus 4.8 | 2026-01 | 0.640 [0.61, 0.67] | **0.928** [0.90, 0.95] | 0.200 [0.17, 0.23] |

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

**Bias-immune metrics tell a different story — and here is every task, post-cutoff,
over the entire dataset, one row per model.** Original + extension pooled; per model,
only events on/after its cutoff month (rule `main`). Binary shows raw merged accuracy
for reference (confounded, §3 above) beside balanced accuracy and MCC. FRQ is the published-rubric
mean. Wilson CIs for proportions, normal for means; refusals excluded. Generated by
`run_evaluation/postcutoff_panel.py` → `tables/10_postcutoff_panel.{md,json}`; the
pre/post split of the same quantities is §10.

| Model | cutoff | events | binary n | raw merged acc | balanced acc | MCC | MCQ (n) | FRQ 0–10 (n) | date score (n) |
|---|---|---|---|---|---|---|---|---|---|
| GPT-4o* | 2023-10 | 5,575 | 7,253 | 0.524 [0.513, 0.536] | 0.472 [0.458, 0.485] | -0.067 | 0.521 [0.507, 0.535] (4,732) | 3.28 [3.25, 3.31] (4,758) | 0.199 [0.190, 0.209] (2,950) |
| LLaMA 3.3 70B* | 2023-12 | 5,575 | 7,204 | 0.432 [0.420, 0.443] | 0.511 [0.502, 0.519] | +0.040 | 0.435 [0.421, 0.449] (4,693) | 3.48 [3.46, 3.50] (4,723) | 0.485 [0.476, 0.495] (2,930) |
| GPT-OSS 20B | 2024-06 | 4,918 | 6,306 | 0.531 [0.519, 0.543] | 0.470 [0.456, 0.485] | -0.069 | 0.474 [0.459, 0.489] (4,153) | 3.86 [3.83, 3.88] (4,182) | 0.337 [0.325, 0.350] (2,479) |
| DeepSeek-R1† | 2024-07 | 3,918 | 5,149 | 0.480 [0.466, 0.494] | 0.482 [0.462, 0.501] | -0.036 | 0.589 [0.571, 0.606] (2,962) | 4.18 [4.15, 4.21] (3,376) | 0.328 [0.316, 0.340] (2,143) |
| Claude S4.5 | 2025-01 | 3,668 | 4,270 | 0.531 [0.516, 0.546] | 0.472 [0.453, 0.491] | -0.062 | 0.708 [0.691, 0.725] (2,784) | 4.01 [3.98, 4.05] (2,909) | 0.275 [0.261, 0.288] (1,624) |
| GPT-5.4 | 2025-08 | 2,203 | 2,679 | 0.469 [0.450, 0.488] | 0.505 [0.478, 0.532] | +0.010 | 0.814 [0.795, 0.831] (1,801) | 4.96 [4.93, 5.00] (1,842) | 0.245 [0.227, 0.264] (924) |
| Claude Sonnet 5 | 2026-01 | 1,270 | 1,387 | 0.624 [0.598, 0.649] | 0.527 [0.492, 0.563] | +0.057 | 0.900 [0.879, 0.918] (930) | 4.47 [4.42, 4.52] (1,008) | 0.288 [0.261, 0.315] (410) |
| GPT-5.6 Sol | 2026-02 | 1,067 | 1,183 | 0.485 [0.457, 0.514] | 0.574 [0.534, 0.612] | +0.141 | 0.864 [0.839, 0.886] (815) | 4.88 [4.82, 4.94] (836) | 0.233 [0.214, 0.252] (327) |
| DeepSeek-V4-Pro‡ | 2026-04 | 815 | 845 | 0.673 [0.641, 0.704] | 0.465 [0.436, 0.501] | -0.088 | 0.665 [0.627, 0.701] (606) | 3.99 [3.92, 4.06] (629) | 0.346 [0.293, 0.399] (196) |
| Claude Opus 4.8 | 2026-01 | 1,270 | 1,374 | 0.604 [0.578, 0.630] | 0.491 [0.459, 0.525] | -0.020 | 0.928 [0.910, 0.943] (922) | 4.64 [4.59, 4.69] (1,013) | 0.249 [0.226, 0.271] (407) |

\* cutoff precedes the corpus (Jan 2024), so post-cutoff is the entire dataset — no retrospective rows exist for this model.  
† original corpus only (4,760 events); no extension run exists (endpoint retired).  
‡ cutoff 2026-04 overlaps the extension: April 2026 (176 events) counts as post under this rule; §2 of RUN2_RESULTS.md reports it May–Aug only, and the choice moves MCC by 0.003.

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
| Claude Opus 4.8 | 0.213 | 0.171 | +0.042 | [−0.006, +0.093] | 334 |

Four models discriminate significantly — Claude Sonnet 5 and GPT-5.6 Sol at
+0.139, GPT-5.4 at +0.068, LLaMA 3.3 at +0.036 — and the remaining six sit at
zero, Claude Opus 4.8 among them (+0.042, CI touching zero) despite the panel's
best MCQ: the two tasks dissociate within a single model. No model is significantly anti-discriminating. The ranking is sensible:
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
| Claude Opus 4.8 | −0.001 ± 0.034 | +0.014 ± 0.034 | 7 |

The two columns agree: the largest shift is 0.018 against CI half-widths near
0.041. The mix difference does not drive these deltas — but that is a measured
result, not an assumption, and χ²=212.3 was large enough to require checking.

Only GPT-4o and GPT-5.4 have CIs excluding zero, in opposite directions. The rest
are consistent with no change between corpora — Claude Opus 4.8 most exactly so,
at +0.014 ± 0.034 on the largest MCQ samples of any recent model (0.935
pre-cutoff vs 0.928 post). DeepSeek-V4-Pro has no
post-cutoff rows on the original corpus (its cutoff postdates it), so no
post-cutoff cross-corpus delta exists for it; its pre/post split is in §10.

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
| Claude Opus 4.8 | −0.023 [−0.10, +0.05] | −0.016 [−0.10, +0.07] | −0.036 [−0.13, +0.08] |

Sol's MCC excludes zero at 0–2 and 3–5 months and collapses into noise by 6–11.
Sonnet 5 traces the same decay one bin later. Claude Opus 4.8 — same cutoff,
same API, same decoding — is flat at chance in every bin. Binary foresight is **real but
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
| Claude Opus 4.8 | 79 | 3.5% | 8.7% | 8.1% | 0.5% |
| GPT-5.4 | 1 | 0.0% | 0.0% | 0.3% | 0.0% |
| GPT-4o, LLaMA 3.3, GPT-OSS 20B, DeepSeek-V4-Pro | 0 | 0.0% | — | — | — |

Refusals are their own outcome category and excluded from denominators. That
choice moves results, so it must be stated:

| Model | MCQ excluded | MCQ as-wrong |
|---|---|---|
| Claude Opus 4.8 | 0.928 (n=569) | 0.871 (n=606) |
| Claude Sonnet 5 | 0.910 (n=569) | 0.855 (n=606) |
| GPT-5.4 | 0.858 (n=606) | 0.858 (n=606) |
| Claude S4.5 | 0.755 (n=473) | 0.592 (n=606) |

**Sonnet 5's MCQ lead over GPT-5.4 does not survive the worst-case convention** —
0.855 vs 0.858 is a tie. Opus 4.8's does (0.871 vs 0.858), narrowly. Any claim that Sonnet 5 leads on MCQ must name the
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
| DeepSeek-V4-Pro | 0.668 | 0.665 | **0.996** |
| Claude Opus 4.8 | 0.935 | 0.928 | 0.993 |

DeepSeek-V4-Pro is the sharpest case: 4,128 pre-cutoff MCQ items (the largest
retrospective sample in the panel) against 606 post-cutoff, and the ratio is
0.996. Full per-task pre/post split with CIs in §10.

MCQ is the task most clearly above chance, and also the task that least
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

## 6b. FRQ quality — every model, both corpora, published rubric

Same judge and four dimensions as the six published models (`judge_frq_combined`,
sha256 `fc24e69d…`, 0–10, pass ≥ 5.0). Coverage 99.7–100% everywhere; the 12
gradeable-but-unscored items across ~19,000 are ones the judge declined to score
on two independent attempts (its rationales are refusals or code-fenced JSON the
frozen parser cannot read) — unassessable by this judge, not unattempted.

**Original corpus** (Jan 2024 – Mar 2026):

| Model | n | mean | pass % | align | spec | novel | feas |
|---|---|---|---|---|---|---|---|
| GPT-5.4 | 4,128 | **5.04** | **60.3** | 3.30 | 6.21 | 4.91 | 5.73 |
| GPT-5.6 Sol | 4,072 | **4.97** | **54.8** | 3.63 | 6.00 | 4.38 | 5.89 |
| Claude Opus 4.8 | 4,030 | 4.80 | 47.6 | 3.56 | 5.60 | 4.30 | 5.72 |
| Claude Sonnet 5 | 4,026 | 4.54 | 37.2 | 3.06 | 5.40 | 4.12 | 5.58 |
| DeepSeek-R1 | 4,100 | 4.18 | 20.0 | 2.29 | 5.32 | 4.07 | 5.04 |
| Claude S4.5 | 3,908 | 3.99 | 14.0 | 2.31 | 4.71 | 3.95 | 5.01 |
| DeepSeek-V4-Pro | 4,132 | 3.97 | 17.2 | 2.11 | 5.32 | 3.72 | 4.73 |
| GPT-OSS 20B | 4,123 | 3.86 | 11.9 | 2.06 | 4.89 | 3.70 | 4.78 |
| LLaMA 3.3 70B | 4,093 | 3.49 | 2.5 | 2.23 | 3.33 | 2.38 | 6.00 |
| GPT-4o | 4,128 | 3.26 | 3.9 | 2.25 | 2.91 | 2.44 | 5.45 |

**Extension** (Apr – Aug 2026, 100% post-cutoff; DeepSeek-V4-Pro May–Aug only,
so its n is 497 not ~630 — the April cutoff-month exclusion, not missing
responses):

| Model | n | mean | pass % | align | spec | novel | feas |
|---|---|---|---|---|---|---|---|
| GPT-5.6 Sol | 623 | **4.84** | **49.3** | 3.37 | 5.91 | 4.41 | 5.68 |
| GPT-5.4 | 628 | **4.83** | **50.0** | 3.32 | 5.73 | 4.63 | 5.64 |
| Claude Opus 4.8 | 622 | 4.58 | 38.6 | 3.19 | 5.35 | 4.40 | 5.38 |
| Claude Sonnet 5 | 618 | 4.44 | 30.1 | 2.84 | 5.22 | 4.22 | 5.48 |
| DeepSeek-V4-Pro | 497 | 4.00 | 15.5 | 2.07 | 5.27 | 3.80 | 4.85 |
| Claude S4.5 | 558 | 3.99 | 11.1 | 2.26 | 4.65 | 4.09 | 4.94 |
| GPT-OSS 20B | 628 | 3.85 | 10.7 | 2.00 | 5.15 | 3.84 | 4.41 |
| LLaMA 3.3 70B | 630 | 3.42 | 1.9 | 2.16 | 3.29 | 2.33 | 5.91 |
| GPT-4o | 630 | 3.40 | 2.7 | 2.22 | 2.96 | 2.43 | 5.99 |

Sol and GPT-5.4 are tied on the extension (0.01 apart) and 0.07 apart on the
original — both inside the noise floor. Claude Opus 4.8 is third on both
(4.80 / 4.58), ahead of Sonnet 5. The
sub-dimension shape is universal: models propose *feasible* approaches (4.4–6.0)
that do not *align* with what the paper did (2.0–3.6). Alignment is the
discriminating dimension, and Sol leads it on the original corpus (3.63).

**Extension vs original, domain-stratified, post-cutoff only** (judge noise
cancels in the difference; sampling CIs are the right bar):

| Model | Δ mean | 95% CI |
|---|---|---|
| GPT-5.4 | **−0.18** | [−0.26, −0.10] |
| GPT-5.6 Sol | −0.07 | [−0.21, +0.07] (6 areas) |
| LLaMA 3.3 70B | −0.06 | [−0.12, −0.00] |
| Claude Sonnet 5 | −0.04 | [−0.15, +0.07] |
| Claude S4.5 | −0.01 | [−0.08, +0.06] |
| GPT-OSS 20B | +0.00 | [−0.07, +0.07] |
| GPT-4o | **+0.16** | [+0.09, +0.22] |

Mostly flat. GPT-5.4's −0.18 (pass rate 60% → 50%) is the one substantive drop
on unseen material. Crude and stratified agree throughout (largest shift 0.03),
so the domain-mix difference between corpora (χ²=212) does not drive this.

Caveats that travel with these numbers: single-item judge noise is 0.39, so
model-to-model gaps below ~0.4 are not meaningful (§9); the two Claude rows are
graded on truncated text, direction of effect not established (§9); Sol's
original-corpus web-search files were regenerated on 2026-09-20 (§9).

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

Claude Opus 4.8 on the same 86-event subset (80 shared ids) shows the same
mechanism on FRQ and date and a different one on binary:

| Metric | n | base | WS + cutoff | WS unrestricted |
|---|---|---|---|---|
| FRQ score (0–10) | 67 | 4.60 | +0.15 (n.s.) | **+1.26** (p<0.001) |
| Date score | 23 | 0.176 | +0.14 (p=0.014) | **+0.48** (p<0.001) |
| Date month error | 23 | 21.8 mo | −2.3 (n.s.) | **−15.3 mo** (p<0.001) |
| Binary (real) | 23 | 0.217 | +0.30 (p=0.039) | +0.61 (p<0.001) |
| Binary (perturbed) | 69 | 0.768 | **−0.17** (p=0.008) | −0.25 (p=0.003) |

As a Δ decomposition (post-cutoff, n = 70 FRQ / 23 date): FRQ Δ_know +0.149,
Δ_fore **+1.108**; date Δ_know +0.141, Δ_fore **+0.336**; MCQ +0.018 / +0.054.
FRQ is the cleanest leakage read in the whole study: cutoff-restricted retrieval
adds 0.15 (n.s.), unrestricted adds 1.26 points. On binary, cutoff-restricted
retrieval raises the yes-rate on *both* the real and the corrupted question —
accuracy up on one, down on the other — so it shifts response bias rather than
adding discrimination. Sonnet 5 did not show that shift; Opus 4.8 does.

## 8. Stage-1 leakage: what it can and cannot show here

Complete: **5,566 judgements on the base runs, 97.9% pass, 1.90% unclear, 0.18%
fail** (10 fails; 27 across all 5,845 judgements including the web-search
conditions). Web search was used on 100%.

| Model | FRQ judged | pass | unclear | fail |
|---|---|---|---|---|
| GPT-4o | 630 | 617 | 13 | 0 |
| LLaMA 3.3 70B | 630 | 615 | 14 | 1 |
| GPT-OSS 20B | 627 | 615 | 8 | 4 |
| Claude S4.5 | 559 | 541 | 17 | 1 |
| GPT-5.4 | 629 | 615 | 14 | 0 |
| Claude Sonnet 5 | 617 | 597 | 18 | 2 |
| GPT-5.6 Sol | 623 | 615 | 6 | 2 |
| DeepSeek-V4-Pro | 629 | 620 | 9 | 0 |
| Claude Opus 4.8 | 622 | 615 | 7 | 0 |

**Do not read `reasoning_metrics.leakage` from the report JSONs.** It counts
every event lacking an FRQ response as "unclear" — 815 events against ~630 FRQ
prompts — overstating judge uncertainty roughly twofold (Claude S4.5 reads as
273 unclear when the judge returned 17). The table above comes from the
judgement files. Pre-existing schema behaviour, not introduced by this run.

### Why a "fail" here cannot mean contamination

The judge's evidence search runs against the live web with no date restriction.
On a corpus postdating every cutoff, a model describing the real finding makes
the search surface the paper, and the judge records leakage. Triage of all 27
(five-model base runs plus every web-search condition):

| Category | n |
|---|---|
| Model had live web access (unrestricted `*_ws` run) | 13 |
| Evidence is the target paper itself | 7 |
| Needs a domain reader | 4 |
| Flagged entity was in the model's own prompt | 3 |

The web-search category matters: that condition hands the model the live web, so
a post-cutoff entity is retrieval working as designed. The two search conditions
are asymmetric — a post-cutoff entity in the unrestricted run is expected, but
one in the cutoff-restricted run would mean the date filter leaked. The single
`ws_cutoff` failure is an entity from the model's own prompt, so the filter held.

The four residuals: `Token-Level Credit Assignment` (LLaMA 3.3),
`Perturb-multiome` (Claude Sonnet 5), `Imaging hidden objects with consumer
LiDAR via motion-induced sampling` (GPT-5.6 Sol, matched to arXiv 2605.17865),
and `Verifiability-Gated On-Policy Distillation (VG-OPD)` (Claude Opus 4.8,
cutoff-restricted run, matched to arXiv 2609.15404). The first two read as
generic compound phrases; the third is a full descriptive title and is the one
case genuinely worth a domain reader.

The Opus 4.8 case is worth stating because it is the artifact in its purest
form. Its restricted retrieval returned ten sources for that item, all
pre-cutoff (latest arXiv Dec 2025), and "VG-OPD" appears in none of them — the
model coined the acronym, and the judge's undated live search matched it to a
paper posted in **September 2026**, three months after the run and eight after
the model's cutoff. The date filter held; the judge's search is what was
unrestricted.

### The "unclear" verdicts are a clean signal

All 99 are cases where a model coined an unverifiable name — `INTERACT-BENCH`,
`ISREV`, `HiTARL-ACG` — and the judge declined to match it to anything real
(median score 0.00). The opposite failure mode from `fail`, and reassuring in
both directions: fabricated names are not pattern-matched to real systems, and
genuine descriptions do surface their papers.

**Reportable claim:** manual review of every flagged case across 5,083
judgements found no evidence of training contamination, with three cases pending
a domain reader. Not "the judge measured a 0.20% leakage rate."

The check still earns its place: it would catch a model whose true cutoff is
later than stated, the one contamination route a post-cutoff corpus does not
rule out by construction.

Two judge-side fixes, outside the freeze and **not made**: date-restrict the
evidence search to the model's cutoff, and filter prompt-present entities before
flagging.

## 9. Reliability and provenance

- **Run-to-run variance** (Sonnet 5, three passes, temperature unavailable):
  merged binary sd 0.0096, MCQ sd 0.0048, date sd 0.0041, refusals 76/79/78.
  Every cross-model difference reported here is an order of magnitude larger.
- **Judge self-consistency**: 255/266 = 95.9% identical verdicts on independent
  re-judgements. All 11 disagreements were pass↔unclear; none flipped pass↔fail.
- **FRQ rubric reproducibility** (44 items graded twice, independently):
  exact agreement 25%, within ±0.5 77%, **within ±1.0 98%**, mean absolute
  difference 0.392, r = 0.701, no systematic drift (means 3.39 vs 3.35). Per
  dimension MAD: alignment 0.45, specificity 0.68, novelty 0.68, feasibility
  0.84. **Do not treat FRQ differences below ~0.4 between models as
  meaningful** — that is the judge noise floor, and it applies to the published
  FRQ numbers too, being a property of the rubric and judge.
- **FRQ truncation asymmetry**: Claude responses are cut off at their token caps
  (S4.5 99.6%, Sonnet 5 97.4% on the extension; 96.3% on the original) while
  every other model answered to completion. Graded as-is by explicit decision.
  Whether this depresses their scores is NOT established: on the original
  corpus Sonnet 5 scores specificity 5.40 and alignment 3.06 despite 96%
  truncation, second in the panel on both. Footnote the asymmetry wherever FRQ
  scores appear, but do not assert a direction for its effect.
- **GPT-OSS 20B serving**: the Azure deployment no longer exists and the published
  checkpoint is not on this host, so its extension row was produced under vLLM
  0.19.0 on local GPUs rather than the HF transformers pipeline behind the
  published row. Empirical check: its extension-vs-original MCQ delta is
  +0.052 ± 0.043, mid-pack against the panel's −0.068 to +0.066, so the change did
  not make it an outlier.
- **Sol web-search runs regenerated 2026-09-20.** The original `ws_500` /
  `ws_cutoff_500` runs for GPT-5.6 Sol had `web_search_error` on every row and
  no retrieval context: the query-generation call in `scripts/web_search.py`
  sent `temperature` to a model that rejects it. A concurrent session fixed the
  call (committed in `5c68bb4`) and re-ran both files; the originals
  are kept as `*.FAILED_no_context.*`. Sonnet 5's web-search runs do **not**
  have the systemic failure (94–97% of rows carry context; the rest are
  scattered transient errors already dropped as `retrieval_failed`), so §7
  stands. Sol's `RAW_HASHES.txt` is re-frozen at finalize with the superseded
  hashes kept for provenance.
- **Concurrent sessions.** Two other Claude Code sessions worked in this repo on
  2026-09-20 (Sol web-search regeneration and stage-1 leakage; study A2 on
  binary-task validity). They share one rate-limited Azure judge deployment
  with the FRQ grading here. Finalize verifies, using A2's own loader, that
  rebuilding reports left every binary/perturbed answer count identical.
- **Claude Opus 4.8 added 2026-09-22** (`claude-opus-4-8`, dateless pinned
  snapshot; `response.model` echoes it). Cutoff **Jan 2026** (reliable and
  training), sourced from the official model page — the freeze script's Sonnet 5
  default happened to match but its provenance was wrong and was corrected by
  hand. Decoding mirrors Sonnet 5: the API rejects `temperature` (400), so
  effort=medium, no sampling params, FRQ cap 384, three extension passes
  (MCQ sd 0.0026, merged binary sd 0.0043). Gate: 150-event pilot on Sonnet 5's
  pilot events — refusals 5.0% (Bio 14.7%, Med 10.0%) vs Sonnet 5's 4.5% /
  11.6% / 11.7%. Full
  treatment: extension base ×3, extension WS pair (86), original WS pair (500),
  original base (4,760). Zero API errors across 26,000+ calls. **Inference cost
  $231, against a $133 projection**: the two 500-event web-search runs cost $87,
  not $16, because retrieved context roughly triples input tokens and the
  projection extrapolated base-condition cost per event; base runs were on
  estimate. Judging: pass 1 started on the extension files and, reaching the
  original-corpus files as they were still being written, judged partial
  snapshots of them (harmless: `--resume` is by event id and the runner writes
  whole lines); pass 2 resumed the remainder. One cutoff-restricted web-search
  item was flagged for a coined acronym ("VG-OPD") the judge matched to arXiv
  2609.15404 — a paper posted in September 2026, after the run; all ten
  retrieved sources for that item were pre-cutoff and the acronym appears in
  none of them. The date filter held; it is the §8 artifact.
- **Cost**: $44.68 on first-party APIs for the eight-model extension panel, plus
  $231 for Claude Opus 4.8's full treatment. Azure and local rows report tokens
  only; no dollar figure is invented for negotiated or local serving.

## 10. Pre- vs post-cutoff performance on the entire dataset

Every model, every task, original + extension pooled (5,575 events; DeepSeek-R1
original only). Partition rule `main`: an event published in the cutoff month
counts as post. GPT-4o and LLaMA 3.3 have no pre-cutoff rows (cutoffs precede the
corpus); DeepSeek-V4-Pro is the inverse profile — all 4,760 original events are
pre-cutoff, the 815 extension events post (April included; §2 shows it May–Aug
only, and the April choice moves MCC by 0.003). Binary is balanced accuracy (raw
merged accuracy is confounded by class balance × response bias and its pre/post
ratio would mislead). FRQ is the published-rubric mean. Refusals excluded.
Ratio = post/pre, the retrospective ceiling; near 1 means the task does not
distinguish seen from unseen material. Generated by
`run_evaluation/prepost_table.py` → `tables/09_prepost_full_corpus.{md,json}`.

### Binary (balanced accuracy, bias-corrected)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.472 [0.458, 0.485] n=7,253 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.511 [0.502, 0.519] n=7,204 | — | — |
| GPT-OSS 20B | 2024-06 | 0.475 [0.442, 0.508] n=949 | 0.470 [0.456, 0.485] n=6,306 | -0.004 | 0.991 |
| DeepSeek-R1 | 2024-07 | 0.487 [0.449, 0.526] n=1,198 | 0.482 [0.462, 0.501] n=5,149 | -0.006 | 0.989 |
| Claude S4.5 | 2025-01 | 0.484 [0.458, 0.510] n=2,516 | 0.472 [0.453, 0.491] n=4,270 | -0.012 | 0.975 |
| GPT-5.4 | 2025-08 | 0.517 [0.497, 0.537] n=4,577 | 0.505 [0.478, 0.532] n=2,679 | -0.012 | 0.976 |
| Claude Sonnet 5 | 2026-01 | 0.560 [0.542, 0.579] n=5,647 | 0.527 [0.492, 0.563] n=1,387 | -0.033 | 0.940 |
| GPT-5.6 Sol | 2026-02 | 0.605 [0.591, 0.619] n=6,070 | 0.574 [0.534, 0.612] n=1,183 | -0.031 | 0.949 |
| DeepSeek-V4-Pro | 2026-04 | 0.489 [0.478, 0.500] n=6,411 | 0.465 [0.436, 0.501] n=845 | -0.024 | 0.951 |
| Claude Opus 4.8 | 2026-01 | 0.563 [0.545, 0.582] n=5,619 | 0.491 [0.459, 0.525] n=1,374 | -0.072 | 0.872 |

### MCQ accuracy

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.521 [0.507, 0.535] n=4,732 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.435 [0.421, 0.449] n=4,693 | — | — |
| GPT-OSS 20B | 2024-06 | 0.497 [0.456, 0.537] n=580 | 0.474 [0.459, 0.489] n=4,153 | -0.023 | 0.954 |
| DeepSeek-R1 | 2024-07 | 0.619 [0.581, 0.656] n=636 | 0.589 [0.571, 0.606] n=2,962 | -0.031 | 0.950 |
| Claude S4.5 | 2025-01 | 0.762 [0.740, 0.783] n=1,546 | 0.708 [0.691, 0.725] n=2,784 | -0.054 | 0.930 |
| GPT-5.4 | 2025-08 | 0.830 [0.816, 0.843] n=2,933 | 0.814 [0.795, 0.831] n=1,801 | -0.016 | 0.980 |
| Claude Sonnet 5 | 2026-01 | 0.912 [0.902, 0.921] n=3,420 | 0.900 [0.879, 0.918] n=930 | -0.012 | 0.987 |
| GPT-5.6 Sol | 2026-02 | 0.879 [0.869, 0.889] n=3,891 | 0.864 [0.839, 0.886] n=815 | -0.015 | 0.982 |
| DeepSeek-V4-Pro | 2026-04 | 0.668 [0.653, 0.682] n=4,128 | 0.665 [0.627, 0.701] n=606 | -0.003 | 0.996 |
| Claude Opus 4.8 | 2026-01 | 0.935 [0.927, 0.943] n=3,376 | 0.928 [0.910, 0.943] n=922 | -0.007 | 0.993 |

### FRQ mean score (0–10, published rubric)

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 3.28 [3.25, 3.31] n=4,758 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 3.48 [3.46, 3.50] n=4,723 | — | — |
| GPT-OSS 20B | 2024-06 | 3.88 [3.80, 3.96] n=569 | 3.86 [3.83, 3.88] n=4,182 | -0.03 | 0.993 |
| DeepSeek-R1 | 2024-07 | 4.17 [4.11, 4.23] n=724 | 4.18 [4.15, 4.21] n=3,376 | +0.01 | 1.003 |
| Claude S4.5 | 2025-01 | 3.95 [3.91, 4.00] n=1,557 | 4.01 [3.98, 4.05] n=2,909 | +0.06 | 1.015 |
| GPT-5.4 | 2025-08 | 5.04 [5.01, 5.07] n=2,914 | 4.96 [4.93, 5.00] n=1,842 | -0.07 | 0.985 |
| Claude Sonnet 5 | 2026-01 | 4.54 [4.51, 4.57] n=3,636 | 4.47 [4.42, 4.52] n=1,008 | -0.07 | 0.984 |
| GPT-5.6 Sol | 2026-02 | 4.97 [4.94, 5.00] n=3,859 | 4.88 [4.82, 4.94] n=836 | -0.09 | 0.981 |
| DeepSeek-V4-Pro | 2026-04 | 3.97 [3.94, 4.00] n=4,132 | 3.99 [3.92, 4.06] n=629 | +0.02 | 1.005 |
| Claude Opus 4.8 | 2026-01 | 4.80 [4.77, 4.83] n=3,639 | 4.64 [4.59, 4.69] n=1,013 | -0.16 | 0.966 |

### Date score

| model | cutoff | pre-cutoff | post-cutoff | Δ (post−pre) | ratio |
|---|---|---|---|---|---|
| GPT-4o | 2023-10 | — | 0.199 [0.190, 0.209] n=2,950 | — | — |
| LLaMA 3.3 70B | 2023-12 | — | 0.485 [0.476, 0.495] n=2,930 | — | — |
| GPT-OSS 20B | 2024-06 | 0.126 [0.115, 0.137] n=472 | 0.337 [0.325, 0.350] n=2,479 | +0.211 | 2.675 |
| DeepSeek-R1 | 2024-07 | 0.145 [0.133, 0.157] n=599 | 0.328 [0.316, 0.340] n=2,143 | +0.183 | 2.264 |
| Claude S4.5 | 2025-01 | 0.201 [0.185, 0.218] n=1,166 | 0.275 [0.261, 0.288] n=1,624 | +0.073 | 1.364 |
| GPT-5.4 | 2025-08 | 0.231 [0.218, 0.244] n=2,027 | 0.245 [0.227, 0.264] n=924 | +0.014 | 1.062 |
| Claude Sonnet 5 | 2026-01 | 0.434 [0.421, 0.446] n=2,431 | 0.288 [0.261, 0.315] n=410 | -0.146 | 0.664 |
| GPT-5.6 Sol | 2026-02 | 0.376 [0.361, 0.391] n=2,624 | 0.233 [0.214, 0.252] n=327 | -0.143 | 0.620 |
| DeepSeek-V4-Pro | 2026-04 | 0.191 [0.182, 0.200] n=2,755 | 0.346 [0.293, 0.399] n=196 | +0.155 | 1.813 |
| Claude Opus 4.8 | 2026-01 | 0.492 [0.479, 0.505] n=2,412 | 0.249 [0.226, 0.271] n=407 | -0.243 | 0.505 |

CIs: Wilson for proportions (balanced-accuracy CI is the mean of the two Wilson halves, conservative), normal approximation for means. Pre-cutoff rows are retrospective: the model may have seen the paper in training.

**What the split shows.** Three of the four tasks are nearly flat across the
cutoff:

- **Binary (balanced accuracy)**: ratios 0.87–0.99. The newest models lose the
  most — Opus 4.8 −0.072 (0.563 → 0.491, the largest binary drop in the panel),
  Sonnet 5 −0.033, Sol −0.031, which is the horizon effect of §4 seen
  from the other side — their post-cutoff windows are the short-horizon ones
  where a little skill exists, and even that is small.
- **MCQ**: ratios 0.93–1.00 (Opus 4.8: 0.993), as §6 already argued; DeepSeek-V4-Pro's 0.996 on
  4,128 pre-cutoff items is the cleanest single number.
- **FRQ**: ratios 0.97–1.02 (Opus 4.8: 0.966) — still the flattest of the four. Every post-pre
  difference is within ±0.09 on a 0–10 scale, and three models score slightly
  *higher* on unseen material. FRQ therefore joins MCQ in §6's open problem:
  a task with real spread across models but no pre/post difference is not
  obviously measuring foresight, and the manuscript should say so rather than
  let the rubric's face validity carry the claim.
- **Date** is the exception, and in both directions: 0.62–0.66 for the two
  newest models, 1.36–2.68 for older ones. That is not knowledge — it is
  window geometry. A model's pre-cutoff date items sit at one distance from
  its typical guess and its post-cutoff items at another, and the
  `exp(−0.1·|Δmonths|)` score rewards whichever happens to be nearer. §1
  shows no model beats a constant guess on either side; the pre/post ratio on
  this task should not be read as a ceiling at all.

The honest summary for the paper: **the retrospective ceiling is near 1.0 on
every task where models show skill.** Whatever the benchmark measures on MCQ and
FRQ, it measures the same amount before and after the cutoff.

## 11. Relationships among the four tasks (A1.2, Reviewer 2 C1)

Full analysis, files and proposed manuscript text in
`results/A1_2_task_correlation/` (`response_A1_2.md`). Ten models, entire
dataset, binary as balanced accuracy, FRQ as the published rubric (nine- and
eight-model variants kept as `*_9models.*` / `*_8models.*`).

- **Across models (n = 10):** binary, MCQ and FRQ rise together with capability
  (MCQ–FRQ r = 0.87 [0.53, 0.97]; binary–MCQ 0.76; binary–FRQ 0.72). **Date is
  weakly and non-significantly related** to MCQ (0.20 [−0.49, +0.74]) and FRQ
  (0.20 [−0.50, +0.73]), and its CI with binary (0.61) spans zero: stronger
  models are not reliably better at predicting *when*, consistent with §1.
- **Within models, across papers** (25k–41k pairs per task pair): every median
  Spearman |ρ| ≤ 0.10. Holding the model fixed, success on one task says almost
  nothing about success on another task about the same paper.
- **Reading:** the tasks are not redundant (near-independent at the paper
  level); three share a capability factor at the aggregate level, which is a
  statement about models, not about the constructs; date is the outlier at both
  levels; nothing here bears on completeness. The response reframes the four
  tasks as one operationalization, not a decomposition.
- Sensitivity: raw merged accuracy would flip binary–date negative through
  response bias — the reason for balanced accuracy. Adding Claude Opus 4.8 as
  the tenth model moved the date correlations from ~0 to ~0.2 (its date score
  is high for a recent model) without changing any conclusion; the nine-model
  values are in `task_correlation_9models.md`.

## 12. Reproducing

```bash
scripts/finalize_run2.sh                    # sweep, merge, reports, every table, A2 check, hash re-freeze
run_evaluation/prepost_table.py             # §10: pre/post split on the entire dataset
results/A1_2_task_correlation/compute_task_correlation.py   # §11
```

All from stored outputs; only the sweep step in finalize makes judge calls, and
only for null-score leftovers. Raw predictions are excluded from git; sha256s are
in each results dir's `RAW_HASHES.txt` (superseded hashes kept).
