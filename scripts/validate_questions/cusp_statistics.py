#!/usr/bin/env python3

import os, json
from collections import defaultdict
import statistics
import datetime
import re

import os
from pathlib import Path
_REPO = Path(__file__).parent.parent.parent
DATA_PATH = os.environ.get(
    "CUSP_DATASET_PATH",
    str(_REPO / "data" / "canonical" / "merged_validated_cusp_fixed.jsonl"),
)

def get_word_count(text):
    if not text:
        return 0
    # simple word count split by whitespace
    return len(str(text).split())

def parse_date(date_str):
    """Attempts to parse YYYY or YYYY-MM into a sortable tuple (YYYY, MM)"""
    if not date_str: return None
    date_str = str(date_str).strip()
    match = re.search(r'\b(20\d{2})(?:-(\d{1,2}))?\b', date_str)
    if match:
        year = int(match.group(1))
        month = int(match.group(2)) if match.group(2) else 1
        return (year, month)
    # fallbacks
    if len(date_str) >= 4 and date_str[:4].isdigit():
        return (int(date_str[:4]), 1)
    return None

def main():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Could not find dataset at {DATA_PATH}")
        return

    papers = []
    with open(DATA_PATH, "r") as f:
        for line in f:
            if not line.strip(): continue
            papers.append(json.loads(line))
            
    print("======================================================")
    print(f" CUSP BENCHMARK STATISTICS (n={len(papers)} milestones)")
    print("======================================================\n")

    # ---------------------------------------------------------
    # 1. Temporal Statistics
    # ---------------------------------------------------------
    dates = []
    for p in papers:
        d = parse_date(p.get("publication_date", ""))
        if d: dates.append(d)
        
    dates.sort()
    
    months_mapped = defaultdict(int)
    for (y, m) in dates:
        months_mapped[f"{y}-{m:02d}"] += 1

    if dates:
        min_date = dates[0]
        max_date = dates[-1]
        span_months = (max_date[0] - min_date[0]) * 12 + (max_date[1] - min_date[1]) + 1
    else:
        span_months = 0
        
    monthly_counts = list(months_mapped.values())
    mean_monthly = statistics.mean(monthly_counts) if monthly_counts else 0
    std_monthly = statistics.stdev(monthly_counts) if len(monthly_counts) > 1 else 0

    print("📊 Temporal Statistics")
    if dates:
        print(f"  - Time span of dataset: {min_date[0]}-{min_date[1]:02d} to {max_date[0]}-{max_date[1]:02d}")
    print(f"  - Total duration (number of months): {span_months} active months")
    print(f"  - Total milestones (papers): {len(dates)} with valid dates")
    print(f"  - Mean number of milestones per month: {mean_monthly:.2f}")
    print(f"  - Variability (std dev) per month: {std_monthly:.2f}")
    print(f"  - Temporal coverage: {len(monthly_counts)} unique months represented")
    print(f"  - Update mechanism: Dynamic / Semi-Live benchmark (auto-generated from continuous API scraping)")
    print()

    # ---------------------------------------------------------
    # 2. Task Composition Statistics
    # ---------------------------------------------------------
    bin_c = sum(1 for p in papers if "binary_question" in p)
    bin_p_c = sum(1 for p in papers if "binary_question_perturbed" in p)
    mcq_c = sum(1 for p in papers if "mcq_question" in p)
    frq_c = sum(1 for p in papers if "frq_prompt" in p)
    date_c = sum(1 for p in papers if "date_prediction_prompt" in p)
    
    total_tasks = bin_c + bin_p_c + mcq_c + frq_c + date_c

    # Completeness (number of tasks available per paper)
    task_counts_per_paper = []
    for p in papers:
        c = 0
        if "binary_question" in p: c += 1
        if "binary_question_perturbed" in p: c += 1
        if "mcq_question" in p: c += 1
        if "frq_prompt" in p: c += 1
        if "date_prediction_prompt" in p: c += 1
        task_counts_per_paper.append(c)
        
    completeness_dist = defaultdict(int)
    for c in task_counts_per_paper:
        completeness_dist[c] += 1
        
    print("📊 Task Composition Statistics")
    print(f"  - Total verified task instances: {total_tasks}")
    print(f"  - Number of base milestones (papers): {len(papers)}")
    print(f"  - Number of distinct task types: 5")
    print(f"  - Task distribution:")
    print(f"      * Multiple-Choice (MCQ): {mcq_c}")
    print(f"      * Free-Response (FRQ): {frq_c}")
    print(f"      * Binary Forecasting: {bin_c}")
    print(f"      * Perturbed Binary: {bin_p_c}")
    print(f"      * Date Prediction: {date_c}")
    print(f"  - Completeness density per milestone:")
    for k in sorted(completeness_dist.keys(), reverse=True):
        print(f"      * {k} tasks available: {completeness_dist[k]} papers ({completeness_dist[k]/len(papers)*100:.1f}%)")
    print(f"  - Primary reason for task omission: Strict LLM-as-a-judge validation filtering (unverifiable outcomes, lack of faithfulness, or logical perturbation failures).")
    print()

    # ---------------------------------------------------------
    # 3. Linguistic / Complexity Statistics
    # ---------------------------------------------------------
    bin_lengths = [get_word_count(p["binary_question"]) for p in papers if "binary_question" in p]
    mcq_lengths = [get_word_count(p["mcq_question"]) for p in papers if "mcq_question" in p]
    frq_lengths = [get_word_count(p["frq_prompt"]) for p in papers if "frq_prompt" in p]
    prob_lengths = [get_word_count(p.get("problem_statement", "")) for p in papers if p.get("problem_statement")]

    def get_stats(arr):
        if not arr: return 0, 0
        if len(arr) == 1: return arr[0], 0
        return statistics.mean(arr), statistics.variance(arr)

    bin_m, bin_v = get_stats(bin_lengths)
    mcq_m, mcq_v = get_stats(mcq_lengths)
    frq_m, frq_v = get_stats(frq_lengths)
    prob_m, prob_v = get_stats(prob_lengths)

    print("📊 Linguistic / Complexity Statistics (Word Counts)")
    print(f"  - Binary Questions:      Mean = {bin_m:.1f} words  |  Var = {bin_v:.1f}")
    print(f"  - MCQ Questions:         Mean = {mcq_m:.1f} words  |  Var = {mcq_v:.1f}")
    print(f"  - FRQ Prompts:           Mean = {frq_m:.1f} words  |  Var = {frq_v:.1f}")
    print(f"  - Problem Statements:    Mean = {prob_m:.1f} words  |  Var = {prob_v:.1f}")
    print(f"  - Structural differences observations:")
    print(f"      * Problem statements provide extensive scientific context prior to question stems.")
    print(f"      * FRQs represent the most free-form, unconstrained cognitive complexity.")
    print(f"      * MCQs demand exact discriminative reasoning over distractors.")
    print()

    # ---------------------------------------------------------
    # 4. Diversity Statistics
    # ---------------------------------------------------------
    domains = defaultdict(int)
    subs = set()
    
    for p in papers:
        domains[p.get("main_area", "Other")] += 1
        sub = p.get("sub_categories")
        if sub:
            if isinstance(sub, list):
                for s in sub: subs.add(s)
            else:
                for s in str(sub).split(","):
                    subs.add(s.strip())

    print("📊 Diversity Statistics")
    print(f"  - Number of top-level domains: {len(domains)}")
    print(f"  - Number of distinct subcategories identified: {len(subs)}")
    print(f"  - Distribution across main domains:")
    for d, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        print(f"      * {d}: {count} papers")
    print(f"  - Coverage & Specialization: Highly specialized multi-disciplinary focus spanning hard sciences, computing, and clinical medicine.")
    print("======================================================\n")

if __name__ == "__main__":
    main()
