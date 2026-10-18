# Fixed-evidence-packet experiment (Figure 3a): extension from 500 to 1,000 events

Run on 2026-10-18. The original 500 events are unchanged. 500 events were added, every one of them published after
February 2026, so every added event is post-cutoff for every evaluated model.

## Summary

- **The goal is met.** Claude Sonnet 5 now has 531 post-cutoff events (31 before) and GPT-5.6 Sol has 504 (4 before).
- **No post-cutoff cell of Figure 3a is suppressed any more.** Before, Sol had no post-cutoff values at all, and Sonnet 5 lacked Feasibility Assessment and Temporal Prediction.
- **The pattern of the paper holds for the two new models.** On post-cutoff events the forecasting gap is positive in every task family, and the knowledge gap is small (between −0.02 and +0.10).
- **The added events reproduce the first 500.** For the four models with post-cutoff events in both halves, the forecasting gaps agree in sign in every task family. The knowledge gaps agree except GPT-4o Temporal Prediction (see Caveats) and Claude S4.5 Mechanistic Forecasting, whose two values are both near zero.

## Events per model

Post-cutoff means the publication month is after the cutoff month. An event counts when the base run and both fixed-packet runs have a record for it.

| Model | Cutoff | Pre-cutoff events | Post-cutoff events (500-event set) | Post-cutoff events (1,000-event set) |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 0 | 500 | **1000** |
| LLaMA 3.3 70B | 2023-12 | 0 | 500 | **1000** |
| Claude S4.5 | 2025-01 | 214 | 286 | **786** |
| GPT-5.4 | 2025-08 | 377 | 123 | **623** |
| Claude Sonnet 5 | 2026-01 | 469 | 31 | **531** |
| GPT-5.6 Sol | 2026-02 | 496 | 4 | **504** |

Not every event has all five tasks. In the added 500, 130 events have a Binary and a Date question, 401 a perturbed Binary question, 379 an MCQ and 385 an FRQ. This is how the extension corpus was built.

## Figure 3a values on post-cutoff events

Each cell is knowledge gap / forecasting gap. Knowledge gap = WS+Cutoff − base. Forecasting gap = WS − WS+Cutoff. Feasibility Assessment is the mean of the original and perturbed binary gaps. Solution Design is the FRQ score divided by 10. A dash means a cell with fewer than 20 events. The 500-event rows are the values in the current Figure 3a, which also require the original-setup runs, so their event sets differ slightly from the first-500 rows of the consistency check.

| Model | Events | Feasibility Assessment | Mechanistic Forecasting | Temporal Prediction | Solution Design |
|---|---|---|---|---|---|
| GPT-4o | 500 | +0.052 / +0.112 | +0.094 / +0.197 | +0.173 / +0.132 | +0.063 / +0.065 |
| GPT-4o | 1,000 | +0.071 / +0.111 | +0.097 / +0.243 | +0.079 / +0.109 | +0.049 / +0.070 |
| LLaMA 3.3 70B | 500 | +0.017 / +0.045 | +0.093 / +0.242 | -0.041 / +0.105 | +0.060 / +0.070 |
| LLaMA 3.3 70B | 1,000 | +0.035 / +0.040 | +0.071 / +0.277 | -0.049 / +0.110 | +0.050 / +0.073 |
| Claude S4.5 | 500 | +0.031 / +0.165 | -0.016 / +0.119 | -0.024 / +0.235 | +0.025 / +0.044 |
| Claude S4.5 | 1,000 | +0.047 / +0.170 | +0.000 / +0.098 | -0.036 / +0.184 | +0.024 / +0.045 |
| GPT-5.4 | 500 | +0.016 / +0.087 | -0.058 / +0.135 | +0.085 / +0.373 | +0.031 / +0.062 |
| GPT-5.4 | 1,000 | +0.031 / +0.074 | -0.048 / +0.130 | +0.095 / +0.387 | +0.040 / +0.067 |
| Claude Sonnet 5 | 500 | — | +0.000 / +0.083 | — | +0.040 / +0.079 |
| Claude Sonnet 5 | 1,000 | +0.011 / +0.193 | -0.013 / +0.075 | +0.090 / +0.383 | +0.041 / +0.083 |
| GPT-5.6 Sol | 500 | — | — | — | — |
| GPT-5.6 Sol | 1,000 | +0.001 / +0.131 | -0.005 / +0.084 | +0.091 / +0.381 | +0.028 / +0.071 |

## Per-task post-cutoff gaps with 95% CIs (1,000 events)

FRQ is on the 0–10 scale here. CIs are paired normal intervals, as in the gap decomposition code.

