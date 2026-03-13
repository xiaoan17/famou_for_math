"""
Finite Difference Method (FDM) solver for 2D two-group neutron diffusion.

System:
  -D1 * lap(phi1) + Sigma_r * phi1 = nu*Sigma_f1*phi1 + nu*Sigma_f2*phi2
  -D2 * lap(phi2) + Sigma_a2 * phi2 = Sigma_12 * phi1

Rearranged:
  -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
  -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

Domain: [-0.5, 0.5]^2
BCs:
  Left  (x=-0.5): -D_g * dphi_g/dx = y
  Right (x=+0.5): dphi_g/dx = 0
  Top   (y=+0.5): dphi_g/dy = 0
  Bottom(y=-0.5): dphi_g/dy = 0

Uses second-order centered finite differences with one-sided differences
at Neumann boundaries.
"""
import json
import time
import logging
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Physical constants
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015

A11 = SIGMA_R - NU * SIGMA_F1   # 0.0075
A12 = -NU * SIGMA_F2            # -0.25
A21 = -SIGMA_12                 # -0.015
A22 = SIGMA_A2                  # 0.1


def build_system(Nx: int, Ny: int) -> Tuple[sparse.csr_matrix, np.ndarray]:
    """Build the sparse linear system for the coupled 2-group diffusion.

    Grid has Nx points in x and Ny points in y.
    Total unknowns: 2 * Nx * Ny (phi1 and phi2 at each grid point).

    Ordering: phi1 values first (row-major), then phi2 values.
    Index for phi1 at (i,j): i*Ny + j
    Index for phi2 at (i,j): Nx*Ny + i*Ny + j

    Args:
        Nx: number of grid points in x direction
        Ny: number of grid points in y direction

    Returns:
        A: sparse coefficient matrix
        b: right-hand side vector
    """
    hx = 1.0 / (Nx - 1)
    hy = 1.0 / (Ny - 1)
    N = Nx * Ny
    total = 2 * N

    rows = []
    cols = []
    vals = []
    rhs = np.zeros(total)

    def idx1(i: int, j: int) -> int:
        return i * Ny + j

    def idx2(i: int, j: int) -> int:
        return N + i * Ny + j

    x_coords = np.linspace(-0.5, 0.5, Nx)
    y_coords = np.linspace(-0.5, 0.5, Ny)

    for i in range(Nx):
        for j in range(Ny):
            eq1 = idx1(i, j)  # equation for phi1 at (i,j)
            eq2 = idx2(i, j)  # equation for phi2 at (i,j)

            x_val = x_coords[i]
            y_val = y_coords[j]

            is_left = (i == 0)
            is_right = (i == Nx - 1)
            is_bottom = (j == 0)
            is_top = (j == Ny - 1)

            # --- Left boundary: -D_g * dphi_g/dx = y ---
            if is_left:
                # Use second-order one-sided: dphi/dx ~ (-3*phi[0] + 4*phi[1] - phi[2]) / (2*hx)
                # -D_g * dphi_g/dx = y  =>  D_g * (3*phi[0] - 4*phi[1] + phi[2]) / (2*hx) = y
                # For phi1:
                rows.append(eq1)
                cols.append(idx1(0, j))
                vals.append(D1 * 3.0 / (2.0 * hx))

                rows.append(eq1)
                cols.append(idx1(1, j))
                vals.append(D1 * (-4.0) / (2.0 * hx))

                rows.append(eq1)
                cols.append(idx1(2, j))
                vals.append(D1 * 1.0 / (2.0 * hx))

                rhs[eq1] = y_val

                # For phi2:
                rows.append(eq2)
                cols.append(idx2(0, j))
                vals.append(D2 * 3.0 / (2.0 * hx))

                rows.append(eq2)
                cols.append(idx2(1, j))
                vals.append(D2 * (-4.0) / (2.0 * hx))

                rows.append(eq2)
                cols.append(idx2(2, j))
                vals.append(D2 * 1.0 / (2.0 * hx))

                rhs[eq2] = y_val
                continue

            # --- Right boundary: dphi_g/dx = 0 ---
            if is_right:
                # Second-order one-sided: (3*phi[Nx-1] - 4*phi[Nx-2] + phi[Nx-3]) / (2*hx) = 0
                rows.append(eq1)
                cols.append(idx1(Nx - 1, j))
                vals.append(3.0 / (2.0 * hx))

                rows.append(eq1)
                cols.append(idx1(Nx - 2, j))
                vals.append(-4.0 / (2.0 * hx))

                rows.append(eq1)
                cols.append(idx1(Nx - 3, j))
                vals.append(1.0 / (2.0 * hx))

                rhs[eq1] = 0.0

                rows.append(eq2)
                cols.append(idx2(Nx - 1, j))
                vals.append(3.0 / (2.0 * hx))

                rows.append(eq2)
                cols.append(idx2(Nx - 2, j))
                vals.append(-4.0 / (2.0 * hx))

                rows.append(eq2)
                cols.append(idx2(Nx - 3, j))
                vals.append(1.0 / (2.0 * hx))

                rhs[eq2] = 0.0
                continue

            # --- Bottom boundary (not corner): dphi_g/dy = 0 ---
            if is_bottom:
                # (3*phi[i,0] - 4*phi[i,1] + phi[i,2]) / (2*hy) = 0
                # But outward normal at bottom is -y, so dphi/dn = -dphi/dy = 0
                # => dphi/dy = 0 same thing
                # Use forward difference: (-3*phi[i,0] + 4*phi[i,1] - phi[i,2])/(2*hy) = 0
                rows.append(eq1)
                cols.append(idx1(i, 0))
                vals.append(-3.0 / (2.0 * hy))

                rows.append(eq1)
                cols.append(idx1(i, 1))
                vals.append(4.0 / (2.0 * hy))

                rows.append(eq1)
                cols.append(idx1(i, 2))
                vals.append(-1.0 / (2.0 * hy))

                rhs[eq1] = 0.0

                rows.append(eq2)
                cols.append(idx2(i, 0))
                vals.append(-3.0 / (2.0 * hy))

                rows.append(eq2)
                cols.append(idx2(i, 1))
                vals.append(4.0 / (2.0 * hy))

                rows.append(eq2)
                cols.append(idx2(i, 2))
                vals.append(-1.0 / (2.0 * hy))

                rhs[eq2] = 0.0
                continue

            # --- Top boundary (not corner): dphi_g/dy = 0 ---
            if is_top:
                # Backward difference: (3*phi[i,Ny-1] - 4*phi[i,Ny-2] + phi[i,Ny-3])/(2*hy) = 0
                rows.append(eq1)
                cols.append(idx1(i, Ny - 1))
                vals.append(3.0 / (2.0 * hy))

                rows.append(eq1)
                cols.append(idx1(i, Ny - 2))
                vals.append(-4.0 / (2.0 * hy))

                rows.append(eq1)
                cols.append(idx1(i, Ny - 3))
                vals.append(1.0 / (2.0 * hy))

                rhs[eq1] = 0.0

                rows.append(eq2)
                cols.append(idx2(i, Ny - 1))
                vals.append(3.0 / (2.0 * hy))

                rows.append(eq2)
                cols.append(idx2(i, Ny - 2))
                vals.append(-4.0 / (2.0 * hy))

                rows.append(eq2)
                cols.append(idx2(i, Ny - 3))
                vals.append(1.0 / (2.0 * hy))

                rhs[eq2] = 0.0
                continue

            # --- Interior point: discretize PDEs ---
            # -D1*(phi1[i+1,j] - 2*phi1[i,j] + phi1[i-1,j])/hx^2
            # -D1*(phi1[i,j+1] - 2*phi1[i,j] + phi1[i,j-1])/hy^2
            # + A11*phi1[i,j] + A12*phi2[i,j] = 0

            coeff_center_1 = 2.0 * D1 / hx**2 + 2.0 * D1 / hy**2 + A11
            coeff_center_2 = 2.0 * D2 / hx**2 + 2.0 * D2 / hy**2 + A22

            # phi1 equation
            rows.append(eq1)
            cols.append(idx1(i, j))
            vals.append(coeff_center_1)

            rows.append(eq1)
            cols.append(idx1(i - 1, j))
            vals.append(-D1 / hx**2)

            rows.append(eq1)
            cols.append(idx1(i + 1, j))
            vals.append(-D1 / hx**2)

            rows.append(eq1)
            cols.append(idx1(i, j - 1))
            vals.append(-D1 / hy**2)

            rows.append(eq1)
            cols.append(idx1(i, j + 1))
            vals.append(-D1 / hy**2)

            # Coupling: A12*phi2
            rows.append(eq1)
            cols.append(idx2(i, j))
            vals.append(A12)

            rhs[eq1] = 0.0

            # phi2 equation
            rows.append(eq2)
            cols.append(idx2(i, j))
            vals.append(coeff_center_2)

            rows.append(eq2)
            cols.append(idx2(i - 1, j))
            vals.append(-D2 / hx**2)

            rows.append(eq2)
            cols.append(idx2(i + 1, j))
            vals.append(-D2 / hx**2)

            rows.append(eq2)
            cols.append(idx2(i, j - 1))
            vals.append(-D2 / hy**2)

            rows.append(eq2)
            cols.append(idx2(i, j + 1))
            vals.append(-D2 / hy**2)

            # Coupling: A21*phi1
            rows.append(eq2)
            cols.append(idx1(i, j))
            vals.append(A21)

            rhs[eq2] = 0.0

    A_mat = sparse.csr_matrix(
        (vals, (rows, cols)), shape=(total, total)
    )
    return A_mat, rhs


