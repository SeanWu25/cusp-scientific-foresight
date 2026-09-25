# Date task — anchoring null

Null predictor: always predict cutoff + k months, k fitted per model on its own post-cutoff items, (a) to maximise mean exp(−0.1|Δ|), (b) to minimise mean |Δ|. Because ground truth = cutoff + horizon, the null's signed error is k − h exactly: slope −1 month per month of horizon with zero forecasting content. A third null uses k = the model's own median (prediction − cutoff): a constant predictor placed where the model typically predicts. Slopes are per month of horizon. 'Share reproduced' = null(median) abs-error slope / model abs-error slope on the same items.


## 1. original corpus (Jan 2024–Mar 2026), base

| model | n | model: mean (median) pred − cutoff, months | k*: max score / min abs / model median | signed-error slope: model / null(k*) / null(median) | abs-error slope: model / null(k*) / null(median) | score slope: model / null(k*) / null(median) | share of model abs-error slope reproduced by null(median) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2573 | +51.6 (+44) | 15 / 15 / 44 | -1.07 / -1.00 / -1.00 | -0.93 / +0.11 / -1.00 | +0.0112 / -0.0047 / +0.0071 | 108% |
| LLaMA 3.3 70B | 2731 | +18.7 (+18) | 13 / 14 / 18 | -0.94 / -1.00 / -1.00 | -0.44 / +0.11 / -0.47 | +0.0151 / -0.0048 / +0.0212 | 107% |
| GPT-OSS 20B | 2126 | +35.8 (+18) | 10 / 10 / 18 | -1.00 / -1.00 / -1.00 | -0.70 / +0.06 / -0.91 | +0.0147 / -0.0032 / +0.0429 | 129% |
| DeepSeek R1 | 1702 | +25.3 (+20) | 10 / 10 / 20 | -1.06 / -1.00 / -1.00 | -0.72 / +0.01 / -1.00 | +0.0166 / -0.0002 / +0.0405 | 139% |
| Claude S4.5 | 1293 | +19.1 (+20) | 7 / 7 / 20 | -0.39 / -1.00 / -1.00 | -0.68 / +0.02 / -1.00 | +0.0107 / -0.0013 / +0.0287 | 147% |
| GPT-5.4 | 612 | +13.4 (+10) | 4 / 4 / 10 | +0.86 / -1.00 / -1.00 | -0.91 / -0.18 / -1.00 | -0.0047 / +0.0147 / +0.0534 | 110% |
| Claude Sonnet 5 | 122 | -14.8 (-10) | 1 / 1 / -10 | +4.88 / -1.00 / -1.00 | -6.98 / +1.00 / +1.00 | -0.0119 / -0.0952 / -0.0317 | -14% |
| Claude Opus 4.8 | 121 | -13.5 (-10) | 1 / 1 / -10 | +2.06 / -1.00 / -1.00 | -6.24 / +1.00 / +1.00 | -0.0051 / -0.0952 / -0.0317 | -16% |

## 2. extension (Apr–Aug 2026), base

