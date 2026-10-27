# Consistency check: SI horizon tables vs. response-letter Tables 5–8

Date: 2026-10-27. Overleaf state after the co-author commits of 2026-10-27.

## What was compared

| Response letter | Supplementary Information (SI, Section N "Forecast horizon") | Source in the repo |
|---|---|---|
| Table 5 (horizon dependence, 4 tasks) | Supplementary Table S30 (pooled horizon effects, `tab:si_hor_pooled`) and SI text | `horizon_study/tables_no_v4pro/pooled.md`, `anchoring_null.md`, `mcc_by_horizon.md` |
| Table 5 (interpretation) | Supplementary Table S31 (within-model horizon slopes, `tab:si_hor_trends`) | `horizon_study/tables_no_v4pro/trends.md` |
| Table 6 (pre vs. post cutoff) | Supplementary Table S32 (`tab:si_hor_prepost`) | `results_extension_run2/tables/09_prepost_full_corpus_cmpre.md` |
| Tables 7 and 8 (retrieval × horizon) | Supplementary Table S33 (`tab:si_hor_retrieval`) and SI text | `horizon_study/tables_no_v4pro/ws_vs_base.md`, `split/ws_vs_base.md` |

Table numbers S30–S33 are from a full build of `sean.tex` today. If your PDF numbers them differently, the labels in the second column identify the tables.

S30 and S31 agree with their source files: every checked value in them is present in `pooled.md` and `trends.md`.

## Inconsistencies found (all in the response letter; fixed in red)

| # | Where | Letter said | SI and source say | Fix |
|---|---|---|---|---|
| 1 | Letter Table 7, FRQ row | "All four model-specific 95% CIs include zero"; no pooled value | SI: pooled FRQ interaction −0.083 points/year [−0.196, +0.031], p = 0.15; **five** models (GPT-4o, LLaMA 3.3, DeepSeek R1, Claude S4.5, GPT-5.4), all CIs include zero | Row now reads "−0.083 points/year; p = 0.15; all five model-specific 95% CIs include zero" |
| 2 | Letter Table 8 (FRQ slope change under retrieval) | 4 models; **LLaMA 3.3 missing** | SI Table S33, panel B and `ws_vs_base.md`: LLaMA 3.3 −0.058 [−0.216, +0.098] | LLaMA 3.3 row added |
| 3 | Letter text before Table 7 (Response on horizon, "Effect of additional pre-cutoff knowledge") | "all four models with sufficient paired observations" | five models | Text now gives the pooled value and "all five models" |
| 4 | Letter Table 7 caption | "Brackets indicate 95% confidence intervals" | the table has no brackets | Sentence removed |

## Checked and consistent (no change)

- Table 5, MCQ original: −0.256 log-odds/year [−0.406, −0.106], Holm p = 0.013 = S30.
- Table 5, MCQ merged: −0.170 [−0.286, −0.053], Holm p = 0.057 = S30.
- Table 5, FRQ: +0.014 points/year [−0.012, +0.039], Holm p = 1 = S30 (merged corpus).
- Table 5, Binary: no significant short- vs. long-horizon MCC difference = SI text (paired CIs include zero for every model with both ranges).
- Table 5, Date: the anchoring null reproduces 107–147% of the absolute-error slope = SI anchoring-null table and the main text (six models, original corpus).
- Table 6, MCQ and FRQ pre/post/ratio values for the seven models = S32, all 42 cells. S32 also gives Binary and Date, which the letter does not show.
- Table 7, Binary +0.031 (p = 0.82), MCQ +0.213 (p = 0.21), Date absolute error +7.9 months/year (p = 3.7×10⁻⁶) = S33 panel A.
- Table 8, the four values that were already in the letter = S33 panel B.

## Style differences (not changed)

- The letter uses long model names ("GPT-OSS-20B", "DeepSeek-R1", "Claude Sonnet 5", "Claude Opus 4.8"); the SI uses the short names defined in Methods ("GPT-OSS", "DeepSeek R1", "Claude S5", "Claude O4.8").
- Table 5's interpretation of the original-corpus MCQ result ("negative horizon dependence across models with sufficient coverage") is right in direction: all six models with range have negative slopes. In S31, the 95% CI excludes zero for only three of them: GPT-4o, LLaMA 3.3 and GPT-5.4. You could soften it to "negative in direction for all six models with sufficient coverage".
