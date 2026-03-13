"""
Pointwise flux comparison: L2 and L-infinity errors of numerical solutions vs analytical reference.
All solvers return dict with 'phi1'[ix,iy], 'phi2'[ix,iy], 'x', 'y' arrays.
FDM/FEM: phi[ix, iy], axes = (x_coords, y_coords)
Spectral: phi[ix, iy], axes = (x_nodes, y_nodes) but unsorted (Chebyshev)
"""
import sys
import os
import json
import time
import numpy as np
from scipy.interpolate import RegularGridInterpolator

WORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(WORK_DIR, 'scripts', 'numerical_solver'))
sys.path.insert(0, os.path.join(WORK_DIR, 'baselines', 'fdm'))
sys.path.insert(0, os.path.join(WORK_DIR, 'baselines', 'fem'))
sys.path.insert(0, os.path.join(WORK_DIR, 'baselines', 'spectral'))

from analytical_solver import evaluate_flux
import fdm_solver
import fem_solver
import spectral_solver

# Dense evaluation grid
xs = np.linspace(-0.45, 0.45, 30)
ys = np.linspace(-0.45, 0.45, 30)
XX, YY = np.meshgrid(xs, ys)
xf = XX.flatten()
yf = YY.flatten()

print("Computing analytical reference (N=500)...")
t0 = time.time()
phi1_ref, phi2_ref = evaluate_flux(xf, yf, N_terms=500)
print(f"  Done in {time.time()-t0:.2f}s")

norm1 = float(np.sqrt(np.mean(phi1_ref**2)))
norm2 = float(np.sqrt(np.mean(phi2_ref**2)))

results = {}


def interp_solver(x_axis, y_axis, phi_xy, xq, yq):
    """Interpolate phi[ix,iy] grid (x=rows, y=cols) at query points (xq, yq)."""
    interp = RegularGridInterpolator((x_axis, y_axis), phi_xy, method='linear',
                                     bounds_error=False, fill_value=None)
    return interp(np.column_stack([xq, yq]))


# ── FDM ──────────────────────────────────────────────────────────────────────
print("Running FDM 101x101...")
t0 = time.time()
res_fdm = fdm_solver.solve_fdm(101, 101)
t_fdm = time.time() - t0

phi1_fdm_pts = interp_solver(res_fdm['x'], res_fdm['y'], res_fdm['phi1'], xf, yf)
phi2_fdm_pts = interp_solver(res_fdm['x'], res_fdm['y'], res_fdm['phi2'], xf, yf)

err1 = np.abs(phi1_fdm_pts - phi1_ref)
err2 = np.abs(phi2_fdm_pts - phi2_ref)
results['FDM'] = {
    'phi1_L2_abs': float(np.sqrt(np.mean(err1**2))),
    'phi1_Linf_abs': float(np.max(err1)),
    'phi1_L2_rel': float(np.sqrt(np.mean(err1**2))) / norm1,
    'phi2_L2_abs': float(np.sqrt(np.mean(err2**2))),
    'phi2_Linf_abs': float(np.max(err2)),
    'phi2_L2_rel': float(np.sqrt(np.mean(err2**2))) / norm2,
    'solve_time': t_fdm
}
print(f"  phi1: L2={results['FDM']['phi1_L2_abs']:.3e}, Linf={results['FDM']['phi1_Linf_abs']:.3e}")
print(f"  phi2: L2={results['FDM']['phi2_L2_abs']:.3e}, Linf={results['FDM']['phi2_Linf_abs']:.3e}")

# ── FEM ──────────────────────────────────────────────────────────────────────
print("Running FEM 101x101...")
t0 = time.time()
res_fem = fem_solver.solve_fem(101, 101)
t_fem = time.time() - t0

phi1_fem_pts = interp_solver(res_fem['x'], res_fem['y'], res_fem['phi1'], xf, yf)
phi2_fem_pts = interp_solver(res_fem['x'], res_fem['y'], res_fem['phi2'], xf, yf)

err1 = np.abs(phi1_fem_pts - phi1_ref)
err2 = np.abs(phi2_fem_pts - phi2_ref)
results['FEM'] = {
    'phi1_L2_abs': float(np.sqrt(np.mean(err1**2))),
    'phi1_Linf_abs': float(np.max(err1)),
    'phi1_L2_rel': float(np.sqrt(np.mean(err1**2))) / norm1,
    'phi2_L2_abs': float(np.sqrt(np.mean(err2**2))),
    'phi2_Linf_abs': float(np.max(err2)),
    'phi2_L2_rel': float(np.sqrt(np.mean(err2**2))) / norm2,
    'solve_time': t_fem
}
print(f"  phi1: L2={results['FEM']['phi1_L2_abs']:.3e}, Linf={results['FEM']['phi1_Linf_abs']:.3e}")
print(f"  phi2: L2={results['FEM']['phi2_L2_abs']:.3e}, Linf={results['FEM']['phi2_Linf_abs']:.3e}")

# ── Spectral ──────────────────────────────────────────────────────────────────
print("Running Spectral N=30...")
t0 = time.time()
res_spec = spectral_solver.solve_spectral(30)
t_spec = time.time() - t0

# Sort Chebyshev nodes and reorder phi accordingly
xi_idx = np.argsort(res_spec['x'])
yi_idx = np.argsort(res_spec['y'])
x_spec = res_spec['x'][xi_idx]
y_spec = res_spec['y'][yi_idx]
# phi[ix, iy] -> after sorting rows by x and cols by y
phi1_spec = res_spec['phi1'][np.ix_(xi_idx, yi_idx)]
phi2_spec = res_spec['phi2'][np.ix_(xi_idx, yi_idx)]

phi1_spec_pts = interp_solver(x_spec, y_spec, phi1_spec, xf, yf)
phi2_spec_pts = interp_solver(x_spec, y_spec, phi2_spec, xf, yf)

err1 = np.abs(phi1_spec_pts - phi1_ref)
err2 = np.abs(phi2_spec_pts - phi2_ref)
results['Spectral'] = {
    'phi1_L2_abs': float(np.sqrt(np.mean(err1**2))),
    'phi1_Linf_abs': float(np.max(err1)),
    'phi1_L2_rel': float(np.sqrt(np.mean(err1**2))) / norm1,
    'phi2_L2_abs': float(np.sqrt(np.mean(err2**2))),
    'phi2_Linf_abs': float(np.max(err2)),
    'phi2_L2_rel': float(np.sqrt(np.mean(err2**2))) / norm2,
    'solve_time': t_spec
}
print(f"  phi1: L2={results['Spectral']['phi1_L2_abs']:.3e}, Linf={results['Spectral']['phi1_Linf_abs']:.3e}")
print(f"  phi2: L2={results['Spectral']['phi2_L2_abs']:.3e}, Linf={results['Spectral']['phi2_Linf_abs']:.3e}")

out_path = os.path.join(WORK_DIR, 'baselines', 'results', 'pointwise_errors.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
