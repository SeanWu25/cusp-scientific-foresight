# Analysis A — code prevalence

Consensus labels: a code counts as present only when **both coders agree** (gpt54mini_low and haiku45). Cells are the share of traces carrying the code, with a 1,000-draw event-cluster bootstrap 95% CI. Codes that failed the reliability rule are shown here for completeness but are excluded from every inferential analysis (see `agreement.md`).

## By task, base condition

| code | reliable | binary | binary_perturbed | mcq | date | frq |
|---|---|---|---|---|---|---|
| BASE_RATE | no | 0.7% | 1.4% | 0.0% | 0.1% | 0.0% |
| HYPOTHESIS_COMPARISON | no | 0.2% | 0.4% | 35.2% | 0.1% | 0.1% |
| EVIDENCE_CITED | yes | 15.7% | 16.5% | 11.7% | 9.2% | 1.2% |
| KNOWLEDGE_GAP_ADMITTED | yes | 1.4% | 1.7% | 0.0% | 0.0% | 0.0% |
| ABSENCE_AS_EVIDENCE | yes | 14.0% | 15.4% | 0.0% | 0.5% | 0.0% |
| CONSTRAINT_CHECKED | no | 33.1% | 38.8% | 9.3% | 5.6% | 12.0% |
| RATE_OF_PROGRESS | yes | 1.6% | 1.4% | 0.4% | 29.6% | 0.5% |
| ROUND_ANCHOR | yes | 0.3% | 0.4% | 0.2% | 23.9% | 0.0% |
| CUTOFF_REFERENCED | no | 1.5% | 1.6% | 0.0% | 0.0% | 0.1% |
| DIFFICULTY_APPEAL | no | 33.1% | 30.2% | 1.3% | 25.1% | 1.5% |
| SPECIFICITY_AS_IMPLAUSIBLE | no | 20.3% | 16.8% | 0.2% | 5.4% | 0.0% |
| PROVENANCE_INFERRED | yes | 8.7% | 2.6% | 7.5% | 15.9% | 0.0% |
| CONJUNCTION_BURDEN | no | 18.2% | 12.9% | 1.8% | 11.7% | 7.4% |
| FIELD_MOMENTUM | yes | 25.5% | 27.1% | 1.1% | 34.3% | 0.0% |
| RESTATEMENT_ONLY | no | 0.1% | 0.1% | 0.7% | 0.2% | 0.1% |

## By model, base condition, all tasks pooled

| code | Claude Opus 4.8 | Claude S4.5 | Claude Sonnet 5 | DeepSeek-R1 | DeepSeek-V4-Pro | GPT-4o | GPT-5.4 | GPT-5.6 Sol | GPT-OSS 20B | LLaMA 3.3 70B |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE_RATE | 0.5% | 0.3% | 0.9% | 0.1% | 0.2% | 0.1% | 0.6% | 0.2% | 0.6% | 0.0% |
| HYPOTHESIS_COMPARISON | 1.0% | 7.0% | 1.8% | 13.6% | 4.4% | 4.7% | 13.2% | 7.5% | 3.2% | 1.0% |
| EVIDENCE_CITED | 13.3% | 18.1% | 20.3% | 12.4% | 8.8% | 0.9% | 4.4% | 9.7% | 10.1% | 0.3% |
| KNOWLEDGE_GAP_ADMITTED | 1.0% | 2.0% | 1.3% | 0.0% | 0.0% | 0.0% | 0.4% | 0.1% | 0.0% | 0.0% |
| ABSENCE_AS_EVIDENCE | 3.0% | 4.3% | 6.1% | 2.7% | 8.9% | 0.7% | 0.9% | 3.8% | 19.6% | 0.0% |
| CONSTRAINT_CHECKED | 9.3% | 24.3% | 6.9% | 26.2% | 24.1% | 9.6% | 27.5% | 13.1% | 25.6% | 1.5% |
| RATE_OF_PROGRESS | 1.1% | 24.0% | 2.1% | 21.9% | 7.0% | 21.9% | 2.2% | 5.7% | 16.3% | 0.5% |
| ROUND_ANCHOR | 2.0% | 1.4% | 2.0% | 9.0% | 10.5% | 3.4% | 23.2% | 4.0% | 21.2% | 0.0% |
| CUTOFF_REFERENCED | 0.0% | 4.1% | 0.3% | 0.2% | 0.0% | 0.0% | 0.1% | 0.1% | 0.0% | 0.0% |
| DIFFICULTY_APPEAL | 6.8% | 26.9% | 5.4% | 30.1% | 37.9% | 36.6% | 20.2% | 7.4% | 7.6% | 21.8% |
| SPECIFICITY_AS_IMPLAUSIBLE | 16.3% | 15.5% | 15.8% | 1.3% | 13.5% | 1.2% | 4.7% | 2.1% | 3.5% | 2.7% |
| PROVENANCE_INFERRED | 21.6% | 6.2% | 22.4% | 0.1% | 4.6% | 0.0% | 8.7% | 11.8% | 0.4% | 0.0% |
| CONJUNCTION_BURDEN | 6.5% | 16.9% | 7.1% | 9.7% | 16.9% | 5.5% | 20.1% | 9.3% | 6.3% | 3.2% |
| FIELD_MOMENTUM | 8.5% | 15.6% | 9.5% | 22.6% | 19.6% | 49.3% | 25.7% | 6.6% | 11.9% | 56.0% |
| RESTATEMENT_ONLY | 0.6% | 0.0% | 0.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.6% | 0.2% | 1.0% |

