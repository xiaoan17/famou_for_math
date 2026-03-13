"""
Pointwise flux comparison: L2 and L-infinity errors of numerical solutions vs analytical reference.
Tests FDM, FEM, Spectral against the analytical solution at a dense grid.
"""
import sys
import os
import json
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'numerical_solver'))
from analytical_solver import evaluate_flux

# Dense evaluation grid
xs = np.linspace(-0.45, 0.45, 30)
ys = np.linspace(-0.45, 0.45, 30)
XX, YY = np.meshgrid(xs, ys)
xf = XX.flatten()
yf = YY.flatten()

print("Computing analytical reference (N=500)...")
t0 = time.time()
phi1_ref, phi2_ref = evaluate_flux(xf, yf, N_terms=500)
print(f"  Reference computed in {time.time()-t0:.2f}s")

results = {}

# ── FDM ──────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'baselines', 'fdm'))
try:
    import fdm_solver
    print("Running FDM 101x101...")
    t0 = time.time()
    phi1_fdm, phi2_fdm = fdm_solver.solve()
    t_fdm = time.time() - t0
    # Interpolate FDM to evaluation grid
    from scipy.interpolate import RegularGridInterpolator
    N = phi1_fdm.shape[0]
    grid_x = np.linspace(-0.5, 0.5, N)
    grid_y = np.linspace(-0.5, 0.5, N)
    interp1 = RegularGridInterpolator((grid_y, grid_x), phi1_fdm, method='linear')
    interp2 = RegularGridInterpolator((grid_y, grid_x), phi2_fdm, method='linear')
    pts = np.column_stack([yf, xf])
    phi1_fdm_pts = interp1(pts)
    phi2_fdm_pts = interp2(pts)
    err1 = np.abs(phi1_fdm_pts - phi1_ref)
    err2 = np.abs(phi2_fdm_pts - phi2_ref)
    l2_1 = float(np.sqrt(np.mean(err1**2)))
    linf_1 = float(np.max(err1))
    l2_2 = float(np.sqrt(np.mean(err2**2)))
    linf_2 = float(np.max(err2))
    norm1 = float(np.sqrt(np.mean(phi1_ref**2)))
    norm2 = float(np.sqrt(np.mean(phi2_ref**2)))
    results['FDM'] = {
        'phi1_L2': l2_1, 'phi1_Linf': linf_1, 'phi1_rel_L2': l2_1/norm1,
        'phi2_L2': l2_2, 'phi2_Linf': linf_2, 'phi2_rel_L2': l2_2/norm2,
        'solve_time': t_fdm
    }
    print(f"  FDM: phi1 L2={l2_1:.3e}, Linf={linf_1:.3e}, phi2 L2={l2_2:.3e}, Linf={linf_2:.3e}")
except Exception as e:
    print(f"  FDM failed: {e}")

# ── FEM ──────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'baselines', 'fem'))
try:
    import fem_solver
    print("Running FEM...")
    t0 = time.time()
    phi1_fem, phi2_fem, grid_x_fem, grid_y_fem = fem_solver.solve()
    t_fem = time.time() - t0
    from scipy.interpolate import RegularGridInterpolator
    interp1 = RegularGridInterpolator((grid_y_fem, grid_x_fem), phi1_fem, method='linear')
    interp2 = RegularGridInterpolator((grid_y_fem, grid_x_fem), phi2_fem, method='linear')
    pts = np.column_stack([yf, xf])
    phi1_fem_pts = interp1(pts)
    phi2_fem_pts = interp2(pts)
    err1 = np.abs(phi1_fem_pts - phi1_ref)
    err2 = np.abs(phi2_fem_pts - phi2_ref)
    l2_1 = float(np.sqrt(np.mean(err1**2)))
    linf_1 = float(np.max(err1))
    l2_2 = float(np.sqrt(np.mean(err2**2)))
    linf_2 = float(np.max(err2))
    results['FEM'] = {
        'phi1_L2': l2_1, 'phi1_Linf': linf_1, 'phi1_rel_L2': l2_1/norm1,
        'phi2_L2': l2_2, 'phi2_Linf': linf_2, 'phi2_rel_L2': l2_2/norm2,
        'solve_time': t_fem
    }
    print(f"  FEM: phi1 L2={l2_1:.3e}, Linf={linf_1:.3e}, phi2 L2={l2_2:.3e}, Linf={linf_2:.3e}")
except Exception as e:
    print(f"  FEM failed: {e}")

# ── Spectral ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'baselines', 'spectral'))
try:
    import spectral_solver
    print("Running Spectral N=30...")
    t0 = time.time()
    phi1_spec, phi2_spec, grid_x_spec, grid_y_spec = spectral_solver.solve()
    t_spec = time.time() - t0
    from scipy.interpolate import RectBivariateSpline
    # Spectral grid may not be regular; use RBS
    # Note: grid_y and grid_x must be sorted
    gy = np.sort(grid_y_spec)
    gx = np.sort(grid_x_spec)
    spline1 = RectBivariateSpline(gy, gx, phi1_spec)
    spline2 = RectBivariateSpline(gy, gx, phi2_spec)
    phi1_spec_pts = np.array([spline1(yv, xv)[0,0] for xv, yv in zip(xf, yf)])
    phi2_spec_pts = np.array([spline2(yv, xv)[0,0] for xv, yv in zip(xf, yf)])
    err1 = np.abs(phi1_spec_pts - phi1_ref)
    err2 = np.abs(phi2_spec_pts - phi2_ref)
    l2_1 = float(np.sqrt(np.mean(err1**2)))
    linf_1 = float(np.max(err1))
    l2_2 = float(np.sqrt(np.mean(err2**2)))
    linf_2 = float(np.max(err2))
    results['Spectral'] = {
        'phi1_L2': l2_1, 'phi1_Linf': linf_1, 'phi1_rel_L2': l2_1/norm1,
        'phi2_L2': l2_2, 'phi2_Linf': linf_2, 'phi2_rel_L2': l2_2/norm2,
        'solve_time': t_spec
    }
    print(f"  Spectral: phi1 L2={l2_1:.3e}, Linf={linf_1:.3e}, phi2 L2={l2_2:.3e}, Linf={linf_2:.3e}")
except Exception as e:
    print(f"  Spectral failed: {e}")

out_path = os.path.join(os.path.dirname(__file__), '../../baselines/results/pointwise_errors.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
