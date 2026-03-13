"""
N_terms convergence study for the analytical solution.
Shows how PDE residual, BC residual, and wall time vary with N_terms.
"""
import sys
import os
import json
import time
import numpy as np

# Add numerical_solver to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'numerical_solver'))
from analytical_solver import evaluate_flux

D1 = 1.0
D2 = 0.5
A11 = 0.0075
A12 = -0.25
A21 = -0.015
A22 = 0.1


def eval_at(x, y, N_terms):
    """Return (phi1, phi2) as scalars."""
    p1, p2 = evaluate_flux(np.array([x]), np.array([y]), N_terms=N_terms)
    return float(p1[0]), float(p2[0])


def compute_residuals(N_terms):
    """Compute max PDE and BC residuals over dense grid."""
    h = 1e-5
    # 15x15 interior grid
    xs = np.linspace(-0.45, 0.45, 15)
    ys = np.linspace(-0.45, 0.45, 15)
    max_pde = 0.0

    for x in xs:
        for y in ys:
            p1c, p2c = eval_at(x, y, N_terms)
            lap1 = ((eval_at(x+h,y,N_terms)[0] - 2*p1c + eval_at(x-h,y,N_terms)[0])/h**2
                  + (eval_at(x,y+h,N_terms)[0] - 2*p1c + eval_at(x,y-h,N_terms)[0])/h**2)
            lap2 = ((eval_at(x+h,y,N_terms)[1] - 2*p2c + eval_at(x-h,y,N_terms)[1])/h**2
                  + (eval_at(x,y+h,N_terms)[1] - 2*p2c + eval_at(x,y-h,N_terms)[1])/h**2)
            R1 = abs(-D1*lap1 + A11*p1c + A12*p2c)
            R2 = abs(-D2*lap2 + A21*p1c + A22*p2c)
            max_pde = max(max_pde, R1, R2)

    max_bc = 0.0
    yv_list = np.linspace(-0.45, 0.45, 10)
    for yv in yv_list:
        dx1 = (eval_at(-0.5+h, yv, N_terms)[0] - eval_at(-0.5-h, yv, N_terms)[0]) / (2*h)
        dx2 = (eval_at(-0.5+h, yv, N_terms)[1] - eval_at(-0.5-h, yv, N_terms)[1]) / (2*h)
        max_bc = max(max_bc, abs(-D1*dx1 - yv), abs(-D2*dx2 - yv))
    for yv in yv_list:
        dx1 = (eval_at(0.5+h, yv, N_terms)[0] - eval_at(0.5-h, yv, N_terms)[0]) / (2*h)
        dx2 = (eval_at(0.5+h, yv, N_terms)[1] - eval_at(0.5-h, yv, N_terms)[1]) / (2*h)
        max_bc = max(max_bc, abs(-D1*dx1), abs(-D2*dx2))
    xv_list = np.linspace(-0.45, 0.45, 10)
    for xv in xv_list:
        dy1 = (eval_at(xv, 0.5+h, N_terms)[0] - eval_at(xv, 0.5-h, N_terms)[0]) / (2*h)
        dy2 = (eval_at(xv, 0.5+h, N_terms)[1] - eval_at(xv, 0.5-h, N_terms)[1]) / (2*h)
        max_bc = max(max_bc, abs(-D1*dy1), abs(-D2*dy2))
    for xv in xv_list:
        dy1 = (eval_at(xv, -0.5+h, N_terms)[0] - eval_at(xv, -0.5-h, N_terms)[0]) / (2*h)
        dy2 = (eval_at(xv, -0.5+h, N_terms)[1] - eval_at(xv, -0.5-h, N_terms)[1]) / (2*h)
        max_bc = max(max_bc, abs(-D1*dy1), abs(-D2*dy2))

    return max_pde, max_bc


N_values = [5, 10, 25, 50, 100, 200, 500]
results = []

print(f"{'N':>6}  {'PDE Residual':>14}  {'BC Residual':>12}  {'Time (s)':>10}")
print("-" * 52)
for N in N_values:
    t0 = time.time()
    max_pde, max_bc = compute_residuals(N)
    elapsed = time.time() - t0
    results.append({
        "N_terms": N,
        "max_pde_residual": float(max_pde),
        "max_bc_residual": float(max_bc),
        "wall_time": float(elapsed)
    })
    print(f"{N:>6}  {max_pde:>14.3e}  {max_bc:>12.3e}  {elapsed:>10.3f}")

out_path = os.path.join(os.path.dirname(__file__), '../../baselines/results/nterms_convergence.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