## Pre- vs post-cutoff, base condition, all tasks pooled

| code | pre-cutoff | post-cutoff | difference [95% CI] | p |
|---|---|---|---|---|
| BASE_RATE | 0.5% (n=4,523) | 0.3% (n=5,226) | -0.2 pts [-0.4, +0.1] | 1.000 |
| HYPOTHESIS_COMPARISON | 6.1% (n=4,523) | 6.0% (n=5,226) | -0.1 pts [-1.0, +0.8] | 1.000 |
| EVIDENCE_CITED | 14.3% (n=4,523) | 7.3% (n=5,226) | -7.0 pts [-8.4, -5.6] | 0.030 |
| KNOWLEDGE_GAP_ADMITTED | 0.9% (n=4,523) | 0.2% (n=5,226) | -0.7 pts [-1.0, -0.3] | 0.030 |
| ABSENCE_AS_EVIDENCE | 6.8% (n=4,523) | 3.6% (n=5,226) | -3.2 pts [-4.1, -2.3] | 0.030 |
| CONSTRAINT_CHECKED | 16.9% (n=4,523) | 18.0% (n=5,226) | +1.1 pts [-0.4, +2.7] | 1.000 |
| RATE_OF_PROGRESS | 8.2% (n=4,523) | 12.1% (n=5,226) | +3.9 pts [+2.8, +5.2] | 0.030 |
| ROUND_ANCHOR | 8.2% (n=4,523) | 7.7% (n=5,226) | -0.5 pts [-1.5, +0.6] | 1.000 |
| CUTOFF_REFERENCED | 0.9% (n=4,523) | 0.2% (n=5,226) | -0.6 pts [-0.9, -0.3] | 0.030 |
| DIFFICULTY_APPEAL | 14.8% (n=4,523) | 23.2% (n=5,226) | +8.4 pts [+6.9, +9.9] | 0.030 |
| SPECIFICITY_AS_IMPLAUSIBLE | 7.9% (n=4,523) | 8.2% (n=5,226) | +0.4 pts [-0.7, +1.5] | 1.000 |
| PROVENANCE_INFERRED | 12.6% (n=4,523) | 4.6% (n=5,226) | -8.1 pts [-9.3, -6.9] | 0.030 |
| CONJUNCTION_BURDEN | 9.7% (n=4,523) | 11.4% (n=5,226) | +1.7 pts [+0.3, +3.0] | 0.084 |
| FIELD_MOMENTUM | 13.4% (n=4,523) | 26.2% (n=5,226) | +12.9 pts [+11.3, +14.5] | 0.030 |
| RESTATEMENT_ONLY | 0.2% (n=4,523) | 0.2% (n=5,226) | +0.0 pts [-0.2, +0.3] | 1.000 |

Differences are post minus pre; p-values are two-sided event-cluster bootstrap, Holm-adjusted across codes.


## By condition (pinned-500 paired subset only)

| code | base | WS+Cutoff | WS |
|---|---|---|---|
| BASE_RATE | 0.4% | 0.4% | 0.1% |
| HYPOTHESIS_COMPARISON | 6.0% | 6.2% | 4.2% |
| EVIDENCE_CITED | 10.6% | 50.4% | 59.5% |
| KNOWLEDGE_GAP_ADMITTED | 0.5% | 0.1% | 0.6% |
| ABSENCE_AS_EVIDENCE | 5.1% | 5.3% | 6.1% |
| CONSTRAINT_CHECKED | 17.5% | 21.0% | 20.2% |
| RATE_OF_PROGRESS | 10.3% | 5.3% | 2.7% |
| ROUND_ANCHOR | 7.9% | 2.3% | 1.6% |
| CUTOFF_REFERENCED | 0.5% | 0.0% | 0.3% |
| DIFFICULTY_APPEAL | 19.3% | 8.7% | 1.9% |
| SPECIFICITY_AS_IMPLAUSIBLE | 8.1% | 1.8% | 1.1% |
| PROVENANCE_INFERRED | 8.3% | 23.7% | 36.6% |
| CONJUNCTION_BURDEN | 10.6% | 5.5% | 3.8% |
| FIELD_MOMENTUM | 20.3% | 8.3% | 2.5% |
| RESTATEMENT_ONLY | 0.2% | 0.0% | 0.2% |

Condition columns are not matched here; analysis F uses the matched triples.


## HEDGING (mean of the two coders' 0-3 levels)

| task | mean level | n |
|---|---|---|
| binary | 1.08 | 1,620 |
| binary_perturbed | 1.10 | 1,615 |
| mcq | 0.40 | 1,607 |
| date | 1.00 | 3,144 |
| frq | 0.13 | 1,629 |
