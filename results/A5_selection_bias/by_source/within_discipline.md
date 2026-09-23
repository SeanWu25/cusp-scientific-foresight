# A5.1b — venue effect with discipline held fixed

CUSP's source strata are nested inside discipline (the arXiv feeds are 99–100% AI, the journals 0–1.3%), so the raw source effect in `source_tables.md` is largely a discipline effect. This table asks the narrower question: **within one discipline, does the venue matter?**

Venues are included when they carry ≥100 events in that discipline. Cells below n=20 are suppressed. p is a 5000-draw permutation test across venues, Holm-corrected within each discipline.

| discipline | venues | events | tests | Holm-significant (p<0.05) |
|---|---|---|---|---|
| Biology | Nature, Science, Cell | 1,438 | 110 | **2** |
| Artificial Intelligence | HF Daily Papers (arXiv), Top-10 AI Paper of Week (arXiv) | 1,181 | 95 | **1** |
| Medicine | Nature, Cell, Science | 878 | 105 | **0** |
| Materials Science | Nature, Science | 460 | 110 | **1** |
| Physics | Nature, Science | 444 | 98 | **0** |
| Neuroscience | Nature, Science | 379 | 93 | **0** |
| Chemistry | Nature, Science | 226 | 94 | **0** |

## Significant venue effects (discipline fixed)

| model | discipline | partition | task | range | lowest | highest | p (Holm) |
|---|---|---|---|---|---|---|---|
| DeepSeek-R1 | Artificial Intelligence | overall | Date (score) | +0.133 | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | 0.0190 |
| DeepSeek-R1 | Materials Science | pre | Binary (bal. acc) | +0.269 | Nature | Science | 0.0220 |
| Claude Opus 4.8 | Biology | pre | Date (score) | +0.124 | Science | Nature | 0.0220 |
| Claude Opus 4.8 | Biology | overall | Date (score) | +0.111 | Science | Nature | 0.0436 |
