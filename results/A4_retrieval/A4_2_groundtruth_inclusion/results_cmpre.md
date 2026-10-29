# A4.2 — Does the retrieved evidence contain the ground truth?

**Cutoff-month rule: an event published in the ceiling month counts as PRE-cutoff (post iff publication month > ceiling month). The Findings paragraph below is the original prose (old rule: post iff month >= ceiling month); the split tables are recomputed.**
**Findings.** (1) In the unrestricted WS condition the retrieved evidence contains the source paper or its stated outcome for 74–93% of events (the provider's native tool for GPT-4o/GPT-5.4: 88–93%; the single-query You.com pipeline: 74–85%). (2) In WS+Cutoff the rate on PRE-cutoff events is 77–85% (the paper existed before the cutoff, so this is recall, not leakage) and on POST-cutoff events it is 20–37% by judge on re-queried evidence, with 9–20% confirmed on the exact URLs the model received (Sol 37% on 30 events). (3) The post-cutoff leakage is not the source paper's own page (URL match 0–3%); it is snippet text: You.com dates a page by `page_age`, but the snippets it returns for researchgate.net publication pages include the abstracts of newer 'related' papers, so a page dated 2022 can carry a 2026 paper's results verbatim (`leak_example.json`). researchgate.net accounts for 332 of 439 post-cutoff inclusions; bioRxiv/medRxiv/arXiv/PubMed pages of the same work under another identifier account for most of the rest. (4) A domain blocklist for aggregator pages, or content-level dating of snippets, would be needed for a clean pre-cutoff condition; the current WS+Cutoff knowledge gap therefore contains a leakage component on post-cutoff events.

Judged cases: 6204 of 6226 (22 judge/retrieval errors excluded). Judge: Claude Sonnet 5 (effort low), asked whether any retrieved result is the source paper itself (same arXiv id / DOI / abstract, including preprint versions) or states the realized outcome. Evidence reconstruction: You.com runs re-queried with the stored query and the run's freshness bound, then filtered/formatted by the unmodified `scripts/web_search.py` code; native-tool runs (GPT-4o WS, GPT-5.4 WS) judged on the fetched text of the URLs the tool cited (a lower bound on what the tool read). `URL match` = deterministic arXiv-id/DOI match against the URLs stored at run time (a floor that needs no judge). 95% Wilson CIs.

## Inclusion rate per model and condition

| model | condition | mechanism | n | ground truth INCLUDED (judge) | of which: source paper / outcome stated | judge's matched URL was in the model's stored list | URL match (stored URLs, arXiv id / DOI) | stored↔live URL overlap |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | youcom | 497 | 24.7% [21.2%, 28.7%] | 84 / 39 | 9.1% (45) | 0.0% [0.0%, 0.8%] (n=497) | 35% |
| GPT-4o | ws | native | 498 | 88.0% [84.8%, 90.5%] | 414 / 24 | 87.8% (437) | 76.5% [72.6%, 80.0%] (n=498) | n/a |
| LLaMA 3.3 70B | ws_cutoff | youcom | 496 | 20.0% [16.7%, 23.7%] | 74 / 25 | 19.2% (95) | 0.0% [0.0%, 0.8%] (n=496) | 73% |
| DeepSeek R1 | ws_cutoff | youcom | 396 | 35.1% [30.6%, 39.9%] | 111 / 28 | 21.7% (86) | 7.3% [5.1%, 10.3%] (n=396) | 39% |
| DeepSeek R1 | ws | youcom | 402 | 81.3% [77.2%, 84.8%] | 299 / 28 | 57.5% (231) | 54.2% [49.3%, 59.0%] (n=402) | 39% |
| Claude S4.5 | ws_cutoff | youcom | 463 | 49.7% [45.1%, 54.2%] | 211 / 19 | 33.7% (156) | 19.9% [16.5%, 23.7%] (n=463) | 42% |
| Claude S4.5 | ws | youcom | 462 | 80.1% [76.2%, 83.5%] | 345 / 25 | 58.2% (269) | 56.3% [51.7%, 60.7%] (n=462) | 41% |
| GPT-5.4 | ws_cutoff | youcom | 497 | 70.4% [66.3%, 74.3%] | 324 / 26 | 50.9% (253) | 41.0% [36.8%, 45.4%] (n=497) | 40% |
| GPT-5.4 | ws | native | 498 | 93.0% [90.4%, 94.9%] | 440 / 23 | 93.0% (463) | 78.7% [74.9%, 82.1%] (n=498) | n/a |
| Claude Sonnet 5 | ws_cutoff | youcom | 499 | 63.7% [59.4%, 67.8%] | 288 / 30 | 61.3% (306) | 43.7% [39.4%, 48.1%] (n=499) | 70% |
| Claude Sonnet 5 | ws | youcom | 501 | 73.5% [69.4%, 77.1%] | 331 / 37 | 70.3% (352) | 56.1% [51.7%, 60.4%] (n=501) | 70% |
| GPT-5.6 Sol | ws_cutoff | youcom | 497 | 80.7% [77.0%, 83.9%] | 371 / 30 | 78.5% (390) | 54.7% [50.3%, 59.1%] (n=497) | 79% |
| GPT-5.6 Sol | ws | youcom | 498 | 84.9% [81.5%, 87.8%] | 393 / 30 | 82.5% (411) | 57.8% [53.5%, 62.1%] (n=498) | 78% |

## By task (events carrying that task type; retrieval is per event, shared across tasks)

| model | condition | binary | perturbed | MCQ | FRQ | date |
|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | 29.6% [24.7%, 35.0%] (n=294) | 24.3% [20.3%, 28.8%] (n=391) | 25.0% [21.1%, 29.3%] (n=432) | 24.8% [20.9%, 29.2%] (n=423) | 29.6% [24.7%, 35.0%] (n=294) |
| GPT-4o | ws | 93.9% [90.6%, 96.1%] (n=295) | 88.0% [84.4%, 90.9%] (n=392) | 89.8% [86.6%, 92.3%] (n=433) | 89.2% [85.8%, 91.8%] (n=424) | 93.9% [90.6%, 96.1%] (n=295) |
| LLaMA 3.3 70B | ws_cutoff | 23.1% [18.7%, 28.3%] (n=294) | 19.2% [15.6%, 23.4%] (n=391) | 19.5% [16.0%, 23.5%] (n=431) | 20.6% [17.0%, 24.7%] (n=422) | 23.1% [18.7%, 28.3%] (n=294) |
| DeepSeek R1 | ws_cutoff | 43.3% [37.1%, 49.8%] (n=233) | 33.7% [28.6%, 39.1%] (n=309) | 35.3% [30.4%, 40.4%] (n=346) | 33.5% [28.7%, 38.7%] (n=337) | 43.3% [37.1%, 49.8%] (n=233) |
| DeepSeek R1 | ws | 87.0% [82.1%, 90.7%] (n=238) | 80.6% [75.9%, 84.6%] (n=320) | 82.0% [77.6%, 85.7%] (n=350) | 81.9% [77.6%, 85.6%] (n=349) | 87.0% [82.1%, 90.7%] (n=238) |
| Claude S4.5 | ws_cutoff | 58.1% [52.2%, 63.7%] (n=279) | 49.2% [44.1%, 54.3%] (n=366) | 50.4% [45.5%, 55.2%] (n=403) | 49.2% [44.4%, 54.1%] (n=398) | 58.1% [52.2%, 63.7%] (n=279) |
| Claude S4.5 | ws | 82.0% [77.1%, 86.1%] (n=278) | 78.6% [74.1%, 82.5%] (n=365) | 80.1% [76.0%, 83.8%] (n=403) | 81.4% [77.2%, 84.9%] (n=397) | 82.0% [77.1%, 86.1%] (n=278) |
| GPT-5.4 | ws_cutoff | 78.2% [73.2%, 82.6%] (n=294) | 70.8% [66.2%, 75.1%] (n=391) | 70.6% [66.1%, 74.7%] (n=432) | 71.6% [67.2%, 75.7%] (n=423) | 78.2% [73.2%, 82.6%] (n=294) |
| GPT-5.4 | ws | 94.2% [91.0%, 96.4%] (n=295) | 91.8% [88.7%, 94.2%] (n=392) | 94.0% [91.3%, 95.9%] (n=433) | 95.3% [92.8%, 96.9%] (n=424) | 94.2% [91.0%, 96.4%] (n=295) |
| Claude Sonnet 5 | ws_cutoff | 73.3% [67.8%, 78.1%] (n=281) | 62.5% [57.7%, 67.1%] (n=403) | 64.1% [59.4%, 68.5%] (n=423) | 64.5% [59.9%, 68.9%] (n=431) | 73.3% [67.8%, 78.1%] (n=281) |
| Claude Sonnet 5 | ws | 78.1% [72.8%, 82.5%] (n=278) | 73.6% [69.1%, 77.7%] (n=398) | 73.8% [69.5%, 77.8%] (n=428) | 74.0% [69.6%, 77.9%] (n=430) | 78.1% [72.8%, 82.5%] (n=278) |
| GPT-5.6 Sol | ws_cutoff | 85.4% [80.9%, 89.0%] (n=294) | 79.5% [75.3%, 83.2%] (n=391) | 80.8% [76.8%, 84.2%] (n=432) | 82.0% [78.1%, 85.4%] (n=423) | 85.4% [80.9%, 89.0%] (n=294) |
| GPT-5.6 Sol | ws | 89.2% [85.1%, 92.2%] (n=295) | 83.9% [80.0%, 87.2%] (n=392) | 85.7% [82.1%, 88.7%] (n=433) | 86.8% [83.2%, 89.7%] (n=424) | 89.2% [85.1%, 92.2%] (n=295) |

## By domain

| model | condition | Artificial Intelligence | Biology | Chemistry | Environmental Science | Materials Science | Medicine | Neuroscience | Other | Physics |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | ws_cutoff | 2.5% [0.9%, 7.1%] (n=120) | 38.8% [30.8%, 47.4%] (n=129) | 52.4% [32.4%, 71.7%] (n=21) | 28.0% [14.3%, 47.6%] (n=25) | 30.8% [18.6%, 46.4%] (n=39) | 13.2% [7.3%, 22.6%] (n=76) | 16.7% [8.3%, 30.6%] (n=42) | 57.1% [25.0%, 84.2%] (n=7) | 50.0% [34.8%, 65.2%] (n=38) |
| GPT-4o | ws | 76.7% [68.3%, 83.3%] (n=120) | 90.0% [83.6%, 94.1%] (n=130) | 100.0% [84.5%, 100.0%] (n=21) | 92.0% [75.0%, 97.8%] (n=25) | 97.4% [86.8%, 99.5%] (n=39) | 84.2% [74.4%, 90.7%] (n=76) | 92.9% [81.0%, 97.5%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 97.4% [86.5%, 99.5%] (n=38) |
| LLaMA 3.3 70B | ws_cutoff | 2.5% [0.9%, 7.1%] (n=120) | 30.2% [23.0%, 38.6%] (n=129) | 47.6% [28.3%, 67.6%] (n=21) | 24.0% [11.5%, 43.4%] (n=25) | 17.9% [9.0%, 32.7%] (n=39) | 17.3% [10.4%, 27.4%] (n=75) | 14.3% [6.7%, 27.8%] (n=42) | 14.3% [2.6%, 51.3%] (n=7) | 36.8% [23.4%, 52.7%] (n=38) |
| DeepSeek R1 | ws_cutoff | 8.2% [4.2%, 15.4%] (n=97) | 54.5% [44.8%, 63.8%] (n=101) | 23.5% [9.6%, 47.3%] (n=17) | 35.3% [17.3%, 58.7%] (n=17) | 33.3% [19.8%, 50.4%] (n=33) | 28.1% [18.6%, 40.1%] (n=64) | 34.4% [20.4%, 51.7%] (n=32) | 66.7% [30.0%, 90.3%] (n=6) | 75.9% [57.9%, 87.8%] (n=29) |
| DeepSeek R1 | ws | 64.5% [54.4%, 73.5%] (n=93) | 90.7% [83.8%, 94.9%] (n=108) | 93.8% [71.7%, 98.9%] (n=16) | 81.0% [60.0%, 92.3%] (n=21) | 78.6% [60.5%, 89.8%] (n=28) | 76.9% [65.4%, 85.5%] (n=65) | 90.3% [75.1%, 96.7%] (n=31) | 100.0% [61.0%, 100.0%] (n=6) | 91.2% [77.0%, 97.0%] (n=34) |
| Claude S4.5 | ws_cutoff | 29.2% [21.8%, 37.8%] (n=120) | 64.9% [55.8%, 73.1%] (n=114) | 57.1% [36.5%, 75.5%] (n=21) | 50.0% [31.4%, 68.6%] (n=24) | 52.6% [37.3%, 67.5%] (n=38) | 40.3% [29.0%, 52.7%] (n=62) | 41.0% [27.1%, 56.6%] (n=39) | 71.4% [35.9%, 91.8%] (n=7) | 81.6% [66.6%, 90.8%] (n=38) |
| Claude S4.5 | ws | 63.0% [54.1%, 71.2%] (n=119) | 92.1% [85.7%, 95.8%] (n=114) | 76.2% [54.9%, 89.4%] (n=21) | 83.3% [64.1%, 93.3%] (n=24) | 73.7% [58.0%, 85.0%] (n=38) | 80.6% [69.1%, 88.6%] (n=62) | 89.7% [76.4%, 95.9%] (n=39) | 100.0% [64.6%, 100.0%] (n=7) | 89.5% [75.9%, 95.8%] (n=38) |
| GPT-5.4 | ws_cutoff | 55.8% [46.9%, 64.4%] (n=120) | 81.4% [73.8%, 87.2%] (n=129) | 71.4% [50.0%, 86.2%] (n=21) | 60.0% [40.7%, 76.6%] (n=25) | 71.8% [56.2%, 83.5%] (n=39) | 61.8% [50.6%, 71.9%] (n=76) | 78.6% [64.1%, 88.3%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 86.8% [72.7%, 94.2%] (n=38) |
| GPT-5.4 | ws | 85.0% [77.5%, 90.3%] (n=120) | 95.4% [90.3%, 97.9%] (n=130) | 100.0% [84.5%, 100.0%] (n=21) | 84.0% [65.3%, 93.6%] (n=25) | 94.9% [83.1%, 98.6%] (n=39) | 97.4% [90.9%, 99.3%] (n=76) | 97.6% [87.7%, 99.6%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |
| Claude Sonnet 5 | ws_cutoff | 56.6% [47.7%, 65.0%] (n=122) | 73.6% [65.1%, 80.6%] (n=121) | 54.5% [34.7%, 73.1%] (n=22) | 71.4% [52.9%, 84.7%] (n=28) | 56.5% [42.2%, 69.8%] (n=46) | 51.5% [39.8%, 62.9%] (n=68) | 68.3% [53.0%, 80.4%] (n=41) | 54.5% [28.0%, 78.7%] (n=11) | 82.5% [68.0%, 91.3%] (n=40) |
| Claude Sonnet 5 | ws | 59.2% [50.2%, 67.5%] (n=120) | 79.3% [71.3%, 85.6%] (n=121) | 66.7% [45.4%, 82.8%] (n=21) | 88.9% [71.9%, 96.1%] (n=27) | 69.0% [54.0%, 80.9%] (n=42) | 76.7% [65.8%, 84.9%] (n=73) | 75.6% [60.7%, 86.2%] (n=41) | 63.6% [35.4%, 84.8%] (n=11) | 88.9% [76.5%, 95.2%] (n=45) |
| GPT-5.6 Sol | ws_cutoff | 69.2% [60.4%, 76.7%] (n=120) | 88.4% [81.7%, 92.8%] (n=129) | 81.0% [60.0%, 92.3%] (n=21) | 84.0% [65.3%, 93.6%] (n=25) | 84.6% [70.3%, 92.8%] (n=39) | 72.4% [61.4%, 81.2%] (n=76) | 83.3% [69.4%, 91.7%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |
| GPT-5.6 Sol | ws | 80.0% [72.0%, 86.2%] (n=120) | 86.9% [80.1%, 91.7%] (n=130) | 81.0% [60.0%, 92.3%] (n=21) | 88.0% [70.0%, 95.8%] (n=25) | 82.1% [67.3%, 91.0%] (n=39) | 82.9% [72.9%, 89.7%] (n=76) | 88.1% [75.0%, 94.8%] (n=42) | 100.0% [64.6%, 100.0%] (n=7) | 94.7% [82.7%, 98.5%] (n=38) |

## WS+Cutoff runs: split by whether the event predates the model's cutoff (post-cutoff inclusion is leakage through the date filter)

| model | pre-cutoff: judge INCLUDED | pre-cutoff: URL match | post-cutoff: judge INCLUDED | post-cutoff: judge match confirmed in stored list | post-cutoff: URL match | post-cutoff: matched domain (top) |
|---|---|---|---|---|---|---|
| GPT-4o | — | — | 24.7% [21.2%, 28.7%] (n=497) | 9.1% [6.8%, 11.9%] (n=497) | 0.0% [0.0%, 0.8%] (n=497) | researchgate.net 107, biorxiv.org 4, researchsquare.com 3 |
| LLaMA 3.3 70B | — | — | 20.0% [16.7%, 23.7%] (n=496) | 19.2% [15.9%, 22.8%] (n=496) | 0.0% [0.0%, 0.8%] (n=496) | researchgate.net 80, sciencedirect.com 4, biorxiv.org 3 |
| DeepSeek R1 | 71.3% [61.8%, 79.2%] (n=101) | 28.7% [20.8%, 38.2%] (n=101) | 22.7% [18.3%, 27.8%] (n=295) | 11.2% [8.1%, 15.3%] (n=295) | 0.0% [0.0%, 1.3%] (n=295) | researchgate.net 52, biorxiv.org 3, pubmed.ncbi.nlm.nih.gov 2 |
| Claude S4.5 | 80.4% [74.3%, 85.3%] (n=199) | 46.2% [39.4%, 53.2%] (n=199) | 26.5% [21.6%, 32.1%] (n=264) | 14.0% [10.3%, 18.7%] (n=264) | 0.0% [0.0%, 1.4%] (n=264) | researchgate.net 48, arxiv.org 8, biorxiv.org 6 |
| GPT-5.4 | 82.4% [78.3%, 86.0%] (n=376) | 54.3% [49.2%, 59.2%] (n=376) | 33.1% [25.3%, 41.8%] (n=121) | 11.6% [7.0%, 18.5%] (n=121) | 0.0% [0.0%, 3.1%] (n=121) | researchgate.net 21, biorxiv.org 6, arxiv.org 5 |
| Claude Sonnet 5 | 75.9% [71.4%, 79.8%] (n=398) | 54.8% [49.9%, 59.6%] (n=398) | 15.8% [10.0%, 24.2%] (n=101) | 15.8% [10.0%, 24.2%] (n=101) | 0.0% [0.0%, 3.7%] (n=101) | researchgate.net 7, biorxiv.org 4, pith.science 1 |
| GPT-5.6 Sol | 81.3% [77.7%, 84.5%] (n=493) | 55.2% [50.8%, 59.5%] (n=493) | 0.0% [0.0%, 49.0%] (n=4) | 0.0% [0.0%, 49.0%] (n=4) | 0.0% [0.0%, 49.0%] (n=4) |  |

## Where the leaked ground truth comes from (WS+Cutoff, post-cutoff events, judge INCLUDED)

| domain of matched result | cases | of which URL in stored list |
|---|---|---|
| researchgate.net | 315 | 169 |
| biorxiv.org | 26 | 18 |
| arxiv.org | 15 | 10 |
| sciencedirect.com | 10 | 6 |
| pubmed.ncbi.nlm.nih.gov | 8 | 6 |
| researchsquare.com | 7 | 5 |
| medrxiv.org | 6 | 5 |
| linkedin.com | 4 | 4 |
| discovery.researcher.life | 3 | 3 |
| huggingface.co | 3 | 1 |
| salk.edu | 3 | 1 |
| academic.oup.com | 2 | 2 |
