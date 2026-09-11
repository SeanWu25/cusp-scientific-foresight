# Paper Scrapers

Scripts that collect the candidate paper pool (metadata + abstracts) from
which CUSP items are built. Each scraper writes CSV/JSON metadata to its
working directory; scraped outputs are gitignored (only abstracts and
metadata are used downstream — no full text is redistributed).

| Script | Source | Notes |
|--------|--------|-------|
| `scrape_nature.py` | Nature (via NCBI E-utilities) | PubMed esearch/efetch |
| `scrape_nature_v3.py` | Nature (Springer Nature Meta API) | requires `SPRINGER_API_KEY` (free: https://dev.springernature.com/) |
| `scrape_nature_sub_journals.py` | Nature family journals (Crossref + Unpaywall) | set `YOUR_EMAIL` in the script for polite API usage |
| `scrape_science_magazine.py` | Science (Crossref) | set your contact email in the script |
| `scrape_cell.py` | Cell (via NCBI E-utilities) | PubMed esearch/efetch |
| `scrape_huggingface.py` | HuggingFace Daily Papers | hybrid upvote/citation ranking, top 80 per month |
| `scrape_weekly_ai/` | Weekly "top AI papers" digests | `scrape_ai_papers.py` → `get_arxiv.py` → `get_abstract.py` |
| `scrape_history.py` | Publication-date history | first-appearance dates for date-prediction tasks |
| `clean_csv.py`, `clean_date.py` | — | post-scrape cleanup (dedupe, normalise dates to YYYY-MM) |

## Pipeline

1. Run the scrapers for each venue (Nature, Science, Cell, HF papers, weekly AI digests).
2. Clean and normalise with `clean_csv.py` and `clean_date.py`.
3. Build benchmark items from the scraped pool with [`../build_dataset/`](../build_dataset/).
4. Validate generated items with [`../validate_questions/`](../validate_questions/).

Requirements: `requests`, `pandas`, `beautifulsoup4`, `tqdm`, `python-dateutil`.
Be polite to the source APIs: the scripts already rate-limit, and Crossref /
Unpaywall / NCBI ask for a contact email in requests.
