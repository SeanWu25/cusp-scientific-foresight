#!/usr/bin/env python3
"""
CUSP binary / perturbed-binary validator using Azure OpenAI (grok-3).

This script reads a JSONL benchmark file, runs three independent LLM judge calls,
and writes:
  1. a full JSONL with per-row judgments
  2. a cleaned JSONL where only the bad field(s) are removed
  3. a removal-log JSONL describing what was removed from each row

Behavior:
  - Faithfulness judge checks whether the binary statement matches the abstract.
    IMPORTANT: do NOT judge the date here; the date is generated externally.
  - Verifiability judge checks whether the binary question is concrete / non-vague.
  - Perturbation judge checks whether the perturbed binary is genuinely perturbed.
  - If the binary statement fails faithfulness or verifiability, remove only the
    binary fields.
  - If the perturbed question fails, remove only the perturbed fields.
  - The rest of the row is kept intact.

Environment (.env):
  AZURE_OPENAI_ENDPOINT=https://bascolm.services.ai.azure.com/openai/v1/
  AZURE_OPENAI_API_KEY=...
  AZURE_OPENAI_DEPLOYMENT=grok-3

Usage:
  python validate_binary_questions.py \
    --input /mnt/data/CUSP_with_other_2024_onwards.jsonl \
    --output /mnt/data/cusp.binary_judged.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple
from tqdm import tqdm

from dotenv import load_dotenv
import openai
from openai import OpenAI


# ============================================================
# Environment / client
# ============================================================

load_dotenv()

from dotenv import load_dotenv
load_dotenv()  # auto-discovers .env from cwd or repo root

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not AZURE_OPENAI_ENDPOINT:
    raise RuntimeError("Missing AZURE_OPENAI_ENDPOINT in .env")
if not AZURE_OPENAI_API_KEY:
    raise RuntimeError("Missing AZURE_OPENAI_API_KEY in .env")

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)


# ============================================================
# Prompt templates
# ============================================================

FAITHFULNESS_SYSTEM_PROMPT = """You are a careful scientific benchmark validator.
Your task is to judge whether a binary forecasting statement is faithful to the source abstract/result text.
Use only the supplied text. Do not use outside knowledge.

What you are checking:
- whether the binary statement preserves the same scientific claim as the abstract/result text
- whether it changes a number, entity, benchmark, condition, threshold, scope, or outcome
- whether it introduces a claim not supported by the source

Important rules:
- Judge ONLY the binary statement itself.
- Do NOT judge the date / time wording. The date is generated externally and should be ignored here.
- Pass if the statement is a faithful restatement of the source claim.
- Fail if the statement changes the meaning or invents unsupported details.
- Be strict about the claim, but do not penalize the externally inserted date.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "mismatch_types": ["numbers", "entity", "condition", "outcome", "time", "scope", "threshold", "none"]
}

Scoring guide:
- 5 = exact or nearly exact match to the source claim
- 4 = minor wording differences, but still faithful
- 3 = partially faithful / borderline
- 2 = mostly unsupported or meaningfully altered
- 1 = clearly unfaithful
"""

VERIFIABILITY_SYSTEM_PROMPT = """You are a careful scientific benchmark validator.
Your task is to judge whether the binary statement is concrete enough to be objectively verified.
Use only the supplied text. Do not use outside knowledge.

This is NOT a writing-quality check.
A sentence can sound fine and still fail if the underlying claim is vague.

What you are checking:
- whether the statement describes a concrete scientific claim
- whether a third party could decide yes/no without guessing
- whether the claim is vague, underspecified, or too interpretive

Important rules:
- Judge the claim as a whole.
- Do NOT reject simply because the wording uses comparison language.
- Reject only if the comparison or claim is not operationalized enough to be checked.
- Pass if the claim is specific enough to be objectively verifiable from the source.
- Fail if it is vague like "better", "good", "strong", "effective", or "comparable" without a clear measurable criterion.

Examples of FAIL:
- "achieves performance comparable to OpenAI-o1-1217 on reasoning tasks" when the source does not define how comparability is measured
- "improves performance" with no metric, benchmark, or threshold
- "better than previous methods" with no objective criterion