def solve_fdm(Nx: int = 101, Ny: int = 101) -> Dict:
    """Solve the two-group diffusion system using FDM.

    Args:
        Nx: grid points in x
        Ny: grid points in y

    Returns:
        Dictionary with solution arrays and metadata.
    """
    logger.info(f"Building FDM system with {Nx}x{Ny} grid...")
    t0 = time.time()

    A_mat, rhs = build_system(Nx, Ny)
    t_build = time.time() - t0
    logger.info(f"  System built in {t_build:.2f}s, size {A_mat.shape}")

    logger.info("Solving sparse system...")
    t1 = time.time()
    sol = spsolve(A_mat, rhs)
    t_solve = time.time() - t1
    logger.info(f"  Solved in {t_solve:.2f}s")

    N = Nx * Ny
    phi1_grid = sol[:N].reshape(Nx, Ny)
    phi2_grid = sol[N:].reshape(Nx, Ny)

    x_coords = np.linspace(-0.5, 0.5, Nx)
    y_coords = np.linspace(-0.5, 0.5, Ny)

    total_time = time.time() - t0
    return {
        "phi1": phi1_grid,
        "phi2": phi2_grid,
        "x": x_coords,
        "y": y_coords,
        "Nx": Nx,
        "Ny": Ny,
        "build_time": t_build,
        "solve_time": t_solve,
        "total_time": total_time,
    }


