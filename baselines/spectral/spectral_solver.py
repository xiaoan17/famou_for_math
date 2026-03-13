"""
Chebyshev spectral collocation solver for 2D two-group neutron diffusion.

Uses Chebyshev-Gauss-Lobatto collocation points mapped to [-0.5, 0.5]^2.
The differentiation matrices are constructed using the standard Chebyshev
approach, then boundary conditions are imposed by row replacement.

System:
  -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
  -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

BCs:
  Left  (x=-0.5): -D_g * dphi_g/dx = y
  Right, Top, Bottom: zero Neumann
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from scipy.interpolate import RegularGridInterpolator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Physical constants
D1 = 1.0
D2 = 0.5
A11 = 0.0075
A12 = -0.25
A21 = -0.015
A22 = 0.1


def cheb_diff_matrix(N: int) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Chebyshev differentiation matrix on [-1, 1].

    Args:
        N: number of collocation points (including endpoints)

    Returns:
        x: Chebyshev-Gauss-Lobatto points (N,), ordered from +1 to -1
        D: differentiation matrix (N, N)
    """
    if N == 0:
        return np.array([0.0]), np.array([[0.0]])

    theta = np.pi * np.arange(N) / (N - 1)
    x = np.cos(theta)  # points from +1 to -1

    # Build differentiation matrix
    c = np.ones(N)
    c[0] = 2.0
    c[-1] = 2.0
    c *= (-1.0) ** np.arange(N)

    X = np.tile(x, (N, 1))
    dX = X - X.T
    D = np.outer(c, 1.0 / c) / (dX + np.eye(N))
    D -= np.diag(D.sum(axis=1))

    return x, D


