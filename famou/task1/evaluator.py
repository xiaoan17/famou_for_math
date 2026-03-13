"""
FaMou Evaluator: 2D Two-Group Neutron Diffusion Equation Solver

Evaluates a candidate numerical solver (init.py) by comparing its output
against the analytical reference solution at test points, and checking
PDE/BC residuals.

The analytical reference is embedded directly in this file (no external deps).

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

# ── Coupling matrix M = D^{-1} * A (embedded analytical solver) ─────────────
_M = np.array([
    [A11 / D1, A12 / D1],
    [A21 / D2, A22 / D2],
])

def _eigen_decomp():
    evals, evecs = np.linalg.eig(_M)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]

_EIGENVALUES, _P = _eigen_decomp()
_P_INV = np.linalg.inv(_P)
_LAMBDA1, _LAMBDA2 = _EIGENVALUES[0], _EIGENVALUES[1]


def _cosine_coeff(n):
    """b_n = 2 * integral_{-0.5}^{0.5} y * cos(n*pi*(y+0.5)) dy"""
    if n == 0:
        return 0.0
    return 2.0 * ((-1.0)**n - 1.0) / (n * np.pi)**2


def _compute_modes(N_terms=200):
    D_vec = np.array([D1, D2])
    modes = []
    for n in range(N_terms + 1):
        kn = n * np.pi
        bn = _cosine_coeff(n)
        if abs(bn) < 1e-30:
            modes.append(None)
            continue
        alphas = np.zeros(2)
        for p in range(2):
            val = _EIGENVALUES[p] + kn**2
            if val < 0:
                raise ValueError(f"Negative sqrt arg: lambda_{p}={_EIGENVALUES[p]}, kn^2={kn**2}")
            alphas[p] = np.sqrt(val)
        Q = np.zeros((2, 2))
        for g in range(2):
            for p in range(2):
                Q[g, p] = D_vec[g] * _P[g, p] * alphas[p] * np.sinh(alphas[p])
        rhs = np.array([bn, bn])
        c_n = np.linalg.solve(Q, rhs)
        modes.append((alphas[0], alphas[1], c_n[0], c_n[1]))
    return modes


def _eval_flux(x_arr, y_arr, N_terms=200):
    """Evaluate analytical flux at arrays of (x, y) points."""
    x_arr = np.atleast_1d(np.asarray(x_arr, float))
    y_arr = np.atleast_1d(np.asarray(y_arr, float))
    modes = _compute_modes(N_terms)
    phi1 = np.zeros_like(x_arr)
    phi2 = np.zeros_like(x_arr)
    for n, mode in enumerate(modes):
        if mode is None:
            continue
        a1, a2, c1, c2 = mode
        kn = n * np.pi
        cos_y = np.cos(kn * (y_arr + 0.5))
        X1 = np.cosh(a1 * (x_arr - 0.5))
        X2 = np.cosh(a2 * (x_arr - 0.5))
        phi1 += (c1 * _P[0, 0] * X1 + c2 * _P[0, 1] * X2) * cos_y
        phi2 += (c1 * _P[1, 0] * X1 + c2 * _P[1, 1] * X2) * cos_y
    return phi1, phi2


# ── Test points ─────────────────────────────────────────────────────────────
TEST_POINTS = [(0.0, 0.0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]

# Precompute reference values once at import time
_REF = None

def _get_ref():
    global _REF
    if _REF is None:
        xp = np.array([p[0] for p in TEST_POINTS])
        yp = np.array([p[1] for p in TEST_POINTS])
        p1, p2 = _eval_flux(xp, yp, N_terms=200)
        _REF = {pt: (float(p1[i]), float(p2[i])) for i, pt in enumerate(TEST_POINTS)}
    return _REF


def _load_user_module(path_user_py):
    abs_path = os.path.abspath(path_user_py)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Candidate file not found: {abs_path}")
    spec = importlib.util.spec_from_file_location("user_solution", abs_path)
    mod = importlib.util.module_from_spec(spec)
    user_dir = os.path.dirname(abs_path)
    if user_dir not in sys.path:
        sys.path.insert(0, user_dir)
    spec.loader.exec_module(mod)
    return mod


def _pde_residual(phi1_func, phi2_func, x, y, h=1e-5):
    p1c = phi1_func(x, y);  p2c = phi2_func(x, y)
    lap1 = ((phi1_func(x+h,y) - 2*p1c + phi1_func(x-h,y))/h**2
            + (phi1_func(x,y+h) - 2*p1c + phi1_func(x,y-h))/h**2)
    lap2 = ((phi2_func(x+h,y) - 2*p2c + phi2_func(x-h,y))/h**2
            + (phi2_func(x,y+h) - 2*p2c + phi2_func(x,y-h))/h**2)
    R1 = abs(-D1*lap1 + A11*p1c + A12*p2c)
    R2 = abs(-D2*lap2 + A21*p1c + A22*p2c)
    return R1, R2


def _bc_residual(phi1_func, phi2_func):
    h = 1e-5
    max_res = 0.0
    for yv in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        dx1 = (phi1_func(-0.5+h, yv) - phi1_func(-0.5-h, yv)) / (2*h)
        dx2 = (phi2_func(-0.5+h, yv) - phi2_func(-0.5-h, yv)) / (2*h)
        max_res = max(max_res, abs(-D1*dx1 - yv), abs(-D2*dx2 - yv))
    for yv in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        dx1 = (phi1_func(0.5+h, yv) - phi1_func(0.5-h, yv)) / (2*h)
        dx2 = (phi2_func(0.5+h, yv) - phi2_func(0.5-h, yv)) / (2*h)
        max_res = max(max_res, abs(-D1*dx1), abs(-D2*dx2))
    for xv in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        dy1 = (phi1_func(xv, 0.5+h) - phi1_func(xv, 0.5-h)) / (2*h)
        dy2 = (phi2_func(xv, 0.5+h) - phi2_func(xv, 0.5-h)) / (2*h)
        max_res = max(max_res, abs(-D1*dy1), abs(-D2*dy2))
    for xv in [-0.4, -0.2, 0.0, 0.2, 0.4]:
        dy1 = (phi1_func(xv, -0.5+h) - phi1_func(xv, -0.5-h)) / (2*h)
        dy2 = (phi2_func(xv, -0.5+h) - phi2_func(xv, -0.5-h)) / (2*h)
        max_res = max(max_res, abs(-D1*dy1), abs(-D2*dy2))
    return max_res


def evaluate(path_user_py: str, task_name: str = "default", timeout: int = 3600) -> dict:
    t_start = time.time()

    try:
        user_mod = _load_user_module(path_user_py)
    except Exception as e:
        return {"validity": 0.0, "combined_score": 0.0,
                "cost_time": time.time()-t_start,
                "error_info": f"Module load failed: {e}\n{traceback.format_exc()}"}

    try:
        if not hasattr(user_mod, "solution"):
            raise AttributeError("solution() not found")
        phi1_func, phi2_func = user_mod.solution()
        if not callable(phi1_func) or not callable(phi2_func):
            raise TypeError("solution() must return two callables")
    except Exception as e:
        return {"validity": 0.0, "combined_score": 0.0,
                "cost_time": time.time()-t_start,
                "error_info": f"solution() failed: {e}\n{traceback.format_exc()}"}

    try:
        ref = _get_ref()
        rel_errors = []
        for pt in TEST_POINTS:
            x, y = pt
            p1 = float(phi1_func(x, y))
            p2 = float(phi2_func(x, y))
            if not (np.isfinite(p1) and np.isfinite(p2)):
                return {"validity": 0.0, "combined_score": 0.0,
                        "cost_time": time.time()-t_start,
                        "error_info": f"Non-finite at ({x},{y}): phi1={p1}, phi2={p2}"}
            p1r, p2r = ref[pt]
            rel_errors.append(abs(p1-p1r) / max(abs(p1r), 1e-10))
            rel_errors.append(abs(p2-p2r) / max(abs(p2r), 1e-10))
        mean_rel_err = float(np.mean(rel_errors))
        max_rel_err  = float(np.max(rel_errors))
    except Exception as e:
        return {"validity": 0.0, "combined_score": 0.0,
                "cost_time": time.time()-t_start,
                "error_info": f"Test-point eval failed: {e}\n{traceback.format_exc()}"}

    try:
        pde_res = []
        for pt in TEST_POINTS:
            r1, r2 = _pde_residual(phi1_func, phi2_func, pt[0], pt[1])
            pde_res.extend([r1, r2])
        max_pde = float(np.max(pde_res))
    except Exception:
        max_pde = 1e10

    try:
        max_bc = _bc_residual(phi1_func, phi2_func)
    except Exception:
        max_bc = 1e10

    # Scoring
    accuracy_score = 1.0 / (1.0 + mean_rel_err * 100)
    pde_factor = (1.0 if max_pde < 1e-6 else
                  0.9 if max_pde < 1e-4 else
                  0.7 if max_pde < 1e-2 else
                  max(0.1, 1.0/(1.0+max_pde)))
    bc_factor  = (1.0 if max_bc  < 1e-6 else
                  0.9 if max_bc  < 1e-4 else
                  0.7 if max_bc  < 1e-2 else
                  max(0.1, 1.0/(1.0+max_bc)))
    combined_score = accuracy_score * pde_factor * bc_factor

    return {
        "validity": 1.0,
        "combined_score": float(combined_score),
        "cost_time": time.time() - t_start,
        "error_info": "",
        "mean_rel_error": mean_rel_err,
        "max_rel_error":  max_rel_err,
        "max_pde_residual": max_pde,
        "max_bc_residual":  max_bc,
    }


if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <path_to_init.py>")
        sys.exit(1)
    print(json.dumps(evaluate(sys.argv[1]), indent=2))
