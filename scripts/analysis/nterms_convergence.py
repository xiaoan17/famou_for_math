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
from analytical_solver import evaluate_flux, evaluate_derivatives

D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015
A11 = SIGMA_R - NU * SIGMA_F1
A12 = -NU * SIGMA_F2
A21 = -SIGMA_12
A22 = SIGMA_A2

def compute_pde_bc_residual(N_terms):
    """Compute max PDE and BC residuals over a 20x20 dense grid."""
    # Dense evaluation grid
    xs = np.linspace(-0.45, 0.45, 20)
    ys = np.linspace(-0.45, 0.45, 20)
    h = 1e-5

    max_pde = 0.0
    for x in xs:
        for y in ys:
            p1c = evaluate_flux(x, y, group=1, N_terms=N_terms)
            p2c = evaluate_flux(x, y, group=2, N_terms=N_terms)
            lap1 = ((evaluate_flux(x+h, y, 1, N_terms) - 2*p1c + evaluate_flux(x-h, y, 1, N_terms))/h**2
                  + (evaluate_flux(x, y+h, 1, N_terms) - 2*p1c + evaluate_flux(x, y-h, 1, N_terms))/h**2)
            lap2 = ((evaluate_flux(x+h, y, 2, N_terms) - 2*p2c + evaluate_flux(x-h, y, 2, N_terms))/h**2
                  + (evaluate_flux(x, y+h, 2, N_terms) - 2*p2c + evaluate_flux(x, y-h, 2, N_terms))/h**2)
            R1 = abs(-D1*lap1 + A11*p1c + A12*p2c)
            R2 = abs(-D2*lap2 + A21*p1c + A22*p2c)
            max_pde = max(max_pde, R1, R2)

    # BC residuals
    max_bc = 0.0
    yv_list = np.linspace(-0.45, 0.45, 10)
    for yv in yv_list:
        dx1 = (evaluate_flux(-0.5+h, yv, 1, N_terms) - evaluate_flux(-0.5-h, yv, 1, N_terms)) / (2*h)
        dx2 = (evaluate_flux(-0.5+h, yv, 2, N_terms) - evaluate_flux(-0.5-h, yv, 2, N_terms)) / (2*h)
        max_bc = max(max_bc, abs(-D1*dx1 - yv), abs(-D2*dx2 - yv))
    for yv in yv_list:
        dx1 = (evaluate_flux(0.5+h, yv, 1, N_terms) - evaluate_flux(0.5-h, yv, 1, N_terms)) / (2*h)
        dx2 = (evaluate_flux(0.5+h, yv, 2, N_terms) - evaluate_flux(0.5-h, yv, 2, N_terms)) / (2*h)
        max_bc = max(max_bc, abs(-D1*dx1), abs(-D2*dx2))
    xv_list = np.linspace(-0.45, 0.45, 10)
    for xv in xv_list:
        dy1 = (evaluate_flux(xv, 0.5+h, 1, N_terms) - evaluate_flux(xv, 0.5-h, 1, N_terms)) / (2*h)
        dy2 = (evaluate_flux(xv, 0.5+h, 2, N_terms) - evaluate_flux(xv, 0.5-h, 2, N_terms)) / (2*h)
        max_bc = max(max_bc, abs(-D1*dy1), abs(-D2*dy2))
    for xv in xv_list:
        dy1 = (evaluate_flux(xv, -0.5+h, 1, N_terms) - evaluate_flux(xv, -0.5-h, 1, N_terms)) / (2*h)
        dy2 = (evaluate_flux(xv, -0.5+h, 2, N_terms) - evaluate_flux(xv, -0.5-h, 2, N_terms)) / (2*h)
        max_bc = max(max_bc, abs(-D1*dy1), abs(-D2*dy2))

    return max_pde, max_bc


N_values = [5, 10, 25, 50, 100, 200, 500]
results = []

for N in N_values:
    t0 = time.time()
    max_pde, max_bc = compute_pde_bc_residual(N)
    elapsed = time.time() - t0
    results.append({
        "N_terms": N,
        "max_pde_residual": float(max_pde),
        "max_bc_residual": float(max_bc),
        "wall_time": float(elapsed)
    })
    print(f"N={N:4d}: PDE={max_pde:.2e}  BC={max_bc:.2e}  t={elapsed:.3f}s")

out_path = os.path.join(os.path.dirname(__file__), '../../baselines/results/nterms_convergence.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