| Model | Task | n | Knowledge gap [95% CI] | Forecasting gap [95% CI] |
|---|---|---|---|---|
| GPT-4o | Binary | 426 | +0.291 [+0.238, +0.344] | +0.347 [+0.298, +0.397] |
| GPT-4o | Binary (pert.) | 795 | -0.148 [-0.187, -0.110] | -0.126 [-0.163, -0.089] |
| GPT-4o | MCQ | 814 | +0.097 [+0.063, +0.131] | +0.243 [+0.209, +0.277] |
| GPT-4o | FRQ (0-10) | 811 | +0.491 [+0.415, +0.568] | +0.696 [+0.607, +0.784] |
| GPT-4o | Date (0-1) | 426 | +0.079 [+0.043, +0.115] | +0.109 [+0.068, +0.149] |
| LLaMA 3.3 70B | Binary | 424 | -0.050 [-0.080, -0.019] | +0.073 [+0.043, +0.103] |
| LLaMA 3.3 70B | Binary (pert.) | 794 | +0.120 [+0.091, +0.148] | +0.008 [-0.024, +0.039] |
| LLaMA 3.3 70B | MCQ | 812 | +0.071 [+0.037, +0.106] | +0.277 [+0.244, +0.310] |
| LLaMA 3.3 70B | FRQ (0-10) | 808 | +0.505 [+0.441, +0.568] | +0.735 [+0.658, +0.811] |
| LLaMA 3.3 70B | Date (0-1) | 424 | -0.049 [-0.078, -0.019] | +0.110 [+0.074, +0.145] |
| Claude S4.5 | Binary | 250 | +0.084 [+0.014, +0.154] | +0.464 [+0.401, +0.527] |
| Claude S4.5 | Binary (pert.) | 520 | +0.010 [-0.034, +0.053] | -0.125 [-0.169, -0.081] |
| Claude S4.5 | MCQ | 479 | +0.000 [-0.046, +0.046] | +0.098 [+0.054, +0.143] |
| Claude S4.5 | FRQ (0-10) | 556 | +0.241 [+0.164, +0.319] | +0.454 [+0.377, +0.531] |
| Claude S4.5 | Date (0-1) | 248 | -0.036 [-0.080, +0.008] | +0.184 [+0.127, +0.241] |
| GPT-5.4 | Binary | 189 | +0.132 [+0.059, +0.206] | +0.148 [+0.093, +0.203] |
| GPT-5.4 | Binary (pert.) | 501 | -0.070 [-0.116, -0.024] | +0.000 [-0.043, +0.043] |
| GPT-5.4 | MCQ | 484 | -0.048 [-0.087, -0.008] | +0.130 [+0.096, +0.164] |
| GPT-5.4 | FRQ (0-10) | 486 | +0.397 [+0.311, +0.482] | +0.667 [+0.571, +0.763] |
| GPT-5.4 | Date (0-1) | 189 | +0.095 [+0.053, +0.137] | +0.387 [+0.333, +0.441] |
| Claude Sonnet 5 | Binary | 144 | +0.111 [+0.011, +0.212] | +0.438 [+0.354, +0.521] |
| Claude Sonnet 5 | Binary (pert.) | 408 | -0.088 [-0.131, -0.045] | -0.051 [-0.095, -0.008] |
| Claude Sonnet 5 | MCQ | 375 | -0.013 [-0.047, +0.020] | +0.075 [+0.042, +0.108] |
| Claude Sonnet 5 | FRQ (0-10) | 402 | +0.412 [+0.313, +0.511] | +0.833 [+0.712, +0.954] |
| Claude Sonnet 5 | Date (0-1) | 144 | +0.090 [+0.045, +0.136] | +0.383 [+0.325, +0.440] |
| GPT-5.6 Sol | Binary | 131 | +0.038 [-0.020, +0.096] | +0.176 [+0.107, +0.244] |
| GPT-5.6 Sol | Binary (pert.) | 404 | -0.037 [-0.089, +0.015] | +0.087 [+0.032, +0.142] |
| GPT-5.6 Sol | MCQ | 379 | -0.005 [-0.042, +0.031] | +0.084 [+0.050, +0.119] |
| GPT-5.6 Sol | FRQ (0-10) | 380 | +0.281 [+0.179, +0.383] | +0.711 [+0.589, +0.832] |
| GPT-5.6 Sol | Date (0-1) | 131 | +0.091 [+0.049, +0.132] | +0.381 [+0.322, +0.440] |

## Consistency check: first 500 against added 500 (post-cutoff)

