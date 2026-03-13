"""
Spectral convergence study: how does spectral residual decrease with N?
Uses spectral solver's own interpolate_at for evaluation.
"""
import sys
import os
import json
import time
import numpy as np

WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(WORK_DIR, 'baselines', 'spectral'))
import spectral_solver

# Evaluation points for PDE residual
eval_pts = [(0.0, 0.0), (0.2, 0.2), (-0.2, 0.3), (0.3, -0.3), (-0.3, 0.1), (0.1, -0.4)]

D1, D2 = 1.0, 0.5
A11, A12 = 0.0075, -0.25
A21, A22 = -0.015, 0.1

def pde_residual_at(res, x, y, h=1e-5):
    """Finite-difference PDE residual using solver's interpolate_at."""
    p1c, p2c = spectral_solver.interpolate_at(res, x, y)
    p1xp, _ = spectral_solver.interpolate_at(res, x+h, y)
    p1xm, _ = spectral_solver.interpolate_at(res, x-h, y)
    p1yp, _ = spectral_solver.interpolate_at(res, x, y+h)
    p1ym, _ = spectral_solver.interpolate_at(res, x, y-h)
    _, p2xp = spectral_solver.interpolate_at(res, x+h, y)
    _, p2xm = spectral_solver.interpolate_at(res, x-h, y)
    _, p2yp = spectral_solver.interpolate_at(res, x, y+h)
    _, p2ym = spectral_solver.interpolate_at(res, x, y-h)
    lap1 = (p1xp - 2*p1c + p1xm)/h**2 + (p1yp - 2*p1c + p1ym)/h**2
    lap2 = (p2xp - 2*p2c + p2xm)/h**2 + (p2yp - 2*p2c + p2ym)/h**2
    R1 = abs(-D1*lap1 + A11*p1c + A12*p2c)
    R2 = abs(-D2*lap2 + A21*p1c + A22*p2c)
    return max(R1, R2)

N_values = [10, 15, 20, 25, 30, 40, 50]
results = []

print(f"{'N':>4}  {'PDE Residual':>14}  {'BC Residual':>12}  {'Time (s)':>10}")
print("-" * 48)

for N in N_values:
    t0 = time.time()
    res = spectral_solver.solve_spectral(N)
    t_solve = time.time() - t0

    # PDE residual via interpolation at eval_pts
    max_pde = max(pde_residual_at(res, x, y) for x, y in eval_pts)

    # BC residual
    bc_dict = spectral_solver.compute_bc_residual(res)
    max_bc = max(
        bc_dict.get('max_left_R1', 0), bc_dict.get('max_left_R2', 0),
        bc_dict.get('max_right_R1', 0), bc_dict.get('max_right_R2', 0),
        bc_dict.get('max_top_R1', 0), bc_dict.get('max_top_R2', 0),
        bc_dict.get('max_bottom_R1', 0), bc_dict.get('max_bottom_R2', 0)
    ) if isinstance(bc_dict, dict) else float(bc_dict)

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