| model | n | model: mean (median) pred − cutoff, months | k*: max score / min abs / model median | signed-error slope: model / null(k*) / null(median) | abs-error slope: model / null(k*) / null(median) | score slope: model / null(k*) / null(median) | share of model abs-error slope reproduced by null(median) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 193 | +39.5 (+31) | 32 / 32 / 31 | +1.09 / -1.00 / -1.00 | +1.70 / -0.06 / +0.58 | -0.0414 / +0.0057 / -0.0492 | 34% |
| LLaMA 3.3 70B | 195 | +19.6 (+18) | 30 / 30 / 18 | +0.20 / -1.00 / -1.00 | +1.63 / -0.06 / +1.00 | -0.0267 / +0.0052 / -0.0305 | 61% |
| GPT-OSS 20B | 190 | +33.3 (+22) | 24 / 24 / 22 | -3.42 / -1.00 / -1.00 | -1.99 / -0.06 / +1.00 | +0.0017 / +0.0051 / -0.0829 | -50% |
| Claude S4.5 | 169 | +21.1 (+20) | 17 / 17 / 20 | +0.50 / -1.00 / -1.00 | -2.00 / -0.07 / -1.00 | +0.0095 / +0.0062 / +0.0738 | 50% |
| GPT-5.4 | 153 | +9.8 (-2) | 10 / 10 / -2 | -1.58 / -1.00 / -1.00 | -0.27 / -0.05 / +1.00 | +0.0052 / +0.0044 / -0.0305 | -376% |
| Claude Sonnet 5 | 193 | -19.4 (-19) | 5 / 5 / -19 | -3.01 / -1.00 / -1.00 | +1.91 / -0.05 / +1.00 | -0.0099 / +0.0049 / -0.0092 | 52% |
| GPT-5.6 Sol | 194 | +12.2 (+16) | 4 / 4 / 16 | -2.43 / -1.00 / -1.00 | +0.20 / -0.06 / -1.00 | -0.0053 / +0.0054 / +0.0301 | -491% |
| DeepSeek-V4-Pro | 153 | +26.1 (+14) | 2 / 2 / 14 | -2.97 / -1.00 / -1.00 | +1.52 / +0.32 / -1.00 | +0.0153 / -0.0285 / +0.0315 | -66% |
| Claude Opus 4.8 | 193 | -16.3 (-16) | 5 / 5 / -16 | -2.79 / -1.00 / -1.00 | +1.27 / -0.05 / +1.00 | -0.0163 / +0.0049 / -0.0124 | 78% |

## 4. merged original + extension, base

| model | n | model: mean (median) pred − cutoff, months | k*: max score / min abs / model median | signed-error slope: model / null(k*) / null(median) | abs-error slope: model / null(k*) / null(median) | score slope: model / null(k*) / null(median) | share of model abs-error slope reproduced by null(median) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 2766 | +50.7 (+44) | 16 / 16 / 44 | -1.24 / -1.00 / -1.00 | -1.03 / +0.15 / -1.00 | +0.0133 / -0.0052 / +0.0089 | 97% |
| LLaMA 3.3 70B | 2926 | +18.7 (+18) | 14 / 14 / 18 | -0.94 / -1.00 / -1.00 | -0.25 / +0.14 / -0.28 | +0.0080 / -0.0051 / +0.0122 | 109% |
| GPT-OSS 20B | 2316 | +35.6 (+18) | 11 / 11 / 18 | -1.06 / -1.00 / -1.00 | -0.66 / +0.12 / -0.67 | +0.0104 / -0.0049 / +0.0305 | 102% |
| DeepSeek R1 | 1702 | +25.3 (+20) | 10 / 10 / 20 | -1.06 / -1.00 / -1.00 | -0.72 / +0.01 / -1.00 | +0.0166 / -0.0002 / +0.0405 | 139% |
| Claude S4.5 | 1462 | +19.4 (+20) | 7 / 8 / 20 | -0.56 / -1.00 / -1.00 | -0.66 / +0.31 / -1.00 | +0.0078 / -0.0168 / +0.0362 | 151% |
| GPT-5.4 | 765 | +12.7 (+7) | 4 / 4 / 7 | -0.94 / -1.00 / -1.00 | -1.21 / +0.49 / -0.27 | -0.0084 / -0.0325 / +0.0188 | 22% |
| Claude Sonnet 5 | 315 | -17.7 (-14) | 3 / 3 / -14 | -2.38 / -1.00 / -1.00 | +2.11 / +0.22 / +1.00 | -0.0271 / -0.0168 / -0.0174 | 47% |
| GPT-5.6 Sol | 199 | +11.8 (+16) | 4 / 4 / 16 | -1.73 / -1.00 / -1.00 | +0.55 / -0.12 / -1.00 | -0.0111 / +0.0102 / +0.0297 | -181% |
| DeepSeek-V4-Pro | 153 | +26.1 (+14) | 2 / 2 / 14 | -2.97 / -1.00 / -1.00 | +1.52 / +0.32 / -1.00 | +0.0153 / -0.0285 / +0.0315 | -66% |
| Claude Opus 4.8 | 314 | -15.3 (-15) | 3 / 3 / -15 | -1.98 / -1.00 / -1.00 | +1.70 / +0.22 / +1.00 | -0.0277 / -0.0169 / -0.0157 | 59% |
