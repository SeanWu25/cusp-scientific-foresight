# A7 Step 0 — inventory of stored reasoning text (read-only; no analysis)

Every stored prediction file of the ten-model panel, by condition and corpus half. "Reasoning text" = the `reasoning` field the JSON answer format requests (`"reasoning": "<1-2 sentence justification>"`); for FRQ it is the answer itself (the prompt asks for 3–4 sentences of method, no separate reasoning field). "Native thinking" = a provider-returned thinking/reasoning text field stored alongside the answer.

## Headline

* **Provider-native thinking text: 0 records in every file.** None was stored for any model, task or condition (see the per-model notes below). Only the in-answer 1–2-sentence justification exists, plus reasoning-token *counts* for GPT-5.4 and GPT-5.6 Sol.
* In-answer reasoning exists for every answered record of every model, task and condition (base, WS+Cutoff, WS; original corpus and extension), including Claude Sonnet 5 and GPT-5.6 Sol on the extension.
* Traces are short by design: the prompt asks for a 1–2-sentence justification (medians below). They are justifications written *after* the answer is chosen inside one JSON object, not a chain of thought.

## Native thinking, per model

| model | status |
|---|---|
| DeepSeek-R1 | native <think>…</think> block was STRIPPED before storage (test_LLM.get_model_response regex); not recoverable |
| GPT-5.4 | reasoning tokens are billed and COUNTED (`*_reasoning_tokens`) but the text is never returned by the API; no text stored |
| GPT-5.6 Sol | reasoning tokens COUNTED only (`*_reasoning_tokens`); text not returned by the API |
| Claude Sonnet 5 | adaptive thinking on; runs used --no-capture-thinking (default) — 0 of 32 probe calls returned any summary text; no thinking text stored |
| Claude Opus 4.8 | same as Sonnet 5: no thinking text stored |
| GPT-OSS 20B | served locally (transformers / vLLM); the analysis channel was not captured, only the final JSON |
| DeepSeek-V4-Pro | non-reasoning chat endpoint; no thinking field |
| GPT-4o | non-reasoning model |
| LLaMA 3.3 70B | non-reasoning model |
| Claude S4.5 | thinking not enabled in the published run |

## Base condition

