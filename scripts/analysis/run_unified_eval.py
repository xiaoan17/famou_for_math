"""Run famou evaluator.py on all baseline adapters for unified scoring."""
import sys
import os
import json

WORK_DIR = "/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313"
sys.path.insert(0, os.path.join(WORK_DIR, "famou", "task1"))
from evaluator import evaluate  # noqa: E402

baselines = [
    ("FDM (2nd-order, N=200)", os.path.join(WORK_DIR, "baselines/fdm/adapter.py")),
    ("High-order FDM (4th-order, N=200)", os.path.join(WORK_DIR, "baselines/fem/adapter.py")),
    ("Truncated Analytical (K=5)", os.path.join(WORK_DIR, "baselines/truncated/adapter.py")),
    ("PINN (numpy)", os.path.join(WORK_DIR, "baselines/pinn/adapter.py")),
    ("Fourier Analytical (N=30)", os.path.join(WORK_DIR, "famou/task1/init.py")),
]

results = []
for name, path in baselines:
    print(f"\nEvaluating: {name}")
    print(f"  Path: {path}")
    r = evaluate(path)
    r["method"] = name
    results.append(r)
    print(f"  validity: {r['validity']}")
    print(f"  combined_score: {r['combined_score']:.6f}")
    print(f"  cost_time: {r['cost_time']:.4f}s")
    if r["error_info"]:
        print(f"  error: {r['error_info'][:200]}")

# Save unified results
out_path = os.path.join(WORK_DIR, "baselines/results/all_baselines_unified.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved unified results to {out_path}")

# Summary table
print("\n" + "=" * 70)
print(f"{'Method':<40} {'Score':>12} {'Time':>8}")
print("-" * 70)
for r in sorted(results, key=lambda x: x["combined_score"], reverse=True):
    print(f"{r['method']:<40} {r['combined_score']:>12.6f} {r['cost_time']:>7.3f}s")
