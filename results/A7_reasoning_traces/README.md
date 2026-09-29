# A7 — analysis of the models' stated reasoning (Reviewer 2, concern C5)

Why do the failures occur? Every CUSP prompt asks the model to return a 1-2 sentence justification
alongside its answer. This study codes those justifications against a 16-code scheme and links the
codes to outcomes. The traces are **post-hoc stated justifications, not chains of thought**: no
provider-native thinking text was stored for any model in the panel (Step 0, `inventory.md`).

    inventory.md         Step 0: what reasoning text exists, per model/task/condition
    traces.jsonl         master table, one record per model x condition x task x event (234k)
    codebook.md          16 codes, definitions, positive and negative examples
    coding_sample.json   the frozen stratified sample that was coded (seed 13)
    raw/<coder>.jsonl    stored coder output, resumable, one record per trace
    coded_traces.jsonl   one record per trace per code per coder, with justifying spans
    agreement.md         Cohen's kappa per code and the reliability gate
    analyses/A..G/       one directory per analysis, each with results.md
    examples/            14 curated boxes, markdown and LaTeX
    tables/, figures/    manuscript-ready outputs
    human_validation.csv 2,149 rows for three annotators (built, not run)
    response_A7.md       the reviewer response
    MANIFEST.json        coders, snapshots, seeds, costs, prompt hashes, git SHA

`traces.jsonl` (364 MB) and `coded_traces.jsonl` (172 MB) are gitignored: both regenerate in seconds
from the benchmark JSONL and from `raw/`, which is the only irreplaceable artifact here and is committed.

Regenerate everything downstream of `raw/` with `bash results/A7_reasoning_traces/run_all.sh`.
Coding (only if `raw/` is lost): `python scripts/a7_code.py --coder haiku45` and
`--coder gpt54mini_low`, then `--coder haiku45 --faithfulness`.

**Blinding.** Coders never see the answer, whether it was correct, the model's identity or the
condition. Enforced by template reconstruction and an identity scan in `scripts/a7_prompts.py`;
tested by `scripts/a7_test_blinding.py`, which must pass before any analysis runs.
