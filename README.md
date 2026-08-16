# Forecasting Scientific Progress with Artificial Intelligence

**CUSP** is a benchmark for evaluating whether AI systems can forecast scientific progress under historical knowledge cutoffs.

> **Paper:** Coming soon  
> **Dataset:** [huggingface.co/datasets/SeanWu25/CUSP](https://huggingface.co/datasets/SeanWu25/CUSP)

<img width="7252" height="3866" alt="CUSP_Fig_1 (1)" src="https://github.com/user-attachments/assets/e2c9cb9d-e526-4a52-bbf9-4df4fac53951" />

## Load the Dataset

```python
from huggingface_hub import hf_hub_download
import json

path = hf_hub_download(
    repo_id="SeanWu25/CUSP",
    filename="CUSP_final.jsonl",
    repo_type="dataset",
)
with open(path) as f:
    records = [json.loads(line) for line in f if line.strip()]

print(f"Loaded {len(records)} items")
print(list(records[0].keys()))
```

Or via the `datasets` library:

```python
from datasets import load_dataset
ds = load_dataset("SeanWu25/CUSP", data_files="CUSP_final.jsonl", split="train")
```

## Quickstart Notebook

```bash
git clone https://github.com/SeanWu25/cusp-scientific-foresight.git
cd cusp-scientific-foresight
pip install -r requirements.txt
jupyter notebook notebooks/quickstart.ipynb
```

## Evaluate a Model

Both scripts automatically download the dataset from HuggingFace if no path is given.

```bash
# Step 1: generate predictions (dataset auto-downloaded)
python scripts/test_LLM.py --model gpt-4o --output predictions.jsonl

# Step 2: evaluate with LLM judge
python scripts/eval.py --predictions predictions.jsonl --output report.json --pretty
```

Set `OPENAI_API_KEY` or `AZURE_OPENAI_KEY` in your environment or a `.env` file.

## Reproduce Paper Figures & Tables

The analysis and visualization code lives in [`run_evaluation/`](run_evaluation/):

```bash
# Multi-model comparison figures (leaderboard, radars, bias, calibration, ...)
python run_evaluation/compare_models.py --results results/ --benchmark CUSP_final.jsonl

# Publication LaTeX tables
python run_evaluation/make_latex_tables.py --results results/ --benchmark CUSP_final.jsonl

# Web-search ablation figures and tables
python run_evaluation/compare_web_search.py
```

See [`run_evaluation/README.md`](run_evaluation/README.md) for details on each script and its outputs.

## Task Types

| Task | Description | Scoring |
|------|-------------|---------|
| Binary | Yes/No — did this finding occur? | Exact match |
| Perturbed Binary | Negated version — probes response bias | Exact match |
| MCQ | 4-choice question about the outcome | Exact match |
| FRQ | Open-ended forecasting prompt | LLM judge (0–10) |
| Date Prediction | Predict the publication month | exp(−0.1·\|Δmonths\|) |

## Citation

```bibtex
@misc{cusp2026,
  title   = {CUSP: Cutoff-conditioned Unseen Scientific Progress},
  author  = {Wu, Sean and Lu, Pan and Chen, Yupeng and Bragg, Jonathan and
             Yamada, Yutaro and Clifton, David and Torr, Philip and
             Zou, James and Yu, Junchi},
  year    = {2026},
  note    = {Preprint}
}
```

## License

MIT
