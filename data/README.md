# CUSP v2 data

| File | Events | Months | Content |
|---|---|---|---|
| [`CUSP_v2_full.jsonl`](CUSP_v2_full.jsonl) | 5,575 | Jan 2024 – Aug 2026 | Original corpus (4,760 events, identical to `CUSP_final.jsonl` on Hugging Face) followed by the extension (815 events) |
| [`CUSP_v2_extension_apr_aug_2026.jsonl`](CUSP_v2_extension_apr_aug_2026.jsonl) | 815 | Apr – Aug 2026 | Extension only |

CUSP v2 has 19,706 validated questions: 2,951 Binary, 4,305 perturbed Binary, 4,734 MCQ, 4,765 FRQ and 2,951 Date questions.

**Format.** Every record has the same fields as `CUSP_final.jsonl` on Hugging Face ([`SeanWu25/CUSP`](https://huggingface.co/datasets/SeanWu25/CUSP)): `id`, `row_index`, `publication_date`, `binary_question`, `binary_answer_key`, `binary_question_perturbed`, `binary_perturbed_answer_key`, `binary_perturbed_result`, `binary_perturbation_detail`, `mcq_question`, `mcq_choices`, `mcq_answer_key`, `frq_prompt`, `date_prediction_prompt`, `ground_truth_date`, `paper_link`, `source_abstract`, `sub_categories`, `main_area`, `source`. A field is `null` when the event has no question of that type. `row_index` counts within each part, so use `id` as the key.

**Extension.** The extension adds events published from April to August 2026 in *Nature*, *Science*, *Cell* and the Hugging Face daily papers. It was built and validated with the same pipeline as the original corpus (`scripts/scrape/`, `scripts/build_dataset/`, `scripts/validate_questions/`). As in the original corpus, `publication_date` and the question deadlines are at month level, and `publication_date` is the earliest publicly observable month of the event. The extension has no weekly-digest AI papers and no leaderboard events.

**Splitting by knowledge cutoff.** In the paper, an event is post-cutoff for a model when its `publication_date` month is after the model's cutoff month; an event in the cutoff month counts as pre-cutoff. The cutoffs of the evaluated models are in [`configs/model_settings.json`](../configs/model_settings.json).

```python
import json
rows = [json.loads(l) for l in open("data/CUSP_v2_full.jsonl")]
post = [r for r in rows if r["publication_date"][:7] > "2025-08"]   # post-cutoff events for GPT-5.4 (cutoff 2025-08)
```
