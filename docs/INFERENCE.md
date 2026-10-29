# Reproducing model inference on CUSP

This page is the entry point for running a language model on CUSP with the protocol of the paper, and for scoring its answers.
The pipeline has three steps: **inference** (`scripts/run_cusp.py`), **FRQ judging** (`scripts/judge_frq.py`) and **scoring** (`scripts/build_report.py`).

| Step | Script | What it does |
|---|---|---|
| 1. Inference | [`scripts/run_cusp.py`](../scripts/run_cusp.py) | Sends the five CUSP task prompts (Binary, perturbed Binary, MCQ, FRQ, Date) for each event to one model and writes one JSONL record per event |
| — | [`scripts/test_LLM.py`](../scripts/test_LLM.py) | Model API wrappers (OpenAI, Azure OpenAI, Azure AI Foundry, Anthropic, local Hugging Face Transformers), the task system prompts and the response parser. `run_cusp.py` imports them unchanged. `test_LLM.py` is also the serial harness of the original six-model runs |
| — | [`scripts/web_search.py`](../scripts/web_search.py) | Retrieval for the WS+Cutoff and WS conditions (You.com Search API, one query per event, optional date ceiling) |
| 2. FRQ judging | [`scripts/judge_frq.py`](../scripts/judge_frq.py) | Two-stage FRQ judge: stage 1 leakage check with web search, stage 2 rubric (alignment, specificity, novelty, feasibility, 0–10) |
| 3. Scoring | [`scripts/build_report.py`](../scripts/build_report.py) | Scores Binary, MCQ and Date deterministically, adds the FRQ judgements and writes the report JSON that the analysis scripts read |
| — | [`scripts/eval.py`](../scripts/eval.py), [`scripts/scoring_v1.py`](../scripts/scoring_v1.py) | The graders and judge prompts. `scoring_v1.py` checks that the graders in `eval.py` are byte-identical to the released version |

## 1. Setup

```bash
git clone https://github.com/SeanWu25/cusp-scientific-foresight.git
cd cusp-scientific-foresight
pip install -r requirements.txt
cp .env.example .env        # fill in only the keys for the services you use
```

