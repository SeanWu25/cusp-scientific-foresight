# Question Validation

Quality-control scripts run on generated benchmark items before they enter
the final dataset. The `check_*` scripts use an LLM verifier (Azure OpenAI —
set `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`
in `.env`) to flag malformed or leaky items per task type.

| Script | Checks |
|--------|--------|
| `check_binary.py` | Binary (yes/no) items |
| `check_mcq.py` | Multiple-choice items |
| `check_frq.py` | Free-response items |
| `check_date_pred.py` | Date-prediction items |
| `merge_cusp.py` | Merge validated per-task files into the final benchmark JSONL |
| `cusp_statistics.py` | Summary statistics of the final dataset |