def solve_spectral(N: int = 30) -> Dict:
    """Solve 2-group diffusion using Chebyshev spectral collocation.

    Args:
        N: number of collocation points per direction

    Returns:
        Dictionary with solution and metadata.
    """
    logger.info(f"Building spectral system with N={N} collocation points...")
    t0 = time.time()

    # Chebyshev points on [-1,1] and diff matrix
    xi, D1_mat = cheb_diff_matrix(N)

    # Map to [-0.5, 0.5]: x = 0.5*xi, dx/dxi = 0.5
    # d/dx = (1/0.5) * d/dxi = 2*D1_mat
    x_phys = 0.5 * xi  # from +0.5 to -0.5
    Dx = 2.0 * D1_mat  # first derivative in x
    Dxx = Dx @ Dx       # second derivative

    # Same for y direction
    eta, _ = cheb_diff_matrix(N)
    y_phys = 0.5 * eta
    Dy = 2.0 * D1_mat
    Dyy = Dy @ Dy

    # Total unknowns: 2 * N * N
    # Ordering: phi1 values at all (N*N) grid points, then phi2
    # Grid point (i,j): x_phys[i], y_phys[j]
    # Index: i*N + j for phi1, N*N + i*N + j for phi2

    NN = N * N
    total = 2 * NN

    # Build the system matrix
    A_sys = np.zeros((total, total))
    rhs = np.zeros(total)

    def idx1(i: int, j: int) -> int:
        return i * N + j

    def idx2(i: int, j: int) -> int:
        return NN + i * N + j

    # Interior equations: -D_g * (d2phi/dx2 + d2phi/dy2) + A*phi = 0
    for i in range(N):
        for j in range(N):
            eq1 = idx1(i, j)
            eq2 = idx2(i, j)

            is_left = (i == N - 1)     # x_phys goes from +0.5 to -0.5
            is_right = (i == 0)
            is_top = (j == 0)          # y_phys goes from +0.5 to -0.5
            is_bottom = (j == N - 1)

            is_boundary = is_left or is_right or is_top or is_bottom

            if is_boundary:
                # Apply Neumann BC via row replacement
                if is_left:
                    # x = -0.5, -D_g * dphi_g/dx = y
                    # dphi/dx at (i,j) = sum_k Dx[i,k] * phi(k,j)
                    # -D1 * sum_k Dx[i,k] * phi1(k,j) = y_phys[j]
                    for k in range(N):
                        A_sys[eq1, idx1(k, j)] = -D1 * Dx[i, k]
                        A_sys[eq2, idx2(k, j)] = -D2 * Dx[i, k]
                    rhs[eq1] = y_phys[j]
                    rhs[eq2] = y_phys[j]

                elif is_right:
                    # x = +0.5, dphi_g/dx = 0
                    for k in range(N):
                        A_sys[eq1, idx1(k, j)] = Dx[i, k]
                        A_sys[eq2, idx2(k, j)] = Dx[i, k]
                    rhs[eq1] = 0.0
                    rhs[eq2] = 0.0

                elif is_top:
                    # y = +0.5, dphi_g/dy = 0
                    for k in range(N):
                        A_sys[eq1, idx1(i, k)] = Dy[j, k]
                        A_sys[eq2, idx2(i, k)] = Dy[j, k]
                    rhs[eq1] = 0.0
                    rhs[eq2] = 0.0

                elif is_bottom:
                    # y = -0.5, dphi_g/dy = 0
                    for k in range(N):
                        A_sys[eq1, idx1(i, k)] = Dy[j, k]
                        A_sys[eq2, idx2(i, k)] = Dy[j, k]
                    rhs[eq1] = 0.0
                    rhs[eq2] = 0.0
            else:
                # Interior: -D1*(d2phi1/dx2 + d2phi1/dy2) + A11*phi1 + A12*phi2 = 0
                for k in range(N):
                    # d2phi1/dx2 contribution
                    A_sys[eq1, idx1(k, j)] += -D1 * Dxx[i, k]
                    # d2phi1/dy2 contribution
                    A_sys[eq1, idx1(i, k)] += -D1 * Dyy[j, k]

                # A11*phi1 + A12*phi2
                A_sys[eq1, idx1(i, j)] += A11
                A_sys[eq1, idx2(i, j)] += A12

                # phi2 equation
                for k in range(N):
                    A_sys[eq2, idx2(k, j)] += -D2 * Dxx[i, k]
                    A_sys[eq2, idx2(i, k)] += -D2 * Dyy[j, k]

                A_sys[eq2, idx1(i, j)] += A21
                A_sys[eq2, idx2(i, j)] += A22

    t_build = time.time() - t0
    logger.info(f"  System built in {t_build:.2f}s")

    logger.info("Solving dense system...")
    t1 = time.time()
    sol = np.linalg.solve(A_sys, rhs)
    t_solve = time.time() - t1
    logger.info(f"  Solved in {t_solve:.2f}s")

    phi1_grid = sol[:NN].reshape(N, N)
    phi2_grid = sol[NN:].reshape(N, N)

    total_time = time.time() - t0
    return {
        "phi1": phi1_grid,
        "phi2": phi2_grid,
        "x": x_phys,  # from +0.5 to -0.5
        "y": y_phys,
        "N": N,
        "build_time": t_build,
        "solve_time": t_solve,
        "total_time": total_time,
    }


def _bary_weights(x: np.ndarray) -> np.ndarray:
    """Compute barycentric interpolation weights for Chebyshev points."""
    N = len(x)
    w = np.ones(N)
    w[0] = 0.5
    w[-1] = 0.5
    for j in range(N):
        w[j] *= (-1) ** j
    return w


def _bary_interp_1d(x_nodes: np.ndarray, f_vals: np.ndarray,
                     w: np.ndarray, x_eval: float) -> float:
    """Barycentric interpolation at a single point."""
    diff = x_eval - x_nodes
    # Check if we're at a node
    idx = np.where(np.abs(diff) < 1e-15)[0]
    if len(idx) > 0:
        return float(f_vals[idx[0]])
    terms = w / diff
    return float(np.dot(terms, f_vals) / np.sum(terms))


def interpolate_at(
    result: Dict, x_eval: float, y_eval: float
) -> Tuple[float, float]:
    """Interpolate spectral solution using barycentric interpolation."""
    x_nodes = result["x"]  # Chebyshev points, +0.5 to -0.5
    y_nodes = result["y"]
    N = len(x_nodes)
    wx = _bary_weights(x_nodes)
    wy = _bary_weights(y_nodes)

    # Interpolate phi1: first in x for each j, then in y
    phi1_at_y = np.zeros(N)
    phi2_at_y = np.zeros(N)
    for j in range(N):
        phi1_at_y[j] = _bary_interp_1d(x_nodes, result["phi1"][:, j], wx, x_eval)
        phi2_at_y[j] = _bary_interp_1d(x_nodes, result["phi2"][:, j], wx, x_eval)

    p1 = _bary_interp_1d(y_nodes, phi1_at_y, wy, y_eval)
    p2 = _bary_interp_1d(y_nodes, phi2_at_y, wy, y_eval)
    return p1, p2


