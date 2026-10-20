"""
CUSP Benchmark Evaluator — Two-Track LLM-as-a-Judge Framework
==============================================================

Evaluates model predictions on the CUSP (Calibrated, Uncontaminated Scientific
Prediction) benchmark using a two-track architecture:

  Track 1 – Outcome Judges   : binary, perturbed-binary, MCQ, FRQ, date
  Track 2 – Reasoning Judges : leakage, mechanistic soundness, constraint awareness

Handles **sparse rows**: not every row has every task.  The evaluator detects
which tasks are present and scores only those.

Usage
-----
# Dry-run (no LLM calls, deterministic grading only):
  python eval.py \\
      --benchmark ../benchmark_data/CUSP/merged_validated_cusp.jsonl \\
      --output cusp_report.json --no-llm --pretty

# Full evaluation with LLM judges (first 50 rows):
  python eval.py \\
      --benchmark ../benchmark_data/CUSP/merged_validated_cusp.jsonl \\
      --output cusp_report.json \\
      --model gpt-4o --api-key $OPENAI_API_KEY \\
      --max-rows 50 --pretty

# With a separate predictions file:
  python eval.py \\
      --benchmark ../benchmark_data/CUSP/merged_validated_cusp.jsonl \\
      --predictions predictions.jsonl \\
      --output cusp_report.json --pretty
  
Yupeng:    
nohup python -u run_evaluation/eval.py \
      --benchmark benchmark_data/CUSP/merged_validated_cusp_fixed.jsonl \
      --predictions benchmark_logs/predictions_gpt-oss-20B_20260425_004831.jsonl \
      --output report_gpt_oss_20B_uncertainty.json --max-rows 20 --pretty  --verbose > eval.log 2>&1 &


CLI Arguments
-------------
  --benchmark   Path to the benchmark JSONL   (default: benchmark_data/CUSP/merged_validated_cusp.jsonl)
  --predictions Optional predictions JSONL keyed by 'id'
  --output      Output JSON report path       (default: cusp_eval_report.json)
  --model       Model name for the judge LLM  (default: gpt-4o)
  --api-key     OpenAI-compatible API key      (or env OPENAI_API_KEY / AZURE_OPENAI_KEY)
  --api-base    OpenAI-compatible API base URL (or env OPENAI_API_BASE / AZURE_OPENAI_ENDPOINT)
  --no-llm      Skip all LLM calls; use deterministic grading only
  --pretty      Pretty-print the JSON report
  --max-rows    Evaluate at most N rows (useful for testing)
  --verbose     Print progress to stderr

Requirements: Python 3.10+, openai (pip install openai)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Optional

try:
    from tqdm import tqdm as _tqdm
    _HAS_TQDM = True
except ImportError:
    _HAS_TQDM = False

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class JudgeVerdict:
    """Structured output from an LLM judge."""
    verdict: str = "unclear"       # "pass" | "fail" | "unclear"
    score: float = 0.0             # 0.0 – 1.0
    reason: str = ""               # short explanation
    details: dict = field(default_factory=dict)  # task-specific extras

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskResult:
    """Result of a single outcome-judge task."""
    task_type: str = ""
    verdict: str = "unclear"
    score: float = 0.0
    raw_answer: str = ""
    parsed_answer: str = ""
    ground_truth: str = ""
    correct: Optional[bool] = None
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RowResult:
    """Aggregated result for a single benchmark row."""
    id: str = ""
    joint_pass: bool = False
    outcome_pass: bool = False
    reasoning_pass: bool = False
    overall_score: float = 0.0
    tasks: dict[str, dict] = field(default_factory=dict)
    reasoning: dict[str, dict] = field(default_factory=dict)
    prediction_found: bool = False
    available_tasks: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTCOME_WEIGHT = 0.6
REASONING_WEIGHT = 0.4

TASK_FIELDS = {
    "binary": ["binary_question"],
    "binary_perturbed": ["binary_question_perturbed"],
    "mcq": ["mcq_question", "mcq_choices", "mcq_answer_key"],
    "frq": ["frq_prompt"],
    "date": ["date_prediction_prompt", "ground_truth_date"],
}

# Prediction field aliases — ordered by specificity
PREDICTION_ALIASES = {
    "binary": ["binary_answer", "binary_prediction", "binary_response"],
    "binary_perturbed": ["binary_perturbed_answer", "binary_perturbed_prediction",
                         "binary_perturbed_response"],
    "mcq": ["mcq_answer", "mcq_prediction", "mcq_response"],
    "frq": ["frq_answer", "frq_prediction", "frq_response"],
    "date": ["date_answer", "date_prediction", "date_response"],
}

GENERIC_PREDICTION_FIELDS = ["model_answer", "response", "output", "prediction"]

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="CUSP Benchmark Evaluator — Two-Track LLM-as-a-Judge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--benchmark", default="benchmark_data/CUSP/merged_validated_cusp.jsonl",
                   help="Path to benchmark JSONL file")
    p.add_argument("--predictions", default=None,
                   help="Optional predictions JSONL keyed by 'id'")
    p.add_argument("--output", default="cusp_eval_report.json",
                   help="Output JSON report path")
    p.add_argument("--model", default=None,
                   help="Model name for judge LLM (default: gpt-5.4-mini)")
    p.add_argument("--api-key", default=None,
                   help="OpenAI-compatible API key")
    p.add_argument("--api-base", default=None,
                   help="OpenAI-compatible API base URL")
    p.add_argument("--no-llm", action="store_true",
                   help="Skip all LLM calls, deterministic only")
    p.add_argument("--no-leakage", action="store_true",
                   help="Skip LLM leakage judge (use heuristic only)")
    p.add_argument("--pretty", action="store_true",
                   help="Pretty-print JSON output")
    p.add_argument("--max-rows", type=int, default=None,
                   help="Max rows to evaluate (for testing)")
    p.add_argument("--verbose", action="store_true",
                   help="Print progress to stderr")
    return p


# ---------------------------------------------------------------------------
# LLM Client
# ---------------------------------------------------------------------------

class LLMClient:
    """Thin wrapper around an OpenAI-compatible chat API."""

    def __init__(self, model: str, api_key: str | None, api_base: str | None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI, AzureOpenAI
        except ImportError:
            print("ERROR: 'openai' package is required.  pip install openai", file=sys.stderr)
            sys.exit(1)

        # Detect Azure vs standard
        is_azure = (
            self.api_base and "azure" in self.api_base.lower()
        ) or os.environ.get("AZURE_OPENAI_ENDPOINT")

        if is_azure:
            endpoint = self.api_base or os.environ.get("AZURE_OPENAI_ENDPOINT", "")
            key = self.api_key or os.environ.get("AZURE_OPENAI_KEY", "")
            api_ver = os.environ.get("AZURE_OPENAI_API_VER", "2024-12-01-preview")
            self._client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=key,
                api_version=api_ver,
            )
        else:
            self._client = OpenAI(
                api_key=self.api_key or os.environ.get("OPENAI_API_KEY", ""),
                base_url=self.api_base or os.environ.get("OPENAI_API_BASE", None),
            )
        return self._client

    def call(self, system: str, user: str, *, json_mode: bool = False,
             max_tokens: int = 1024, temperature: float = 0.0,
             retries: int = 2) -> str:
        """Send a chat completion request and return the assistant text."""
        client = self._get_client()
        kwargs: dict[str, Any] = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_err = None
        tokens_key = "max_completion_tokens"  # preferred; fall back to max_tokens
        for attempt in range(1, retries + 2):
            try:
                resp = client.chat.completions.create(**kwargs, **{tokens_key: max_tokens})
                return resp.choices[0].message.content.strip()
            except Exception as exc:
                err_str = str(exc)
                # Some models only accept max_tokens; others only max_completion_tokens
                if "max_completion_tokens" in err_str and tokens_key == "max_completion_tokens":
                    tokens_key = "max_tokens"
                    continue
                if "max_tokens" in err_str and tokens_key == "max_tokens":
                    tokens_key = "max_completion_tokens"
                    continue
                last_err = exc
                if attempt <= retries:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM call failed after {retries + 1} attempts: {last_err}")

    def call_judge(self, system: str, user: str) -> JudgeVerdict:
        """Call the LLM and parse the response as a JudgeVerdict JSON."""
        raw = self.call(system, user, json_mode=True)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown fences
            m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if m:
                obj = json.loads(m.group(1))
            else:
                return JudgeVerdict(
                    verdict="unclear", score=0.0,
                    reason=f"Could not parse LLM response as JSON: {raw[:200]}",
                )
        return JudgeVerdict(
            verdict=str(obj.get("verdict", "unclear")).lower().strip(),
            score=float(obj.get("score", 0.0)),
            reason=str(obj.get("reason", "")),
            details=obj.get("details", {}),
        )

    def _call_responses_api(
        self, system: str, user: str, retries: int = 2, tool_choice: str = "required"
    ) -> tuple[str, list[dict]]:
        """
        Call the OpenAI Responses API with the web_search tool enabled.

        Returns (response_text, web_searches) where web_searches is a list of
        dicts describing every search the model issued, e.g.:
          [{"query": "...", "queries": [...], "status": "...", "citations": [...]}]

        Uses the same endpoint/key as the regular LLM client — the Responses API
        with web_search tool is available on the same deployment.
        """
        # Use existing credentials — same key as regular calls.
        # The Responses API lives at /openai/responses on Azure endpoints, so
        # we normalise AZURE_OPENAI_ENDPOINT (designed for AzureOpenAI client)
        # by appending /openai/ so OpenAI(base_url=...) constructs the right path.
        endpoint = self.api_base or os.environ.get("AZURE_OPENAI_ENDPOINT") or os.environ.get("OPENAI_API_BASE")
        key      = self.api_key  or os.environ.get("AZURE_OPENAI_KEY")      or os.environ.get("OPENAI_API_KEY")
        model    = os.environ.get("AZURE_OPENAI_DEPLOYMENT") or self.model

        if not endpoint or not key:
            text = self.call(system, user, json_mode=False, max_tokens=1536)
            return text, []

        # Azure: https://resource.openai.azure.com/ → https://resource.openai.azure.com/openai/
        if "openai.azure.com" in endpoint and "/openai" not in endpoint:
            endpoint = endpoint.rstrip("/") + "/openai/"

        print(f"[web_search] base_url={endpoint!r} model={model!r}", file=sys.stderr)
        from openai import OpenAI
        ws_client = OpenAI(base_url=endpoint, api_key=key)

        last_err = None
        for attempt in range(1, retries + 2):
            try:
                response = ws_client.responses.create(
                    model=model,
                    tools=[{"type": "web_search"}],
                    tool_choice=tool_choice,
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                )

                # Parse output items — structure matches the Responses API:
                #   ResponseFunctionWebSearch  (type="web_search_call")
                #     .action.query     -> str
                #     .action.queries   -> list[str]
                #     .action.sources   -> list (URL objects in some API versions)
                #     .status           -> str
                #   ResponseOutputMessage (type="message")
                #     .content[].annotations -> AnnotationURLCitation
                #       .url, .title, .start_index, .end_index
                web_searches: list[dict] = []
                citations:    list[dict] = []

                for item in getattr(response, "output", []) or []:
                    item_type = getattr(item, "type", None)

                    if item_type == "web_search_call":
                        action = getattr(item, "action", None)
                        # Deep-scan the full item via model_dump() to capture any
                        # URL data the API returns (sources, results, etc.) regardless
                        # of which field name the current SDK version uses.
                        try:
                            item_dict = item.model_dump() if hasattr(item, "model_dump") else {}
                        except Exception:
                            item_dict = {}
                        source_urls = list(dict.fromkeys(_extract_urls_deep(item_dict)))

                        web_searches.append({
                            "query":        getattr(action, "query",   "") if action else "",
                            "queries":      getattr(action, "queries", []) if action else [],
                            "status":       getattr(item, "status", ""),
                            "urls_reached": source_urls,
                        })

                    elif item_type == "message":
                        for part in getattr(item, "content", []) or []:
                            for ann in getattr(part, "annotations", []) or []:
                                if getattr(ann, "type", None) == "url_citation":
                                    url = getattr(ann, "url", "")
                                    citations.append({
                                        "title":       getattr(ann, "title", ""),
                                        "url":         url,
                                        "start_index": getattr(ann, "start_index", None),
                                        "end_index":   getattr(ann, "end_index",   None),
                                    })

                # Citations come from the final message — attach to last search entry.
                if citations:
                    if web_searches:
                        entry = web_searches[-1]
                        entry["citations"] = citations
                        existing = set(entry["urls_reached"])
                        for c in citations:
                            if c["url"] and c["url"] not in existing:
                                entry["urls_reached"].append(c["url"])
                                existing.add(c["url"])
                    else:
                        web_searches.append({
                            "query": "", "queries": [], "status": "",
                            "citations":    citations,
                            "urls_reached": [c["url"] for c in citations if c["url"]],
                        })

                # Regex fallback: scan output_text for any bare https:// URLs the
                # model wrote (e.g. in its explanation before the JSON block).
                _merge_text_urls(response.output_text or "", web_searches)

                # Debug: log output_text when still no URLs found, so we can see
                # exactly what the model returned.
                if web_searches and not any(ws.get("urls_reached") for ws in web_searches):
                    print(f"[web_search] no URLs found; output_text={repr((response.output_text or '')[:400])}",
                          file=sys.stderr)

                return response.output_text, web_searches

            except Exception as exc:
                last_err = exc
                if attempt <= retries:
                    time.sleep(2 ** attempt)

        # Responses API unavailable — fall back to standard call without web search
        print(f"[web_search] Responses API failed ({last_err}), falling back to standard call",
              file=sys.stderr)
        text = self.call(system, user, json_mode=False, max_tokens=1536)
        return text, []

    def call_with_web_search(self, system: str, user: str, retries: int = 2) -> str:
        """Public wrapper that returns just the response text (searches discarded)."""
        text, _ = self._call_responses_api(system, user, retries)
        return text

    def call_judge_with_search(self, system: str, user: str,
                               tool_choice: str = "required") -> JudgeVerdict:
        """
        Call the LLM with web search enabled and parse the response as a JudgeVerdict.

        Web search queries (and any result snippets) are captured and stored in
        verdict.details["web_searches"] so they appear in the report JSON.
        verdict.details["web_search_used"] is True when real searches fired.
        """
        # Ask for prose + inline citations before the JSON so AnnotationURLCitation
        # objects are produced. Regex fallback in _call_responses_api catches any
        # URLs the model includes even without structured citation markers.
        system_json = (
            system
            + "\n\nBefore your verdict, write 1-2 sentences explaining your "
            "reasoning and cite the specific URLs you consulted using "
            "([title](url)) format. Then return your verdict as a JSON code "
            "block (```json ... ```)."
        )
        raw, web_searches = self._call_responses_api(system_json, user,
                                                     tool_choice=tool_choice)

        # Parse JSON — try fence extraction first (preferred), then raw parse
        obj: dict | None = None
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if m:
            try:
                obj = json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        if obj is None:
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                pass

        if obj is None:
            return JudgeVerdict(
                verdict="unclear", score=0.0,
                reason=f"Could not parse response as JSON: {raw[:300]}",
                details={
                    "web_searches":     web_searches,
                    "web_search_used":  bool(web_searches),
                    "raw_response":     raw[:500],
                },
            )

        details: dict = dict(obj.get("details", {}))
        details["web_searches"]    = web_searches
        details["web_search_used"] = bool(web_searches)

        return JudgeVerdict(
            verdict=str(obj.get("verdict", "unclear")).lower().strip(),
            score=float(obj.get("score", 0.0)),
            reason=str(obj.get("reason", "")),
            details=details,
        )


# ---------------------------------------------------------------------------
# Task Detection
# ---------------------------------------------------------------------------

def detect_tasks(row: dict) -> dict[str, bool]:
    """Return a map of task_name -> bool indicating which tasks the row has."""
    result = {}
    for task, required_fields in TASK_FIELDS.items():
        result[task] = all(
            row.get(f) is not None and row.get(f) != ""
            for f in required_fields
        )
    return result


# ---------------------------------------------------------------------------
# Prediction Merging
# ---------------------------------------------------------------------------

def _find_prediction_for_task(row: dict, task: str) -> str | None:
    """Find a prediction value for a specific task, checking all aliases."""
    # 1. Check in a nested "predictions" object
    preds = row.get("predictions", {})
    if isinstance(preds, dict):
        for alias in PREDICTION_ALIASES.get(task, []):
            if alias in preds and preds[alias]:
                return str(preds[alias])

    # 2. Check top-level task-specific aliases
    for alias in PREDICTION_ALIASES.get(task, []):
        if alias in row and row[alias]:
            return str(row[alias])

    # 3. Check model_reasoning / reasoning as prediction for reasoning-aware tasks
    if task in ("binary", "binary_perturbed", "mcq", "frq"):
        for gf in GENERIC_PREDICTION_FIELDS:
            if gf in preds and preds[gf]:
                return str(preds[gf])
            if gf in row and gf not in TASK_FIELDS.get(task, []):
                val = row.get(gf)
                if val:
                    return str(val)

    return None


def _get_reasoning_text(row: dict) -> str:
    """Extract the model's reasoning text from the row if available.

    Prefers per-task reasoning fields written by structured-output runs
    (binary_reasoning, mcq_reasoning, etc.) then falls back to the legacy
    combined model_reasoning blob.
    """
    per_task_keys = (
        "binary_reasoning", "binary_perturbed_reasoning",
        "mcq_reasoning", "date_reasoning",
        "frq_answer",  # FRQ full response carries the richest reasoning signal
    )
    parts = [str(row[k]) for k in per_task_keys if row.get(k)]
    if parts:
        return "\n---\n".join(parts)

    for key in ("model_reasoning", "reasoning", "chain_of_thought", "explanation"):
        val = row.get(key)
        if val:
            return str(val)
    preds = row.get("predictions", {})
    if isinstance(preds, dict):
        parts = [str(preds[k]) for k in per_task_keys if preds.get(k)]
        if parts:
            return "\n---\n".join(parts)
        for key in ("model_reasoning", "reasoning", "chain_of_thought", "explanation"):
            val = preds.get(key)
            if val:
                return str(val)
    return ""


def merge_predictions(row: dict, pred_row: dict | None) -> dict:
    """Merge a predictions record into a benchmark row (non-destructive copy)."""
    merged = dict(row)
    if pred_row is None:
        return merged

    # Copy prediction fields into the row (don't overwrite benchmark fields)
    for k, v in pred_row.items():
        if k == "id":
            continue
        if k not in merged or k in ("predictions",):
            merged[k] = v
        # If top-level alias, add it
        for task_aliases in PREDICTION_ALIASES.values():
            if k in task_aliases:
                merged[k] = v
    return merged


def load_predictions(path: str) -> dict[str, dict]:
    """Load a predictions JSONL file, keyed by 'id'."""
    preds: dict[str, dict] = {}
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                rid = obj.get("id")
                if rid is None:
                    print(f"WARNING: predictions line {lineno} has no 'id', skipping",
                          file=sys.stderr)
                    continue
                preds[str(rid)] = obj
            except json.JSONDecodeError as e:
                print(f"WARNING: predictions line {lineno} malformed JSON: {e}",
                      file=sys.stderr)
    return preds


# ---------------------------------------------------------------------------
# Track 1 — Outcome Judges
# ---------------------------------------------------------------------------

def _normalize_yes_no(text: str) -> str | None:
    """Extract a yes/no answer from free text. Returns 'yes', 'no', or None."""
    if not text:
        return None
    text_lower = text.strip().lower()

    # Check last line first (final answer pattern)
    lines = [l.strip() for l in text_lower.split("\n") if l.strip()]
    last = lines[-1] if lines else text_lower

    for candidate in [last, text_lower]:
        # Exact match
        if candidate in ("yes", "yes.", "yes!"):
            return "yes"
        if candidate in ("no", "no.", "no!"):
            return "no"
        # Pattern: "answer: yes" or "final answer: no"
        m = re.search(r"(?:final\s+)?answer\s*[:=]\s*(yes|no)\b", candidate)
        if m:
            return m.group(1)

    # Fallback: count occurrences
    yes_count = len(re.findall(r"\byes\b", text_lower))
    no_count = len(re.findall(r"\bno\b", text_lower))
    if yes_count > 0 and no_count == 0:
        return "yes"
    if no_count > 0 and yes_count == 0:
        return "no"
    # Last occurrence wins if both present
    last_yes = text_lower.rfind("yes")
    last_no = text_lower.rfind("no")
    if last_yes > last_no:
        return "yes"
    if last_no > last_yes:
        return "no"
    return None


def grade_binary(response: str, ground_truth: str = "Yes") -> dict:
    """
    Grade a binary (yes/no) prediction.

    Returns dict with: correct (bool), parsed_answer, ground_truth, score.
    """
    parsed = _normalize_yes_no(response)
    gt = _normalize_yes_no(ground_truth) or ground_truth.strip().lower()

    correct = parsed is not None and parsed == gt
    return {
        "correct": correct,
        "parsed_answer": parsed or "UNPARSEABLE",
        "ground_truth": gt,
        "score": 1.0 if correct else 0.0,
    }


def _normalize_letter(text: str) -> str | None:
    """Extract a single choice letter (A-Z) from a response."""
    if not text:
        return None
    text = text.strip()

    # Direct single letter
    if len(text) == 1 and text.upper().isalpha():
        return text.upper()

    # Patterns: "(A)", "A.", "A)", "Answer: A", etc.
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    last = lines[-1] if lines else text

    for candidate in [last, text]:
        m = re.search(
            r"(?:answer|choice|option|select)\s*[:=]?\s*\(?([A-Za-z])\)?",
            candidate, re.IGNORECASE,
        )
        if m:
            return m.group(1).upper()
        # Standalone letter with optional punctuation
        m = re.match(r"^\(?([A-Za-z])\)?[.\s]*$", candidate.strip())
        if m:
            return m.group(1).upper()

    # Final fallback — first standalone uppercase letter in parentheses
    m = re.search(r"\(([A-Z])\)", text)
    if m:
        return m.group(1)

    return None


def grade_mcq(
    response: str,
    answer_key: str | int,
    choices: list[str] | None = None,
    *,
    llm_client: Optional["LLMClient"] = None,
) -> dict:
    """
    Grade an MCQ prediction.

    answer_key: correct choice letter ("A") or 0-based index.
    choices:    the list of choice texts (optional, used for semantic fallback).

    Returns dict with: correct, parsed_answer, ground_truth, score.
    """
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Normalize ground truth
    if isinstance(answer_key, int):
        gt_letter = labels[answer_key] if answer_key < len(labels) else str(answer_key)
    else:
        gt_letter = str(answer_key).strip().upper()

    parsed = _normalize_letter(response)

    # If letter extraction worked, compare directly
    if parsed:
        correct = parsed == gt_letter
        return {
            "correct": correct,
            "parsed_answer": parsed,
            "ground_truth": gt_letter,
            "score": 1.0 if correct else 0.0,
        }

    # Semantic fallback: if we have choices, check if response text matches correct choice
    if choices and gt_letter in labels:
        idx = labels.index(gt_letter)
        if idx < len(choices):
            correct_text = choices[idx].strip().lower()
            response_lower = response.strip().lower()
            # Check if the response contains the correct choice text
            if correct_text in response_lower:
                return {
                    "correct": True,
                    "parsed_answer": f"(semantic match → {gt_letter})",
                    "ground_truth": gt_letter,
                    "score": 1.0,
                }
            # Check if any other choice matches — if so, it's wrong
            for i, ch in enumerate(choices):
                if i != idx and ch.strip().lower() in response_lower:
                    wrong_letter = labels[i]
                    return {
                        "correct": False,
                        "parsed_answer": f"(semantic match → {wrong_letter})",
                        "ground_truth": gt_letter,
                        "score": 0.0,
                    }

    # LLM semantic fallback (if client available and choices given)
    if llm_client and choices:
        try:
            verdict = _mcq_llm_fallback(llm_client, response, choices, gt_letter)
            return {
                "correct": verdict.verdict == "pass",
                "parsed_answer": verdict.details.get("extracted_answer", "LLM-judged"),
                "ground_truth": gt_letter,
                "score": verdict.score,
            }
        except Exception:
            pass  # Fall through to unparseable

    return {
        "correct": False,
        "parsed_answer": "UNPARSEABLE",
        "ground_truth": gt_letter,
        "score": 0.0,
    }


def _mcq_llm_fallback(client: LLMClient, response: str, choices: list[str],
                       gt_letter: str) -> JudgeVerdict:
    """Use the LLM to extract the intended choice from an ambiguous MCQ response."""
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    choices_str = "\n".join(f"({labels[i]}) {c}" for i, c in enumerate(choices))
    system = (
        "You are an answer-extraction assistant. Given a model's response to a "
        "multiple-choice question and the available choices, determine which choice "
        "the model intended. Respond with valid JSON:\n"
        '{"selected": "<letter>", "confidence": <0.0-1.0>}'
    )
    user = (
        f"Model response:\n{response}\n\n"
        f"Choices:\n{choices_str}\n\n"
        f"Which choice (letter) did the model select?"
    )
    raw = client.call(system, user, json_mode=True)
    obj = json.loads(raw)
    selected = str(obj.get("selected", "")).strip().upper()
    confidence = float(obj.get("confidence", 0.0))
    correct = selected == gt_letter
    return JudgeVerdict(
        verdict="pass" if correct else "fail",
        score=1.0 if correct else 0.0,
        reason=f"LLM extracted answer '{selected}' (confidence {confidence:.2f})",
        details={"extracted_answer": selected, "confidence": confidence},
    )


def grade_frq(
    response: str,
    results_and_metrics: str = "",
    technical_approach: str = "",
    abstract: str = "",
    problem_statement: str = "",
    *,
    llm_call_fn: Callable | None = None,
    llm_client: Optional["LLMClient"] = None,
) -> dict:
    """
    Grade a free-response question using an LLM rubric judge.

    Returns dict with: score (0–10), alignment, specificity, novelty, rationale.
    Compatible with test_LLM.py's call signature (accepts llm_call_fn).
    """
    # Build the reference context from whatever is available
    ref_parts = []
    if abstract:
        ref_parts.append(f"Source abstract:\n{abstract}")
    if technical_approach:
        ref_parts.append(f"Reference technical approach:\n{technical_approach}")
    if results_and_metrics:
        ref_parts.append(f"Reference results and metrics:\n{results_and_metrics}")
    if problem_statement:
        ref_parts.append(f"Problem statement:\n{problem_statement}")
    reference = "\n\n".join(ref_parts) if ref_parts else "(no reference available)"

    system = (
        "You are a scientific evaluation judge. You will assess a model's proposed "
        "research methodology against a reference from the source paper.\n\n"
        "Evaluate on three dimensions (each 0–10):\n"
        "1. **Alignment**: How well does the proposed method align with the actual "
        "approach, findings, or methodology described in the reference?\n"
        "2. **Specificity**: How concrete and technically detailed is the proposal? "
        "Penalize vague or generic answers.\n"
        "3. **Novelty**: Does the proposal show genuine technical insight, or is it "
        "just restating obvious approaches?\n\n"
        "USE WEB SEARCH to look up the paper or methods mentioned in the reference "
        "context. Verify whether the model's proposed approach matches what was "
        "actually done in the paper, and whether the techniques it names are real "
        "and correctly described.\n\n"
        "There may be multiple valid approaches — do NOT require exact matching. "
        "Judge faithfulness to the problem, overlap with the reference methodology, "
        "and concreteness.\n\n"
        "Respond with valid JSON:\n"
        "{\n"
        '  "alignment": <0-10>,\n'
        '  "specificity": <0-10>,\n'
        '  "novelty": <0-10>,\n'
        '  "score": <0-10 overall>,\n'
        '  "rationale": "<1-2 sentence explanation>"\n'
        "}"
    )
    user = (
        f"REFERENCE:\n{reference}\n\n"
        f"MODEL RESPONSE:\n{response}"
    )

    # Use whichever LLM interface is available
    try:
        if llm_client:
            raw, web_searches = llm_client._call_responses_api(system, user)
        elif llm_call_fn:
            raw = llm_call_fn(system, user)
            web_searches = []
        else:
            return _frq_heuristic_fallback(response, reference)

        import re
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
            if m:
                obj = json.loads(m.group(1))
            else:
                raise ValueError(f"Could not parse LLM response as JSON: {raw[:200]}")
        return {
            "score":       _clamp(obj.get("score", 0), 0, 10),
            "alignment":   _clamp(obj.get("alignment", 0), 0, 10),
            "specificity": _clamp(obj.get("specificity", 0), 0, 10),
            "novelty":     _clamp(obj.get("novelty", 0), 0, 10),
            "rationale":   str(obj.get("rationale", "")),
            "web_searches": web_searches,
            "web_search_used": bool(web_searches),
        }
    except Exception as e:
        return {
            "score": None,
            "alignment": None,
            "specificity": None,
            "novelty": None,
            "rationale": f"FRQ grading error: {e}",
            "web_searches": [],
            "web_search_used": False,
        }


def _frq_heuristic_fallback(response: str, reference: str) -> dict:
    """Rough heuristic FRQ scoring when no LLM is available (--no-llm mode)."""
    if not response or not response.strip():
        return {"score": 0, "alignment": 0, "specificity": 0, "novelty": 0,
                "rationale": "Empty response"}

    # Very rough: score by response length and token overlap
    resp_words = set(response.lower().split())
    ref_words = set(reference.lower().split())
    overlap = len(resp_words & ref_words)
    total = max(len(ref_words), 1)
    overlap_ratio = min(overlap / total, 1.0)

    length_score = min(len(response.split()) / 100, 1.0)  # up to ~100 words = full
    raw = (overlap_ratio * 5 + length_score * 5)  # 0-10 range
    score = round(min(raw, 10), 1)
    return {
        "score": score,
        "alignment": None,
        "specificity": None,
        "novelty": None,
        "rationale": f"Heuristic (no LLM): overlap={overlap_ratio:.2f}, length={length_score:.2f}",
    }


def _parse_date(text: str) -> tuple[int, int] | None:
    """Parse a YYYY-MM date string. Returns (year, month) or None."""
    if not text:
        return None
    text = text.strip()
    # Try several patterns
    for pat in [
        r"(\d{4})-(\d{1,2})",
        r"(\d{4})/(\d{1,2})",
        r"(\d{4})\.(\d{1,2})",
    ]:
        m = re.search(pat, text)
        if m:
            year, month = int(m.group(1)), int(m.group(2))
            if 1900 <= year <= 2100 and 1 <= month <= 12:
                return (year, month)
    return None


def grade_date(response: str, ground_truth: str) -> dict:
    """
    Grade a date prediction (YYYY-MM).

    Returns dict with: exact_match, month_distance, parsed_date, ground_truth.
    """
    pred = _parse_date(response)
    gt = _parse_date(ground_truth)

    if pred is None:
        return {
            "exact_match": False,
            "month_distance": None,
            "parsed_date": None,
            "ground_truth": ground_truth,
            "score": 0.0,
        }
    if gt is None:
        return {
            "exact_match": False,
            "month_distance": None,
            "parsed_date": f"{pred[0]:04d}-{pred[1]:02d}",
            "ground_truth": ground_truth,
            "score": 0.0,
        }

    distance = abs((pred[0] - gt[0]) * 12 + (pred[1] - gt[1]))
    exact = distance == 0

    # Score: 1.0 for exact, decaying with distance
    # 0 months=1.0, 1 month≈0.92, 3 months≈0.78, 6 months≈0.55, 12 months≈0.30
    score = round(math.exp(-0.1 * distance), 4)

    return {
        "exact_match": exact,
        "month_distance": distance,
        "parsed_date": f"{pred[0]:04d}-{pred[1]:02d}",
        "ground_truth": f"{gt[0]:04d}-{gt[1]:02d}",
        "score": score,
    }


# ---------------------------------------------------------------------------
# Track 2 — Reasoning Judges
# ---------------------------------------------------------------------------

def _build_row_context(row: dict, leakage_mode: bool = False) -> str:
    """Build a context summary from the benchmark row for reasoning judges.

    leakage_mode=True: omit actual paper content (abstract/approach/results) so
    the leakage judge cannot false-positive on terminology overlap with the paper.
    It only receives the problem statement and dates — i.e. what the model could
    legitimately have known.
    """
    parts = []

    # Problem statement is always included (model saw this)
    ps = row.get("problem_statement")
    if ps:
        parts.append(f"Problem Statement:\n{ps}")

    if not leakage_mode:
        # Mechanistic/constraint judges get the full paper context for reference
        for key in ("source_abstract", "technical_approach", "results_and_metrics"):
            val = row.get(key)
            if val:
                label = key.replace("_", " ").title()
                parts.append(f"{label}:\n{val}")

    pub_date = row.get("publication_date", "")
    cutoff = row.get("cutoff_date", "")
    if pub_date:
        parts.append(f"Publication date: {pub_date}")
    if cutoff:
        parts.append(f"Knowledge cutoff: {cutoff}")
    return "\n\n".join(parts)


def judge_leakage(
    row: dict,
    prediction: str,
    reasoning: str,
    *,
    llm_client: Optional[LLMClient] = None,
) -> JudgeVerdict:
    """
    Detect information leakage / hindsight in the model's response.

    Checks for: explicit use of post-cutoff information, unavailable benchmark/
    model names, or future dates relative to the stated cutoff.
    """
    if not llm_client:
        return _leakage_heuristic(row, prediction, reasoning)

    context = _build_row_context(row, leakage_mode=True)
    pub_date = row.get("publication_date", "unknown")
    cutoff = row.get("cutoff_date", pub_date)

    system = (
        "You are a data-contamination and leakage auditor for a scientific "
        "forecasting benchmark.\n\n"
        "The benchmark tests whether models can predict future scientific results. "
        "Each question is about a discovery published AFTER the model's knowledge "
        f"cutoff. The paper's publication date is {pub_date}.\n\n"
        "====== YOUR ONLY JOB ======\n"
        "Decide whether the LLM RESPONSE (delimited by <<LLM_RESPONSE>> tags in the "
        "user message) explicitly names a specific post-cutoff entity.\n\n"
        "FOLLOW THESE STEPS IN ORDER — DO NOT SKIP:\n"
        "  STEP 1 — READ THE LLM RESPONSE TEXT ONLY.\n"
        "    Copy out every proper noun, model name, paper title, system name, or "
        "    dataset name that appears VERBATIM between the <<LLM_RESPONSE>> tags.\n"
        "    If you find zero such names, immediately return verdict='pass' — DO NOT "
        "    perform any web search.\n\n"
        "  STEP 2 — FOR EACH NAME FOUND IN STEP 1 ONLY:\n"
        "    Use web search to verify when that exact name was first publicly released.\n"
        f"    If it was released AFTER {cutoff}, that is a leakage indicator.\n\n"
        "  STEP 3 — DECIDE:\n"
        "    LEAKAGE (verdict=fail) requires ALL THREE:\n"
        "      a. The name appears VERBATIM in the LLM RESPONSE text (quote it).\n"
        f"      b. It was first released AFTER {cutoff} (confirmed by web search).\n"
        "      c. It could not have been independently invented.\n\n"
        "ABSOLUTE PROHIBITIONS:\n"
        "  - NEVER use web search to find papers that match the methodology described "
        "    in the LLM response, then claim the model named them. If the model wrote "
        "    'use a coordinate-based MLP' and you find a paper called FooNet that does "
        "    exactly that, this is NOT leakage — the model did not write 'FooNet'.\n"
        "  - NEVER flag something as leakage unless you can copy-paste the exact name "
        "    from the <<LLM_RESPONSE>> block.\n"
        "  - NEVER consider anything from web search results as part of the LLM response.\n\n"
        "NOT leakage — return verdict 'pass' for these:\n"
        "  - Descriptions of methods without naming a specific post-cutoff system.\n"
        "  - Correct predictions or methodologies that happen to match the paper.\n"
        "  - Numerical predictions that coincidentally match the paper.\n\n"
        "Be CONSERVATIVE. If uncertain, return 'unclear'.\n\n"
        "Respond with valid JSON:\n"
        '{"verdict": "pass"|"fail"|"unclear", "score": <0.0-1.0>, '
        '"reason": "<verbatim quote from LLM_RESPONSE if fail, else explanation>", '
        '"details": {"leakage_indicators": ["<verbatim quote>", ...]}}'
    )
    user = (
        f"ROW CONTEXT:\n{context}\n\n"
        f"<<LLM_RESPONSE>>\n{prediction}\n<</LLM_RESPONSE>>\n\n"
        f"LLM REASONING (if available):\n{reasoning if reasoning else '(none provided)'}"
    )
    return llm_client.call_judge_with_search(system, user, tool_choice="required")


def _leakage_heuristic(row: dict, prediction: str, reasoning: str) -> JudgeVerdict:
    """Minimal deterministic leakage check (--no-llm mode)."""
    text = f"{prediction} {reasoning}".lower()
    pub_date = row.get("publication_date", "")

    indicators = []
    # Check if future dates are mentioned
    if pub_date:
        parsed = _parse_date(pub_date)
        if parsed:
            # Look for dates after publication
            for m in re.finditer(r"(\d{4})-(\d{1,2})", text):
                y, mo = int(m.group(1)), int(m.group(2))
                if (y, mo) > parsed and 2020 <= y <= 2100:
                    indicators.append(f"mentions future date {y}-{mo:02d}")

    if indicators:
        return JudgeVerdict(
            verdict="fail", score=0.0,
            reason=f"Heuristic leakage indicators: {'; '.join(indicators)}",
            details={"leakage_indicators": indicators},
        )
    return JudgeVerdict(
        verdict="pass", score=1.0,
        reason="No obvious leakage detected (heuristic only)",
        details={"leakage_indicators": []},
    )


def judge_mechanistic(
    row: dict,
    prediction: str,
    reasoning: str,
    *,
    llm_client: Optional[LLMClient] = None,
) -> JudgeVerdict:
    """
    Evaluate whether the model's reasoning is scientifically coherent
    and not just buzzword filler.
    """
    if not llm_client:
        return _mechanistic_heuristic(reasoning or prediction)

    context = _build_row_context(row)

    system = (
        "You are a scientific reasoning quality judge.\n\n"
        "Evaluate whether the model's reasoning demonstrates genuine scientific "
        "understanding relevant to the problem. Assess:\n"
        "1. **Coherence**: Does the reasoning follow a logical chain?\n"
        "2. **Relevance**: Is the reasoning actually about the specific problem, "
        "   not generic filler?\n"
        "3. **Depth**: Does it engage with technical specifics rather than "
        "   surface-level buzzwords?\n\n"
        "USE WEB SEARCH to verify specific technical claims in the reasoning. "
        "For any named method, algorithm, dataset, or result the model cites, "
        "search for it to confirm it is real, correctly described, and relevant "
        "to the problem domain. Flag reasoning that invents or misattributes "
        "methods as low-depth.\n\n"
        "Do NOT require a unique or correct answer — judge coherence, not style.\n"
        "A well-reasoned wrong answer can still pass.\n\n"
        "Respond with valid JSON:\n"
        '{"verdict": "pass"|"fail"|"unclear", "score": <0.0-1.0>, '
        '"reason": "<explanation>", "details": {"coherence": <0-1>, '
        '"relevance": <0-1>, "depth": <0-1>}}'
    )
    user = (
        f"PROBLEM CONTEXT:\n{context}\n\n"
        f"MODEL PREDICTION:\n{prediction}\n\n"
        f"MODEL REASONING:\n{reasoning if reasoning else '(none provided)'}"
    )
    return llm_client.call_judge_with_search(system, user)


def _mechanistic_heuristic(text: str) -> JudgeVerdict:
    """Rough mechanistic check when no LLM is available."""
    if not text or len(text.strip()) < 20:
        return JudgeVerdict(
            verdict="fail", score=0.0,
            reason="Response too short for meaningful reasoning assessment",
        )
    word_count = len(text.split())
    # Very basic: pass if substantive length
    score = min(word_count / 50, 1.0)
    verdict = "pass" if score >= 0.4 else "unclear"
    return JudgeVerdict(
        verdict=verdict, score=round(score, 2),
        reason=f"Heuristic (no LLM): {word_count} words",
    )


def judge_constraint(
    row: dict,
    prediction: str,
    reasoning: str,
    *,
    llm_client: Optional[LLMClient] = None,
) -> JudgeVerdict:
    """
    Evaluate whether the model's reasoning shows awareness of practical
    constraints or feasibility limits implied by the task.
    """
    if not llm_client:
        return _constraint_heuristic(reasoning or prediction)

    context = _build_row_context(row)

    system = (
        "You are a scientific feasibility judge.\n\n"
        "Your job is to evaluate whether the model's PROPOSED ANSWER is actually "
        "feasible given real-world constraints. You are NOT checking whether the "
        "model discusses or mentions constraints — you are judging whether the "
        "approach it proposes could realistically work.\n\n"
        "Consider whether the proposed approach is feasible in light of:\n"
        "- Computational and hardware requirements (is it realistically runnable?)\n"
        "- Data availability and quality requirements\n"
        "- Time and resource budgets typical for this type of research\n"
        "- Known technical limitations of the proposed methods\n"
        "- Scalability to the problem scale described\n"
        "- Whether proposed methods actually exist and work as described\n\n"
        "verdict='pass'  → the proposed approach is plausibly feasible\n"
        "verdict='fail'  → the proposal has a clear real-world feasibility problem "
        "(e.g., requires unavailable data, prohibitive compute, non-existent method)\n"
        "verdict='unclear' → cannot determine feasibility from the response\n\n"
        "Do NOT penalize a response just because it doesn't discuss constraints. "
        "Judge whether the APPROACH itself is feasible, not whether the model "
        "mentioned constraints in its explanation.\n\n"
        "USE WEB SEARCH to verify whether the methods, datasets, or hardware the "
        "model proposes are real and feasible (e.g., check compute requirements, "
        "dataset availability, known limitations of cited techniques).\n\n"
        "Respond with valid JSON:\n"
        '{"verdict": "pass"|"fail"|"unclear", "score": <0.0-1.0>, '
        '"reason": "<explanation of why the proposed approach is/is not feasible>", '
        '"details": {"feasibility_issues": []}}'
    )
    user = (
        f"PROBLEM CONTEXT:\n{context}\n\n"
        f"MODEL PREDICTION:\n{prediction}\n\n"
        f"MODEL REASONING:\n{reasoning if reasoning else '(none provided)'}"
    )
    return llm_client.call_judge_with_search(system, user)


def _constraint_heuristic(text: str) -> JudgeVerdict:
    """Rough constraint check when no LLM is available."""
    if not text:
        return JudgeVerdict(verdict="unclear", score=0.5,
                            reason="No reasoning text to assess")

    # Look for general constraint language (no domain-specific terms)
    constraint_patterns = [
        r"\blimit", r"\bconstraint", r"\bchalleng", r"\bfeasib",
        r"\bscalab", r"\btrade.?off", r"\bbottleneck", r"\bdifficult",
        r"\bcaveat", r"\bassumption", r"\brequir", r"\bresource",
        r"\bcost", r"\bcomplex", r"\boverhead",
    ]
    found = []
    text_lower = text.lower()
    for pat in constraint_patterns:
        if re.search(pat, text_lower):
            found.append(pat.replace(r"\b", "").rstrip(""))

    if found:
        score = min(len(found) / 3, 1.0)
        return JudgeVerdict(
            verdict="pass" if score >= 0.33 else "unclear",
            score=round(score, 2),
            reason=f"Heuristic: found constraint language ({len(found)} indicators)",
            details={"constraints_mentioned": found},
        )
    return JudgeVerdict(
        verdict="unclear", score=0.3,
        reason="Heuristic: no constraint language detected",
    )


def judge_frq_combined(
    row: dict,
    frq_response: str,
    *,
    llm_client: Optional["LLMClient"] = None,
) -> dict:
    """
    Single LLM+web-search call that combines FRQ grading, mechanistic soundness,
    and constraint awareness.

    Returns a flat dict with keys:
      frq_score, alignment, specificity, novelty, frq_rationale,
      mechanistic_verdict, mechanistic_score, coherence, relevance, depth,
      mechanistic_reason,
      constraint_verdict, constraint_score, constraints_mentioned, constraint_reason,
      web_searches, web_search_used.
    """
    if not llm_client:
        fg = _frq_heuristic_fallback(frq_response, "")
        mv = _mechanistic_heuristic(frq_response)
        cv = _constraint_heuristic(frq_response)
        return {
            "frq_score":           fg["score"],
            "alignment":           fg.get("alignment"),
            "specificity":         fg.get("specificity"),
            "novelty":             fg.get("novelty"),
            "feasibility":         fg.get("feasibility"),
            "urls":                [],
            "frq_rationale":       fg.get("rationale", ""),
            "mechanistic_verdict": mv.verdict,
            "mechanistic_score":   mv.score,
            "coherence":           mv.details.get("coherence"),
            "relevance":           mv.details.get("relevance"),
            "depth":               mv.details.get("depth"),
            "mechanistic_reason":  mv.reason,
            "constraint_verdict":  cv.verdict,
            "constraint_score":    cv.score,
            "constraints_mentioned": cv.details.get("constraints_mentioned", []),
            "constraint_reason":   cv.reason,
            "web_searches":        [],
            "web_search_used":     False,
        }

    ref_parts = []
    abstract           = row.get("source_abstract", "")
    technical_approach = row.get("technical_approach", "")
    results_and_metrics = row.get("results_and_metrics", "")
    problem_statement  = row.get("problem_statement", "")
    pub_date           = row.get("publication_date", "")
    cutoff             = row.get("cutoff_date", pub_date)

    if abstract:           ref_parts.append(f"Source abstract:\n{abstract}")
    if technical_approach: ref_parts.append(f"Reference technical approach:\n{technical_approach}")
    if results_and_metrics: ref_parts.append(f"Reference results and metrics:\n{results_and_metrics}")
    if problem_statement:  ref_parts.append(f"Problem statement:\n{problem_statement}")
    if pub_date:           ref_parts.append(f"Publication date: {pub_date}")
    if cutoff:             ref_parts.append(f"Knowledge cutoff: {cutoff}")
    reference = "\n\n".join(ref_parts) if ref_parts else "(no reference available)"

    system = (
    "You are a rigorous scientific evaluation judge. Your job is to assess the LLM RESPONSE "
    "(delimited by <<LLM_RESPONSE>> tags in the user message) against the GROUND-TRUTH "
    "REFERENCE (everything outside those tags). Never confuse what the web search returns "
    "with what the LLM wrote — the LLM RESPONSE is ONLY the text inside <<LLM_RESPONSE>>.\n"
    "\n"
    "USE WEB SEARCH to look up the actual paper, verify the real methodology, and check "
    "whether claims inside <<LLM_RESPONSE>> are accurate. Use search results as ground "
    "truth — not to confirm the LLM.\n"
    "\n"
    "=== PART 1: FRQ SCORING — use strict anchors ===\n"
    "\n"
    "1. alignment (0–10): Does the LLM RESPONSE describe the specific approach used in the paper? "
    "Use web search to find the actual paper method.\n"
    "   - 0–2: completely wrong direction or no meaningful content\n"
    "   - 3–4: roughly right area but missing key specifics of the actual method\n"
    "   - 5–6: captures the main idea but lacks important details or misstates them\n"
    "   - 7–8: matches the core technique with most key details correct\n"
    "   - 9–10: precise match including specific design choices and implementation\n"
    "\n"
    "2. specificity (0–10): Is the LLM RESPONSE technically concrete?\n"
    "   - 0–2: pure buzzwords or single-sentence vague claims\n"
    "   - 3–4: names a technique but no explanation of how it is applied\n"
    "   - 5–6: explains the method at a conceptual level\n"
    "   - 7–8: provides implementation-level details (architecture, loss, data)\n"
    "   - 9–10: full technical recipe that could be directly implemented\n"
    "\n"
    "3. novelty (0–10): Does the LLM RESPONSE show non-obvious insight?\n"
    "   - 0–2: restates the most obvious baseline for this problem area\n"
    "   - 3–4: proposes minor, obvious variations on standard baselines\n"
    "   - 5–6: goes beyond obvious but the insight is well-known in the field\n"
    "   - 7–8: proposes something non-trivial and technically justified\n"
    "   - 9–10: highly original and technically justified breakthrough insight\n"
    "\n"
    "4. feasibility (0–10): Is the proposed approach actually feasible given real-world constraints?\n"
    "   - 0–2: clearly infeasible (non-existent methods, impossible assumptions)\n"
    "   - 3–4: major feasibility issues (unrealistic compute/data or unsupported claims)\n"
    "   - 5–6: plausible but with notable practical concerns\n"
    "   - 7–8: largely feasible with minor caveats\n"
    "   - 9–10: clearly feasible and consistent with real-world implementations\n"
    "\n"
    "Respond with a ```json code block. Write 1-2 sentences of reasoning with inline citations "
    "([title](url)) before the block.\n"
    "\n"
    "{\n"
    "  \"alignment\": <0-10>,\n"
    "  \"specificity\": <0-10>,\n"
    "  \"novelty\": <0-10>,\n"
    "  \"feasibility\": <0-10>,\n"
    "  \"rationale\": \"<2-3 sentence summary explaining the scores for alignment, specificity, novelty, and feasibility>\",\n"
    "  \"urls\": [\"<url1>\", \"<url2>\"]\n"
    "}\n"
    )
    user = (
        f"GROUND-TRUTH REFERENCE:\n{reference}\n\n"
        f"<<LLM_RESPONSE>>\n{frq_response}\n<</LLM_RESPONSE>>"
    )

    raw, web_searches = llm_client._call_responses_api(system, user)

    # Fence-first parse: the model may write prose + citations around the JSON block
    obj: dict | None = None
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    if obj is None:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            pass

    if obj is None:
        return {
            "frq_score": None, "alignment": None, "specificity": None,
            "novelty": None, "feasibility": None,
            "frq_rationale": f"Could not parse response: {raw[:200]}",
            "urls": [],
            "mechanistic_verdict": "unclear", "mechanistic_score": 0.5,
            "coherence": None, "relevance": None, "depth": None,
            "mechanistic_reason": "Parse error",
            "constraint_verdict": "unclear", "constraint_score": 0.5,
            "constraints_mentioned": [], "constraint_reason": "Parse error",
            "web_searches": web_searches, "web_search_used": bool(web_searches),
        }

    def _safe(v, lo, hi):
        return _clamp(v, lo, hi) if v is not None else None

    alignment   = _safe(obj.get("alignment"),   0, 10)
    specificity = _safe(obj.get("specificity"), 0, 10)
    novelty     = _safe(obj.get("novelty"),     0, 10)
    feasibility = _safe(obj.get("feasibility"), 0, 10)
    sub_scores  = [s for s in [alignment, specificity, novelty, feasibility] if s is not None]
    frq_score   = round(sum(sub_scores) / len(sub_scores), 2) if sub_scores else None

    return {
        "frq_score":           frq_score,
        "alignment":           alignment,
        "specificity":         specificity,
        "novelty":             novelty,
        "feasibility":         feasibility,
        "frq_rationale":       str(obj.get("rationale", "")),
        "urls":                list(obj.get("urls", [])),
        "mechanistic_verdict": str(obj.get("mechanistic_verdict", "unclear")).lower(),
        "mechanistic_score":   _clamp(obj.get("mechanistic_score", 0.5), 0, 1),
        "coherence":           _safe(obj.get("coherence"), 0, 1),
        "relevance":           _safe(obj.get("relevance"), 0, 1),
        "depth":               _safe(obj.get("depth"), 0, 1),
        "mechanistic_reason":  str(obj.get("mechanistic_reason", "")),
        "constraint_verdict":  str(obj.get("constraint_verdict", "unclear")).lower(),
        "constraint_score":    _clamp(obj.get("constraint_score", 0.5), 0, 1),
        "constraints_mentioned": list(obj.get("constraints_mentioned", [])),
        "constraint_reason":   str(obj.get("constraint_reason", "")),
        "web_searches":        web_searches,
        "web_search_used":     bool(web_searches),
    }


# ---------------------------------------------------------------------------
# Scoring & Aggregation
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r'https?://[^\s\)\]"\'<>]+')


def _extract_urls_deep(obj, _depth: int = 0) -> list[str]:
    """Recursively extract https:// URLs from any nested dict/list/str structure.

    Used to scan model_dump() output of Responses API items so we pick up URLs
    from any field the SDK exposes (sources, results, etc.) regardless of name.
    """
    if _depth > 8 or obj is None:
        return []
    if isinstance(obj, str):
        return [u.rstrip(".,)\"'") for u in _URL_RE.findall(obj)]
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(_extract_urls_deep(v, _depth + 1))
        return out
    if isinstance(obj, (list, tuple)):
        out = []
        for v in obj:
            out.extend(_extract_urls_deep(v, _depth + 1))
        return out
    return []


def _merge_text_urls(text: str, web_searches: list[dict]) -> None:
    """Extract https:// URLs from a text string and merge into the last search entry."""
    urls = list(dict.fromkeys(u.rstrip(".,)\"'") for u in _URL_RE.findall(text)))
    if not urls:
        return
    if web_searches:
        existing = set(web_searches[-1].get("urls_reached", []))
        for u in urls:
            if u not in existing:
                web_searches[-1].setdefault("urls_reached", []).append(u)
                existing.add(u)
    else:
        web_searches.append({"query": "", "queries": [], "status": "",
                              "urls_reached": urls})


