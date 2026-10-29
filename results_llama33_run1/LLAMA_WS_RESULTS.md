# LLaMA 3.3 70B — new unrestricted web-search run and its effect on the retrieval replication (A4.3)

Prepared 2026-10-05 for the Reviewer 2 C4 response. All numbers below are regenerated from stored
outputs by `bash results_llama33_run1/postrun_ws.sh` (which ends by calling the A4.3 regenerate chain).

## Why this run exists

The published experiment had a WS+Cutoff run for LLaMA 3.3 70B but no unrestricted WS run, so
LLaMA's *original-setup* forecasting gap (WS − WS+Cutoff) was undefined in the replication table
and LLaMA contributed no cell to the forecasting-gap agreement statistics. We generated the missing
run so every model has both columns.

## What was run

| item | value |
|---|---|
| model | `Llama-3.3-70B-Instruct`, Azure AI Foundry OpenAI-compatible endpoint (same deployment as the 2026-09-20 WS+Cutoff run) |
| condition | `ws` (unrestricted You.com retrieval, single self-generated query, unmodified `scripts/run_cusp.py`) |
| decoding | temperature 0, max 2048 tokens, FRQ 2048 tokens — identical to the WS+Cutoff run |
| items | the pinned 500-event subset (`results_sonnet5_run1/subset500_ids.txt`); all 500 are post-cutoff for LLaMA (cutoff 2023-12) |
| outcome | 500 rows, 0 errors, 2 retrieval failures (dropped from gap computations, as elsewhere) |
| FRQ | 426 answers rubric-scored the same day with the unchanged legacy stage-2 rubric (Azure `gpt-5.4-mini` judge) |
| files | `raw/ws_500.jsonl` (sha256 `305d5043…`), `reports/ws_500.json`, `judgements_merged/ws_500.jsonl` |
| run date caveat | retrieval was unrestricted on 2026-10-05, so it could see documents published after the spring-2026 original runs; the run is not yet in the A4.2 ground-truth-inclusion audit |

## Condition means on the shared post-cutoff items (original query pipeline vs fixed evidence packets)

| task | N | Base | WS+Cutoff orig | WS+Cutoff fixed | WS orig (new) | WS fixed |
|---|---|---|---|---|---|---|
| Binary | 294 | 0.932 | 0.864 | 0.878 | 0.922 | 0.963 |
| Binary (perturbed) | 392 | 0.102 | 0.176 | 0.191 | 0.189 | 0.196 |
| MCQ | 430 | 0.488 | 0.533 | 0.581 | 0.793 | 0.823 |
| FRQ (0–10) | 420 | 3.464 | 3.922 | 4.063 | 4.521 | 4.766 |
| Date (0–1) | 294 | 0.506 | 0.486 | 0.466 | 0.548 | 0.571 |

## Table 18 rows for LLaMA 3.3 70B (post-cutoff; paired 95% CIs)

Knowledge gap = WS+Cutoff − Base; forecasting gap = WS − WS+Cutoff. Binary, MCQ and Date in
accuracy/score units on [0, 1]; FRQ in rubric points on the 0–10 scale.

| Task | Knowledge gap, original | Knowledge gap, fixed | Forecasting gap, original (new) | Forecasting gap, fixed |
|---|---|---|---|---|
| Binary | −0.068 [−0.107, −0.029] | −0.054 [−0.093, −0.016] | +0.058 [+0.017, +0.099] | +0.085 [+0.046, +0.124] |
| Binary (perturbed) | +0.074 [+0.032, +0.116] | +0.089 [+0.047, +0.132] | +0.013 [−0.031, +0.056] | +0.005 [−0.038, +0.048] |
| MCQ | +0.044 [−0.004, +0.092] | +0.093 [+0.043, +0.143] | +0.260 [+0.212, +0.309] | +0.242 [+0.198, +0.286] |
| FRQ (0–10) | +0.458 [+0.361, +0.554] | +0.599 [+0.511, +0.686] | +0.599 [+0.485, +0.713] | +0.703 [+0.600, +0.806] |
| Date | −0.020 [−0.056, +0.015] | −0.041 [−0.080, −0.001] | +0.062 [+0.019, +0.104] | +0.105 [+0.063, +0.148] |

Four of the five original forecasting gaps lie inside the fixed-packet CI; Date is the one outside
(+0.06 vs +0.11). N values differ by one or two items from the earlier table because the
shared-id intersection now includes the new run.

