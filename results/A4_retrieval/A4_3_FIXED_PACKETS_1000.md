# Fixed evidence packets on 1,000 events: results

CUSP revision, Reviewer 2 comment C4.3 (knowledge-access experiment, Figure 3a, response Tables 20–22). Computed 2026-10-20.

## Summary

- **Both designs give the same picture.** Across 50 model × task × partition cells, the knowledge gap correlates at r = 0.99 between the original design and the fixed-evidence design, and the forecasting gap at r = 0.91.
- **After the cutoff, forecasting gaps dominate.** With fixed evidence, the forecasting gap is larger than the knowledge gap in all 24 post-cutoff model × task-family comparisons.
- **Before the cutoff, knowledge gaps dominate.** The knowledge gap is larger than the forecasting gap in all 16 pre-cutoff comparisons.
- **The two late-cutoff models are now covered.** Claude Sonnet 5 and GPT-5.6 Sol had too few post-cutoff events in the first 500 (31 and 4). With 1,000 events they have 143–399 and 131–403 matched post-cutoff events per task, and they show the same pattern as the other models.

## Design

- **Original design.** Each evaluated model writes its own search query. WS+Cutoff retrieves only documents dated before the model's knowledge cutoff; WS has no date limit. GPT-4o and GPT-5.4 used the OpenAI web-search tool in WS; all other runs used one You.com query per event.
- **Fixed-evidence design.** Claude Opus 4.8 wrote one query per event (GPT-5.4-mini for events Opus declined). Each query was sent once per date limit, so every model received the same evidence packet for a given limit.
- **Gaps.** Knowledge gap = WS+Cutoff − Base. Forecasting gap = WS − WS+Cutoff. Post-cutoff events have a publication month after the model's cutoff month.
- **Statistics.** Paired differences on events present in all conditions of both designs ("matched events"), with normal 95% confidence intervals. Cells with fewer than 20 events are not reported. Binary, MCQ and Date use a 0–1 scale; FRQ uses rubric points on 0–10.

## Events

The 1,000 events are the pinned 500-event subset (published Jan 2024 – Mar 2026) and 500 added events published Mar–Aug 2026 (seed 20261018, stratified by month). Every added event is a post-cutoff event for all six models.

| Model | Knowledge cutoff | Matched pre-cutoff events (max over tasks) | Matched post-cutoff events (max over tasks) |
|---|---|---|---|
| GPT-4o | 2023-10 | 0 | 805 |
| LLaMA 3.3 70B | 2023-12 | 0 | 809 |
| Claude S4.5 | 2025-01 | 152 | 539 |
| GPT-5.4 | 2025-08 | 330 | 500 |
| Claude Sonnet 5 | 2026-01 | 381 | 399 |
| GPT-5.6 Sol | 2026-02 | 423 | 403 |

## Table 20. Pre-cutoff gaps, original vs fixed evidence