| model | half | task | applicable | answered | with reasoning text | native thinking | reasoning-token count only (mean tokens) | truncated | refusals | fallback-parsed | words mean / median / p10 / p90 / max | < 10 words |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 44 / 44 / 37 / 53 / 79 | 0 |
| GPT-4o | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 0 | 43 / 43 / 35 / 51 / 81 | 0 |
| GPT-4o | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 0 | 47 / 47 / 37 / 58 / 100 | 0 |
| GPT-4o | orig | date | 2755 | 2755 | 2580 | 0 | 0 | 0 | 0 | 0 | 42 / 41 / 34 / 50 / 74 | 0 |
| GPT-4o | orig | frq | 4135 | 4135 | 4133 | 0 | 0 | 0 | 0 | 0 | 54 / 52 / 39 / 71 / 104 | 0 |
| LLaMA 3.3 70B | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 147 | 49 / 47 / 36 / 65 / 91 | 0 |
| LLaMA 3.3 70B | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 163 | 46 / 44 / 35 / 61 / 87 | 0 |
| LLaMA 3.3 70B | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 59 | 44 / 42 / 33 / 57 / 138 | 0 |
| LLaMA 3.3 70B | orig | date | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 1 | 41 / 41 / 33 / 51 / 73 | 0 |
| LLaMA 3.3 70B | orig | frq | 4135 | 4135 | 4135 | 0 | 0 | 0 | 0 | 0 | 81 / 81 / 70 / 92 / 157 | 0 |
| GPT-OSS 20B | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 1 | 41 / 36 / 27 / 49 / 1487 | 1 |
| GPT-OSS 20B | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 0 | 38 / 34 / 26 / 44 / 1647 | 0 |
| GPT-OSS 20B | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 1 | 36 / 34 / 27 / 44 / 1363 | 0 |
| GPT-OSS 20B | orig | date | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 6 | 53 / 37 / 28 / 49 / 1691 | 1 |
| GPT-OSS 20B | orig | frq | 4135 | 4135 | 4135 | 0 | 0 | 0 | 0 | 0 | 102 / 92 / 70 / 118 / 1774 | 2 |
| DeepSeek-R1 | orig | binary | 2755 | 2740 | 2740 | 0 | 0 | 0 | 0 | 2 | 44 / 43 / 33 / 55 / 89 | 0 |
| DeepSeek-R1 | orig | binary_perturbed | 3656 | 3624 | 3624 | 0 | 0 | 0 | 0 | 7 | 42 / 41 / 32 / 52 / 89 | 1 |
| DeepSeek-R1 | orig | mcq | 4128 | 3609 | 3609 | 0 | 0 | 0 | 0 | 46 | 55 / 53 / 40 / 74 / 128 | 5 |
| DeepSeek-R1 | orig | date | 2755 | 2748 | 2333 | 0 | 0 | 0 | 0 | 1 | 43 / 42 / 33 / 53 / 87 | 1 |
| DeepSeek-R1 | orig | frq | 4135 | 4121 | 4119 | 0 | 0 | 0 | 0 | 0 | 110 / 110 / 86 / 134 / 179 | 3 |
| Claude S4.5 | orig | binary | 2755 | 2755 | 2641 | 0 | 0 | 0 | 0 | 2 | 79 / 69 / 57 / 88 / 285 | 0 |
| Claude S4.5 | orig | binary_perturbed | 3656 | 3656 | 3495 | 0 | 0 | 0 | 0 | 8 | 78 / 66 / 54 / 86 / 294 | 1 |
| Claude S4.5 | orig | mcq | 4128 | 4128 | 3858 | 0 | 0 | 0 | 0 | 4 | 58 / 57 / 48 / 70 / 111 | 0 |
| Claude S4.5 | orig | date | 2755 | 2755 | 2593 | 0 | 0 | 0 | 0 | 0 | 52 / 51 / 42 / 65 / 231 | 0 |
| Claude S4.5 | orig | frq | 4135 | 4135 | 3951 | 0 | 0 | 0 | 0 | 0 | 136 / 135 / 118 / 156 / 185 | 0 |
| GPT-5.4 | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 58 / 58 / 48 / 69 / 86 | 0 |
| GPT-5.4 | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 0 | 58 / 58 / 48 / 68 / 89 | 0 |
| GPT-5.4 | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 0 | 54 / 54 / 45 / 63 / 81 | 0 |
| GPT-5.4 | orig | date | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 52 / 52 / 42 / 62 / 83 | 0 |
| GPT-5.4 | orig | frq | 4135 | 4135 | 4134 | 0 | 0 | 0 | 0 | 0 | 138 / 135 / 108 / 170 / 283 | 0 |
| Claude Sonnet 5 | orig | binary | 2755 | 2677 | 2677 | 0 | 0 | 0 | 78 | 88 | 41 / 40 / 31 / 54 / 106 | 0 |
| Claude Sonnet 5 | orig | binary_perturbed | 3656 | 3542 | 3542 | 0 | 0 | 0 | 120 | 147 | 41 / 39 / 30 / 52 / 92 | 3 |
| Claude Sonnet 5 | orig | mcq | 4128 | 3792 | 3792 | 0 | 0 | 0 | 347 | 347 | 31 / 31 / 25 / 38 / 61 | 0 |
| Claude Sonnet 5 | orig | date | 2755 | 2650 | 2650 | 0 | 0 | 0 | 107 | 107 | 30 / 30 / 23 / 39 / 71 | 0 |
| Claude Sonnet 5 | orig | frq | 4135 | 4037 | 4037 | 0 | 0 | 3893 | 104 | 0 | 128 / 128 / 111 / 148 / 179 | 4 |
| GPT-5.6 Sol | orig | binary | 2755 | 2747 | 2747 | 0 | 2753 (429) | 6 | 2 | 8 | 32 / 32 / 25 / 41 / 57 | 0 |
| GPT-5.6 Sol | orig | binary_perturbed | 3656 | 3651 | 3651 | 0 | 3655 (412) | 4 | 1 | 5 | 34 / 33 / 26 / 44 / 60 | 0 |
| GPT-5.6 Sol | orig | mcq | 4128 | 4102 | 4102 | 0 | 4069 (169) | 2 | 24 | 26 | 34 / 33 / 26 / 43 / 56 | 0 |
| GPT-5.6 Sol | orig | date | 2755 | 2719 | 2719 | 0 | 2755 (604) | 36 | 0 | 36 | 25 / 25 / 19 / 33 / 50 | 0 |
| GPT-5.6 Sol | orig | frq | 4135 | 4077 | 4077 | 0 | 4079 (274) | 2 | 56 | 0 | 93 / 91 / 77 / 112 / 165 | 0 |
| DeepSeek-V4-Pro | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 42 / 41 / 32 / 53 / 75 | 0 |
| DeepSeek-V4-Pro | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 0 | 40 / 39 / 31 / 51 / 91 | 0 |
| DeepSeek-V4-Pro | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 2 | 39 / 37 / 30 / 50 / 110 | 1 |
| DeepSeek-V4-Pro | orig | date | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 41 / 40 / 30 / 52 / 109 | 0 |
| DeepSeek-V4-Pro | orig | frq | 4135 | 4135 | 4135 | 0 | 0 | 0 | 0 | 0 | 84 / 82 / 66 / 103 / 165 | 0 |
| Claude Opus 4.8 | orig | binary | 2755 | 2668 | 2668 | 0 | 0 | 0 | 87 | 87 | 35 / 34 / 26 / 45 / 69 | 0 |
| Claude Opus 4.8 | orig | binary_perturbed | 3656 | 3511 | 3511 | 0 | 0 | 0 | 145 | 145 | 35 / 34 / 27 / 44 / 68 | 0 |
| Claude Opus 4.8 | orig | mcq | 4128 | 3739 | 3739 | 0 | 0 | 0 | 399 | 399 | 26 / 26 / 21 / 32 / 55 | 0 |
| Claude Opus 4.8 | orig | date | 2755 | 2628 | 2628 | 0 | 0 | 0 | 129 | 130 | 29 / 28 / 23 / 35 / 52 | 0 |
| Claude Opus 4.8 | orig | frq | 4135 | 4035 | 4035 | 0 | 0 | 3715 | 104 | 0 | 140 / 139 / 123 / 159 / 190 | 0 |
| GPT-4o | ext | binary | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 44 / 44 / 35 / 55 / 75 | 0 |
| GPT-4o | ext | binary_perturbed | 649 | 649 | 649 | 0 | 0 | 0 | 0 | 0 | 42 / 42 / 33 / 52 / 73 | 0 |
| GPT-4o | ext | mcq | 606 | 606 | 606 | 0 | 0 | 0 | 0 | 0 | 35 / 34 / 27 / 45 / 66 | 0 |
| GPT-4o | ext | date | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 41 / 40 / 31 / 53 / 67 | 0 |
| GPT-4o | ext | frq | 630 | 630 | 630 | 0 | 0 | 0 | 0 | 0 | 77 / 75 / 58 / 100 / 125 | 0 |
| LLaMA 3.3 70B | ext | binary | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 47 / 45 / 35 / 62 / 86 | 0 |
| LLaMA 3.3 70B | ext | binary_perturbed | 649 | 649 | 648 | 0 | 0 | 0 | 0 | 0 | 45 / 43 / 34 / 58 / 80 | 0 |
| LLaMA 3.3 70B | ext | mcq | 606 | 606 | 606 | 0 | 0 | 0 | 0 | 0 | 45 / 44 / 34 / 60 / 84 | 0 |
| LLaMA 3.3 70B | ext | date | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 42 / 42 / 32 / 52 / 82 | 0 |
| LLaMA 3.3 70B | ext | frq | 630 | 630 | 630 | 0 | 0 | 0 | 0 | 0 | 82 / 81 / 70 / 94 / 114 | 0 |
| GPT-OSS 20B | ext | binary | 196 | 193 | 193 | 0 | 0 | 3 | 0 | 3 | 42 / 40 / 31 / 55 / 78 | 0 |
| GPT-OSS 20B | ext | binary_perturbed | 649 | 648 | 648 | 0 | 0 | 1 | 0 | 1 | 37 / 37 / 29 / 47 / 68 | 0 |
| GPT-OSS 20B | ext | mcq | 606 | 605 | 605 | 0 | 0 | 1 | 0 | 1 | 37 / 36 / 29 / 48 / 70 | 0 |
| GPT-OSS 20B | ext | date | 196 | 192 | 192 | 0 | 0 | 4 | 0 | 4 | 40 / 39 / 29 / 53 / 86 | 1 |
| GPT-OSS 20B | ext | frq | 630 | 628 | 628 | 0 | 0 | 2 | 0 | 0 | 107 / 104 / 77 / 141 / 241 | 0 |
| Claude S4.5 | ext | binary | 196 | 175 | 175 | 0 | 0 | 0 | 22 | 27 | 76 / 71 / 59 / 85 / 270 | 0 |
| Claude S4.5 | ext | binary_perturbed | 649 | 544 | 544 | 0 | 0 | 0 | 111 | 147 | 76 / 66 / 55 / 85 / 257 | 0 |
| Claude S4.5 | ext | mcq | 606 | 478 | 478 | 0 | 0 | 0 | 133 | 133 | 59 / 58 / 49 / 71 / 88 | 0 |
| Claude S4.5 | ext | date | 196 | 175 | 175 | 0 | 0 | 0 | 24 | 27 | 53 / 52 / 42 / 68 / 82 | 0 |
| Claude S4.5 | ext | frq | 630 | 561 | 561 | 0 | 0 | 559 | 71 | 0 | 137 / 137 / 119 / 155 / 171 | 0 |
| GPT-5.4 | ext | binary | 196 | 192 | 192 | 0 | 196 (598) | 4 | 0 | 4 | 57 / 56 / 45 / 68 / 76 | 0 |
| GPT-5.4 | ext | binary_perturbed | 649 | 646 | 646 | 0 | 649 (550) | 3 | 0 | 3 | 56 / 56 / 48 / 66 / 76 | 0 |
| GPT-5.4 | ext | mcq | 606 | 600 | 600 | 0 | 606 (373) | 6 | 0 | 6 | 53 / 53 / 45 / 61 / 74 | 0 |
| GPT-5.4 | ext | date | 196 | 153 | 153 | 0 | 196 (1263) | 43 | 0 | 43 | 48 / 49 / 37 / 58 / 71 | 0 |
| GPT-5.4 | ext | frq | 630 | 629 | 629 | 0 | 629 (309) | 0 | 1 | 0 | 126 / 125 / 101 / 152 / 189 | 0 |
| Claude Sonnet 5 | ext | binary | 196 | 193 | 193 | 0 | 0 | 0 | 3 | 3 | 43 / 42 / 32 / 54 / 80 | 0 |
| Claude Sonnet 5 | ext | binary_perturbed | 649 | 628 | 628 | 0 | 0 | 0 | 21 | 27 | 41 / 40 / 31 / 51 / 75 | 0 |
| Claude Sonnet 5 | ext | mcq | 606 | 569 | 569 | 0 | 0 | 0 | 37 | 37 | 31 / 31 / 25 / 38 / 48 | 0 |
| Claude Sonnet 5 | ext | date | 196 | 193 | 193 | 0 | 0 | 0 | 3 | 3 | 32 / 31 / 23 / 41 / 62 | 0 |
| Claude Sonnet 5 | ext | frq | 630 | 618 | 618 | 0 | 0 | 602 | 12 | 0 | 128 / 128 / 112 / 147 / 172 | 0 |
| GPT-5.6 Sol | ext | binary | 196 | 196 | 196 | 0 | 196 (325) | 0 | 0 | 0 | 39 / 39 / 30 / 47 / 58 | 0 |
| GPT-5.6 Sol | ext | binary_perturbed | 649 | 649 | 649 | 0 | 649 (297) | 0 | 0 | 0 | 38 / 38 / 30 / 46 / 54 | 0 |
| GPT-5.6 Sol | ext | mcq | 606 | 602 | 602 | 0 | 598 (137) | 0 | 4 | 4 | 36 / 35 / 28 / 46 / 56 | 0 |
| GPT-5.6 Sol | ext | date | 196 | 194 | 194 | 0 | 196 (688) | 2 | 0 | 2 | 29 / 28 / 21 / 41 / 52 | 0 |
| GPT-5.6 Sol | ext | frq | 630 | 623 | 623 | 0 | 623 (267) | 0 | 7 | 0 | 97 / 95 / 80 / 119 / 145 | 0 |
| DeepSeek-V4-Pro | ext | binary | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 44 / 44 / 33 / 56 / 65 | 0 |
| DeepSeek-V4-Pro | ext | binary_perturbed | 649 | 649 | 649 | 0 | 0 | 0 | 0 | 0 | 42 / 41 / 32 / 53 / 75 | 0 |
| DeepSeek-V4-Pro | ext | mcq | 606 | 606 | 606 | 0 | 0 | 0 | 0 | 0 | 40 / 38 / 31 / 52 / 72 | 0 |
| DeepSeek-V4-Pro | ext | date | 196 | 196 | 196 | 0 | 0 | 0 | 0 | 0 | 41 / 40 / 31 / 51 / 80 | 0 |
| DeepSeek-V4-Pro | ext | frq | 630 | 630 | 630 | 0 | 0 | 0 | 0 | 0 | 86 / 84 / 68 / 105 / 146 | 0 |
| Claude Opus 4.8 | ext | binary | 196 | 192 | 192 | 0 | 0 | 0 | 4 | 4 | 38 / 38 / 30 / 48 / 57 | 0 |
| Claude Opus 4.8 | ext | binary_perturbed | 649 | 622 | 622 | 0 | 0 | 0 | 27 | 27 | 37 / 36 / 29 / 46 / 61 | 0 |
| Claude Opus 4.8 | ext | mcq | 606 | 569 | 569 | 0 | 0 | 0 | 37 | 37 | 27 / 27 / 22 / 33 / 49 | 0 |
| Claude Opus 4.8 | ext | date | 196 | 193 | 193 | 0 | 0 | 0 | 3 | 3 | 29 / 29 / 23 / 37 / 48 | 0 |
| Claude Opus 4.8 | ext | frq | 630 | 622 | 622 | 0 | 0 | 604 | 8 | 0 | 140 / 139 / 125 / 158 / 173 | 0 |