def interpolate_at(
    result: Dict, x_eval: float, y_eval: float
) -> Tuple[float, float]:
    """Bilinear interpolation of the FDM solution at a point.

    Args:
        result: output from solve_fdm
        x_eval: x coordinate
        y_eval: y coordinate

    Returns:
        (phi1_value, phi2_value)
    """
    from scipy.interpolate import RegularGridInterpolator

    x_coords = result["x"]
    y_coords = result["y"]

    interp1 = RegularGridInterpolator(
        (x_coords, y_coords), result["phi1"], method="cubic"
    )
    interp2 = RegularGridInterpolator(
        (x_coords, y_coords), result["phi2"], method="cubic"
    )

    p1 = float(interp1(np.array([[x_eval, y_eval]]))[0])
    p2 = float(interp2(np.array([[x_eval, y_eval]]))[0])
    return p1, p2


def compute_pde_residual(
    result: Dict, x_eval: float, y_eval: float, h: float = 1e-4
) -> Tuple[float, float]:
    """Compute PDE residual at a point using finite differences on the FDM solution.

    Args:
        result: output from solve_fdm
        x_eval: x coordinate
        y_eval: y coordinate
        h: FD step size for residual evaluation

    Returns:
        (R1, R2) residuals for both groups
    """
    p1_c, p2_c = interpolate_at(result, x_eval, y_eval)
    p1_xp, p2_xp = interpolate_at(result, x_eval + h, y_eval)
    p1_xm, p2_xm = interpolate_at(result, x_eval - h, y_eval)
    p1_yp, p2_yp = interpolate_at(result, x_eval, y_eval + h)
    p1_ym, p2_ym = interpolate_at(result, x_eval, y_eval - h)

    lap1 = (p1_xp - 2 * p1_c + p1_xm) / h**2 + (p1_yp - 2 * p1_c + p1_ym) / h**2
    lap2 = (p2_xp - 2 * p2_c + p2_xm) / h**2 + (p2_yp - 2 * p2_c + p2_ym) / h**2

    R1 = -D1 * lap1 + A11 * p1_c + A12 * p2_c
    R2 = -D2 * lap2 + A21 * p1_c + A22 * p2_c
    return R1, R2