| Model | Task | N | Knowledge gap, original | Knowledge gap, fixed | Forecasting gap, original | Forecasting gap, fixed |
|---|---|---|---|---|---|---|
| Claude S4.5 | Binary | 129 | +0.380 [+0.267, +0.492] | +0.380 [+0.278, +0.481] | +0.039 [-0.034, +0.112] | +0.078 [+0.014, +0.141] |
|  | Binary (perturbed) | 137 | -0.007 [-0.104, +0.089] | +0.022 [-0.079, +0.122] | +0.015 [-0.056, +0.085] | -0.007 [-0.066, +0.052] |
|  | MCQ | 152 | +0.039 [-0.044, +0.123] | +0.020 [-0.067, +0.106] | -0.013 [-0.084, +0.058] | -0.013 [-0.082, +0.055] |
|  | FRQ (0–10) | 142 | +0.683 [+0.485, +0.881] | +0.780 [+0.579, +0.981] | +0.130 [-0.021, +0.282] | +0.058 [-0.068, +0.185] |
|  | Date | 129 | +0.235 [+0.145, +0.325] | +0.287 [+0.201, +0.372] | +0.083 [-0.000, +0.167] | -0.072 [-0.155, +0.010] |
| GPT-5.4 | Binary | 237 | +0.270 [+0.201, +0.339] | +0.270 [+0.203, +0.337] | +0.051 [+0.011, +0.091] | +0.013 [-0.021, +0.047] |
|  | Binary (perturbed) | 294 | +0.024 [-0.050, +0.098] | +0.058 [-0.016, +0.132] | -0.061 [-0.126, +0.003] | +0.020 [-0.027, +0.068] |
|  | MCQ | 330 | +0.088 [+0.047, +0.128] | +0.094 [+0.054, +0.134] | +0.030 [+0.004, +0.057] | +0.000 [-0.022, +0.022] |
|  | FRQ (0–10) | 317 | +1.003 [+0.869, +1.137] | +1.096 [+0.967, +1.225] | -0.294 [-0.432, -0.157] | -0.019 [-0.105, +0.068] |
|  | Date | 237 | +0.440 [+0.383, +0.498] | +0.454 [+0.397, +0.510] | +0.024 [-0.033, +0.080] | +0.022 [-0.012, +0.057] |
| Claude Sonnet 5 | Binary | 266 | +0.267 [+0.195, +0.339] | +0.286 [+0.214, +0.357] | +0.004 [-0.046, +0.053] | +0.026 [-0.013, +0.066] |
|  | Binary (perturbed) | 349 | +0.011 [-0.050, +0.073] | -0.003 [-0.061, +0.055] | +0.032 [-0.003, +0.066] | +0.011 [-0.021, +0.044] |
|  | MCQ | 371 | +0.062 [+0.030, +0.094] | +0.057 [+0.022, +0.091] | +0.011 [-0.006, +0.027] | +0.016 [-0.000, +0.033] |
|  | FRQ (0–10) | 381 | +1.394 [+1.262, +1.526] | +1.430 [+1.303, +1.558] | -0.044 [-0.141, +0.053] | +0.029 [-0.060, +0.117] |
|  | Date | 268 | +0.325 [+0.274, +0.376] | +0.326 [+0.275, +0.376] | +0.011 [-0.023, +0.045] | +0.020 [-0.008, +0.048] |
| GPT-5.6 Sol | Binary | 294 | +0.034 [-0.013, +0.081] | +0.017 [-0.031, +0.065] | -0.007 [-0.041, +0.027] | +0.034 [+0.008, +0.060] |
|  | Binary (perturbed) | 388 | +0.168 [+0.106, +0.229] | +0.144 [+0.087, +0.202] | +0.010 [-0.030, +0.050] | +0.003 [-0.028, +0.033] |
|  | MCQ | 423 | +0.059 [+0.026, +0.092] | +0.073 [+0.041, +0.106] | +0.014 [-0.005, +0.034] | +0.014 [+0.001, +0.027] |
|  | FRQ (0–10) | 407 | +1.094 [+0.978, +1.210] | +1.080 [+0.963, +1.197] | +0.079 [-0.018, +0.175] | +0.065 [-0.009, +0.139] |
|  | Date | 295 | +0.417 [+0.366, +0.468] | +0.405 [+0.353, +0.457] | +0.016 [-0.016, +0.049] | +0.024 [+0.000, +0.048] |

GPT-4o and LLaMA 3.3 70B have no pre-cutoff events.

## Table 21. Post-cutoff gaps, original vs fixed evidence