Examples of PASS:
- "achieves 72.4% accuracy on MMLU"
- "improves F1 from 81.2 to 84.0 on the stated benchmark"
- "reduces error rate by 20% under the specified evaluation protocol"

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation"
}

Scoring guide:
- 5 = fully specific, objective, and easy to verify
- 4 = mostly specific with minor ambiguity
- 3 = borderline / partly testable
- 2 = mostly vague or underspecified
- 1 = not objectively verifiable
"""

PERTURBATION_SYSTEM_PROMPT = """You are a careful scientific benchmark validator.
Your task is to judge whether the perturbed binary question is a genuine perturbation.
Use only the supplied text. Do not use outside knowledge.

What you are checking:
- whether the perturbed question changes a salient detail from the original question
- whether that change meaningfully breaks support from the source abstract/result text
- whether the perturbed question is not merely a paraphrase or trivial rewording

Important rules:
- Pass only if the perturbation changes a meaningful aspect such as number, threshold, entity, outcome, time, scope, or condition.
- Pass only if the perturbed version is no longer directly supported by the source.
- Fail if it is basically the same question with cosmetic wording changes.
- Fail if it does not introduce a real challenge to the source claim.

Return ONLY valid JSON with this schema:
{
  "verdict": "pass|fail|unclear",
  "score": 1-5,
  "reason": "short explanation",
  "changed_elements": ["numbers", "entity", "condition", "outcome", "time", "scope", "threshold", "none"]
}

Scoring guide:
- 5 = strong, clearly altered perturbation
- 4 = valid perturbation with minor ambiguity
- 3 = borderline / weak perturbation
- 2 = likely not a real perturbation
- 1 = clearly not perturbed
"""


# ============================================================
# CLI
# ============================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge and clean binary benchmark items.")
    parser.add_argument("--input", required=True, help="Input JSONL benchmark file")
    parser.add_argument("--output", required=True, help="Base output path for judged file")
    parser.add_argument("--model", default=AZURE_OPENAI_DEPLOYMENT, help="Azure deployment name")
    parser.add_argument("--max-rows", type=int, default=0, help="Process at most N rows (0 = all)")
    parser.add_argument("--sleep", type=float, default=0.0, help="Optional sleep between rows")
    parser.add_argument("--write-stats", action="store_true", help="Write summary stats JSON")
    return parser.parse_args()


# ============================================================
# Helpers
# ============================================================


def make_base_name(path: str) -> str:
    return path[:-6] if path.endswith(".jsonl") else path


def output_paths(base_output: str) -> Tuple[str, str, str, str]:
    base = make_base_name(base_output)
    full_path = base + ".full.jsonl"
    cleaned_path = base + ".cleaned.jsonl"
    removed_path = base + ".removed.jsonl"
    stats_path = base + ".stats.json"
    return full_path, cleaned_path, removed_path, stats_path


def compact_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def parse_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        obj = json.loads(text[start : end + 1])
        if isinstance(obj, dict):
            return obj
    raise ValueError(f"Model returned invalid JSON: {text[:500]}")


def normalize_verdict(obj: Dict[str, Any], task: str) -> Dict[str, Any]:
    verdict = str(obj.get("verdict", "unclear")).strip().lower()
    if verdict not in {"pass", "fail", "unclear"}:
        verdict = "unclear"

    try:
        score = max(1, min(5, int(obj.get("score", 3))))
    except Exception:
        score = 3

    reason = compact_text(obj.get("reason", ""))

    out: Dict[str, Any] = {
        "verdict": verdict,
        "score": score,
        "reason": reason,
    }
    if task == "faithfulness":
        mts = obj.get("mismatch_types", [])
        out["mismatch_types"] = mts if isinstance(mts, list) else []
    if task == "perturbation":
        ces = obj.get("changed_elements", [])
        out["changed_elements"] = ces if isinstance(ces, list) else []
    return out


def build_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": compact_text(row.get("id", "")),
        "row_index": row.get("row_index"),
        "publication_date": compact_text(row.get("publication_date", "")),
        "main_area": compact_text(row.get("main_area", "")),
        "sub_categories": row.get("sub_categories", []),
        "source": compact_text(row.get("source", "")),
        "paper_link": compact_text(row.get("paper_link", "")),
        "source_abstract": compact_text(row.get("source_abstract", "")),
        "results_and_metrics": compact_text(row.get("results_and_metrics", "")),
        "binary_question": compact_text(row.get("binary_question", "")),
        "binary_question_perturbed": compact_text(row.get("binary_question_perturbed", "")),
        "binary_perturbation_detail": compact_text(row.get("binary_perturbation_detail", "")),
        "binary_perturbed_result": compact_text(row.get("binary_perturbed_result", "")),
    }


# ============================================================
# Prompt builders
# ============================================================


def prompt_for(task: str, row: Dict[str, Any]) -> List[Dict[str, str]]:
    payload = build_payload(row)

    if task == "faithfulness":
        system = FAITHFULNESS_SYSTEM_PROMPT
        user = f"""
