"""estimate_cost.py — pre-run token/cost estimate for arms B1, B2, D, E (no API calls)."""
import json, sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C, tiktoken
from run_arm import system_prompts, user_prompt
enc = tiktoken.get_encoding("cl100k_base")
prices = json.load(open(C.STUDY / "prices.json"))
bench, subset = C.load_bench(), C.load_subset()
OUT_TOK = {"B1": 95, "B2": 100, "D": 70, "E": 95}  # per call; base runs averaged ~85 incl. JSON wrapper (measured, cl100k)
models = sys.argv[1].split(",") if len(sys.argv) > 1 else C.PANEL
rows = []
for m in models:
    br = C.load_base_raw(m); pr = prices.get(C.MODELS[m]["deploy"] or "", {})
    for arm in ("B1", "B2", "D", "E"):
        sp = system_prompts(arm); n = C.MODELS[m]["n_sc"] if arm == "D" else 1
        tin = calls = 0
        for i in subset:
            b = bench[i]
            for task, field in (("binary", "binary_question"), ("binary_perturbed", "binary_question_perturbed"), ("mcq", "mcq_question")):
                if b.get(field):
                    up, _, _ = user_prompt(task, b, br.get(i)); tin += (len(enc.encode(sp[task])) + len(enc.encode(up)) + 8) * n; calls += n
        tout = calls * OUT_TOK[arm]
        usd = (tin * pr.get("input_per_m", 0) + tout * pr.get("output_per_m", 0)) / 1e6 if pr else float("nan")
        rows.append((C.MODELS[m]["name"], arm, n, calls, tin, tout, usd))
print(f"{'model':16s}{'arm':5s}{'n':>3s}{'calls':>7s}{'in_tok':>10s}{'out_tok':>9s}{'USD':>8s}")
tot = 0
for r in rows:
    print(f"{r[0]:16s}{r[1]:5s}{r[2]:3d}{r[3]:7d}{r[4]:10,d}{r[5]:9,d}{r[6]:8.2f}"); tot += r[6] if r[6] == r[6] else 0
print(f"TOTAL USD ≈ {tot:.2f}  (prices: {', '.join(k + ' ' + str(v['input_per_m']) + '/' + str(v['output_per_m']) for k, v in prices.items() if not k.startswith('_'))})")
