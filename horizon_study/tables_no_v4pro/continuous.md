# Continuous horizon fits (pooled, model fixed effects, natural cubic spline with 4 df; broken-stick breakpoint search)

Curves are for the model-average intercept; 95% band from 500 event-bootstrap refits. The broken-stick model fits `h + max(h − b, 0)` with model FE and picks b by deviance/SSE; its breakpoint CI is a 200-resample event bootstrap over a coarse grid. `bend (curvature)` is the grid month where the spline's second difference is largest. No event effects here: these fits describe the pooled shape, they do not identify horizon from calendar drift.


## 1. original corpus (Jan 2024–Mar 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 28298 | -0.0024 | 15 [4, 26] | -0.0043 | 0.0008 | 0.5 (deviance) | 7 |
| mcq:accuracy | 17941 | -0.0113 | 4 [4, 26] | -0.0660 | -0.0090 | 4.4 (deviance) | 8 |
| date:signed_err | 11285 | -0.9732 | 12 [4, 26] | -0.7666 | -1.1408 | 5005.4 (SSE) | 7 |
| date:abs_err | 11285 | -0.6872 | 17 [5, 26] | -0.8081 | -0.3577 | 5580.5 (SSE) | 7 |
| date:date_score | 11285 | 0.0136 | 17 [17, 18] | 0.0211 | -0.0066 | 21.0 (SSE) | 14 |
| frq:frq_score | 18461 | 0.0024 | 4 [4, 24] | 0.0361 | 0.0009 | 8.0 (SSE) | 8 |

## 2. extension (Apr–Aug 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 6572 | -0.0259 | 17 [5, 31] | -0.0490 | 0.0047 | 1.9 (deviance) | 8 |
| mcq:accuracy | 4637 | -0.0354 | 11 [5, 31] | 0.0896 | -0.0842 | 8.3 (deviance) | 7 |
| date:signed_err | 1480 | -1.4506 | 29 [7, 31] | -2.1981 | 0.9922 | 4534.5 (SSE) | 22 |
| date:abs_err | 1480 | 0.3686 | 26 [5, 29] | -0.0918 | 1.6650 | 1626.2 (SSE) | 6 |
| date:date_score | 1480 | -0.0112 | 29 [7, 31] | -0.0033 | -0.0370 | 0.5 (SSE) | 23 |
| frq:frq_score | 4937 | -0.0118 | 8 [5, 29] | 0.0099 | -0.0250 | 2.7 (SSE) | 7 |

## 4. merged original + extension, base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 34870 | -0.0043 | 24 [4, 30] | -0.0015 | -0.0241 | 6.7 (deviance) | 7 |
| mcq:accuracy | 22578 | -0.0063 | 30 [4, 30] | -0.0042 | -0.1058 | 7.9 (deviance) | 8 |
| date:signed_err | 12765 | -1.0519 | 22 [4, 28] | -0.9417 | -1.6536 | 11824.1 (SSE) | 14 |
| date:abs_err | 12765 | -0.6410 | 17 [4, 30] | -0.7505 | -0.4358 | 4663.0 (SSE) | 7 |
| date:date_score | 12765 | 0.0105 | 17 [16, 18] | 0.0181 | -0.0037 | 22.3 (SSE) | 14 |
| frq:frq_score | 23398 | 0.0010 | 27 [4, 30] | 0.0004 | 0.0105 | 1.6 (SSE) | 8 |
