# Continuous horizon fits (pooled, model fixed effects, natural cubic spline with 4 df; broken-stick breakpoint search)

Curves are for the model-average intercept; 95% band from 500 event-bootstrap refits. The broken-stick model fits `h + max(h − b, 0)` with model FE and picks b by deviance/SSE; its breakpoint CI is a 200-resample event bootstrap over a coarse grid. `bend (curvature)` is the grid month where the spline's second difference is largest. No event effects here: these fits describe the pooled shape, they do not identify horizon from calendar drift.


## 1. original corpus (Jan 2024–Mar 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 11844 | 0.0568 | 16 [5, 25] | 0.0471 | 0.0803 | 5.2 (deviance) | 7 |
| binary_perturbed:accuracy | 16454 | -0.0428 | 26 [4, 26] | -0.0410 | -0.1658 | 2.9 (deviance) | 8 |
| frq:frq_score | 18461 | 0.0024 | 4 [4, 24] | 0.0361 | 0.0009 | 8.0 (SSE) | 8 |
| frq:frq_alignment | 18461 | -0.0005 | 8 [4, 23] | 0.0181 | -0.0052 | 18.9 (SSE) | 8 |
| frq:frq_specificity | 18461 | -0.0028 | 4 [4, 24] | 0.0381 | -0.0046 | 11.7 (SSE) | 8 |
| frq:frq_novelty | 18461 | 0.0098 | 4 [4, 26] | 0.0290 | 0.0089 | 2.6 (SSE) | 8 |
| frq:frq_feasibility | 18461 | 0.0032 | 7 [4, 26] | 0.0221 | -0.0003 | 13.4 (SSE) | 8 |

## 2. extension (Apr–Aug 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 1539 | -0.0041 | 9 [5, 31] | -0.0529 | 0.0375 | 0.9 (deviance) | 7 |
| binary_perturbed:accuracy | 5033 | -0.0400 | 17 [5, 31] | -0.0665 | 0.0012 | 1.8 (deviance) | 22 |
| frq:frq_score | 4937 | -0.0118 | 8 [5, 29] | 0.0099 | -0.0250 | 2.7 (SSE) | 7 |
| frq:frq_alignment | 4937 | -0.0073 | 7 [5, 31] | 0.0108 | -0.0183 | 1.9 (SSE) | 7 |
| frq:frq_specificity | 4937 | -0.0116 | 7 [7, 31] | 0.0194 | -0.0304 | 5.5 (SSE) | 7 |
| frq:frq_novelty | 4937 | -0.0136 | 17 [5, 31] | 0.0085 | -0.0420 | 5.4 (SSE) | 7 |
| frq:frq_feasibility | 4937 | -0.0147 | 9 [5, 31] | -0.0037 | -0.0222 | 0.7 (SSE) | 7 |

## 4. merged original + extension, base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary:accuracy | 13383 | 0.0482 | 29 [4, 30] | 0.0523 | -0.1428 | 12.0 (deviance) | 7 |
| binary_perturbed:accuracy | 21487 | -0.0396 | 31 [4, 30] | -0.0409 | 0.0523 | 2.6 (deviance) | 8 |
| frq:frq_score | 23398 | 0.0010 | 27 [4, 30] | 0.0004 | 0.0105 | 1.6 (SSE) | 8 |
| frq:frq_alignment | 23398 | -0.0019 | 9 [6, 28] | 0.0094 | -0.0048 | 12.8 (SSE) | 8 |
| frq:frq_specificity | 23398 | -0.0014 | 12 [4, 26] | -0.0062 | 0.0013 | 5.2 (SSE) | 15 |
| frq:frq_novelty | 23398 | 0.0053 | 28 [20, 30] | 0.0072 | -0.0320 | 15.8 (SSE) | 8 |
| frq:frq_feasibility | 23398 | 0.0021 | 27 [26, 30] | -0.0027 | 0.0694 | 80.8 (SSE) | 8 |
