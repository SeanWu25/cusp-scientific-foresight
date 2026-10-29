# Analysis C — the delayed-date mechanism (priority)

CUSP's temporal task asks for the month a development was or will first be achieved. The paper reports systematic lateness. The hypothesis under test is that traces which reason from the absence of known work, anchor on a round future year, invoke the knowledge cutoff, or appeal to difficulty are the ones that run late.

Outcome: **signed error in months**, predicted minus ground truth. Positive is late. Model: Gaussian random-intercept fit with an intercept for event and for model, so item difficulty and model-level lateness are absorbed; the coefficient is the extra lateness in months attributable to the code. p-values Holm-adjusted across the codes tested. Base condition only.

Date traces with a signed error and a consensus label: **3,172**. Mean signed error +13.6 months, median +9.

| code | tested as | n with code | mean signed error, with | without | difference [95% CI] | beta months [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|---|
| ROUND_ANCHOR | hypothesised | 761 | +28.5 | +8.9 | +19.6 [+16.2, +23.4] | +19.6 [+16.6, +22.7] | <0.001 |
| PROVENANCE_INFERRED | contrast | 504 | -17.7 | +19.5 | -37.2 [-40.6, -34.5] | -37.2 [-40.6, -33.8] | <0.001 |
| RATE_OF_PROGRESS | contrast | 941 | +23.4 | +9.5 | +14.0 [+11.5, +16.5] | +14.0 [+11.1, +16.8] | <0.001 |
| FIELD_MOMENTUM | contrast | 1,091 | +17.0 | +11.8 | +5.2 [+2.6, +8.0] | +5.2 [+2.4, +8.0] | <0.001 |
| EVIDENCE_CITED | contrast | 291 | +4.1 | +14.6 | -10.5 [-15.0, -6.1] | -10.5 [-15.1, -5.9] | <0.001 |

**Codes the hypothesis named that could not be tested here:** ABSENCE_AS_EVIDENCE (present in only 15 date traces (0.5%)); CUTOFF_REFERENCED (failed the inter-coder reliability rule); DIFFICULTY_APPEAL (failed the inter-coder reliability rule). These are reported as prevalence only. The hypothesis is therefore tested on the subset of its named mechanisms that the data can support, and that restriction is part of the result.


**Verdict on the hypothesis.** Of the 1 hypothesised codes that could be tested, 1 are associated with significantly LATER predictions (ROUND_ANCHOR +19.6 months), 0 with significantly EARLIER, and 0 show no significant association.


## Distribution of the signed error conditional on each code

| code | n | p10 | p25 | median | p75 | p90 | share late (> 0) | share more than a year late |
|---|---|---|---|---|---|---|---|---|
| ROUND_ANCHOR (present) | 761 | -7 | +3 | +17 | +48 | +80 | 79% | 59% |
| DIFFICULTY_APPEAL (present) | 799 | +1 | +11 | +28 | +51 | +85 | 90% | 72% |
| PROVENANCE_INFERRED (present) | 504 | -43 | -24 | -11 | -1 | +0 | 10% | 1% |
| RATE_OF_PROGRESS (present) | 941 | +0 | +8 | +18 | +33 | +52 | 89% | 64% |
| FIELD_MOMENTUM (present) | 1,091 | -6 | +2 | +12 | +25 | +46 | 78% | 47% |
| EVIDENCE_CITED (present) | 291 | -25 | -7 | +2 | +16 | +34 | 56% | 30% |
| *all date traces* | 3,172 | -17 | -3 | +9 | +26 | +50 | 65% | 44% |