Evaluate faithfulness only.

SOURCE ABSTRACT / RESULT TEXT:
{payload['source_abstract']}

BINARY QUESTION:
{payload['binary_question']}

Reminder: ignore the date portion entirely. Judge only the scientific claim.
Return JSON only.
"""
    elif task == "verifiability":
        system = VERIFIABILITY_SYSTEM_PROMPT
        user = f"""
Evaluate verifiability only.

SOURCE ABSTRACT / RESULT TEXT:
{payload['source_abstract']}

BINARY QUESTION:
{payload['binary_question']}

Return JSON only.
"""
    elif task == "perturbation":
        system = PERTURBATION_SYSTEM_PROMPT
        user = f"""
Evaluate perturbation only.

ORIGINAL QUESTION:
{payload['binary_question']}

PERTURBED QUESTION:
{payload['binary_question_perturbed']}

SOURCE ABSTRACT / RESULT TEXT:
{payload['source_abstract']}

PERTURBATION DETAIL:
{payload['binary_perturbation_detail']}

Return JSON only.
"""
    else:
        raise ValueError(f"Unknown task: {task}")

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# ============================================================
# LLM call
# ============================================================


def call_judge(task: str, row: Dict[str, Any], model: str, retries: int = 3) -> Dict[str, Any]:
    messages = prompt_for(task, row)
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            print(content)
            parsed = parse_json_object(content)
            return normalize_verdict(parsed, task)
        except openai.BadRequestError as e:
            if getattr(e, 'code', None) == 'content_filter' or getattr(getattr(e, 'error', None), 'code', None) == 'content_filter' or 'content management policy' in str(e):
                print(f"\n[{task}] Content filter triggered. Returning unclear.", file=sys.stderr)
                return normalize_verdict({"verdict": "unclear", "score": 1, "reason": "Content filter triggered"}, task)
            last_error = e
            if attempt < retries:
                time.sleep(1.5 * attempt)
            else:
                print(f"\n[{task}] judge failed after {retries} attempts: {e}. Returning unclear.", file=sys.stderr)
                return normalize_verdict({"verdict": "unclear", "score": 1, "reason": f"Error: {e}"}, task)
        except Exception as e:
            last_error = e
            if attempt < retries:
                time.sleep(1.5 * attempt)
            else:
                print(f"\n[{task}] judge failed after {retries} attempts: {e}. Returning unclear.", file=sys.stderr)
                return normalize_verdict({"verdict": "unclear", "score": 1, "reason": f"Error: {e}"}, task)

    return normalize_verdict({"verdict": "unclear", "score": 1, "reason": f"Unexpected error: {last_error}"}, task)


# ============================================================
# Cleaning logic
# ============================================================


def field_removals(faithfulness: Dict[str, Any], verifiability: Dict[str, Any], perturbation: Dict[str, Any]) -> List[str]:
    removed: List[str] = []

    if faithfulness.get("verdict") != "pass" or verifiability.get("verdict") != "pass":
        removed.append("binary_question")

    if perturbation.get("verdict") != "pass":
        removed.extend(["binary_question_perturbed", "binary_perturbation_detail", "binary_perturbed_result"])

    seen = set()
    ordered: List[str] = []
    for field in removed:
        if field not in seen:
            ordered.append(field)
            seen.add(field)
    return ordered


def cleaned_row(row: Dict[str, Any], removed_fields: List[str]) -> Dict[str, Any]:
    out = dict(row)
    for field in removed_fields:
        out.pop(field, None)
    out["removed_fields"] = removed_fields
    return out


# ============================================================
# Main processing
# ============================================================


def process(input_path: str, output_base: str, model: str, max_rows: int, sleep_s: float, write_stats: bool) -> None:
    full_path, cleaned_path, removed_path, stats_path = output_paths(output_base)

    accepted = 0
    rejected = 0
    total = 0

    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)

    already_processed = 0
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                already_processed += 1
                try:
                    obj = json.loads(line)
                    overall = obj.get("binary_llm_judge", {}).get("overall_verdict")
                    if overall == "accept":
                        accepted += 1
                    else:
                        rejected += 1
                except:
                    pass
        total = already_processed
        print(f"Resuming from line {already_processed} (accepted={accepted}, rejected={rejected})")

    mode = "a" if already_processed > 0 else "w"

    # Count lines for progress bar
    try:
        total_lines = sum(1 for _ in open(input_path, "r", encoding="utf-8"))
    except Exception:
        total_lines = None

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(full_path, mode, encoding="utf-8") as f_full, \
         open(cleaned_path, mode, encoding="utf-8") as f_clean, \
         open(removed_path, mode, encoding="utf-8") as f_removed:

        if already_processed > 0:
            for _ in range(already_processed):
                next(fin, None)

        iterator = fin if total_lines is None else tqdm(fin, total=total_lines, initial=already_processed, desc="Validating")

        for line in iterator:
            if max_rows and total >= max_rows:
                break

            line = line.strip()
            if not line:
                continue

            row = json.loads(line)

            faithfulness = call_judge("faithfulness", row, model=model)
            verifiability = call_judge("verifiability", row, model=model)
            perturbation = call_judge("perturbation", row, model=model)

            overall = "accept" if (
                faithfulness["verdict"] == "pass"
                and verifiability["verdict"] == "pass"
                and perturbation["verdict"] == "pass"
            ) else "reject"

            judge = {
                "faithfulness": faithfulness,
                "verifiability": verifiability,
                "perturbation": perturbation,
                "overall_verdict": overall,
            }

            enriched = dict(row)
            enriched["binary_llm_judge"] = judge

            removed_fields = field_removals(faithfulness, verifiability, perturbation)
            cleaned = cleaned_row(enriched, removed_fields)

            f_full.write(json.dumps(enriched, ensure_ascii=False) + "\n")
            f_clean.write(json.dumps(cleaned, ensure_ascii=False) + "\n")

            removed_record = {
                "id": row.get("id"),
                "row_index": row.get("row_index"),
                "overall_verdict": overall,
                "removed_fields": removed_fields,
                "faithfulness_verdict": faithfulness["verdict"],
                "verifiability_verdict": verifiability["verdict"],
                "perturbation_verdict": perturbation["verdict"],
            }
            f_removed.write(json.dumps(removed_record, ensure_ascii=False) + "\n")

            if overall == "accept":
                accepted += 1
            else:
                rejected += 1

            total += 1
            if total % 20 == 0 and total_lines is None:
                print(f"Processed {total} rows | accepted={accepted} | rejected={rejected}")

            if sleep_s > 0:
                time.sleep(sleep_s)

    print("Done")
    print(f"Full file:    {full_path}")
    print(f"Cleaned file: {cleaned_path}")
    print(f"Removed log:   {removed_path}")
    print(f"Accepted: {accepted}")
    print(f"Rejected: {rejected}")

    if write_stats:
        stats = {
            "input": input_path,
            "full_output": full_path,
            "cleaned_output": cleaned_path,
            "removed_log": removed_path,
            "model": model,
            "processed_rows": total,
            "accepted_rows": accepted,
            "rejected_rows": rejected,
            "accept_rate": (accepted / total) if total else None,
        }
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"Stats file:   {stats_path}")


# ============================================================
# Entry point
# ============================================================


def main() -> int:
    args = parse_args()
    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    process(
        input_path=args.input,
        output_base=args.output,
        model=args.model,
        max_rows=args.max_rows,
        sleep_s=args.sleep,
        write_stats=args.write_stats,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