The benchmark file is `CUSP_final.jsonl` on Hugging Face ([`SeanWu25/CUSP`](https://huggingface.co/datasets/SeanWu25/CUSP)).
`judge_frq.py` and `build_report.py` download it automatically when you do not give `--benchmark`.
For `run_cusp.py`, download it once and pass the path with `--input`:

```bash
python -c "from huggingface_hub import hf_hub_download as d; print(d('SeanWu25/CUSP','CUSP_final.jsonl',repo_type='dataset'))"
```

## 2. Run inference

General form:

```bash
python scripts/run_cusp.py \
  --input CUSP_final.jsonl \
  --output results/<model>/base_run1.jsonl \
  --provider <OPENAI|AZURE|AZURE_DEEPSEEK|ANTHROPIC> \
  --model <identifier> \
  --condition base \
  <decoding flags> --concurrency 8 --resume
```

The decoding flags of every model in the paper are in [`configs/model_settings.json`](../configs/model_settings.json).
Examples:

```bash
# Claude Sonnet 5 (Anthropic API)
python scripts/run_cusp.py --input CUSP_final.jsonl --output results/sonnet5/base_run1.jsonl \
  --provider ANTHROPIC --model claude-sonnet-5 --condition base \
  --effort medium --max-tokens 2048 --frq-max-tokens 384 --concurrency 8 --resume

# GPT-5.4 (OpenAI API; reasoning model, no temperature is sent when --effort is set)
python scripts/run_cusp.py --input CUSP_final.jsonl --output results/gpt54/base_run1.jsonl \
  --provider OPENAI --model gpt-5.4 --condition base \
  --effort medium --max-tokens 2048 --frq-max-tokens 2048 --concurrency 8 --resume

# GPT-OSS 20B, open weights, served locally by vLLM (OpenAI-compatible endpoint)
vllm serve openai/gpt-oss-20b --port 8000 &
OPENAI_API_BASE=http://localhost:8000/v1 OPENAI_API_KEY=EMPTY \
python scripts/run_cusp.py --input CUSP_final.jsonl --output results/gptoss20b/base_run1.jsonl \
  --provider OPENAI --model openai/gpt-oss-20b --condition base \
  --temperature 0 --max-tokens 2048 --frq-max-tokens 2048 --concurrency 16 --resume
```

Useful options: `--max-rows N` (pilot run), `--ids-file` (restrict to a list of event ids), `--run-index` (label repeated runs), `--seed` (MCQ option order; default 42, as in the paper), `--resume` (skip events already in `--output`).

### Retrieval conditions

| Condition | Flag | Retrieval |
|---|---|---|
| Base | `--condition base` | none |
| WS+Cutoff | `--condition ws_cutoff --ws-cutoff YYYY-MM` | one model-written query per event; You.com results dated before the first day of the cutoff month only |
| WS | `--condition ws` | the same query with no date limit |

Use the model's knowledge cutoff (column `cutoff` in `configs/model_settings.json`) as `--ws-cutoff`. The retrieval conditions need `YOU_API_KEY`.

### Prompts

The task system prompts are the constants `BINARY_SYSTEM`, `MCQ_SYSTEM`, `FRQ_SYSTEM`, `DATE_SYSTEM` and `FRQ_SYSTEM_WS` in [`scripts/test_LLM.py`](../scripts/test_LLM.py). Each CUSP question goes to the model as a separate user message, and all models use the same system prompt for a task. The FRQ judge prompts are in `judge_leakage` and `judge_frq_combined` in [`scripts/eval.py`](../scripts/eval.py). Supplementary Section R of the paper lists the system prompts verbatim.

### Output format

`run_cusp.py` appends one JSON record per event to `--output` (never overwritten). Each record has the event id and metadata (`paper_link`, `doi`, `arxiv_id`, `source_venue`, `main_area`, `first_observable_date`), the `model`, `effort`, `condition` and `run_index`, and, for each task `<task>` in `binary`, `binary_perturbed`, `mcq`, `frq`, `date`: the prompt sent (`<task>_prompt_sent`), the verbatim response (`<task>_raw`), the parsed answer (`<task>_answer`), the stated confidence (`<task>_confidence`), the model's reasoning field (`<task>_reasoning`), token counts, latency, retries, stop reason, and truncation and refusal flags. MCQ records also keep the option permutation (`mcq_permutation`, `mcq_shuffled_choices`, `mcq_shuffled_answer_key`). For the retrieval conditions, the record has `web_search_query` and the exact list of retrieved URLs (`web_search_urls`). The legacy field names match what `eval.py` reads.

## 3. Judge the FRQ answers

```bash
python scripts/judge_frq.py \
  --predictions results/sonnet5/base_run1.jsonl \
  --output results/sonnet5/base_run1_frq_judged.jsonl \
  --endpoint azure --stage both --concurrency 3 --resume
```

The paper's judge is GPT-5 on an Azure OpenAI deployment (`AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT`). Stage 1 needs live web search. Keep the concurrency low: when the deployment rate-limits, the script retries until the web-search path succeeds.

## 4. Score

```bash
python scripts/build_report.py \
  --predictions results/sonnet5/base_run1.jsonl \
  --judged results/sonnet5/base_run1_frq_judged.jsonl \
  --out results/sonnet5/report_base_run1.json
```

Binary and MCQ use exact match, Date uses exp(−0.1·|Δmonths|), and FRQ uses the mean of the four rubric dimensions. A refused instance is recorded as refused and excluded from the denominators (`--score-refusals-as-wrong` counts it as wrong instead). The report JSON is the input of the analysis and table scripts in [`run_evaluation/`](../run_evaluation/).

## Proprietary API access vs. open weights

| Needs a proprietary API key | Can run with open weights |
|---|---|
| GPT-4o, GPT-5.4, GPT-5.6 Sol (OpenAI) | LLaMA 3.3 70B (`meta-llama/Llama-3.3-70B-Instruct`) |
| Claude Sonnet 4.5, Claude Sonnet 5, Claude Opus 4.8 (Anthropic) | GPT-OSS 20B (`openai/gpt-oss-20b`) |
| FRQ judge (GPT-5, Azure OpenAI) | DeepSeek R1 (open weights; the paper used an Azure AI Foundry deployment that is now retired) |
| WS+Cutoff and WS retrieval (You.com Search API) | Base-condition inference and Binary/MCQ/Date scoring need no paid service when the model is open-weight |

Proprietary models can change behind a fixed identifier, and the reasoning models (Claude Sonnet 5, Claude Opus 4.8, GPT-5.6 Sol) do not accept temperature 0, so repeated runs of these models are not deterministic.