## WS+Cutoff (knowledge-access) condition

| model | half | task | applicable | answered | with reasoning text | native thinking | reasoning-token count only (mean tokens) | truncated | refusals | fallback-parsed | words mean / median / p10 / p90 / max | < 10 words |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | orig | binary | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 59 / 59 / 46 / 74 / 105 | 0 |
| GPT-4o | orig | binary_perturbed | 3656 | 3656 | 3656 | 0 | 0 | 0 | 0 | 0 | 58 / 57 / 46 / 71 / 99 | 0 |
| GPT-4o | orig | mcq | 4128 | 4128 | 4128 | 0 | 0 | 0 | 0 | 0 | 48 / 48 / 37 / 59 / 108 | 0 |
| GPT-4o | orig | date | 2755 | 2755 | 2755 | 0 | 0 | 0 | 0 | 0 | 51 / 50 / 38 / 65 / 89 | 0 |
| GPT-4o | orig | frq | 4135 | 4135 | 4135 | 0 | 0 | 0 | 0 | 0 | 79 / 72 / 57 / 115 / 181 | 0 |
| GPT-5.4 | orig | binary | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 47 / 44 / 33 / 66 / 88 | 0 |
| GPT-5.4 | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 54 / 55 / 38 / 68 / 84 | 0 |
| GPT-5.4 | orig | mcq | 435 | 435 | 435 | 0 | 0 | 0 | 0 | 0 | 51 / 50 / 42 / 61 / 72 | 0 |
| GPT-5.4 | orig | date | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 51 / 50 / 40 / 64 / 79 | 0 |
| GPT-5.4 | orig | frq | 426 | 426 | 426 | 0 | 0 | 0 | 0 | 0 | 143 / 140 / 105 / 182 / 263 | 0 |
| DeepSeek-R1 | orig | binary | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 61 / 57 / 40 / 88 / 120 | 0 |
| DeepSeek-R1 | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 62 / 62 / 41 / 85 / 118 | 0 |
| DeepSeek-R1 | orig | mcq | 435 | 435 | 435 | 0 | 0 | 0 | 0 | 0 | 82 / 84 / 51 / 111 / 150 | 0 |
| DeepSeek-R1 | orig | date | 296 | 296 | 284 | 0 | 0 | 0 | 0 | 0 | 60 / 57 / 41 / 82 / 108 | 0 |
| DeepSeek-R1 | orig | frq | 426 | 426 | 426 | 0 | 0 | 0 | 0 | 0 | 142 / 142 / 104 / 176 / 226 | 0 |
| Claude S4.5 | orig | binary | 296 | 296 | 284 | 0 | 0 | 0 | 0 | 0 | 110 / 78 / 55 / 268 / 351 | 0 |
| Claude S4.5 | orig | binary_perturbed | 394 | 394 | 369 | 0 | 0 | 0 | 0 | 0 | 121 / 81 / 61 / 277 / 326 | 0 |
| Claude S4.5 | orig | mcq | 435 | 435 | 394 | 0 | 0 | 0 | 0 | 0 | 101 / 74 / 55 / 278 / 336 | 0 |
| Claude S4.5 | orig | date | 296 | 296 | 279 | 0 | 0 | 0 | 0 | 0 | 134 / 95 / 57 / 245 / 307 | 0 |
| Claude S4.5 | orig | frq | 426 | 426 | 407 | 0 | 0 | 0 | 0 | 0 | 135 / 135 / 117 / 155 / 175 | 0 |
| LLaMA 3.3 70B | orig | binary | 296 | 296 | 294 | 0 | 0 | 0 | 0 | 0 | 52 / 50 / 36 / 76 / 112 | 0 |
| LLaMA 3.3 70B | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 53 / 52 / 37 / 72 / 104 | 0 |
| LLaMA 3.3 70B | orig | mcq | 435 | 435 | 431 | 0 | 0 | 0 | 0 | 0 | 53 / 52 / 37 / 71 / 126 | 0 |
| LLaMA 3.3 70B | orig | date | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 59 / 58 / 37 / 84 / 121 | 0 |
| LLaMA 3.3 70B | orig | frq | 426 | 426 | 421 | 0 | 0 | 0 | 0 | 0 | 83 / 80 / 65 / 103 / 170 | 0 |
| Claude Sonnet 5 | orig | binary | 296 | 289 | 289 | 0 | 0 | 0 | 8 | 8 | 33 / 32 / 22 / 44 / 84 | 1 |
| Claude Sonnet 5 | orig | binary_perturbed | 394 | 383 | 383 | 0 | 0 | 0 | 11 | 11 | 36 / 35 / 26 / 48 / 66 | 0 |
| Claude Sonnet 5 | orig | mcq | 435 | 403 | 403 | 0 | 0 | 0 | 34 | 34 | 28 / 28 / 21 / 36 / 49 | 0 |
| Claude Sonnet 5 | orig | date | 296 | 287 | 287 | 0 | 0 | 0 | 9 | 9 | 23 / 22 / 14 / 34 / 49 | 3 |
| Claude Sonnet 5 | orig | frq | 426 | 416 | 416 | 0 | 0 | 328 | 12 | 0 | 131 / 131 / 116 / 148 / 191 | 2 |
| GPT-5.6 Sol | orig | binary | 296 | 295 | 295 | 0 | 292 (138) | 1 | 0 | 1 | 33 / 32 / 25 / 41 / 54 | 0 |
| GPT-5.6 Sol | orig | binary_perturbed | 394 | 394 | 394 | 0 | 394 (168) | 0 | 0 | 0 | 36 / 36 / 27 / 46 / 57 | 0 |
| GPT-5.6 Sol | orig | mcq | 435 | 431 | 431 | 0 | 227 (128) | 0 | 4 | 4 | 34 / 33 / 27 / 43 / 51 | 0 |
| GPT-5.6 Sol | orig | date | 296 | 296 | 296 | 0 | 278 (202) | 0 | 0 | 0 | 23 / 22 / 16 / 30 / 42 | 0 |
| GPT-5.6 Sol | orig | frq | 426 | 413 | 413 | 0 | 413 (149) | 0 | 13 | 0 | 85 / 84 / 72 / 101 / 141 | 0 |
| Claude Opus 4.8 | orig | binary | 296 | 287 | 287 | 0 | 0 | 0 | 9 | 9 | 31 / 29 / 21 / 43 / 69 | 0 |
| Claude Opus 4.8 | orig | binary_perturbed | 394 | 378 | 378 | 0 | 0 | 0 | 16 | 16 | 34 / 33 / 24 / 47 / 84 | 0 |
| Claude Opus 4.8 | orig | mcq | 435 | 400 | 400 | 0 | 0 | 0 | 35 | 35 | 28 / 27 / 21 / 36 / 62 | 0 |
| Claude Opus 4.8 | orig | date | 296 | 283 | 283 | 0 | 0 | 0 | 13 | 13 | 28 / 27 / 19 / 37 / 55 | 0 |
| Claude Opus 4.8 | orig | frq | 426 | 415 | 415 | 0 | 0 | 322 | 11 | 0 | 137 / 136 / 121 / 156 / 182 | 0 |
| Claude Sonnet 5 | ext | binary | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 48 / 49 / 35 / 63 / 67 | 0 |
| Claude Sonnet 5 | ext | binary_perturbed | 74 | 72 | 72 | 0 | 0 | 0 | 2 | 2 | 43 / 42 / 32 / 54 / 65 | 0 |
| Claude Sonnet 5 | ext | mcq | 63 | 59 | 59 | 0 | 0 | 0 | 4 | 4 | 32 / 32 / 25 / 38 / 41 | 0 |
| Claude Sonnet 5 | ext | date | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 32 / 30 / 18 / 49 / 61 | 0 |
| Claude Sonnet 5 | ext | frq | 72 | 70 | 70 | 0 | 0 | 66 | 2 | 0 | 132 / 131 / 117 / 149 / 179 | 0 |
| Claude Opus 4.8 | ext | binary | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 40 / 40 / 27 / 50 / 71 | 0 |
| Claude Opus 4.8 | ext | binary_perturbed | 74 | 71 | 71 | 0 | 0 | 0 | 3 | 3 | 40 / 40 / 28 / 50 / 65 | 0 |
| Claude Opus 4.8 | ext | mcq | 63 | 58 | 58 | 0 | 0 | 0 | 5 | 5 | 33 / 33 / 24 / 43 / 48 | 0 |
| Claude Opus 4.8 | ext | date | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 36 / 34 / 29 / 47 / 56 | 0 |
| Claude Opus 4.8 | ext | frq | 72 | 70 | 70 | 0 | 0 | 64 | 2 | 0 | 138 / 135 / 121 / 158 / 170 | 0 |

