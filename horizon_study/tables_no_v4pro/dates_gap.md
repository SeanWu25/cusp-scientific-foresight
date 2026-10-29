# First-observable vs DOI/journal date

Horizon uses the FIRST-OBSERVABLE month. For the original corpus the stored `publication_date` already is the earliest date the build pipeline found (Crossref creation, bioRxiv/medRxiv, Semantic Scholar, Europe PMC); the journal date was recovered from the build-stage CSVs for 3,150 of 3,642 DOI-linked events (the other 492 fall back to the first-observable date, so their gap is recorded as 0). arXiv-linked events use the earlier of the stored month and the month in the arXiv id; their 'DOI date' is the listing month. Extension events carry both fields natively (`original_publication_date` − `first_date_found`).


## orig (n = 4760)

gap = DOI/journal month − first-observable month: mean 1.09, median 0, 90th pct 2, max 24; 63.7% zero, 8.3% ≥ 3 months.

| gap (months) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| events | 3031 | 923 | 412 | 78 | 22 | 25 | 28 | 42 | 31 | 17 | 32 | 17 | 16 | 12 | 14 | 15 | 10 | 8 | 5 | 9 | 2 | 6 | 4 | 1 |

| source | n | mean gap | share zero | p90 |
|---|---|---|---|---|
| cell | 492 | 0.00 | 100.0% | 0 |
| hugging_face_top_ai_papers | 763 | 0.10 | 90.0% | 0 |
| leaderboard_questions | 59 | 0.00 | 100.0% | 0 |
| nature | 2111 | 1.85 | 32.0% | 3 |
| science | 1039 | 1.03 | 87.9% | 3 |
| top_ai_papers | 296 | 0.39 | 68.9% | 1 |

## ext (n = 815)

gap = DOI/journal month − first-observable month: mean 0.47, median 0, 90th pct 2, max 3; 67.4% zero, 1.1% ≥ 3 months.

| gap (months) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| events | 549 | 156 | 101 | 9 |

| source | n | mean gap | share zero | p90 |
|---|---|---|---|---|
| cell | 92 | 1.00 | 35.9% | 2 |
| hugging_face_top_ai_papers | 131 | 0.01 | 99.2% | 0 |
| nature | 382 | 0.76 | 46.3% | 2 |
| science | 210 | 0.01 | 99.5% | 0 |