def _clamp(val, lo, hi):
    """Clamp a numeric value to [lo, hi]."""
    try:
        return max(lo, min(float(val), hi))
    except (TypeError, ValueError):
        return lo


def _attach_confidence(task_result: dict, raw_confidence) -> None:
    """Attach a confidence float to a task result dict if the value is usable."""
    if raw_confidence is None:
        return
    try:
        task_result["confidence"] = round(max(0.0, min(1.0, float(raw_confidence))), 4)
    except (TypeError, ValueError):
        pass


def score_row(
    row: dict,
    *,
    llm_client: Optional[LLMClient] = None,
    skip_leakage: bool = False,
    verbose: bool = False,
) -> RowResult:
    """
    Run all applicable judges on a single benchmark row and produce a RowResult.
    """
    rid = str(row.get("id", "unknown"))
    tasks = detect_tasks(row)
    available = [t for t, present in tasks.items() if present]

    result = RowResult(id=rid, available_tasks=available)

    # ---- Gather predictions ----
    predictions_found = False

    # ---- Track 1: Outcome judges ----
    outcome_scores: list[float] = []
    outcome_passes: list[bool] = []

    # Binary
    if tasks["binary"]:
        pred = _find_prediction_for_task(row, "binary")
        if pred:
            predictions_found = True
            bg = grade_binary(pred, row.get("binary_ground_truth", "Yes"))
            _attach_confidence(bg, row.get("binary_confidence"))
            result.tasks["binary"] = bg
            outcome_scores.append(bg["score"])
            outcome_passes.append(bg["correct"])
            if verbose:
                _log(f"  [binary] {'✓' if bg['correct'] else '✗'} "
                     f"parsed={bg['parsed_answer']} gt={bg['ground_truth']}")
        else:
            result.tasks["binary"] = {"skipped": True, "reason": "no prediction"}

    # Binary perturbed
    if tasks["binary_perturbed"]:
        pred = _find_prediction_for_task(row, "binary_perturbed")
        if pred:
            predictions_found = True
            gt = "No"
            bg = grade_binary(pred, str(gt))
            _attach_confidence(bg, row.get("binary_perturbed_confidence"))
            result.tasks["binary_perturbed"] = bg
            outcome_scores.append(bg["score"])
            outcome_passes.append(bg["correct"])
            if verbose:
                _log(f"  [binary_perturbed] {'✓' if bg['correct'] else '✗'}")
        else:
            result.tasks["binary_perturbed"] = {"skipped": True, "reason": "no prediction"}

    # MCQ
    if tasks["mcq"]:
        pred = _find_prediction_for_task(row, "mcq")
        if pred:
            predictions_found = True
            mg = grade_mcq(
                pred,
                row.get("mcq_shuffled_answer_key") or row["mcq_answer_key"],
                choices=row.get("mcq_shuffled_choices") or row.get("mcq_choices"),
                llm_client=llm_client,
            )
            _attach_confidence(mg, row.get("mcq_confidence"))
            result.tasks["mcq"] = mg
            outcome_scores.append(mg["score"])
            outcome_passes.append(mg["correct"])
            if verbose:
                _log(f"  [mcq] {'✓' if mg['correct'] else '✗'} "
                     f"parsed={mg['parsed_answer']} gt={mg['ground_truth']}")
        else:
            result.tasks["mcq"] = {"skipped": True, "reason": "no prediction"}

    # FRQ — combined judge handles grading + mechanistic + constraint in one call
    _frq_combined: dict | None = None
    if tasks["frq"]:
        pred = _find_prediction_for_task(row, "frq")
        if pred:
            predictions_found = True
            if llm_client:
                _frq_combined = judge_frq_combined(row, pred, llm_client=llm_client)
                fg: dict = {
                    "score":          _frq_combined["frq_score"],
                    "alignment":      _frq_combined["alignment"],
                    "specificity":    _frq_combined["specificity"],
                    "novelty":        _frq_combined["novelty"],
                    "feasibility":    _frq_combined["feasibility"],
                    "rationale":      _frq_combined["frq_rationale"],
                    "urls":           _frq_combined["urls"],
                    "web_searches":   _frq_combined["web_searches"],
                    "web_search_used": _frq_combined["web_search_used"],
                }
            else:
                fg = grade_frq(
                    pred,
                    results_and_metrics=row.get("results_and_metrics", ""),
                    technical_approach=row.get("technical_approach", ""),
                    abstract=row.get("source_abstract", ""),
                    problem_statement=row.get("problem_statement", ""),
                )
            result.tasks["frq"] = fg
            if fg["score"] is not None:
                outcome_scores.append(fg["score"] / 10.0)  # normalize to 0-1
                outcome_passes.append(fg["score"] >= 5.0)
            if verbose:
                _log(f"  [frq] score={fg['score']}")
        else:
            result.tasks["frq"] = {"skipped": True, "reason": "no prediction"}

    # Date
    if tasks["date"]:
        pred = _find_prediction_for_task(row, "date")
        if pred:
            predictions_found = True
            dg = grade_date(pred, row["ground_truth_date"])
            _attach_confidence(dg, row.get("date_confidence"))
            result.tasks["date"] = dg
            outcome_scores.append(dg["score"])
            outcome_passes.append(dg["exact_match"])
            if verbose:
                _log(f"  [date] exact={dg['exact_match']} "
                     f"distance={dg['month_distance']}mo")
        else:
            result.tasks["date"] = {"skipped": True, "reason": "no prediction"}

    result.prediction_found = predictions_found

    # ---- Track 2: Reasoning judges (FRQ only) ----
    frq_response = _find_prediction_for_task(row, "frq")

    reasoning_scores: list[float] = []
    reasoning_passes: list[bool] = []

    if frq_response:
        # Leakage is always its own web-search call (conceptually distinct)
        lv = (_leakage_heuristic(row, frq_response, "")
              if skip_leakage
              else judge_leakage(row, frq_response, "", llm_client=llm_client))
        result.reasoning["leakage"] = lv.to_dict()
        reasoning_scores.append(lv.score)
        reasoning_passes.append(lv.verdict != "fail")

        if _frq_combined:
            # Mechanistic and constraint come free from the combined FRQ call
            result.reasoning["mechanistic"] = {
                "verdict": _frq_combined["mechanistic_verdict"],
                "score":   _frq_combined["mechanistic_score"],
                "reason":  _frq_combined["mechanistic_reason"],
                "details": {
                    "coherence": _frq_combined.get("coherence"),
                    "relevance": _frq_combined.get("relevance"),
                    "depth":     _frq_combined.get("depth"),
                },
            }
            reasoning_scores.append(_frq_combined["mechanistic_score"])
            reasoning_passes.append(_frq_combined["mechanistic_verdict"] != "fail")

            result.reasoning["constraint"] = {
                "verdict": _frq_combined["constraint_verdict"],
                "score":   _frq_combined["constraint_score"],
                "reason":  _frq_combined["constraint_reason"],
                "details": {"constraints_mentioned": _frq_combined.get("constraints_mentioned", [])},
            }
            reasoning_scores.append(_frq_combined["constraint_score"])
            reasoning_passes.append(_frq_combined["constraint_verdict"] != "fail")
        else:
            # --no-llm heuristic fallback
            mv = _mechanistic_heuristic(frq_response)
            result.reasoning["mechanistic"] = mv.to_dict()
            reasoning_scores.append(mv.score)
            reasoning_passes.append(mv.verdict != "fail")

            cv = _constraint_heuristic(frq_response)
            result.reasoning["constraint"] = cv.to_dict()
            reasoning_scores.append(cv.score)
            reasoning_passes.append(cv.verdict != "fail")
    else:
        for name in ("leakage", "mechanistic", "constraint"):
            result.reasoning[name] = {
                "verdict": "unclear", "score": 0.5,
                "reason": "No FRQ response to assess",
                "details": {},
            }
            reasoning_scores.append(0.5)
            reasoning_passes.append(True)  # Don't penalize missing FRQ

    # ---- Joint scoring ----
    outcome_avg = sum(outcome_scores) / len(outcome_scores) if outcome_scores else 0.0
    reasoning_avg = (sum(reasoning_scores) / len(reasoning_scores)
                     if reasoning_scores else 0.0)

    result.outcome_pass = any(outcome_passes) if outcome_passes else False
    result.reasoning_pass = all(reasoning_passes)
    result.joint_pass = result.outcome_pass and result.reasoning_pass

    result.overall_score = round(
        OUTCOME_WEIGHT * outcome_avg + REASONING_WEIGHT * reasoning_avg, 4
    )

    return result