## WS (unrestricted) condition

| model | half | task | applicable | answered | with reasoning text | native thinking | reasoning-token count only (mean tokens) | truncated | refusals | fallback-parsed | words mean / median / p10 / p90 / max | < 10 words |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | orig | binary | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 49 / 44 / 31 / 63 / 265 | 0 |
| GPT-4o | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 61 / 50 / 34 / 81 / 476 | 0 |
| GPT-4o | orig | mcq | 435 | 435 | 435 | 0 | 0 | 0 | 0 | 0 | 45 / 40 / 29 / 60 / 259 | 0 |
| GPT-4o | orig | date | 296 | 296 | 278 | 0 | 0 | 0 | 0 | 1 | 49 / 41 / 23 / 78 / 342 | 0 |
| GPT-4o | orig | frq | 426 | 426 | 426 | 0 | 0 | 0 | 0 | 0 | 119 / 118 / 61 / 177 / 347 | 1 |
| GPT-5.4 | orig | binary | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 44 / 42 / 34 / 55 / 81 | 1 |
| GPT-5.4 | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 53 / 52 / 38 / 69 / 94 | 4 |
| GPT-5.4 | orig | mcq | 435 | 435 | 435 | 0 | 0 | 0 | 0 | 0 | 50 / 49 / 39 / 61 / 81 | 0 |
| GPT-5.4 | orig | date | 296 | 296 | 274 | 0 | 0 | 0 | 0 | 0 | 8 / 1 / 1 / 38 / 68 | 228 |
| GPT-5.4 | orig | frq | 426 | 426 | 424 | 0 | 0 | 0 | 0 | 0 | 223 / 220 / 181 / 277 / 338 | 0 |
| DeepSeek-R1 | orig | binary | 296 | 296 | 296 | 0 | 0 | 0 | 0 | 0 | 56 / 53 / 37 / 79 / 136 | 0 |
| DeepSeek-R1 | orig | binary_perturbed | 394 | 394 | 394 | 0 | 0 | 0 | 0 | 0 | 60 / 59 / 39 / 81 / 112 | 0 |
| DeepSeek-R1 | orig | mcq | 435 | 435 | 435 | 0 | 0 | 0 | 0 | 0 | 89 / 77 / 49 / 108 / 2399 | 0 |
| DeepSeek-R1 | orig | date | 296 | 296 | 288 | 0 | 0 | 0 | 0 | 0 | 55 / 52 / 38 / 75 / 150 | 0 |
| DeepSeek-R1 | orig | frq | 426 | 426 | 426 | 0 | 0 | 0 | 0 | 0 | 138 / 140 / 102 / 168 / 211 | 0 |
| Claude S4.5 | orig | binary | 296 | 296 | 281 | 0 | 0 | 0 | 0 | 0 | 119 / 76 / 52 / 269 / 319 | 0 |
| Claude S4.5 | orig | binary_perturbed | 394 | 394 | 369 | 0 | 0 | 0 | 0 | 0 | 120 / 79 / 57 / 278 / 332 | 0 |
| Claude S4.5 | orig | mcq | 435 | 435 | 403 | 0 | 0 | 0 | 0 | 0 | 104 / 69 / 52 / 280 / 342 | 0 |
| Claude S4.5 | orig | date | 296 | 296 | 283 | 0 | 0 | 0 | 0 | 0 | 134 / 135 / 51 / 232 / 313 | 0 |
| Claude S4.5 | orig | frq | 426 | 426 | 405 | 0 | 0 | 0 | 0 | 0 | 135 / 135 / 117 / 155 / 174 | 0 |
| Claude Sonnet 5 | orig | binary | 296 | 288 | 288 | 0 | 0 | 0 | 8 | 8 | 34 / 32 / 24 / 48 / 73 | 0 |
| Claude Sonnet 5 | orig | binary_perturbed | 394 | 383 | 383 | 0 | 0 | 0 | 11 | 11 | 36 / 36 / 26 / 46 / 70 | 0 |
| Claude Sonnet 5 | orig | mcq | 435 | 401 | 401 | 0 | 0 | 0 | 34 | 34 | 28 / 28 / 22 / 35 / 44 | 0 |
| Claude Sonnet 5 | orig | date | 296 | 286 | 286 | 0 | 0 | 0 | 10 | 10 | 24 / 22 / 13 / 35 / 50 | 3 |
| Claude Sonnet 5 | orig | frq | 426 | 416 | 416 | 0 | 0 | 323 | 11 | 0 | 131 / 130 / 116 / 150 / 166 | 0 |
| GPT-5.6 Sol | orig | binary | 296 | 295 | 295 | 0 | 290 (109) | 0 | 1 | 1 | 32 / 31 / 25 / 40 / 53 | 0 |
| GPT-5.6 Sol | orig | binary_perturbed | 394 | 392 | 392 | 0 | 391 (163) | 0 | 2 | 2 | 36 / 36 / 27 / 45 / 55 | 0 |
| GPT-5.6 Sol | orig | mcq | 435 | 430 | 430 | 0 | 201 (118) | 0 | 5 | 5 | 34 / 33 / 27 / 42 / 54 | 0 |
| GPT-5.6 Sol | orig | date | 296 | 296 | 296 | 0 | 274 (157) | 0 | 0 | 0 | 23 / 22 / 16 / 30 / 44 | 0 |
| GPT-5.6 Sol | orig | frq | 426 | 413 | 413 | 0 | 413 (146) | 0 | 13 | 0 | 85 / 83 / 72 / 99 / 134 | 0 |
| Claude Opus 4.8 | orig | binary | 296 | 287 | 287 | 0 | 0 | 0 | 9 | 9 | 30 / 28 / 20 / 44 / 71 | 0 |
| Claude Opus 4.8 | orig | binary_perturbed | 394 | 379 | 379 | 0 | 0 | 0 | 15 | 15 | 34 / 32 / 24 / 45 / 68 | 0 |
| Claude Opus 4.8 | orig | mcq | 435 | 401 | 401 | 0 | 0 | 0 | 35 | 35 | 27 / 26 / 20 / 34 / 65 | 0 |
| Claude Opus 4.8 | orig | date | 296 | 283 | 283 | 0 | 0 | 0 | 13 | 13 | 27 / 27 / 19 / 36 / 51 | 0 |
| Claude Opus 4.8 | orig | frq | 426 | 415 | 415 | 0 | 0 | 323 | 11 | 0 | 137 / 136 / 121 / 155 / 177 | 0 |
| Claude Sonnet 5 | ext | binary | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 35 / 32 / 27 / 48 / 61 | 0 |
| Claude Sonnet 5 | ext | binary_perturbed | 74 | 72 | 72 | 0 | 0 | 0 | 2 | 2 | 40 / 38 / 29 / 54 / 72 | 0 |
| Claude Sonnet 5 | ext | mcq | 63 | 59 | 59 | 0 | 0 | 0 | 4 | 4 | 29 / 29 / 20 / 35 / 44 | 0 |
| Claude Sonnet 5 | ext | date | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 26 / 25 / 17 / 36 / 40 | 0 |
| Claude Sonnet 5 | ext | frq | 72 | 70 | 70 | 0 | 0 | 62 | 2 | 0 | 134 / 134 / 119 / 153 / 166 | 0 |
| Claude Opus 4.8 | ext | binary | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 31 / 30 / 23 / 39 / 56 | 0 |
| Claude Opus 4.8 | ext | binary_perturbed | 74 | 71 | 71 | 0 | 0 | 0 | 3 | 3 | 36 / 34 / 26 / 46 / 75 | 0 |
| Claude Opus 4.8 | ext | mcq | 63 | 59 | 59 | 0 | 0 | 0 | 4 | 4 | 28 / 27 / 21 / 35 / 49 | 0 |
| Claude Opus 4.8 | ext | date | 23 | 23 | 23 | 0 | 0 | 0 | 0 | 0 | 27 / 27 / 19 / 34 / 39 | 0 |
| Claude Opus 4.8 | ext | frq | 72 | 70 | 70 | 0 | 0 | 59 | 2 | 0 | 139 / 139 / 121 / 159 / 175 | 0 |

