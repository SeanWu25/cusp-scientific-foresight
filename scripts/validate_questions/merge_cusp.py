#!/usr/bin/env python3

import os, json, glob
from collections import defaultdict

import os; from pathlib import Path; BASE_DIR = os.environ.get("CUSP_DATA_DIR", str(Path(__file__).parent.parent.parent / "data" / "source"))
SOURCES = ["top_ai_papers", "hugging_face_top_ai_papers", "nature", "science", "cell", "leaderboard_questions"]

def find_categorized_jsonl(source_dir):
    files = glob.glob(os.path.join(source_dir, "*categorized.jsonl"))
    if files: return files[0]
    return None

def main():
    merged_data = []
    
    KEEP_AREAS = {
        "Biology",
        "Artificial Intelligence",
        "Medicine",
        "Neuroscience",
        "Physics",
        "Materials Science",
        "Environmental Science",
        "Chemistry",
    }

    overall_stats = {
        "pre": {"total": 0, "binary": 0, "binary_perturb": 0, "mcq": 0, "frq": 0, "date": 0},
        "post": {"total": 0, "binary": 0, "binary_perturb": 0, "mcq": 0, "frq": 0, "date": 0}
    }

    print(f"{'Source':<30} | {'Pre-Val (Tot/Bin/BinP/MCQ/FRQ/Date)':<35} | {'Post-Val (Tot/Bin/BinP/MCQ/FRQ/Date)'}")
    print("-" * 110)

    for source in SOURCES:
        source_dir = os.path.join(BASE_DIR, source)
        if not os.path.exists(source_dir):
            continue
        
        orig_file = find_categorized_jsonl(source_dir)
        if not orig_file:
            continue

        # Load orig
        papers = {}
        with open(orig_file) as f:
            for line in f:
                if not line.strip(): continue
                row = json.loads(line)
                papers[row["id"]] = row

        # Initialize tracking maps
        removed_map = defaultdict(set)

        # 1. Binary removed
        bin_rem = os.path.join(source_dir, "binary_outputs", "cusp_binary.removed.jsonl")
        if os.path.exists(bin_rem):
            with open(bin_rem) as f:
                for line in f:
                    if not line.strip(): continue
                    d = json.loads(line)
                    for r in d.get("removed_fields", d.get("removed", [])): removed_map[d["id"]].add(r)
        
        # 2. MCQ removed
        mcq_rem = os.path.join(source_dir, "mcq_outputs", "cusp_mcq.removed.jsonl")
        if os.path.exists(mcq_rem):
            with open(mcq_rem) as f:
                for line in f:
                    if not line.strip(): continue
                    d = json.loads(line)
                    for r in d.get("removed_fields", d.get("removed", [])): removed_map[d["id"]].add(r)

        # 3. FRQ removed
        frq_rem = os.path.join(source_dir, "frq_outputs", "cusp_frq.removed.jsonl")
        if os.path.exists(frq_rem):
            with open(frq_rem) as f:
                for line in f:
                    if not line.strip(): continue
                    d = json.loads(line)
                    for r in d.get("removed_fields", d.get("removed", [])): removed_map[d["id"]].add(r)

        # 4. Date Pred removed
        date_rem = os.path.join(source_dir, "date_pred_outputs", "cusp_date_pred.removed.jsonl")
        if os.path.exists(date_rem):
            with open(date_rem) as f:
                for line in f:
                    if not line.strip(): continue
                    d = json.loads(line)
                    for r in d.get("removed_fields", d.get("removed", [])): removed_map[d["id"]].add(r)

        # Stats tracking for this source
        s_pre = {"total": len(papers), "binary": 0, "binary_perturb": 0, "mcq": 0, "frq": 0, "date": 0}
        s_post = {"total": 0, "binary": 0, "binary_perturb": 0, "mcq": 0, "frq": 0, "date": 0}

        for pid, row in papers.items():
            main_area = row.get("main_area", "Other")
            if main_area not in KEEP_AREAS:
                row["main_area"] = "Other"
                
            pub_date = str(row.get("publication_date", ""))
            year = ""
            if len(pub_date) >= 4 and pub_date[:4].isdigit():
                year = pub_date[:4]
                
            if year < "2024":
                continue

            pre_bin = "binary_question" in row
            pre_bin_p = "binary_question_perturbed" in row
            pre_mcq = "mcq_question" in row
            pre_frq = "frq_prompt" in row
            pre_date = "date_prediction_prompt" in row

            if pre_bin: s_pre["binary"] += 1
            if pre_bin_p: s_pre["binary_perturb"] += 1
            if pre_mcq: s_pre["mcq"] += 1
            if pre_frq: s_pre["frq"] += 1
            if pre_date: s_pre["date"] += 1

            # apply removals
            rems = removed_map.get(pid, set())
            
            # Ensure MCQ fields are totally wiped if partially removed
            if "mcq_question" in rems or "mcq_choices" in rems or "mcq_answer_key" in rems:
                rems.update(["mcq_question", "mcq_choices", "mcq_answer_key"])
                
            for r in rems:
                row.pop(r, None)

            post_bin = "binary_question" in row
            post_bin_p = "binary_question_perturbed" in row
            post_mcq = "mcq_question" in row
            post_frq = "frq_prompt" in row
            post_date = "date_prediction_prompt" in row

            if post_bin: s_post["binary"] += 1
            if post_bin_p: s_post["binary_perturb"] += 1
            if post_mcq: s_post["mcq"] += 1
            if post_frq: s_post["frq"] += 1
            if post_date: s_post["date"] += 1

            if post_bin or post_bin_p or post_mcq or post_frq or post_date:
                s_post["total"] += 1
                row["source"] = source
                merged_data.append(row)

        str_pre = f"{s_pre['total']}/{s_pre['binary']}/{s_pre['binary_perturb']}/{s_pre['mcq']}/{s_pre['frq']}/{s_pre['date']}"
        str_post = f"{s_post['total']}/{s_post['binary']}/{s_post['binary_perturb']}/{s_post['mcq']}/{s_post['frq']}/{s_post['date']}"
        print(f"{source:<30} | {str_pre:<35} | {str_post}")

        # Update overall
        for k in overall_stats["pre"]:
            overall_stats["pre"][k] += s_pre[k]
            overall_stats["post"][k] += s_post[k]

    print("-" * 110)
    str_pre = f"{overall_stats['pre']['total']}/{overall_stats['pre']['binary']}/{overall_stats['pre']['binary_perturb']}/{overall_stats['pre']['mcq']}/{overall_stats['pre']['frq']}/{overall_stats['pre']['date']}"
    str_post = f"{overall_stats['post']['total']}/{overall_stats['post']['binary']}/{overall_stats['post']['binary_perturb']}/{overall_stats['post']['mcq']}/{overall_stats['post']['frq']}/{overall_stats['post']['date']}"
    print(f"{'OVERALL':<30} | {str_pre:<35} | {str_post}")

    sum_pre_qs = sum([overall_stats['pre']['binary'], overall_stats['pre']['binary_perturb'], overall_stats['pre']['mcq'], overall_stats['pre']['frq'], overall_stats['pre']['date']])
    sum_post_qs = sum([overall_stats['post']['binary'], overall_stats['post']['binary_perturb'], overall_stats['post']['mcq'], overall_stats['post']['frq'], overall_stats['post']['date']])
    
    print(f"\nTotal Questions Before Validation: {sum_pre_qs}")
    print(f"Total Questions REMAINING After Validation: {sum_post_qs}")

    out_dir = os.path.join(BASE_DIR, "CUSP")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "merged_validated_cusp.jsonl")
    with open(out_file, "w") as f:
        for row in merged_data:
            f.write(json.dumps(row) + "\n")
    print(f"\nSaved {len(merged_data)} completely finalized items to {out_file}")

if __name__ == "__main__":
    main()
