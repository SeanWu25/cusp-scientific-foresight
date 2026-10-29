"""run_no_v4pro.py — rerun the A4 horizon study WITHOUT DeepSeek-V4-Pro (Reviewer 1 c4 request, 2026-10-18).
Does not modify any shared file: outputs go to horizon_study/tables_no_v4pro/ (and figures_no_v4pro/).
  python horizon_study/run_no_v4pro.py main     # run_all.py stages
  python horizon_study/run_no_v4pro.py bincoef  # binned_coef.py (reviewer's bin-dummy model)
  python horizon_study/run_no_v4pro.py split    # run_split.py stages
Each mode must run in its own process (run_split patches module globals on import)."""
import sys, time
from pathlib import Path
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import data as D
D.MODELS.pop("dsv4pro"); D.MODEL_ORDER[:] = [m for m in D.MODEL_ORDER if m != "dsv4pro"]
OUT = H / "tables_no_v4pro"; FIG = H / "figures_no_v4pro"; OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
mode = sys.argv[1]
ev = D.load_events()
if mode == "main":
    import run_all as R; R.T = OUT
    for name, fn in R.STAGES.items():
        t = time.time(); print(f"== {name}", file=sys.stderr, flush=True); fn(ev); print(f"== {name} done {time.time()-t:.0f}s", file=sys.stderr, flush=True)
elif mode == "bincoef":
    import binned_coef as BC; BC.T = OUT; BC.F = FIG; BC.run()
elif mode == "split":
    import run_split as RS
    (OUT / "split").mkdir(exist_ok=True); (FIG / "split").mkdir(exist_ok=True)
    RS.T = OUT / "split"; RS.F = FIG / "split"; RS.R.T = RS.T; RS.BC.T = RS.T; RS.BC.F = RS.F
    for name, fn in RS.STAGES.items():
        t = time.time(); print(f"== split {name}", file=sys.stderr, flush=True); fn(ev); print(f"== split {name} done {time.time()-t:.0f}s", file=sys.stderr, flush=True)
