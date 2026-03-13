"""
Spectral convergence study: how does spectral residual decrease with N?
"""
import sys
import os
import json
import time
import numpy as np

WORK_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.join(WORK_DIR, 'baselines', 'spectral'))
import spectral_solver

N_values = [10, 15, 20, 25, 30, 40, 50]
results = []

print(f"{'N':>4}  {'PDE Residual':>14}  {'BC Residual':>12}  {'Time (s)':>10}")
print("-" * 48)

for N in N_values:
    t0 = time.time()
    res = spectral_solver.solve_spectral(N)
    t_solve = time.time() - t0

    # Compute PDE residual using spectral solver's own function
    pde_res = spectral_solver.compute_pde_residual(res)
    bc_res = spectral_solver.compute_bc_residual(res)

    max_pde = max(pde_res['max_R1'], pde_res['max_R2'])
    max_bc = bc_res['max_bc'] if isinstance(bc_res, dict) else float(bc_res)

    results.append({
        "N": N,
        "max_pde_residual": float(max_pde),
        "max_bc_residual": float(max_bc),
        "solve_time": t_solve
    })
    print(f"{N:>4}  {max_pde:>14.3e}  {max_bc:>12.3e}  {t_solve:>10.3f}")

out_path = os.path.join(WORK_DIR, 'baselines', 'results', 'spectral_convergence.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