| Model | Task | N | Knowledge gap, original | Knowledge gap, fixed | Forecasting gap, original | Forecasting gap, fixed |
|---|---|---|---|---|---|---|
| GPT-4o | Binary | 421 | +0.290 [+0.237, +0.343] | +0.292 [+0.239, +0.346] | +0.361 [+0.306, +0.416] | +0.342 [+0.293, +0.392] |
|  | Binary (perturbed) | 789 | -0.147 [-0.183, -0.111] | -0.147 [-0.186, -0.108] | +0.151 [+0.110, +0.192] | -0.127 [-0.164, -0.090] |
|  | MCQ | 805 | +0.045 [+0.010, +0.080] | +0.097 [+0.063, +0.131] | +0.340 [+0.303, +0.378] | +0.243 [+0.209, +0.278] |
|  | FRQ (0–10) | 799 | +0.297 [+0.223, +0.371] | +0.485 [+0.408, +0.562] | +0.642 [+0.522, +0.762] | +0.697 [+0.608, +0.786] |
|  | Date | 421 | +0.093 [+0.056, +0.129] | +0.078 [+0.042, +0.114] | +0.273 [+0.225, +0.322] | +0.104 [+0.064, +0.145] |
| LLaMA 3.3 70B | Binary | 424 | -0.064 [-0.095, -0.033] | -0.050 [-0.080, -0.019] | +0.052 [+0.019, +0.085] | +0.073 [+0.043, +0.103] |
|  | Binary (perturbed) | 793 | +0.116 [+0.087, +0.145] | +0.120 [+0.091, +0.148] | -0.006 [-0.037, +0.025] | +0.008 [-0.024, +0.039] |
|  | MCQ | 809 | +0.042 [+0.008, +0.077] | +0.073 [+0.038, +0.108] | +0.284 [+0.249, +0.319] | +0.277 [+0.244, +0.310] |
|  | FRQ (0–10) | 805 | +0.409 [+0.344, +0.474] | +0.507 [+0.444, +0.571] | +0.648 [+0.568, +0.728] | +0.733 [+0.656, +0.809] |
|  | Date | 424 | -0.042 [-0.068, -0.016] | -0.049 [-0.078, -0.019] | +0.084 [+0.049, +0.118] | +0.110 [+0.074, +0.145] |
| Claude S4.5 | Binary | 247 | +0.097 [+0.025, +0.169] | +0.085 [+0.014, +0.156] | +0.449 [+0.384, +0.515] | +0.462 [+0.398, +0.525] |
|  | Binary (perturbed) | 509 | +0.020 [-0.024, +0.063] | +0.010 [-0.034, +0.053] | -0.151 [-0.195, -0.108] | -0.128 [-0.172, -0.083] |
|  | MCQ | 475 | -0.029 [-0.074, +0.015] | +0.004 [-0.042, +0.050] | +0.158 [+0.114, +0.202] | +0.097 [+0.052, +0.142] |
|  | FRQ (0–10) | 539 | +0.159 [+0.077, +0.240] | +0.229 [+0.155, +0.303] | +0.333 [+0.251, +0.415] | +0.464 [+0.385, +0.542] |
|  | Date | 244 | -0.019 [-0.061, +0.023] | -0.039 [-0.083, +0.006] | +0.111 [+0.054, +0.167] | +0.182 [+0.125, +0.240] |
| GPT-5.4 | Binary | 188 | +0.128 [+0.061, +0.195] | +0.128 [+0.055, +0.201] | +0.191 [+0.133, +0.250] | +0.149 [+0.094, +0.204] |
|  | Binary (perturbed) | 500 | -0.082 [-0.127, -0.037] | -0.068 [-0.114, -0.022] | -0.020 [-0.067, +0.027] | +0.000 [-0.043, +0.043] |
|  | MCQ | 483 | -0.056 [-0.096, -0.016] | -0.048 [-0.087, -0.008] | +0.182 [+0.146, +0.219] | +0.130 [+0.096, +0.165] |
|  | FRQ (0–10) | 484 | +0.437 [+0.350, +0.524] | +0.398 [+0.312, +0.483] | +0.163 [+0.064, +0.263] | +0.668 [+0.571, +0.764] |
|  | Date | 188 | +0.086 [+0.045, +0.128] | +0.093 [+0.051, +0.135] | +0.538 [+0.480, +0.596] | +0.389 [+0.335, +0.443] |
| Claude Sonnet 5 | Binary | 143 | +0.140 [+0.045, +0.234] | +0.112 [+0.011, +0.213] | +0.406 [+0.320, +0.491] | +0.434 [+0.350, +0.517] |
|  | Binary (perturbed) | 399 | -0.075 [-0.119, -0.032] | -0.090 [-0.134, -0.047] | -0.108 [-0.152, -0.063] | -0.058 [-0.102, -0.014] |
|  | MCQ | 367 | -0.027 [-0.059, +0.005] | -0.011 [-0.045, +0.023] | +0.071 [+0.035, +0.107] | +0.074 [+0.041, +0.106] |
|  | FRQ (0–10) | 396 | +0.332 [+0.226, +0.438] | +0.422 [+0.322, +0.522] | +0.828 [+0.706, +0.950] | +0.838 [+0.717, +0.959] |
|  | Date | 143 | +0.094 [+0.050, +0.137] | +0.091 [+0.045, +0.137] | +0.338 [+0.279, +0.396] | +0.379 [+0.322, +0.437] |
| GPT-5.6 Sol | Binary | 131 | +0.061 [+0.006, +0.116] | +0.038 [-0.020, +0.096] | +0.153 [+0.084, +0.221] | +0.176 [+0.107, +0.244] |
|  | Binary (perturbed) | 403 | +0.007 [-0.043, +0.058] | -0.037 [-0.089, +0.015] | +0.089 [+0.035, +0.144] | +0.087 [+0.032, +0.142] |
|  | MCQ | 378 | +0.011 [-0.025, +0.046] | -0.005 [-0.042, +0.031] | +0.085 [+0.051, +0.118] | +0.085 [+0.050, +0.119] |
|  | FRQ (0–10) | 380 | +0.365 [+0.264, +0.466] | +0.281 [+0.179, +0.383] | +0.742 [+0.620, +0.864] | +0.711 [+0.589, +0.832] |
|  | Date | 131 | +0.054 [+0.017, +0.091] | +0.091 [+0.049, +0.132] | +0.396 [+0.333, +0.458] | +0.381 [+0.322, +0.440] |

