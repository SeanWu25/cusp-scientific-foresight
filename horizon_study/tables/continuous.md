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
| binary_merged:accuracy | 7233 | -0.0256 | 4 [4, 26] | -0.0982 | -0.0105 | 2.2 (deviance) | 21 |
| mcq:accuracy | 5115 | -0.0306 | 11 [8, 30] | 0.0744 | -0.0840 | 8.4 (deviance) | 24 |
| date:signed_err | 1633 | -1.5461 | 29 [4, 30] | -2.2617 | 0.9969 | 4830.0 (SSE) | 7 |
| date:abs_err | 1633 | 0.4410 | 26 [4, 28] | 0.0425 | 1.6650 | 1418.0 (SSE) | 6 |
| date:date_score | 1633 | -0.0095 | 29 [4, 30] | -0.0017 | -0.0371 | 0.6 (SSE) | 22 |
| frq:frq_score | 5434 | -0.0110 | 7 [4, 30] | 0.0088 | -0.0250 | 2.8 (SSE) | 6 |

## 4. merged original + extension, base

| task:metric | n | linear slope /mo | breakpoint b [CI] | slope before b | slope after b | gain vs linear | bend (curvature) |
|---|---|---|---|---|---|---|---|
| binary_merged:accuracy | 35531 | -0.0044 | 24 [4, 30] | -0.0015 | -0.0241 | 6.7 (deviance) | 15 |
| mcq:accuracy | 23056 | -0.0063 | 30 [4, 30] | -0.0042 | -0.1059 | 7.9 (deviance) | 7 |
| date:signed_err | 12918 | -1.0525 | 22 [4, 28] | -0.9427 | -1.6521 | 11744.8 (SSE) | 14 |
| date:abs_err | 12918 | -0.6404 | 17 [4, 30] | -0.7487 | -0.4371 | 4575.0 (SSE) | 7 |
| date:date_score | 12918 | 0.0105 | 17 [16, 18] | 0.0180 | -0.0037 | 22.3 (SSE) | 14 |
| frq:frq_score | 23895 | 0.0010 | 27 [4, 30] | 0.0004 | 0.0105 | 1.6 (SSE) | 7 |
