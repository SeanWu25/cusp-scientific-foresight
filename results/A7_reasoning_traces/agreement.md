# A7 inter-coder agreement

Two independent coders, blind to ground truth, correctness, model identity and condition: **gpt54mini_low** and **haiku45**. Cohen's kappa on the binary verdicts (ordinal for HEDGING), with a 2,000-draw bootstrap 95% CI over traces.

**Pre-registered reliability rule:** a code enters the inferential analyses (B, C, E, F) only if kappa >= 0.6 AND at least 30 traces were marked positive by either coder. Kappa is unstable at very low prevalence, so the second condition prevents a near-empty code from passing on a handful of agreements. Codes that fail are reported as prevalence only and are excluded from every model of outcome.

| code | kappa [95% CI] | raw agreement | positives (either coder) | rate, coder A | rate, coder B | verbatim spans | enters inference |
|---|---|---|---|---|---|---|---|
| RATE_OF_PROGRESS | 0.80 [0.78, 0.82] | 0.96 | 1,565 | 12% | 11% | 99% | yes |
| ABSENCE_AS_EVIDENCE | 0.76 [0.73, 0.78] | 0.97 | 976 | 8% | 6% | 98% | yes |
| HEDGING | 0.71 [0.70, 0.72] | 0.83 (within 1: 0.98) | 11,698 | -- | -- | 98% | yes |
| PROVENANCE_INFERRED | 0.69 [0.68, 0.71] | 0.92 | 2,446 | 18% | 15% | 98% | yes |
| ROUND_ANCHOR | 0.69 [0.67, 0.71] | 0.95 | 1,453 | 11% | 8% | 97% | yes |
| FIELD_MOMENTUM | 0.65 [0.63, 0.66] | 0.87 | 3,654 | 30% | 19% | 99% | yes |
| KNOWLEDGE_GAP_ADMITTED | 0.65 [0.56, 0.72] | 0.99 | 123 | 1% | 1% | 99% | yes |
| EVIDENCE_CITED | 0.61 [0.59, 0.62] | 0.85 | 3,982 | 24% | 28% | 98% | yes |
| SPECIFICITY_AS_IMPLAUSIBLE | 0.59 [0.57, 0.62] | 0.92 | 1,744 | 11% | 10% | 98% | no |
| DIFFICULTY_APPEAL | 0.58 [0.56, 0.59] | 0.84 | 3,875 | 28% | 22% | 96% | no |
| HYPOTHESIS_COMPARISON | 0.53 [0.51, 0.56] | 0.92 | 1,705 | 11% | 9% | 97% | no |
| BASE_RATE | 0.48 [0.38, 0.56] | 0.99 | 133 | 1% | 1% | 98% | no |
| CONSTRAINT_CHECKED | 0.46 [0.44, 0.47] | 0.77 | 4,838 | 34% | 25% | 92% | no |
| CONJUNCTION_BURDEN | 0.43 [0.41, 0.45] | 0.83 | 3,111 | 17% | 19% | 92% | no |
| CUTOFF_REFERENCED | 0.34 [0.27, 0.41] | 0.98 | 257 | 1% | 1% | 99% | no |
| RESTATEMENT_ONLY | 0.16 [0.11, 0.22] | 0.98 | 254 | 1% | 2% | 95% | no |

**8 of 16 codes enter the inferential analyses:** RATE_OF_PROGRESS, ABSENCE_AS_EVIDENCE, HEDGING, PROVENANCE_INFERRED, ROUND_ANCHOR, FIELD_MOMENTUM, KNOWLEDGE_GAP_ADMITTED, EVIDENCE_CITED.

Excluded: SPECIFICITY_AS_IMPLAUSIBLE, DIFFICULTY_APPEAL, HYPOTHESIS_COMPARISON, BASE_RATE, CONSTRAINT_CHECKED, CONJUNCTION_BURDEN, CUTOFF_REFERENCED, RESTATEMENT_ONLY.

"Verbatim spans" is the share of positive verdicts whose quoted justification is a contiguous quote of the passage; a span joined by an ellipsis counts if its longest fragment is verbatim.