## Table 22. Agreement between the original and fixed-evidence designs

One point per model × task × partition cell with at least 20 matched events. FRQ is divided by 10 so all tasks share a 0–1 scale. r = Pearson correlation; MAD = mean absolute difference. Brackets: 95% CIs from 10,000 cell-level bootstrap resamples.

| Quantity | r (pre + post) | MAD (pre + post) | r (post only) | MAD (post only) |
|---|---|---|---|---|
| WS+Cutoff performance | 1.00 [0.99, 1.00] | 0.015 [0.012, 0.019] | 0.99 [0.99, 1.00] | 0.016 [0.011, 0.020] |
| Unrestricted WS performance | 0.96 [0.91, 0.99] | 0.037 [0.025, 0.052] | 0.95 [0.87, 0.99] | 0.043 [0.025, 0.065] |
| **Knowledge gap** | 0.99 [0.98, 0.99] | 0.015 [0.012, 0.019] | 0.97 [0.92, 0.99] | 0.016 [0.011, 0.020] |
| **Forecasting gap** | 0.91 [0.79, 0.97] | 0.037 [0.024, 0.053] | 0.90 [0.77, 0.98] | 0.044 [0.025, 0.066] |
| Forecasting gap, without GPT-4o | 0.95 [0.89, 0.98] | 0.028 [0.019, 0.038] | 0.97 [0.95, 0.99] | 0.030 [0.019, 0.043] |

Cells: 50 (pre + post), 30 (post only); without GPT-4o: 45 and 25.

## FRQ only (rubric points, 0–10)

| Quantity | r (pre + post) | MAD (pre + post) | Cells | r (post only) | MAD (post only) | Cells |
|---|---|---|---|---|---|---|
| WS+Cutoff score | 1.00 [0.99, 1.00] | 0.081 [0.055, 0.111] | 10 | 1.00 [0.99, 1.00] | 0.095 [0.063, 0.136] | 6 |
| WS score | 0.97 [0.91, 1.00] | 0.184 [0.105, 0.271] | 10 | 0.97 [0.88, 1.00] | 0.218 [0.136, 0.326] | 6 |
| Knowledge gap | 0.98 [0.90, 1.00] | 0.081 [0.055, 0.111] | 10 | 0.56 [-0.84, 0.96] | 0.095 [0.063, 0.136] | 6 |
| Forecasting gap | 0.89 [0.67, 0.99] | 0.125 [0.051, 0.225] | 10 | 0.68 [0.20, 1.00] | 0.136 [0.038, 0.290] | 6 |