def compute_bc_residual(result: Dict) -> Dict[str, Tuple[float, float]]:
    """Compute boundary condition residuals.

    Returns:
        Dictionary of BC residuals at sample boundary points.
    """
    bc_res = {}
    h = 1e-4

    # Left BC: -D_g * dphi_g/dx = y at x=-0.5
    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        x_val = -0.5
        # Forward difference for dx at left boundary
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val + h, y_val)
        p1_2h, p2_2h = interpolate_at(result, x_val + 2 * h, y_val)

        dx1 = (-3 * p1_0 + 4 * p1_h - p1_2h) / (2 * h)
        dx2 = (-3 * p2_0 + 4 * p2_h - p2_2h) / (2 * h)

        R1 = -D1 * dx1 - y_val
        R2 = -D2 * dx2 - y_val
        bc_res[f"left(x={x_val},y={y_val})"] = (R1, R2)

    # Right BC: dphi_g/dx = 0 at x=0.5
    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        x_val = 0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val - h, y_val)
        p1_2h, p2_2h = interpolate_at(result, x_val - 2 * h, y_val)

        dx1 = (3 * p1_0 - 4 * p1_h + p1_2h) / (2 * h)
        dx2 = (3 * p2_0 - 4 * p2_h + p2_2h) / (2 * h)

        R1 = -D1 * dx1
        R2 = -D2 * dx2
        bc_res[f"right(x={x_val},y={y_val})"] = (R1, R2)

    # Top BC: dphi_g/dy = 0 at y=0.5
    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        y_val = 0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val, y_val - h)
        p1_2h, p2_2h = interpolate_at(result, x_val, y_val - 2 * h)

        dy1 = (3 * p1_0 - 4 * p1_h + p1_2h) / (2 * h)
        dy2 = (3 * p2_0 - 4 * p2_h + p2_2h) / (2 * h)

        R1 = -D1 * dy1
        R2 = -D2 * dy2
        bc_res[f"top(x={x_val},y={y_val})"] = (R1, R2)

    # Bottom BC: dphi_g/dy = 0 at y=-0.5
    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        y_val = -0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val, y_val + h)
        p1_2h, p2_2h = interpolate_at(result, x_val, y_val + 2 * h)

        dy1 = (-3 * p1_0 + 4 * p1_h - p1_2h) / (2 * h)
        dy2 = (-3 * p2_0 + 4 * p2_h - p2_2h) / (2 * h)

        R1 = -D1 * dy1
        R2 = -D2 * dy2
        bc_res[f"bottom(x={x_val},y={y_val})"] = (R1, R2)

    return bc_res


def main() -> None:
    """Run FDM solver and save results."""
    out_dir = Path(__file__).parent

    # Solve with 101x101 grid
    result = solve_fdm(Nx=101, Ny=101)

    # PDE residuals at test points
    test_points = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]
    pde_residuals = {}
    for xp, yp in test_points:
        R1, R2 = compute_pde_residual(result, xp, yp)
        pde_residuals[f"({xp},{yp})"] = {"R1": R1, "R2": R2}
        logger.info(f"  PDE residual at ({xp},{yp}): R1={R1:.6e}, R2={R2:.6e}")

    # BC residuals
    bc_residuals_raw = compute_bc_residual(result)
    bc_residuals = {}
    for key, (R1, R2) in bc_residuals_raw.items():
        bc_residuals[key] = {"R1": R1, "R2": R2}

    # Solution values at test points
    solution_values = {}
    for xp, yp in test_points:
        p1, p2 = interpolate_at(result, xp, yp)
        solution_values[f"({xp},{yp})"] = {"phi1": p1, "phi2": p2}

    # Summary
    all_pde = []
    for v in pde_residuals.values():
        all_pde.extend([abs(v["R1"]), abs(v["R2"])])
    all_bc = []
    for v in bc_residuals.values():
        all_bc.extend([abs(v["R1"]), abs(v["R2"])])

    max_pde = max(all_pde)
    max_bc = max(all_bc)

    logger.info(f"Max PDE residual: {max_pde:.6e}")
    logger.info(f"Max BC residual:  {max_bc:.6e}")
    logger.info(f"Total time: {result['total_time']:.2f}s")

    output = {
        "method": "Finite Difference Method (FDM)",
        "grid": f"{result['Nx']}x{result['Ny']}",
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