| Model | Half | Feasibility Assessment | Mechanistic Forecasting | Temporal Prediction | Solution Design |
|---|---|---|---|---|---|
| GPT-4o | first 500 | +0.051 / +0.117 | +0.094 / +0.198 | +0.174 / +0.138 | +0.064 / +0.065 |
| GPT-4o | added 500 | +0.096 / +0.091 | +0.100 / +0.296 | -0.136 / +0.042 | +0.032 / +0.074 |
| LLaMA 3.3 70B | first 500 | +0.017 / +0.045 | +0.090 / +0.242 | -0.041 / +0.105 | +0.059 / +0.071 |
| LLaMA 3.3 70B | added 500 | +0.056 / +0.028 | +0.050 / +0.317 | -0.067 / +0.119 | +0.041 / +0.076 |
| Claude S4.5 | first 500 | +0.031 / +0.171 | -0.026 / +0.122 | -0.019 / +0.237 | +0.028 / +0.042 |
| Claude S4.5 | added 500 | +0.049 / +0.174 | +0.017 / +0.083 | -0.055 / +0.124 | +0.022 / +0.048 |
| GPT-5.4 | first 500 | +0.019 / +0.086 | -0.057 / +0.133 | +0.091 / +0.367 | +0.030 / +0.062 |
| GPT-5.4 | added 500 | +0.024 / +0.076 | -0.045 / +0.129 | +0.097 / +0.396 | +0.042 / +0.068 |

## Caveats

- **GPT-4o Temporal Prediction knowledge gap.** It is +0.174 on the first 500 and -0.136 on the added 500. The fixed-packet scores are similar (0.355 and 0.387), but the base score moves from 0.181 to 0.524. Most added events take their base scores from the Apr–Aug 2026 extension base runs (the Table 1 runs), not from the original-corpus base runs. The base Date scores of the older models differ between those runs. LLaMA 3.3 shows the same base shift (0.506 to 0.283), in the other direction. The shift is in the base, not in the evidence. The paper should not read much into the GPT-4o and LLaMA 3.3 Temporal Prediction knowledge gaps.
- **Retrieval date.** The added evidence was retrieved on 2026-10-18; the first 500 on 2026-09-21.
- **Original-setup comparison stays on 500 events.** The self-query runs of the original manuscript exist only for the first 500. The fixed − original tables (response Tables 20/21) are unchanged. Only Figure 3a, which uses base and fixed-packet runs, moves to 1,000 events.
- **Query writer.** The fixed queries are again from Claude Opus 4.8, which is now in the evaluated panel (open decision 1 in REVISION_STATUS.md applies to the added events too).

## Method

- **Sample.** Pool: CUSP events not in the first 500, published after 2026-02, with a stored base record for all six models (852 events). 500 were drawn, stratified by month, seed 20261018. By month: 2026-03 22, 2026-04 103, 2026-05 97, 2026-06 100, 2026-07 102, 2026-08 76.
- **Queries.** Claude Opus 4.8 wrote 466 queries with the same prompt (same prompt hash). It returned empty content for 34 events; those got gpt-5.4-mini queries, as in the first 500.
- **Evidence.** One You.com call per event for each of seven freshness bounds (the six model cutoffs and unrestricted), filtered by the unmodified retrieval code. 3,500 calls, no errors, one empty packet. The DeepSeek R1 bound was skipped; R1 has no fixed-packet run.
- **Model runs.** Six models × two conditions × 500 events, each model with its original decoding parameters. 97 records hit provider rate limits (GPT-4o, LLaMA 3.3, GPT-5.4); they were removed and re-run until no transport errors remained. Claude Sonnet 4.5 API refusals were kept as model behaviour, as in the first 500.
- **FRQ.** Graded with the same stage-2 rubric and Azure judge as the first 500. Every judgeable answer in all 12 runs has a score.

## Files

- `results/A4_retrieval/A4_3_fixed_queries/ext500/`: sample, queries, evidence, model outputs, judgements, reports, logs, README.
- `results/A4_retrieval/A4_3_fixed_queries/gaps_fixed1000.md` and `results/A4_retrieval/tables/A4_3_gaps_fixed1000*.json`: full tables, including pre-cutoff.
- `manuscript_updates/forecasting_gap_rev_1000.png` (and `.pdf`): Figure 3 with panel a on 1,000 events. Panel b is unchanged. Not pushed to Overleaf.

Regenerate (no inference):

```
python results/A4_retrieval/scripts/a43_gaps_1000.py
python results/A4_retrieval/scripts/a43_report_1000.py
python run_evaluation/make_fig3_overleaf.py --packets 1000
```
