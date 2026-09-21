# Continuous horizon fits (pooled, model fixed effects, natural cubic spline with 4 df; broken-stick breakpoint search)

Curves are for the model-average intercept; 95% band from 500 event-bootstrap refits. The broken-stick model fits `h + max(h − b, 0)` with model FE and picks b by deviance/SSE; its breakpoint CI is a 200-resample event bootstrap over a coarse grid. `bend (curvature)` is the grid month where the spline's second difference is largest. No event effects here: these fits describe the pooled shape, they do not identify horizon from calendar drift.


## 1. original corpus (Jan 2024–Mar 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 27982 | -0.0024 | 15 [4, 26] | -0.0043 | 0.0008 | 0.6 (deviance) | 8 |
| mcq:accuracy | 17751 | -0.0113 | 4 [4, 26] | -0.0657 | -0.0090 | 4.4 (deviance) | 8 |
| date:signed_err | 11164 | -0.9732 | 12 [4, 26] | -0.7668 | -1.1408 | 4999.6 (SSE) | 7 |
| date:abs_err | 11164 | -0.6871 | 17 [5, 26] | -0.8080 | -0.3578 | 5574.1 (SSE) | 7 |
| date:date_score | 11164 | 0.0136 | 17 [17, 18] | 0.0211 | -0.0066 | 21.0 (SSE) | 14 |

## 2. extension (Apr–Aug 2026), base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 6419 | -0.0282 | 17 [4, 26] | -0.0563 | 0.0050 | 2.3 (deviance) | 8 |
| mcq:accuracy | 4546 | -0.0417 | 11 [8, 30] | 0.0536 | -0.0837 | 5.7 (deviance) | 24 |
| date:signed_err | 1440 | -1.3732 | 29 [4, 30] | -2.1612 | 0.9896 | 4322.4 (SSE) | 7 |
| date:abs_err | 1440 | 0.3252 | 27 [4, 28] | -0.1953 | 1.6650 | 1779.7 (SSE) | 6 |
| date:date_score | 1440 | -0.0086 | 26 [4, 30] | 0.0013 | -0.0340 | 0.6 (SSE) | 23 |

## 4. merged original + extension, base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 34401 | -0.0045 | 24 [22, 30] | -0.0018 | -0.0237 | 6.3 (deviance) | 8 |
| mcq:accuracy | 22297 | -0.0064 | 30 [4, 30] | -0.0043 | -0.1056 | 7.8 (deviance) | 8 |
| date:signed_err | 12604 | -1.0502 | 22 [4, 28] | -0.9386 | -1.6579 | 12059.7 (SSE) | 15 |
| date:abs_err | 12604 | -0.6462 | 17 [4, 30] | -0.7639 | -0.4263 | 5353.2 (SSE) | 7 |
| date:date_score | 12604 | 0.0106 | 17 [16, 18] | 0.0183 | -0.0039 | 23.2 (SSE) | 15 |
