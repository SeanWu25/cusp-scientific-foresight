#!/usr/bin/env python3
"""
freeze_manifest.py — pin everything run 1 depends on, so run 2 can be pooled with it.

Emits a JSON manifest recording:
  * repo git SHA + dirty-file list
  * sha256 of every prompt template and every judge rubric, extracted from source
    (AST literal evaluation, not a source-text hash, so reformatting cannot change it)
  * sha256 of the scoring modules
  * judge configuration verbatim, incl. the deployment/snapshot the API reports
  * the exact model identifier the Anthropic API echoes back (pinned snapshot)
  * decoding parameters actually sent, and an explicit list of parameters that
    CANNOT be matched to the six published models, with the API's own error text

Usage:
  python scripts/freeze_manifest.py --out results_sonnet5_run1/MANIFEST.json \
      [--model claude-sonnet-5] [--effort medium] [--no-probe]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def module_constants(path: str, names: list[str]) -> dict:
    """sha256 + length of module-level string constants, by literal value."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    try:
                        v = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    if isinstance(v, str):
                        out[t.id] = {"sha256": sha(v), "chars": len(v)}
    return out


def function_prompt(path: str, fn: str, var: str = "system") -> dict | None:
    """sha256 + length of a `system = (...)` string literal inside a function."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn:
            for st in ast.walk(node):
                if isinstance(st, ast.Assign) and any(
                    getattr(t, "id", "") == var for t in st.targets
                ):
                    try:
                        v = ast.literal_eval(st.value)
                    except Exception:
                        return {"sha256": None, "chars": None,
                                "note": "prompt is an f-string; hashed from source text",
                                "source_sha256": sha(ast.get_source_segment(src, st) or "")}
                    return {"sha256": sha(v), "chars": len(v)}
    return None


def git(*a) -> str:
    try:
        return subprocess.check_output(["git", "-C", ROOT, *a], text=True).strip()
    except Exception as e:
        return f"<error: {e}>"


def probe_anthropic(model: str) -> dict:
    """Ask the API which snapshot answers to this id, and record the params it rejects."""
    out: dict = {"requested_model_id": model}
    try:
        import anthropic
        c = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        r = c.messages.create(model=model, max_tokens=8,
                              messages=[{"role": "user", "content": "OK"}])
        out["api_reported_model"] = r.model
        out["sdk_version"] = anthropic.__version__
        out["is_pinned_snapshot"] = True
        out["snapshot_note"] = (
            "Claude 4.6-generation and later use dateless model IDs. Per Anthropic's "
            "model-versioning docs the dateless ID IS the pinned snapshot, not a "
            "floating alias; weights for a given ID never change. "
            "https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions"
        )
        for param, val in (("temperature", 0.0), ("top_p", 0.9), ("top_k", 5)):
            try:
                c.messages.create(model=model, max_tokens=8,
                                  messages=[{"role": "user", "content": "OK"}],
                                  **{param: val})
                out.setdefault("accepted_sampling_params", []).append(param)
            except Exception as e:
                out.setdefault("rejected_sampling_params", {})[param] = str(e)[:300]
    except Exception as e:
        out["probe_error"] = f"{type(e).__name__}: {e}"
    return out


def probe_judge() -> dict:
    """Record the judge deployment and the snapshot the Azure endpoint reports."""
    dep = os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    ep = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    out = {
        "judge_model": dep,
        "endpoint_host": ep.split("//")[-1].split("/")[0] if ep else None,
        "api_surface": "OpenAI Responses API with the web_search tool "
                       "(eval.LLMClient._call_responses_api)",
        "tool_choice_leakage": "required",
        "tool_choice_rubric": "auto (default)",
        "two_stage_protocol": [
            "stage 1: judge_leakage  — contamination audit, web search forced",
            "stage 2: judge_frq_combined — 4-dimension rubric, 0-10 each, "
            "frq_score = unweighted mean of the four",
        ],
    }
    try:
        from openai import OpenAI
        c = OpenAI(base_url=ep, api_key=os.environ["AZURE_OPENAI_KEY"])
        r = c.responses.create(model=dep, tools=[{"type": "web_search"}],
                               tool_choice="required",
                               input=[{"role": "user",
                                       "content": "Reply with the single word OK."}])
        out["api_reported_model"] = getattr(r, "model", None)
        out["reachable"] = True
    except Exception as e:
        out["reachable"] = False
        out["probe_error"] = f"{type(e).__name__}: {str(e)[:300]}"
    return out


def probe_openai(model: str) -> dict:
    """Ask the OpenAI API which snapshot answers to this id, and what it rejects."""
    out: dict = {"requested_model_id": model, "provider": "OPENAI"}
    try:
        from openai import OpenAI
        c = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        r = c.chat.completions.create(
            model=model, max_completion_tokens=2000,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}])
        out["api_reported_model"] = r.model
        out["is_pinned_snapshot"] = r.model == model
        try:
            c.chat.completions.create(
                model=model, max_completion_tokens=2000, temperature=0.0,
                messages=[{"role": "user", "content": "OK"}])
            out.setdefault("accepted_sampling_params", []).append("temperature")
        except Exception as e:
            out.setdefault("rejected_sampling_params", {})["temperature"] = str(e)[:300]
        levels = []
        for eff in ("none", "low", "medium", "high", "xhigh", "max"):
            try:
                c.chat.completions.create(
                    model=model, max_completion_tokens=2000, reasoning_effort=eff,
                    messages=[{"role": "user", "content": "OK"}])
                levels.append(eff)
            except Exception:
                pass
        out["accepted_reasoning_effort"] = levels
    except Exception as e:
        out["probe_error"] = f"{type(e).__name__}: {e}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--effort", default=None)
    ap.add_argument("--frq-max-tokens", type=int, default=2048)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--no-probe", action="store_true")
    a = ap.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, ".env"))
    except ImportError:
        pass

    test_llm = os.path.join(ROOT, "scripts", "test_LLM.py")
    evalpy = os.path.join(ROOT, "scripts", "eval.py")
    websearch = os.path.join(ROOT, "scripts", "web_search.py")
    runner = os.path.join(ROOT, "scripts", "run_cusp.py")

    manifest = {
        "manifest_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_label": "sonnet5_run1",
        "corpus_window": "2024-01..2026-03",
        "repo": {
            "git_sha": git("rev-parse", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": git("status", "--porcelain"),
        },
        "datasets": {},
        "prompt_templates": module_constants(
            test_llm,
            ["BINARY_SYSTEM", "MCQ_SYSTEM", "FRQ_SYSTEM", "DATE_SYSTEM",
             "BINARY_SYSTEM_WS", "MCQ_SYSTEM_WS", "DATE_SYSTEM_WS", "FRQ_SYSTEM_WS"],
        ),
        "judge_rubrics": {
            "judge_frq_combined": function_prompt(evalpy, "judge_frq_combined"),
            "judge_leakage": function_prompt(evalpy, "judge_leakage"),
            "judge_mechanistic": function_prompt(evalpy, "judge_mechanistic"),
            "judge_constraint": function_prompt(evalpy, "judge_constraint"),
            "grade_frq_legacy": function_prompt(evalpy, "grade_frq"),
        },
        "code_sha256": {
            "scripts/eval.py": file_sha(evalpy),
            "scripts/test_LLM.py": file_sha(test_llm),
            "scripts/web_search.py": file_sha(websearch),
            "scripts/run_cusp.py": file_sha(runner),
        },
        "scoring_constants": {
            "date_score": "exp(-0.1 * |months between predicted and ground truth|)",
            "frq_scale": "0-10 per dimension; frq_score = mean(alignment, specificity, "
                         "novelty, feasibility); FRQ pass = score >= 5.0",
            "merged_binary": "pooled correct counts: (c_orig + c_pert)/(n_orig + n_pert)",
            "outcome_weight": 0.6,
            "reasoning_weight": 0.4,
            "mcq_shuffle_seed": 42,
        },
        "partition_rule": {
            "field": "publication_date (YYYY-MM) from the benchmark JSONL",
            "main_tables": "pre if pub_month < cutoff_month else post "
                           "(cutoff month counts as POST) — make_latex_tables.py, "
                           "compare_models.py",
            "gap_and_calibration_tables": "post if pub_month > cutoff_month "
                                          "(cutoff month counts as PRE) — "
                                          "filter_ids_by_cutoff in "
                                          "make_web_search_cutoff_table.py",
            "note": "These two conventions differ by one month and BOTH are used in "
                    "the published tables. Each table is reproduced under the "
                    "convention its own generator used, so every Sonnet 5 row is "
                    "comparable with the six published rows in that same table.",
        },
        "model_under_test": {
            "display_name": "Claude Sonnet 5",
            "model_id": a.model,
            "provider": "ANTHROPIC",
            "knowledge_cutoff": "2026-01",
            "training_cutoff": "2026-01",
            "cutoff_source": "https://support.claude.com/en/articles/"
                             "8114494-how-up-to-date-is-claude-s-training-data "
                             "and https://platform.claude.com/docs/en/models/"
                             "sonnet-5/overview (Reliable knowledge cutoff: Jan 2026; "
                             "Training data cutoff: Jan 2026)",
            "released": "2026-06-30",
        },
        "decoding": {
            "temperature": None,
            "top_p": None,
            "top_k": None,
            "effort": a.effort,
            "thinking": "adaptive (always on for this model; not configurable off "
                        "in the way older models were effectively greedy)",
            "max_tokens": a.max_tokens,
            "frq_max_tokens": a.frq_max_tokens,
            "retries": 2,
            "retry_backoff": "2**attempt seconds",
        },
        "unmatchable_parameters": [
            {
                "parameter": "temperature",
                "six_published_models": 0.0,
                "sonnet5": "cannot be sent — HTTP 400 'temperature is deprecated for "
                           "this model'. The model runs at its default sampling "
                           "setting, so it is stochastic where the other six were "
                           "greedy. This is the reason run 1 is executed three times.",
            },
            {
                "parameter": "reasoning/thinking effort",
                "six_published_models": "not exposed; no run recorded a reasoning "
                                        "effort setting",
                "sonnet5": f"adaptive thinking always on; effort pinned to {a.effort!r} "
                           "(API default is 'high')",
            },
            {
                "parameter": "FRQ max_tokens",
                "six_published_models": "250 for Claude Sonnet 4.5 (ANTHROPIC branch), "
                                        "2048 for the five OpenAI/Azure models",
                "sonnet5": f"{a.frq_max_tokens}; note Sonnet 5 uses a newer tokenizer, "
                           "so an identical token cap yields ~26% fewer characters "
                           "than it did for Claude Sonnet 4.5 (~770 vs ~1036 chars)",
            },
        ],
    }

    for label, rel in (("corpus", "archive/data/canonical/merged_validated_cusp_fixed.jsonl"),
                       ("pinned_500_subset", "archive/data/sample/sample_500_stratified.jsonl")):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            manifest["datasets"][label] = {
                "path": rel,
                "sha256": file_sha(p),
                "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
                "n_rows": sum(1 for _ in open(p, encoding="utf-8")),
            }

    if not a.no_probe:
        is_anthropic = a.model.startswith("claude")
        manifest["model_under_test"]["provider"] = "ANTHROPIC" if is_anthropic else "OPENAI"
        manifest["model_under_test"]["api_probe"] = (
            probe_anthropic(a.model) if is_anthropic else probe_openai(a.model))
        manifest["judge"] = probe_judge()
    else:
        manifest["judge"] = probe_judge.__doc__

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"wrote {a.out}")
    print(json.dumps({k: manifest[k] for k in
                      ("repo", "datasets", "prompt_templates", "judge_rubrics")},
                     indent=2)[:2000])


if __name__ == "__main__":
    main()
