# Analysis D — faithfulness of the stated justification to the emitted answer

A judge saw the question and the justification with the answer stripped out, and predicted which answer the justification argues toward. The judge was blind to the answer, the model, the condition and the ground truth (same blinding machinery as the coders). Inconsistency = the judge's reading differs from the answer the model actually gave.

Traces judged: **6,159** binary, perturbed-binary and MCQ. Judge returned UNDETERMINED on 1.2%; those are excluded from the rate, leaving **6,082**.

## Inconsistency rate

| model | task | n | inconsistent | accuracy when consistent | accuracy when inconsistent | difference [95% CI] | p (Holm) |
|---|---|---|---|---|---|---|---|
| Claude Opus 4.8 | binary | 243 | 2.5% | 0.519 | 0.667 | +0.148 [-0.356, +0.507] | 1.000 |
| Claude Opus 4.8 | binary_perturbed | 246 | 4.1% | 0.686 | 0.200 | -0.486 [-0.717, -0.167] | 0.250 |
| Claude Opus 4.8 | mcq | 248 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| Claude Opus 4.8 | all tasks | 737 | 2.2% | 0.717 | 0.375 | -0.342 [-0.576, -0.084] | 0.336 |
| Claude S4.5 | binary | 237 | 4.2% | 0.410 | 0.200 | -0.210 [-0.436, +0.084] | 1.000 |
| Claude S4.5 | binary_perturbed | 231 | 3.5% | 0.623 | 0.875 | +0.252 [-0.062, +0.436] | 1.000 |
| Claude S4.5 | mcq | 244 | 2.0% | 0.724 | 0.400 | -0.324 [-0.749, +0.222] | 1.000 |
| Claude S4.5 | all tasks | 712 | 3.2% | 0.588 | 0.478 | -0.110 [-0.321, +0.087] | 1.000 |
| Claude Sonnet 5 | binary | 240 | 4.6% | 0.511 | 0.636 | +0.125 [-0.157, +0.415] | 1.000 |
| Claude Sonnet 5 | binary_perturbed | 236 | 4.2% | 0.673 | 0.300 | -0.373 [-0.675, -0.046] | 0.545 |
| Claude Sonnet 5 | mcq | 250 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| Claude Sonnet 5 | all tasks | 726 | 2.9% | 0.711 | 0.476 | -0.234 [-0.453, -0.034] | 0.559 |
| DeepSeek-R1 | binary | 246 | 8.5% | 0.391 | 1.000 | +0.609 [+0.540, +0.676] | 0.070 |
| DeepSeek-R1 | binary_perturbed | 244 | 9.4% | 0.529 | 0.000 | -0.529 [-0.601, -0.457] | 0.070 |
| DeepSeek-R1 | mcq | 249 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| DeepSeek-R1 | all tasks | 739 | 6.0% | 0.524 | 0.477 | -0.046 [-0.208, +0.102] | 1.000 |
| DeepSeek-V4-Pro | binary | 156 | 1.3% | 0.097 | 0.500 | +0.403 [-0.135, +0.929] | 1.000 |
| DeepSeek-V4-Pro | binary_perturbed | 156 | 3.2% | 0.887 | 0.000 | -0.887 [-0.935, -0.836] | 0.070 |
| DeepSeek-V4-Pro | mcq | 160 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| DeepSeek-V4-Pro | all tasks | 472 | 1.5% | 0.542 | 0.143 | -0.399 [-0.576, -0.062] | 0.527 |
| GPT-4o | binary | 164 | 6.1% | 0.305 | 1.000 | +0.695 [+0.626, +0.765] | 0.070 |
| GPT-4o | binary_perturbed | 165 | 4.2% | 0.791 | 0.143 | -0.648 [-0.839, -0.284] | 0.156 |
| GPT-4o | mcq | 170 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| GPT-4o | all tasks | 499 | 3.4% | 0.581 | 0.647 | +0.066 [-0.176, +0.293] | 1.000 |
| GPT-5.4 | binary | 249 | 2.0% | 0.705 | 1.000 | +0.295 [+0.235, +0.356] | 0.368 |
| GPT-5.4 | binary_perturbed | 246 | 3.3% | 0.408 | 0.000 | -0.408 [-0.485, -0.338] | 0.070 |
| GPT-5.4 | mcq | 248 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| GPT-5.4 | all tasks | 743 | 1.7% | 0.648 | 0.385 | -0.263 [-0.525, +0.025] | 1.000 |
| GPT-5.6 Sol | binary | 250 | 1.2% | 0.866 | 1.000 | +0.134 [-0.870, +0.177] | 1.000 |
| GPT-5.6 Sol | binary_perturbed | 248 | 1.2% | 0.376 | 0.000 | -0.376 [-0.445, -0.303] | 0.070 |
| GPT-5.6 Sol | mcq | 248 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| GPT-5.6 Sol | all tasks | 746 | 0.8% | 0.711 | 0.500 | -0.211 [-0.706, +0.285] | 1.000 |
| GPT-OSS 20B | binary | 158 | 1.3% | 0.179 | 1.000 | +0.821 [-0.203, +0.873] | 1.000 |
| GPT-OSS 20B | binary_perturbed | 160 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| GPT-OSS 20B | mcq | 160 | 0.0% | -- | -- | +nan [+nan, +nan] | -- |
| GPT-OSS 20B | all tasks | 478 | 0.4% | 0.483 | 1.000 | +0.517 [-0.505, +0.559] | 1.000 |
| LLaMA 3.3 70B | binary | 77 | 2.6% | 0.933 | 1.000 | +0.067 [-0.961, +0.122] | 1.000 |
| LLaMA 3.3 70B | binary_perturbed | 76 | 3.9% | 0.041 | 0.000 | -0.041 [-0.093, +0.000] | 1.000 |
| LLaMA 3.3 70B | mcq | 77 | 1.3% | 0.461 | 1.000 | +0.539 [-0.545, +0.649] | 1.000 |
| LLaMA 3.3 70B | all tasks | 230 | 2.6% | 0.482 | 0.500 | +0.018 [-0.474, +0.520] | 1.000 |
| all models | binary | 2,020 | 3.6% | 0.496 | 0.792 | +0.295 [+0.190, +0.391] | 0.070 |
| all models | binary_perturbed | 2,008 | 3.8% | 0.592 | 0.169 | -0.424 [-0.503, -0.325] | 0.070 |
| all models | mcq | 2,054 | 0.3% | 0.754 | 0.500 | -0.254 [-0.751, +0.236] | 1.000 |
| all models | all tasks | 6,082 | 2.5% | 0.617 | 0.471 | -0.146 [-0.224, -0.067] | 0.070 |

**Overall: 2.5% of justifications argue toward a different answer than the one emitted.** Accuracy is 0.617 when the justification and the answer agree and 0.471 when they do not, a difference of -0.146 [-0.224, -0.067].


## Direction of the inconsistency, binary tasks

| model | justification argues Yes, answer No | justification argues No, answer Yes | n |
|---|---|---|---|
| Claude Opus 4.8 | 0.8% | 2.5% | 489 |
| Claude S4.5 | 3.2% | 0.6% | 468 |
| Claude Sonnet 5 | 1.5% | 2.9% | 476 |
| DeepSeek-R1 | 0.0% | 9.0% | 490 |
| DeepSeek-V4-Pro | 0.3% | 1.9% | 312 |
| GPT-4o | 0.3% | 4.9% | 329 |
| GPT-5.4 | 0.0% | 2.6% | 495 |
| GPT-5.6 Sol | 0.0% | 1.2% | 498 |
| GPT-OSS 20B | 0.0% | 0.6% | 318 |
| LLaMA 3.3 70B | 0.0% | 3.3% | 153 |

The judge is itself a language model, so this measures agreement between two readings of the same text, not ground truth about faithfulness. The human validation file covers the coding task; the faithfulness judgments are a separate instrument and are reported as such.