def compute_pde_residual(
    result: Dict, x_eval: float, y_eval: float, h: float = 1e-5
) -> Tuple[float, float]:
    """Compute PDE residual using spectral differentiation matrices."""
    N = result["N"]
    x_nodes = result["x"]
    y_nodes = result["y"]
    phi1 = result["phi1"]
    phi2 = result["phi2"]

    _, D_mat = cheb_diff_matrix(N)
    Dx = 2.0 * D_mat
    Dxx = Dx @ Dx
    Dy = 2.0 * D_mat
    Dyy = Dy @ Dy

    wx = _bary_weights(x_nodes)
    wy = _bary_weights(y_nodes)

    # d2phi/dx2 at all grid points, then interpolate
    d2phi1_dx2 = Dxx @ phi1  # (N, N)
    d2phi1_dy2 = (Dyy @ phi1.T).T  # phi1 (N_x, N_y), apply Dyy along y

    d2phi2_dx2 = Dxx @ phi2
    d2phi2_dy2 = (Dyy @ phi2.T).T

    lap1 = d2phi1_dx2 + d2phi1_dy2
    lap2 = d2phi2_dx2 + d2phi2_dy2

    # PDE residual at all grid points
    R1_grid = -D1 * lap1 + A11 * phi1 + A12 * phi2
    R2_grid = -D2 * lap2 + A21 * phi1 + A22 * phi2

    # Interpolate to evaluation point
    R1_at_y = np.zeros(N)
    R2_at_y = np.zeros(N)
    for j in range(N):
        R1_at_y[j] = _bary_interp_1d(x_nodes, R1_grid[:, j], wx, x_eval)
        R2_at_y[j] = _bary_interp_1d(x_nodes, R2_grid[:, j], wx, x_eval)

    R1 = _bary_interp_1d(y_nodes, R1_at_y, wy, y_eval)
    R2 = _bary_interp_1d(y_nodes, R2_at_y, wy, y_eval)
    return R1, R2