## Item-level agreement, original vs fixed-packet answer on the same event (LLaMA, post-cutoff)

Binary/MCQ: exact agreement and Cohen's κ. FRQ and Date are continuous, so Pearson r.

| task | N | WS+Cutoff agreement | WS+Cutoff κ / r | WS agreement | WS κ / r |
|---|---|---|---|---|---|
| Binary | 294 | 0.871 | κ = 0.43 | 0.912 | κ = 0.20 |
| Binary (perturbed) | 392 | 0.821 | κ = 0.41 | 0.895 | κ = 0.66 |
| MCQ | 430 | 0.816 | κ = 0.63 | 0.835 | κ = 0.47 |
| FRQ (0–10) | 420 | — | r = 0.36 | — | r = 0.43 |
| Date (0–1) | 294 | — | r = 0.51 | — | r = 0.42 |

## Effect on the agreement tables (Table 19 and the FRQ-only table)

The LLaMA cells join the forecasting-gap and unrestricted-WS rows; the WS+Cutoff and
knowledge-gap rows are unchanged. r and MAD with 10,000 cell-level bootstrap CIs; N = cells.

**Pooled, five tasks, FRQ rescaled to [0, 1]:**

| Quantity | Pre + post: r [CI] | MAD [CI] | N | Post only: r [CI] | MAD [CI] | N |
|---|---|---|---|---|---|---|
| WS+Cutoff performance | 0.99 [0.99, 1.00] | 0.020 [0.015, 0.024] | 43 | 0.99 [0.98, 1.00] | 0.025 [0.018, 0.031] | 23 |
| Unrestricted WS performance | 0.96 [0.90, 0.99] | 0.037 [0.026, 0.052] | 43 | 0.95 [0.85, 0.99] | 0.045 [0.027, 0.069] | 23 |
| Knowledge gap | 0.99 [0.97, 0.99] | 0.020 [0.015, 0.024] | 43 | 0.97 [0.94, 0.99] | 0.025 [0.018, 0.031] | 23 |
| Forecasting gap | 0.87 [0.66, 0.96] | 0.039 [0.026, 0.054] | 43 | 0.87 [0.65, 0.97] | 0.050 [0.031, 0.074] | 23 |
| Forecasting gap, excl. GPT-4o | 0.91 [0.69, 0.97] | 0.032 [0.022, 0.044] | 38 | 0.95 [0.83, 0.99] | 0.039 [0.024, 0.055] | 18 |

**FRQ only, 0–10 rubric units:**

| Quantity | Pre + post: r [CI] | MAD [CI] | N | Post only: r [CI] | MAD [CI] | N |
|---|---|---|---|---|---|---|
| WS+Cutoff performance | 1.00 [1.00, 1.00] | 0.100 [0.065, 0.136] | 9 | 1.00 [0.99, 1.00] | 0.132 [0.097, 0.169] | 5 |
| Unrestricted WS performance | 0.97 [0.93, 1.00] | 0.228 [0.133, 0.329] | 9 | 0.99 [0.96, 1.00] | 0.305 [0.228, 0.418] | 5 |
| Knowledge gap | 0.99 [0.98, 1.00] | 0.100 [0.065, 0.136] | 9 | 0.97 [0.94, 1.00] | 0.132 [0.097, 0.169] | 5 |
| Forecasting gap | 0.89 [0.70, 0.99] | 0.144 [0.077, 0.232] | 9 | 0.67 [0.14, 1.00] | 0.173 [0.100, 0.306] | 5 |

Before this run the FRQ post-only forecasting row had 4 cells and a bootstrap interval of
[−1, 1]; the fifth cell brings it to [0.14, 1.00]. The WS+Cutoff and knowledge-gap rows share a
MAD because the Base condition is identical in both setups.

## Where everything lives

* Full Table 18 (all models, tasks, pre/post, CIs): `results/A4_retrieval/tables/table17_gaps_full.{tex,md}`
* FRQ-only agreement table: `results/A4_retrieval/tables/table19_agreement_frq.{tex,md}`
* All agreement statistics and containment counts: `results/A4_retrieval/A4_3_fixed_queries/correlation.md`
* Pre/post gap tables under both setups: `results/A4_retrieval/A4_3_fixed_queries/gaps_pre_post.md`
* Response text: `results/A4_retrieval/response_A4.md` (A4.3 section), summary in `REVIEWER_RESPONSE_R2_C4.md` finding 7
