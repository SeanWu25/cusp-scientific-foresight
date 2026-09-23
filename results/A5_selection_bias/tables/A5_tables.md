# A5 manuscript-ready tables

Pooled columns average over models carrying **every** stratum unsuppressed, so all columns rest on the same model set. `n sig` counts model x task permutation tests surviving Holm correction within the stratification.

## Source / Venue — POST-cutoff

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.506 (15,871) | 0.496 (8,184) | 0.497 (3,303) | 0.483 (6,191) | 0.493 (2,514) | 0.681 (742) | 9 | 10 | **5** |
| MCQ (acc) | 0.620 (9,087) | 0.574 (4,708) | 0.605 (2,205) | 0.538 (3,542) | 0.591 (1,262) | 0.375 (321) | 6 | 10 | **7** |
| Date (score) | 0.264 (5,999) | 0.240 (3,115) | 0.294 (1,082) | 0.461 (1,718) | 0.523 (810) | 0.446 (326) | 6 | 10 | **9** |
| FRQ (0-10) | 4.14 (10,924) | 4.10 (5,151) | 4.30 (2,468) | 4.32 (4,446) | 4.39 (1,658) | no items | 9 | 10 | **9** |

## Source / Venue — OVERALL-cutoff

| task | Nature | Science | Cell | HF Daily Papers (arXiv) | Top-10 AI Paper of Week (arXiv) | Leaderboards | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.517 (31,299) | 0.508 (16,188) | 0.519 (6,292) | 0.512 (11,546) | 0.525 (4,136) | 0.679 (1,176) | 10 | 10 | **7** |
| MCQ (acc) | 0.711 (19,805) | 0.685 (10,163) | 0.696 (4,595) | 0.683 (7,485) | 0.700 (2,277) | 0.529 (583) | 10 | 10 | **10** |
| Date (score) | 0.280 (13,660) | 0.248 (7,057) | 0.291 (2,366) | 0.502 (3,767) | 0.538 (1,438) | 0.464 (588) | 10 | 10 | **10** |
| FRQ (0-10) | 4.16 (21,022) | 4.10 (9,917) | 4.32 (4,609) | 4.32 (8,032) | 4.34 (2,726) | no items | 10 | 10 | **10** |

## Citation Quartile — POST-cutoff

| task | Q1 (<=8) | Q2 (<=22) | Q3 (<=59) | Q4 (>59) | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.502 (755) | 0.496 (725) | 0.488 (591) | 0.500 (659) | 5 | 6 | **0** |
| MCQ (acc) | 0.561 (528) | 0.572 (406) | 0.550 (378) | 0.568 (385) | 5 | 6 | **0** |
| Date (score) | 0.378 (231) | 0.404 (266) | 0.302 (213) | 0.293 (275) | 4 | 5 | **1** |
| FRQ (0-10) | 3.84 (529) | 3.74 (447) | 3.80 (419) | 3.61 (380) | 5 | 6 | **0** |

## Citation Quartile — OVERALL-cutoff

| task | Q1 (<=8) | Q2 (<=22) | Q3 (<=59) | Q4 (>59) | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.528 (1,544) | 0.509 (1,603) | 0.517 (1,493) | 0.521 (1,853) | 10 | 10 | **0** |
| MCQ (acc) | 0.693 (1,075) | 0.712 (914) | 0.703 (948) | 0.740 (1,074) | 10 | 10 | **0** |
| Date (score) | 0.319 (571) | 0.346 (700) | 0.298 (625) | 0.338 (857) | 10 | 10 | **4** |
| FRQ (0-10) | 4.26 (1,084) | 4.20 (975) | 4.27 (1,009) | 4.18 (1,072) | 10 | 10 | **0** |

## Publication Latency — POST-cutoff

| task | 0 mo | 1 mo | 2-3 mo | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.499 (4,115) | 0.510 (1,310) | 0.519 (948) | 9 | 9 | **0** |
| MCQ (acc) | 0.722 (2,845) | 0.658 (916) | 0.732 (664) | 9 | 9 | **0** |
| Date (score) | 0.277 (964) | 0.267 (200) | 0.274 (222) | 8 | 9 | **0** |
| FRQ (0-10) | 4.12 (2,912) | 4.11 (1,088) | 4.27 (684) | 9 | 9 | **0** |

## Publication Latency — OVERALL-cutoff

| task | 0 mo | 1 mo | 2-3 mo | models pooled | tests | Holm-sig |
|---|---|---|---|---|---|---|
| Binary (bal. acc) | 0.499 (4,115) | 0.510 (1,310) | 0.519 (948) | 9 | 9 | **0** |
| MCQ (acc) | 0.722 (2,845) | 0.658 (916) | 0.732 (664) | 9 | 9 | **0** |
| Date (score) | 0.277 (964) | 0.267 (200) | 0.274 (222) | 8 | 9 | **0** |
| FRQ (0-10) | 4.12 (2,912) | 4.11 (1,088) | 4.27 (684) | 9 | 9 | **0** |

## Pre/post partition sizes (entire dataset)

Partition rule: an event published in the cutoff month counts as POST. **These are very unequal, so OVERALL columns are not comparable between models.**

| model | cutoff | n events | pre-cutoff | post-cutoff |
|---|---|---|---|---|
| GPT-4o | 2023-10 | 5,575 | 0 | 5,575 |
| LLaMA 3.3 70B | 2023-12 | 5,575 | 0 | 5,575 |
| GPT-OSS 20B | 2024-06 | 5,575 | 657 | 4,918 |
| DeepSeek-R1 | 2024-07 | 4,760 | 842 | 3,918 |
| Claude S4.5 | 2025-01 | 5,575 | 1,907 | 3,668 |
| GPT-5.4 | 2025-08 | 5,575 | 3,372 | 2,203 |
| Claude Sonnet 5 | 2026-01 | 5,575 | 4,305 | 1,270 |
| GPT-5.6 Sol | 2026-02 | 5,575 | 4,508 | 1,067 |
| DeepSeek-V4-Pro | 2026-04 | 5,575 | 4,760 | 815 |
| Claude Opus 4.8 | 2026-01 | 5,575 | 4,305 | 1,270 |