## Anomalies (computed): missing, degenerate or truncated traces

* GPT-OSS 20B / base / orig / binary: max 1487 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* GPT-OSS 20B / base / orig / binary_perturbed: max 1647 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* GPT-OSS 20B / base / orig / mcq: max 1363 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* GPT-OSS 20B / base / orig / date: max 1691 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* GPT-OSS 20B / base / orig / frq: max 1774 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* DeepSeek-R1 / base / orig / date: 415 answered records have no reasoning text
* Claude Sonnet 5 / base / orig / mcq: 347 refusals (8%)
* Claude Sonnet 5 / base / orig / frq: 3893 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / base / orig / mcq: 399 refusals (10%)
* Claude Opus 4.8 / base / orig / frq: 3715 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* GPT-OSS 20B / base / ext / date: 4 truncated at the token cap (no answer/reasoning)
* Claude S4.5 / base / ext / binary: 22 refusals (11%)
* Claude S4.5 / base / ext / binary_perturbed: 111 refusals (17%)
* Claude S4.5 / base / ext / mcq: 133 refusals (22%)
* Claude S4.5 / base / ext / date: 24 refusals (12%)
* Claude S4.5 / base / ext / frq: 559 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence); 71 refusals (11%)
* GPT-5.4 / base / ext / binary: 4 truncated at the token cap (no answer/reasoning)
* GPT-5.4 / base / ext / date: 43 truncated at the token cap (no answer/reasoning)
* Claude Sonnet 5 / base / ext / mcq: 37 refusals (6%)
* Claude Sonnet 5 / base / ext / frq: 602 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / base / ext / mcq: 37 refusals (6%)
* Claude Opus 4.8 / base / ext / frq: 604 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* GPT-5.4 / ws / orig / date: median reasoning length 1 words (228 under 10 words) — degenerate
* DeepSeek-R1 / ws / orig / mcq: max 2399 words: a few `reasoning` fields hold the whole raw response (fallback parse)
* Claude Sonnet 5 / ws_cutoff / orig / mcq: 34 refusals (8%)
* Claude Sonnet 5 / ws_cutoff / orig / frq: 328 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Sonnet 5 / ws / orig / mcq: 34 refusals (8%)
* Claude Sonnet 5 / ws / orig / frq: 323 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / ws_cutoff / orig / mcq: 35 refusals (8%)
* Claude Opus 4.8 / ws_cutoff / orig / frq: 322 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / ws / orig / mcq: 35 refusals (8%)
* Claude Opus 4.8 / ws / orig / frq: 323 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Sonnet 5 / ws_cutoff / ext / mcq: 4 refusals (6%)
* Claude Sonnet 5 / ws_cutoff / ext / frq: 66 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Sonnet 5 / ws / ext / mcq: 4 refusals (6%)
* Claude Sonnet 5 / ws / ext / frq: 62 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / ws_cutoff / ext / mcq: 5 refusals (8%)
* Claude Opus 4.8 / ws_cutoff / ext / frq: 64 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)
* Claude Opus 4.8 / ws / ext / mcq: 4 refusals (6%)
* Claude Opus 4.8 / ws / ext / frq: 59 FRQ answers cut at the 384-token FRQ cap (text present but truncated mid-sentence)

## Missing files

none

## Other stored traces (available, not part of the base/WS inventory)

* Claude Sonnet 5 base passes 2,3 + low-effort: `results_sonnet5_run1/raw/base_medium_run{2,3}.jsonl, base_low_run1.jsonl (4,760 each)`
* GPT-5.6 Sol base passes 2,3 (1,000-event subsample): `results_sol_run1/raw/base_medium_run{2,3}.jsonl`
* Sonnet 5 / Opus 4.8 extension passes 2,3: `results_extension_run2/raw/{sonnet5,opus48}_base_run{2,3}.jsonl (815 each)`
* Sol WS/WS+Cutoff FAILED_no_context runs: `results_sol_run1/raw/*.FAILED_no_context.jsonl — retrieval failed; effectively extra base passes on the 500 subset`
* A6 calibration arms B1/B2/D/E (3 models, 500 subset): `calibration_study/raw/*.jsonl — modified prompts; reasoning field present`
* A8 base-rate sweep (9 models x 5 X, 500 events, binary only): `results/A8_base_rate/raw/*.jsonl — modified prompts; reasoning field present`