def compute_bc_residual(result: Dict) -> Dict[str, Tuple[float, float]]:
    """Compute BC residuals using spectral differentiation.

    For the spectral method, we use the differentiation matrix to compute
    derivatives at boundary, then interpolate in the tangential direction
    using barycentric interpolation.
    """
    bc_res = {}
    N = result["N"]
    x_nodes = result["x"]
    y_nodes = result["y"]
    phi1 = result["phi1"]
    phi2 = result["phi2"]

    _, D_mat = cheb_diff_matrix(N)
    Dx = 2.0 * D_mat
    Dy = 2.0 * D_mat

    wx = _bary_weights(x_nodes)
    wy = _bary_weights(y_nodes)

    i_left = N - 1   # x = -0.5
    i_right = 0      # x = +0.5
    j_top = 0        # y = +0.5
    j_bottom = N - 1 # y = -0.5

    # Compute dphi/dx at left boundary for all j using spectral diff
    dphi1_dx_left = np.zeros(N)
    dphi2_dx_left = np.zeros(N)
    for j in range(N):
        dphi1_dx_left[j] = np.dot(Dx[i_left, :], phi1[:, j])
        dphi2_dx_left[j] = np.dot(Dx[i_left, :], phi2[:, j])

    # Compute dphi/dx at right boundary
    dphi1_dx_right = np.zeros(N)
    dphi2_dx_right = np.zeros(N)
    for j in range(N):
        dphi1_dx_right[j] = np.dot(Dx[i_right, :], phi1[:, j])
        dphi2_dx_right[j] = np.dot(Dx[i_right, :], phi2[:, j])

    # Compute dphi/dy at top boundary
    dphi1_dy_top = np.zeros(N)
    dphi2_dy_top = np.zeros(N)
    for i in range(N):
        dphi1_dy_top[i] = np.dot(Dy[j_top, :], phi1[i, :])
        dphi2_dy_top[i] = np.dot(Dy[j_top, :], phi2[i, :])

    # Compute dphi/dy at bottom boundary
    dphi1_dy_bot = np.zeros(N)
    dphi2_dy_bot = np.zeros(N)
    for i in range(N):
        dphi1_dy_bot[i] = np.dot(Dy[j_bottom, :], phi1[i, :])
        dphi2_dy_bot[i] = np.dot(Dy[j_bottom, :], phi2[i, :])

    # Left BC: -D_g * dphi_g/dx = y at x=-0.5
    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        dx1 = _bary_interp_1d(y_nodes, dphi1_dx_left, wy, y_val)
        dx2 = _bary_interp_1d(y_nodes, dphi2_dx_left, wy, y_val)
        R1 = -D1 * dx1 - y_val
        R2 = -D2 * dx2 - y_val
        bc_res[f"left(x=-0.5,y={y_val})"] = (R1, R2)

    # Right BC: dphi_g/dx = 0 at x=+0.5
    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        dx1 = _bary_interp_1d(y_nodes, dphi1_dx_right, wy, y_val)
        dx2 = _bary_interp_1d(y_nodes, dphi2_dx_right, wy, y_val)
        R1 = -D1 * dx1
        R2 = -D2 * dx2
        bc_res[f"right(x=0.5,y={y_val})"] = (R1, R2)

    # Top BC: dphi_g/dy = 0 at y=+0.5
    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        dy1 = _bary_interp_1d(x_nodes, dphi1_dy_top, wx, x_val)
        dy2 = _bary_interp_1d(x_nodes, dphi2_dy_top, wx, x_val)
        R1 = -D1 * dy1
        R2 = -D2 * dy2
        bc_res[f"top(x={x_val},y=0.5)"] = (R1, R2)

    # Bottom BC: dphi_g/dy = 0 at y=-0.5
    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        dy1 = _bary_interp_1d(x_nodes, dphi1_dy_bot, wx, x_val)
        dy2 = _bary_interp_1d(x_nodes, dphi2_dy_bot, wx, x_val)
        R1 = -D1 * dy1
        R2 = -D2 * dy2
        bc_res[f"bottom(x={x_val},y=-0.5)"] = (R1, R2)

    return bc_res


def main() -> None:
    """Run spectral solver and save results."""
    out_dir = Path(__file__).parent
    test_points = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]

    result = solve_spectral(N=30)

    pde_residuals = {}
    all_pde = []
    for xp, yp in test_points:
        R1, R2 = compute_pde_residual(result, xp, yp)
        pde_residuals[f"({xp},{yp})"] = {"R1": R1, "R2": R2}
        all_pde.extend([abs(R1), abs(R2)])
        logger.info(f"  PDE residual at ({xp},{yp}): R1={R1:.6e}, R2={R2:.6e}")

    bc_raw = compute_bc_residual(result)
    bc_residuals = {}
    all_bc = []
    for key, (R1, R2) in bc_raw.items():
        bc_residuals[key] = {"R1": R1, "R2": R2}
        all_bc.extend([abs(R1), abs(R2)])

    solution_values = {}
    for xp, yp in test_points:
        p1, p2 = interpolate_at(result, xp, yp)
        solution_values[f"({xp},{yp})"] = {"phi1": p1, "phi2": p2}

    max_pde = max(all_pde)
    max_bc = max(all_bc)

    logger.info(f"Max PDE residual: {max_pde:.6e}")
    logger.info(f"Max BC residual:  {max_bc:.6e}")
    logger.info(f"Total time: {result['total_time']:.2f}s")

    output = {
        "method": "Chebyshev Spectral Collocation",
        "N": result["N"],
        "grid": f"{result['N']}x{result['N']}",
        "dof": 2 * result["N"] ** 2,
        "pde_residuals": pde_residuals,
        "bc_residuals": bc_residuals,
        "solution_values": solution_values,
        "max_pde_residual": max_pde,
        "max_bc_residual": max_bc,
        "build_time_s": result["build_time"],
        "solve_time_s": result["solve_time"],
        "total_time_s": result["total_time"],
    }

    with open(out_dir / "results.json", "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Results saved to {out_dir / 'results.json'}")


if __name__ == "__main__":
    main()
