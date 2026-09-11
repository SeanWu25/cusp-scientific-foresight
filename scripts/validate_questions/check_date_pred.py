#!/usr/bin/env python3

import argparse, json, os
from tqdm import tqdm

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to the original dataset JSONL")
    p.add_argument("--binary-removed", required=True, help="Path to cusp_binary.removed.jsonl")
    p.add_argument("--output", required=True, help="Base path for date_pred outputs")
    return p.parse_args()

def output_paths(base):
    base = base.replace(".jsonl", "")
    return (
        base + ".full.jsonl",
        base + ".cleaned.jsonl",
        base + ".removed.jsonl"
    )

def main():
    args = parse_args()
    
    # 1. Load the rejected binary reasons
    binary_rejections = {}
    if os.path.exists(args.binary_removed):
        with open(args.binary_removed) as f:
            for line in f:
                if not line.strip(): continue
                data = json.loads(line)
                # Ensure we only track actually rejected ones
                rems = data.get("removed_fields", data.get("removed", []))
                if "binary_question" in rems:
                    binary_rejections[data["id"]] = data
    else:
        print(f"Warning: {args.binary_removed} not found. Assuming no binary rejections.")

    full_path, clean_path, removed_path = output_paths(args.output)
    
    if os.path.dirname(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(args.input) as fin, \
         open(full_path, "w") as f_full, \
         open(clean_path, "w") as f_clean, \
         open(removed_path, "w") as f_removed:

        for line in tqdm(fin, desc="Date Pred Verification"):
            if not line.strip(): continue
            row = json.loads(line)
            row_id = row.get("id")

            # -------------------
            # CHECK AGAINST BINARY
            # -------------------
            if row_id in binary_rejections:
                overall = "reject"
                judge = binary_rejections[row_id]
            else:
                overall = "accept"
                judge = {"verdict": "pass", "reason": "Binary was accepted"}

            row["date_pred_judge"] = {
                "overall_verdict": overall,
                "reason_copied_from_binary": judge
            }

            # -------------------
            # FIELD REMOVAL
            # -------------------
            removed = []
            if overall != "accept":
                removed.extend(["date_prediction_prompt", "ground_truth_date"])

            clean = dict(row)
            for r in removed:
                clean.pop(r, None)

            # -------------------
            # WRITE
            # -------------------
            f_full.write(json.dumps(row)+"\n")
            f_clean.write(json.dumps(clean)+"\n")
            if overall != "accept":
                f_removed.write(json.dumps({
                    "id": row_id,
                    "removed": removed,
                    "judge": judge
                })+"\n")

    print(f"Done. Rejected {len(binary_rejections)} date prediction questions based on binary validation.")

if __name__ == "__main__":
    main()