def aggregate_results(results: list[RowResult], all_rows: list[dict]) -> dict:
    """
    Compute aggregate metrics from a list of RowResults.

    Returns a dict with: summary, task_availability, task_metrics,
    reasoning_metrics, results.
    """
    total = len(results)
    if total == 0:
        return {"summary": {"total_rows": 0}, "results": []}

    # Task availability counts
    task_avail: dict[str, int] = {}
    for r in results:
        for t in r.available_tasks:
            task_avail[t] = task_avail.get(t, 0) + 1

    # Per-task metrics
    task_metrics: dict[str, dict] = {}

    # Binary
    binary_results = [r.tasks["binary"] for r in results
                      if "binary" in r.tasks and not r.tasks["binary"].get("skipped")]
    if binary_results:
        correct = sum(1 for b in binary_results if b.get("correct"))
        confs = [b["confidence"] for b in binary_results if b.get("confidence") is not None]
        task_metrics["binary"] = {
            "count": len(binary_results),
            "correct": correct,
            "accuracy": round(correct / len(binary_results), 4),
            "mean_score": round(sum(b.get("score", 0) for b in binary_results) /
                                len(binary_results), 4),
        }
        if confs:
            task_metrics["binary"]["mean_confidence"] = round(
                sum(confs) / len(confs), 4)

    # Binary perturbed
    bp_results = [r.tasks["binary_perturbed"] for r in results
                  if "binary_perturbed" in r.tasks
                  and not r.tasks["binary_perturbed"].get("skipped")]
    if bp_results:
        correct = sum(1 for b in bp_results if b.get("correct"))
        confs = [b["confidence"] for b in bp_results if b.get("confidence") is not None]
        task_metrics["binary_perturbed"] = {
            "count": len(bp_results),
            "correct": correct,
            "accuracy": round(correct / len(bp_results), 4),
            "mean_score": round(sum(b.get("score", 0) for b in bp_results) /
                                len(bp_results), 4),
        }
        if confs:
            task_metrics["binary_perturbed"]["mean_confidence"] = round(
                sum(confs) / len(confs), 4)

    # MCQ
    mcq_results = [r.tasks["mcq"] for r in results
                   if "mcq" in r.tasks and not r.tasks["mcq"].get("skipped")]
    if mcq_results:
        correct = sum(1 for m in mcq_results if m.get("correct"))
        confs = [m["confidence"] for m in mcq_results if m.get("confidence") is not None]
        task_metrics["mcq"] = {
            "count": len(mcq_results),
            "correct": correct,
            "accuracy": round(correct / len(mcq_results), 4),
            "mean_score": round(sum(m.get("score", 0) for m in mcq_results) /
                                len(mcq_results), 4),
        }
        if confs:
            task_metrics["mcq"]["mean_confidence"] = round(
                sum(confs) / len(confs), 4)

    # FRQ
    frq_results = [r.tasks["frq"] for r in results
                   if "frq" in r.tasks and not r.tasks["frq"].get("skipped")]
    frq_scores = [f["score"] for f in frq_results
                  if f.get("score") is not None]
    if frq_scores:
        task_metrics["frq"] = {
            "count": len(frq_results),
            "scored": len(frq_scores),
            "mean_score": round(sum(frq_scores) / len(frq_scores), 4),
            "min_score": min(frq_scores),
            "max_score": max(frq_scores),
            "pass_rate": round(
                sum(1 for s in frq_scores if s >= 5.0) / len(frq_scores), 4
            ),
        }

    # Date
    date_results = [r.tasks["date"] for r in results
                    if "date" in r.tasks and not r.tasks["date"].get("skipped")]
    if date_results:
        exact = sum(1 for d in date_results if d.get("exact_match"))
        distances = [d["month_distance"] for d in date_results
                     if d.get("month_distance") is not None]
        confs = [d["confidence"] for d in date_results if d.get("confidence") is not None]
        task_metrics["date"] = {
            "count": len(date_results),
            "exact_matches": exact,
            "exact_match_rate": round(exact / len(date_results), 4),
            "mean_month_distance": round(sum(distances) / len(distances), 2)
                                   if distances else None,
            "median_month_distance": round(sorted(distances)[len(distances) // 2], 1)
                                     if distances else None,
            "mean_score": round(sum(d.get("score", 0) for d in date_results) /
                                len(date_results), 4),
        }
        if confs:
            task_metrics["date"]["mean_confidence"] = round(
                sum(confs) / len(confs), 4)

    # Reasoning metrics
    reasoning_metrics: dict[str, dict] = {}
    for judge_name in ("leakage", "mechanistic", "constraint"):
        judge_results = [r.reasoning[judge_name] for r in results
                         if judge_name in r.reasoning]
        if judge_results:
            verdicts = [j.get("verdict", "unclear") for j in judge_results]
            scores = [j.get("score", 0) for j in judge_results]
            reasoning_metrics[judge_name] = {
                "count": len(judge_results),
                "pass": verdicts.count("pass"),
                "fail": verdicts.count("fail"),
                "unclear": verdicts.count("unclear"),
                "pass_rate": round(verdicts.count("pass") / len(verdicts), 4),
                "fail_rate": round(verdicts.count("fail") / len(verdicts), 4),
                "mean_score": round(sum(scores) / len(scores), 4),
            }

    # Joint metrics
    joint_passes = sum(1 for r in results if r.joint_pass)
    outcome_passes = sum(1 for r in results if r.outcome_pass)
    reasoning_passes = sum(1 for r in results if r.reasoning_pass)
    overall_scores = [r.overall_score for r in results]
    predictions_found = sum(1 for r in results if r.prediction_found)

    summary = {
        "total_rows": total,
        "predictions_found": predictions_found,
        "predictions_missing": total - predictions_found,
        "joint_pass_count": joint_passes,
        "joint_pass_rate": round(joint_passes / total, 4),
        "outcome_pass_count": outcome_passes,
        "outcome_pass_rate": round(outcome_passes / total, 4),
        "reasoning_pass_count": reasoning_passes,
        "reasoning_pass_rate": round(reasoning_passes / total, 4),
        "mean_overall_score": round(sum(overall_scores) / len(overall_scores), 4),
        "outcome_weight": OUTCOME_WEIGHT,
        "reasoning_weight": REASONING_WEIGHT,
    }

    return {
        "summary": summary,
        "task_availability": task_avail,
        "task_metrics": task_metrics,
        "reasoning_metrics": reasoning_metrics,
        "results": [r.to_dict() for r in results],
    }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _log(msg: str):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def _save_report(row_results: list, all_rows: list, errors: list,
                 output_path: str, indent) -> None:
    """Write the current (possibly partial) report to disk."""
    report = aggregate_results(row_results, all_rows)
    if errors:
        report["errors"] = errors
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=indent, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    # ---- Load environment ----
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    # ---- Setup LLM client ----
    llm_client: Optional[LLMClient] = None
    if not args.no_llm:
        model = (args.model
                 or os.environ.get("AZURE_OPENAI_DEPLOYMENT")
                 or os.environ.get("OPENAI_MODEL")
                 or "gpt-5.4-mini")
        api_key = (args.api_key
                   or os.environ.get("OPENAI_API_KEY")
                   or os.environ.get("AZURE_OPENAI_KEY"))
        api_base = (args.api_base
                    or os.environ.get("OPENAI_API_BASE")
                    or os.environ.get("AZURE_OPENAI_ENDPOINT"))

        if not api_key:
            _log("WARNING: No API key provided and --no-llm not set. "
                 "LLM judges will be skipped for FRQ and reasoning tasks.")
        else:
            llm_client = LLMClient(model=model, api_key=api_key, api_base=api_base)
            if args.verbose:
                _log(f"LLM client initialized: model={model}, "
                     f"base={'Azure' if 'azure' in (api_base or '').lower() else api_base}")

    # ---- Load predictions ----
    pred_map: dict[str, dict] = {}
    if args.predictions:
        if not os.path.exists(args.predictions):
            _log(f"ERROR: predictions file not found: {args.predictions}")
            sys.exit(1)
        pred_map = load_predictions(args.predictions)
        if args.verbose:
            _log(f"Loaded {len(pred_map)} predictions from {args.predictions}")

    # ---- Load and process benchmark ----
    if not os.path.exists(args.benchmark):
        _log(f"ERROR: benchmark file not found: {args.benchmark}")
        sys.exit(1)

    all_rows: list[dict] = []
    row_results: list[RowResult] = []
    errors: list[dict] = []
    indent = 2 if args.pretty else None

    if args.verbose:
        _log(f"Reading benchmark: {args.benchmark}")

    # Determine total rows for the progress bar
    if args.max_rows:
        pbar_total = args.max_rows
    elif pred_map:
        pbar_total = len(pred_map)
    else:
        with open(args.benchmark, "r", encoding="utf-8") as _f:
            pbar_total = sum(1 for ln in _f if ln.strip())

    pbar = (_tqdm(total=pbar_total, desc="Evaluating", unit="row", file=sys.stderr)
            if _HAS_TQDM else None)

    with open(args.benchmark, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Parse row
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append({"line": lineno, "error": f"Malformed JSON: {e}"})
                _log(f"WARNING: line {lineno}: malformed JSON, skipping")
                continue

            rid = str(row.get("id", f"line_{lineno}"))

            # Merge predictions
            pred_row = pred_map.get(rid)

            # When a predictions file is given, max-rows counts matched rows only
            if pred_map and pred_row is None:
                continue  # skip unmatched benchmark rows
            all_rows.append(row)

            # Check max-rows limit (counts matched rows when predictions provided)
            if args.max_rows and len(all_rows) > args.max_rows:
                all_rows.pop()
                break

            merged = merge_predictions(row, pred_row)

            # Score the row
            try:
                rr = score_row(merged, llm_client=llm_client,
                               skip_leakage=args.no_leakage, verbose=args.verbose)
                row_results.append(rr)
                if len(row_results) % 100 == 0:
                    _save_report(row_results, all_rows, errors, args.output, indent)
                if pbar:
                    pbar.update(1)
                elif args.verbose and len(row_results) % 100 == 0:
                    _log(f"  processed {len(row_results)} rows...")
            except Exception as e:
                tb = traceback.format_exc()
                errors.append({"line": lineno, "id": rid, "error": str(e),
                               "traceback": tb})
                _log(f"WARNING: row {rid} (line {lineno}): error during scoring: {e}")
                # Add a placeholder result
                rr = RowResult(id=rid, error=str(e))
                row_results.append(rr)
                if len(row_results) % 10 == 0:
                    _save_report(row_results, all_rows, errors, args.output, indent)
                if pbar:
                    pbar.update(1)

    if pbar:
        pbar.close()

    if args.verbose:
        _log(f"Finished processing {len(row_results)} rows "
             f"({len(errors)} errors)")

    # ---- Final report ----
    _save_report(row_results, all_rows, errors, args.output, indent)
    report = aggregate_results(row_results, all_rows)

    if args.verbose or True:  # Always print summary
        s = report["summary"]
        _log(f"\n{'='*60}")
        _log("CUSP EVALUATION SUMMARY")
        _log(f"{'='*60}")
        _log(f"  Total rows:          {s['total_rows']}")
        _log(f"  Predictions found:   {s['predictions_found']}")
        _log(f"  Joint pass rate:     {s['joint_pass_rate']:.1%}")
        _log(f"  Outcome pass rate:   {s['outcome_pass_rate']:.1%}")
        _log(f"  Reasoning pass rate: {s['reasoning_pass_rate']:.1%}")
        _log(f"  Mean overall score:  {s['mean_overall_score']:.4f}")

        tm = report.get("task_metrics", {})
        if tm:
            _log(f"\n  Task Metrics:")
            for task_name, metrics in tm.items():
                if "accuracy" in metrics:
                    _log(f"    {task_name}: accuracy={metrics['accuracy']:.1%} "
                         f"({metrics.get('correct', '?')}/{metrics['count']})")
                elif "mean_score" in metrics:
                    _log(f"    {task_name}: mean_score={metrics['mean_score']:.2f} "
                         f"(n={metrics['count']})")

        _log(f"\n  Report saved to: {args.output}")
        _log(f"{'='*60}")


if __name__ == "__main__":
    main()
