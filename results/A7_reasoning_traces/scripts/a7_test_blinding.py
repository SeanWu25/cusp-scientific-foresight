"""a7_test_blinding.py — the blinding guarantee, tested. Run before any coding call."""
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a7_common as C, a7_prompts as P
ids = {r["trace_id"] for r in json.load(open(C.STUDY / "coding_sample.json"))["traces"]}
tr = [r for r in C.iter_traces(lambda r: r["trace_id"] in ids)]
rng = random.Random(2); sub = rng.sample(tr, 2000)
ok = 0
for r in sub:
    s, u = P.code_prompt(r)
    if r["task"] in ("binary", "binary_perturbed", "mcq"): P.faith_prompt(r)
    ok += 1
print(f"[1] {ok} prompts built; reconstruction + identity asserts passed")
fails = 0
for bad in ("model", "condition", "correct", "ground_truth", "parsed_answer"):
    r = dict(sub[0])
    try:
        v = P.blind_view(r); v[bad] = r.get(bad)
        P.assert_blind(r, P.SYSTEM, P.CODE_TEMPLATE.format(task_description=v["task_description"], question=v["question"], passage=v["passage"]), P.CODE_TEMPLATE, v)
        print(f"[2] FAIL: injecting {bad} into the view was not caught"); fails += 1
    except AssertionError:
        pass
print(f"[2] injecting each outcome/identity field into the blind view is caught ({5 - fails}/5)")
try:
    r = dict(sub[0])
    P.assert_blind(r, P.SYSTEM, "Question type: x.\n\n=== QUESTION ===\nq\n\n=== PASSAGE ===\np\nMODEL: GPT-4o", P.CODE_TEMPLATE, P.blind_view(r))
    print("[3] FAIL: tampered user message was not caught"); fails += 1
except AssertionError:
    print("[3] a tampered user message is caught")
try:
    P.assert_blind(sub[0], "you are a helpful assistant", P.CODE_TEMPLATE.format(**{k: P.blind_view(sub[0])[k] for k in ("task_description", "question", "passage")}), P.CODE_TEMPLATE, P.blind_view(sub[0]))
    print("[4] FAIL: a non-study system prompt was not caught"); fails += 1
except AssertionError:
    print("[4] a non-study system prompt is caught")
print("ALL BLINDING TESTS PASSED" if not fails else f"{fails} FAILURES")
