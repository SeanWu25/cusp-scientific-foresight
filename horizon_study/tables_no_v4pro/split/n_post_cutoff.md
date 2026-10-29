# Split analysis — post-cutoff N per dataset × model × task (h ≥ 1)

N = events with a scored item. `binary` = the original question, `binary_perturbed` = the perturbed twin; FRQ counts items with all four rubric dimensions.


## 1. original corpus (Jan 2024–Mar 2026), base — condition `base`

| model | binary (original) | binary (perturbed) | FRQ (4 dims) |
|---|---|---|---|
| GPT-4o | 2754 | 3654 | 4128 |
| LLaMA 3.3 70B | 2734 | 3625 | 4093 |
| GPT-OSS 20B | 2153 | 3038 | 3390 |
| DeepSeek R1 | 2014 | 2871 | 3231 |
| Claude S4.5 | 1327 | 1932 | 2181 |
| GPT-5.4 | 612 | 934 | 1019 |
| Claude Sonnet 5 | 123 | 194 | 204 |
| GPT-5.6 Sol | 5 | 12 | 10 |
| Claude Opus 4.8 | 122 | 194 | 205 |

## 2. extension (Apr–Aug 2026), base — condition `base`

| model | binary (original) | binary (perturbed) | FRQ (4 dims) |
|---|---|---|---|
| GPT-4o | 196 | 649 | 630 |
| LLaMA 3.3 70B | 196 | 649 | 630 |
| GPT-OSS 20B | 196 | 649 | 628 |
| DeepSeek R1 | 0 | 0 | 0 |
| Claude S4.5 | 174 | 538 | 558 |
| GPT-5.4 | 196 | 649 | 628 |
| Claude Sonnet 5 | 193 | 628 | 618 |
| GPT-5.6 Sol | 196 | 649 | 623 |
| Claude Opus 4.8 | 192 | 622 | 622 |

## 4. merged original + extension, base — condition `base`

| model | binary (original) | binary (perturbed) | FRQ (4 dims) |
|---|---|---|---|
| GPT-4o | 2950 | 4303 | 4758 |
| LLaMA 3.3 70B | 2930 | 4274 | 4723 |
| GPT-OSS 20B | 2349 | 3687 | 4018 |
| DeepSeek R1 | 2014 | 2871 | 3231 |
| Claude S4.5 | 1501 | 2470 | 2739 |
| GPT-5.4 | 808 | 1583 | 1647 |
| Claude Sonnet 5 | 316 | 822 | 822 |
| GPT-5.6 Sol | 201 | 661 | 633 |
| Claude Opus 4.8 | 314 | 816 | 827 |

## 3. WS+Cutoff on the pinned 500 subset — condition `base`

| model | binary (original) | binary (perturbed) | FRQ (4 dims) |
|---|---|---|---|
| GPT-4o | 296 | 394 | 426 |
| LLaMA 3.3 70B | 294 | 393 | 423 |
| GPT-OSS 20B | 0 | 0 | 0 |
| DeepSeek R1 | 204 | 305 | 329 |
| Claude S4.5 | 141 | 219 | 231 |
| GPT-5.4 | 59 | 100 | 107 |
| Claude Sonnet 5 | 14 | 23 | 24 |
| GPT-5.6 Sol | 0 | 1 | 1 |
| Claude Opus 4.8 | 14 | 23 | 24 |

## 3. WS+Cutoff on the pinned 500 subset — condition `ws_cutoff`

| model | binary (original) | binary (perturbed) | FRQ (4 dims) |
|---|---|---|---|
| GPT-4o | 296 | 394 | 425 |
| LLaMA 3.3 70B | 296 | 394 | 426 |
| GPT-OSS 20B | 0 | 0 | 0 |
| DeepSeek R1 | 204 | 307 | 320 |
| Claude S4.5 | 140 | 213 | 224 |
| GPT-5.4 | 59 | 100 | 106 |
| Claude Sonnet 5 | 15 | 23 | 24 |
| GPT-5.6 Sol | 0 | 1 | 1 |
| Claude Opus 4.8 | 14 | 22 | 24 |