The post-only FRQ rows have six cells, so their intervals are wide.

## Figure 3a values (fixed evidence)

Knowledge gap / forecasting gap per task family. Feasibility Assessment is the mean of the original and perturbed binary gaps; Solution Design is FRQ ÷ 10. These are the Fixed columns of Tables 20 and 21.

**Post-cutoff events**

| Model | Feasibility Assessment | Mechanistic Forecasting | Temporal Prediction | Solution Design |
|---|---|---|---|---|
| GPT-4o | +0.073 / +0.108 | +0.097 / +0.243 | +0.078 / +0.104 | +0.048 / +0.070 |
| LLaMA 3.3 70B | +0.035 / +0.040 | +0.073 / +0.277 | -0.049 / +0.110 | +0.051 / +0.073 |
| Claude S4.5 | +0.047 / +0.167 | +0.004 / +0.097 | -0.039 / +0.182 | +0.023 / +0.046 |
| GPT-5.4 | +0.030 / +0.074 | -0.048 / +0.130 | +0.093 / +0.389 | +0.040 / +0.067 |
| Claude Sonnet 5 | +0.011 / +0.188 | -0.011 / +0.074 | +0.091 / +0.379 | +0.042 / +0.084 |
| GPT-5.6 Sol | +0.000 / +0.131 | -0.005 / +0.085 | +0.091 / +0.381 | +0.028 / +0.071 |

**Pre-cutoff events**

| Model | Feasibility Assessment | Mechanistic Forecasting | Temporal Prediction | Solution Design |
|---|---|---|---|---|
| Claude S4.5 | +0.201 / +0.035 | +0.020 / -0.013 | +0.287 / -0.072 | +0.078 / +0.006 |
| GPT-5.4 | +0.164 / +0.017 | +0.094 / +0.000 | +0.454 / +0.022 | +0.110 / -0.002 |
| Claude Sonnet 5 | +0.141 / +0.019 | +0.057 / +0.016 | +0.326 / +0.020 | +0.143 / +0.003 |
| GPT-5.6 Sol | +0.081 / +0.018 | +0.073 / +0.014 | +0.405 / +0.024 | +0.108 / +0.007 |

## Where the two designs differ

- **Knowledge gap.** The fixed-evidence value lies inside the original value's 95% CI in 47 of 50 cells. The exceptions are GPT-4o MCQ (+0.045 → +0.097); GPT-4o FRQ (0-10) (+0.297 → +0.485); LLaMA 3.3 70B FRQ (0-10) (+0.409 → +0.507). In each, fixed evidence gives the larger knowledge gap.
- **Forecasting gap.** Inside the CI in 34 of 50 cells. GPT-4o changes most, because its original unrestricted run used the OpenAI web-search tool rather than a single You.com query; without GPT-4o the forecasting-gap correlation rises to 0.95.
- **Single answers.** The same WS+Cutoff answer is given under both designs for 84.0% of Binary items and 86.3% of MCQ items (Cohen's κ 0.604 and 0.639).

## Notes and caveats

- **Added events, original design.** Each model was re-run on the 500 added events with the harness, prompts and decoding settings of its original retrieval run. The retired Azure OpenAI deployments of GPT-4o, GPT-5.4 and LLaMA 3.3 were replaced by the Azure AI Foundry deployments of the same models.
- **Retrieval dates.** Fixed packets were retrieved on 2026-09-21 (first 500) and 2026-10-18 (added 500); the added original-design runs were made on 2026-10-19/20.
- **Claude Sonnet 4.5 query failures.** It returned no search query for 84–85 of the added events (37 in the first 500). As in its original runs, those events keep the answer given without retrieved evidence.
- **Query writer.** Claude Opus 4.8 wrote the fixed queries; it is evaluated elsewhere in the paper but not in this experiment.
- **DeepSeek R1** is not included: its deployment was retired before the fixed-evidence runs.

Source: `results/A4_retrieval/` (scripts `a43_pre_post_correlation.py` with `A43_EVENTS=1000`, `a43_report_1000.py`).
