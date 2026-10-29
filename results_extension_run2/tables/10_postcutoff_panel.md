# Post-cutoff performance on the entire dataset — one row per model

Original + extension pooled; per model, only events published on/after its cutoff month (rule `main`). Binary: raw merged accuracy is shown for reference but is confounded by class balance × response bias (RUN2_RESULTS.md §3); **balanced accuracy** and MCC are the bias-corrected metrics. FRQ is the published-rubric mean (0–10). 95% CIs: Wilson for proportions (balanced accuracy = mean of the two Wilson halves), normal approximation for means. Refusals excluded.

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
