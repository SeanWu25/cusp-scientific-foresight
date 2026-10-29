# Analysis E — what differs in the traces of a yes-biased and a no-biased model

Table S13 puts **LLaMA 3.3 70B** at the yes-biased extreme and **GPT-OSS 20B** at the no-biased extreme. Comparison is on binary and perturbed-binary traces, base condition.

| code | LLaMA 3.3 70B | GPT-OSS 20B | difference [95% CI] | p (Holm) |
|---|---|---|---|---|
| EVIDENCE_CITED | 1.2% | 16.2% | -15.0 pts [-19.4, -10.8] | 0.014 |
| KNOWLEDGE_GAP_ADMITTED | 0.0% | 0.0% | +0.0 pts [+0.0, +0.0] | 1.000 |
| ABSENCE_AS_EVIDENCE | 0.0% | 57.2% | -57.2 pts [-62.2, -51.5] | 0.014 |
| RATE_OF_PROGRESS | 0.0% | 0.6% | -0.6 pts [-1.6, +0.0] | 0.845 |
| ROUND_ANCHOR | 0.0% | 0.9% | -0.9 pts [-2.2, +0.0] | 0.464 |
| PROVENANCE_INFERRED | 0.0% | 0.3% | -0.3 pts [-1.0, +0.0] | 1.000 |
| FIELD_MOMENTUM | 82.5% | 8.4% | +74.1 pts [+67.5, +80.7] | 0.014 |

## Does the biased model engage with the item, or repeat a generic pattern?

| measure | LLaMA 3.3 70B | GPT-OSS 20B |
|---|---|---|
| traces compared | 160 | 320 |
| mean trace length (words) | 46 | 42 |
| share of trace vocabulary drawn from the item | 26.7% | 34.0% |
| type-token ratio of the trace corpus | 0.299 | 0.274 |
| share of traces sharing the single commonest 5-word opening | 25.6% | 1.9% |

Commonest opening for LLaMA 3.3 70B: "given the rapid advancements in..." (41 traces).

Commonest opening for GPT-OSS 20B: "the claim is highly specific..." (6 traces).
