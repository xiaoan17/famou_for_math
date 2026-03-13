"""
FaMou Evaluator: 2D Two-Group Neutron Diffusion Equation Solver

Evaluates a candidate numerical solver (init.py) by comparing its output
against the analytical reference solution at test points, and checking
PDE/BC residuals.

Interface (READONLY):
    evaluate(path_user_py, task_name="default", timeout=3600) -> dict
    {
        "validity": float,       # 0 or 1
        "combined_score": float, # higher is better; 0 = invalid
        "cost_time": float,
        "error_info": str,       # "" on success
    }
"""
import os
import sys
import time
import importlib.util
import traceback
import numpy as np

# ── Physical constants ──────────────────────────────────────────────────────
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015

A11 = SIGMA_R - NU * SIGMA_F1    # 0.0075
A12 = -NU * SIGMA_F2              # -0.25
A21 = -SIGMA_12                   # -0.015
A22 = SIGMA_A2                    # 0.1

# ── Test points ─────────────────────────────────────────────────────────────
TEST_POINTS = [(0.0, 0.0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]


def _get_analytical_reference():
    """Load analytical solution values (ground truth)."""
    # Path relative to this evaluator file
    eval_dir = os.path.dirname(os.path.abspath(__file__))
    analytical_path = os.path.join(
        eval_dir, "..", "..", "scripts", "numerical_solver", "analytical_solver.py"
    )
    analytical_path = os.path.normpath(analytical_path)

    if not os.path.exists(analytical_path):
        raise FileNotFoundError(f"Analytical solver not found: {analytical_path}")

    spec = importlib.util.spec_from_file_location("analytical_solver", analytical_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    ref = {}
    xp = np.array([p[0] for p in TEST_POINTS])
    yp = np.array([p[1] for p in TEST_POINTS])
    p1_vals, p2_vals = mod.evaluate_flux(xp, yp, N_terms=200)
    for i, pt in enumerate(TEST_POINTS):
        ref[pt] = (float(p1_vals[i]), float(p2_vals[i]))
    return ref, mod


# Precompute reference once at module load (cached)
_REF_CACHE = None
_ANALYTICAL_MOD = None


def _get_ref():
    global _REF_CACHE, _ANALYTICAL_MOD
    if _REF_CACHE is None:
        _REF_CACHE, _ANALYTICAL_MOD = _get_analytical_reference()
    return _REF_CACHE, _ANALYTICAL_MOD


def _load_user_module(path_user_py: str):
    """Dynamically load the candidate solution module."""
    abs_path = os.path.abspath(path_user_py)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Candidate file not found: {abs_path}")
    spec = importlib.util.spec_from_file_location("user_solution", abs_path)
    mod = importlib.util.module_from_spec(spec)
    # Set sys.path so the user module can import local files
    user_dir = os.path.dirname(abs_path)
    if user_dir not in sys.path:
        sys.path.insert(0, user_dir)
    spec.loader.exec_module(mod)
    return mod


def _compute_pde_residual(phi1_func, phi2_func, x: float, y: float, h: float = 1e-5) -> tuple:
    """Numerical PDE residual at (x, y) via central finite differences."""
    p1_c = phi1_func(x, y)
    p2_c = phi2_func(x, y)

    p1_xp = phi1_func(x + h, y);  p1_xm = phi1_func(x - h, y)
    p1_yp = phi1_func(x, y + h);  p1_ym = phi1_func(x, y - h)
    p2_xp = phi2_func(x + h, y);  p2_xm = phi2_func(x - h, y)
    p2_yp = phi2_func(x, y + h);  p2_ym = phi2_func(x, y - h)

    lap1 = (p1_xp - 2*p1_c + p1_xm)/h**2 + (p1_yp - 2*p1_c + p1_ym)/h**2
    lap2 = (p2_xp - 2*p2_c + p2_xm)/h**2 + (p2_yp - 2*p2_c + p2_ym)/h**2

    R1 = -D1*lap1 + A11*p1_c + A12*p2_c
    R2 = -D2*lap2 + A21*p1_c + A22*p2_c
    return abs(R1), abs(R2)


def _compute_bc_residual(phi1_func, phi2_func) -> float:
    """Max BC residual across boundary sample points."""
    h = 1e-5
    max_res = 0.0

    # Left boundary: -D_g * dphi_g/dx = y  at x=-0.5
    for y_val in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        x0 = -0.5
        dx1 = (phi1_func(x0+h, y_val) - phi1_func(x0-h, y_val)) / (2*h)
        dx2 = (phi2_func(x0+h, y_val) - phi2_func(x0-h, y_val)) / (2*h)
        max_res = max(max_res, abs(-D1*dx1 - y_val), abs(-D2*dx2 - y_val))

    # Right boundary: dphi_g/dx = 0 at x=+0.5
    for y_val in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        x0 = 0.5
        dx1 = (phi1_func(x0+h, y_val) - phi1_func(x0-h, y_val)) / (2*h)
        dx2 = (phi2_func(x0+h, y_val) - phi2_func(x0-h, y_val)) / (2*h)
        max_res = max(max_res, abs(-D1*dx1), abs(-D2*dx2))

    # Top boundary: dphi_g/dy = 0 at y=+0.5
    for x_val in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        y0 = 0.5
        dy1 = (phi1_func(x_val, y0+h) - phi1_func(x_val, y0-h)) / (2*h)
        dy2 = (phi2_func(x_val, y0+h) - phi2_func(x_val, y0-h)) / (2*h)
        max_res = max(max_res, abs(-D1*dy1), abs(-D2*dy2))

    # Bottom boundary: dphi_g/dy = 0 at y=-0.5
    for x_val in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        y0 = -0.5
        dy1 = (phi1_func(x_val, y0+h) - phi1_func(x_val, y0-h)) / (2*h)
        dy2 = (phi2_func(x_val, y0+h) - phi2_func(x_val, y0-h)) / (2*h)
        max_res = max(max_res, abs(-D1*dy1), abs(-D2*dy2))

    return max_res


def evaluate(path_user_py: str, task_name: str = "default", timeout: int = 3600) -> dict:
    """Evaluate a candidate neutron diffusion solver.

    Args:
        path_user_py: path to the candidate init.py
        task_name: experiment identifier (unused internally)
        timeout: max seconds (not enforced here; caller may wrap)

    Returns:
        dict with validity, combined_score, cost_time, error_info
    """
    t_start = time.time()

    # ── Step 1: Load candidate module ───────────────────────────────────────
    try:
        user_mod = _load_user_module(path_user_py)
    except Exception as e:
        return {
            "validity": 0.0,
            "combined_score": 0.0,
            "cost_time": time.time() - t_start,
            "error_info": f"Module load failed: {e}\n{traceback.format_exc()}",
        }

    # ── Step 2: Call solution() ─────────────────────────────────────────────
    try:
        if not hasattr(user_mod, "solution"):
            raise AttributeError("solution() function not found in candidate script")
        phi1_func, phi2_func = user_mod.solution()
        if not callable(phi1_func) or not callable(phi2_func):
            raise TypeError("solution() must return two callables (phi1_func, phi2_func)")
    except Exception as e:
        return {
            "validity": 0.0,
            "combined_score": 0.0,
            "cost_time": time.time() - t_start,
            "error_info": f"solution() failed: {e}\n{traceback.format_exc()}",
        }

    # ── Step 3: Evaluate at test points ────────────────────────────────────
    try:
        ref, _ = _get_ref()
        rel_errors = []
        for pt in TEST_POINTS:
            x, y = pt
            p1_pred = float(phi1_func(x, y))
            p2_pred = float(phi2_func(x, y))

            if not (np.isfinite(p1_pred) and np.isfinite(p2_pred)):
                return {
                    "validity": 0.0,
                    "combined_score": 0.0,
                    "cost_time": time.time() - t_start,
                    "error_info": f"Non-finite value at ({x},{y}): phi1={p1_pred}, phi2={p2_pred}",
                }

            p1_ref, p2_ref = ref[pt]
            # Relative error (avoid division by near-zero)
            denom1 = max(abs(p1_ref), 1e-10)
            denom2 = max(abs(p2_ref), 1e-10)
            rel_errors.append(abs(p1_pred - p1_ref) / denom1)
            rel_errors.append(abs(p2_pred - p2_ref) / denom2)

        mean_rel_error = float(np.mean(rel_errors))
        max_rel_error = float(np.max(rel_errors))

    except Exception as e:
        return {
            "validity": 0.0,
            "combined_score": 0.0,
            "cost_time": time.time() - t_start,
            "error_info": f"Evaluation at test points failed: {e}\n{traceback.format_exc()}",
        }

    # ── Step 4: PDE residuals ────────────────────────────────────────────────
    try:
        pde_residuals = []
        for pt in TEST_POINTS:
            r1, r2 = _compute_pde_residual(phi1_func, phi2_func, pt[0], pt[1])
            pde_residuals.extend([r1, r2])
        max_pde_res = float(np.max(pde_residuals))
        mean_pde_res = float(np.mean(pde_residuals))
    except Exception as e:
        max_pde_res = 1e10
        mean_pde_res = 1e10

    # ── Step 5: BC residuals ────────────────────────────────────────────────
    try:
        max_bc_res = _compute_bc_residual(phi1_func, phi2_func)
    except Exception as e:
        max_bc_res = 1e10

    # ── Step 6: Scoring ─────────────────────────────────────────────────────
    # Primary score: accuracy vs analytical solution
    accuracy_score = 1.0 / (1.0 + mean_rel_error * 100)

    # PDE penalty: heavy penalty for large PDE residuals
    if max_pde_res < 1e-6:
        pde_factor = 1.0
    elif max_pde_res < 1e-4:
        pde_factor = 0.9
    elif max_pde_res < 1e-2:
        pde_factor = 0.7
    else:
        pde_factor = max(0.1, 1.0 / (1.0 + max_pde_res))

    # BC penalty
    if max_bc_res < 1e-6:
        bc_factor = 1.0
    elif max_bc_res < 1e-4:
        bc_factor = 0.9
    elif max_bc_res < 1e-2:
        bc_factor = 0.7
    else:
        bc_factor = max(0.1, 1.0 / (1.0 + max_bc_res))

    combined_score = accuracy_score * pde_factor * bc_factor

    return {
        "validity": 1.0,
        "combined_score": float(combined_score),
        "cost_time": time.time() - t_start,
        "error_info": "",
        # Extra diagnostics (optional, ignored by famou-ctl)
        "mean_rel_error": mean_rel_error,
        "max_rel_error": max_rel_error,
        "max_pde_residual": max_pde_res,
        "max_bc_residual": max_bc_res,
    }


if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <path_to_init.py>")
        sys.exit(1)
    result = evaluate(sys.argv[1])
    print(json.dumps(result, indent=2))
