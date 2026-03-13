"""
Finite Element Method (FEM) solver for 2D two-group neutron diffusion.

Uses bilinear quadrilateral elements (Q1) on a uniform mesh with
Galerkin weak formulation. Neumann BCs are naturally incorporated
via the boundary integral terms.

System:
  -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
  -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

Domain: [-0.5, 0.5]^2
BCs:
  Left  (x=-0.5): -D_g * dphi_g/dx = y   (inhomogeneous Neumann)
  Right (x=+0.5): dphi_g/dx = 0           (homogeneous Neumann)
  Top   (y=+0.5): dphi_g/dy = 0           (homogeneous Neumann)
  Bottom(y=-0.5): dphi_g/dy = 0           (homogeneous Neumann)
"""
import json
import logging
import time
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
A11 = 0.0075
A12 = -0.25
A21 = -0.015
A22 = 0.1


def _gauss_2d() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """2x2 Gauss quadrature points and weights on [-1,1]^2."""
    g = 1.0 / np.sqrt(3.0)
    pts_1d = np.array([-g, g])
    w_1d = np.array([1.0, 1.0])
    xi = np.array([pts_1d[i] for i in range(2) for _ in range(2)])
    eta = np.array([pts_1d[j] for _ in range(2) for j in range(2)])
    w = np.array([w_1d[i] * w_1d[j] for i in range(2) for j in range(2)])
    return xi, eta, w


def _shape_functions(xi: float, eta: float) -> np.ndarray:
    """Bilinear shape functions on reference element [-1,1]^2.

    Node ordering: (0,0)->(1,0)->(1,1)->(0,1) mapped to
    (-1,-1), (1,-1), (1,1), (-1,1).
    """
    return 0.25 * np.array([
        (1 - xi) * (1 - eta),
        (1 + xi) * (1 - eta),
        (1 + xi) * (1 + eta),
        (1 - xi) * (1 + eta),
    ])


def _shape_derivatives(xi: float, eta: float) -> Tuple[np.ndarray, np.ndarray]:
    """Derivatives of shape functions wrt xi, eta."""
    dN_dxi = 0.25 * np.array([
        -(1 - eta), (1 - eta), (1 + eta), -(1 + eta)
    ])
    dN_deta = 0.25 * np.array([
        -(1 - xi), -(1 + xi), (1 + xi), (1 - xi)
    ])
    return dN_dxi, dN_deta


def solve_fem(Nx: int = 101, Ny: int = 101) -> Dict:
    """Solve the 2-group diffusion system using bilinear Q1 FEM.

    Args:
        Nx: number of nodes in x
        Ny: number of nodes in y

    Returns:
        Dictionary with solution arrays and metadata.
    """
    logger.info(f"Building FEM system with {Nx}x{Ny} nodes...")
    t0 = time.time()

    x_coords = np.linspace(-0.5, 0.5, Nx)
    y_coords = np.linspace(-0.5, 0.5, Ny)
    hx = x_coords[1] - x_coords[0]
    hy = y_coords[1] - y_coords[0]

    N_nodes = Nx * Ny
    total_dof = 2 * N_nodes

    # Node index: node(i,j) = i*Ny + j
    def nidx(i: int, j: int) -> int:
        return i * Ny + j

    # Gauss quadrature
    xi_g, eta_g, w_g = _gauss_2d()
    n_gp = len(w_g)

    # Jacobian for uniform rectangular elements
    # x = x0 + hx/2*(1+xi), y = y0 + hy/2*(1+eta)
    # dx/dxi = hx/2, dy/deta = hy/2
    Jdet = hx * hy / 4.0

    rows = []
    cols = []
    vals = []
    rhs = np.zeros(total_dof)

    # Element assembly
    n_elem_x = Nx - 1
    n_elem_y = Ny - 1

    for ei in range(n_elem_x):
        for ej in range(n_elem_y):
            # Element nodes (local: 0,1,2,3 -> global)
            nodes = [
                nidx(ei, ej),
                nidx(ei + 1, ej),
                nidx(ei + 1, ej + 1),
                nidx(ei, ej + 1),
            ]

            # Element stiffness and mass matrices (4x4)
            Ke = np.zeros((4, 4))  # stiffness
            Me = np.zeros((4, 4))  # mass

            for gp in range(n_gp):
                N = _shape_functions(xi_g[gp], eta_g[gp])
                dN_dxi, dN_deta = _shape_derivatives(xi_g[gp], eta_g[gp])

                # Transform to physical coords
                dN_dx = dN_dxi / (hx / 2.0)
                dN_dy = dN_deta / (hy / 2.0)

                Ke += w_g[gp] * Jdet * (np.outer(dN_dx, dN_dx) + np.outer(dN_dy, dN_dy))
                Me += w_g[gp] * Jdet * np.outer(N, N)

            # Assemble into global system
            for a_loc in range(4):
                for b_loc in range(4):
                    ga = nodes[a_loc]
                    gb = nodes[b_loc]

                    # phi1 equation: D1*Ke + A11*Me
                    rows.append(ga)
                    cols.append(gb)
                    vals.append(D1 * Ke[a_loc, b_loc] + A11 * Me[a_loc, b_loc])

                    # phi1-phi2 coupling: A12*Me
                    rows.append(ga)
                    cols.append(N_nodes + gb)
                    vals.append(A12 * Me[a_loc, b_loc])

                    # phi2 equation: D2*Ke + A22*Me
                    rows.append(N_nodes + ga)
                    cols.append(N_nodes + gb)
                    vals.append(D2 * Ke[a_loc, b_loc] + A22 * Me[a_loc, b_loc])

                    # phi2-phi1 coupling: A21*Me
                    rows.append(N_nodes + ga)
                    cols.append(gb)
                    vals.append(A21 * Me[a_loc, b_loc])

    # Neumann BC at left boundary (x=-0.5): integral of q*N ds where q = y
    # The boundary integral -D_g * dphi_g/dn = q  contributes -q*N_a to RHS
    # Since outward normal at x=-0.5 is -x, we have -D_g * (-dphi_g/dx) = q
    # => D_g * dphi_g/dx = q, but the weak form gives integral of D*grad*N = ... + boundary
    # The natural BC in weak form: boundary integral = integral(q * N_a) ds
    # where q = -D_g * dphi_g/dn (the prescribed Neumann data)
    # At left boundary: outward normal n = (-1,0), so -D_g*dphi_g/dn = D_g*dphi_g/dx
    # The BC says: -D_g * dphi_g/dx = y => D_g * dphi_g/dn = y (since dn = -dx at left)
    # Wait, let me be precise.
    # The weak form of -D*lap(phi) + ... = 0 gives:
    #   integral(D * grad(phi) . grad(N)) + integral(A*phi*N) = integral_boundary(D * dphi/dn * N) ds
    # At left boundary (x=-0.5), outward normal n = (-1,0):
    #   D * dphi/dn = D * dphi/d(-x) = -D * dphi/dx
    # The BC states: -D * dphi/dx = y => D * dphi/dn = -(-D*dphi/dx) = ...
    # Actually: dphi/dn = grad(phi).n = dphi/dx * (-1) = -dphi/dx
    # So D * dphi/dn = -D * dphi/dx = y (from BC)
    # The boundary integral is: integral(D * dphi/dn * N_a) ds = integral(y * N_a) ds
    # This goes to the RHS.

    # Left boundary: x=-0.5, i=0, j varies
    # 1D Gauss quadrature on each edge element
    g1d = 1.0 / np.sqrt(3.0)
    pts_1d = np.array([-g1d, g1d])
    w_1d = np.array([1.0, 1.0])

    for ej in range(n_elem_y):
        # Edge on left boundary of element (ei=0, ej)
        # Nodes: nidx(0, ej) and nidx(0, ej+1) — local nodes 0 and 3
        n0 = nidx(0, ej)
        n3 = nidx(0, ej + 1)

        y0 = y_coords[ej]
        y1 = y_coords[ej + 1]

        for gp in range(2):
            eta_val = pts_1d[gp]
            # Map to physical y
            y_phys = 0.5 * (y0 + y1) + 0.5 * (y1 - y0) * eta_val
            # 1D shape functions on edge
            N0 = 0.5 * (1 - eta_val)
            N1 = 0.5 * (1 + eta_val)
            # Jacobian of 1D mapping
            J1d = hy / 2.0

            q = y_phys  # BC: D*dphi/dn = y

            # phi1 RHS
            rhs[n0] += w_1d[gp] * J1d * q * N0
            rhs[n3] += w_1d[gp] * J1d * q * N1
            # phi2 RHS (same BC)
            rhs[N_nodes + n0] += w_1d[gp] * J1d * q * N0
            rhs[N_nodes + n3] += w_1d[gp] * J1d * q * N1

    t_build = time.time() - t0
    logger.info(f"  System built in {t_build:.2f}s")

    # Assemble sparse matrix
    A_mat = sparse.csr_matrix(
        (vals, (rows, cols)), shape=(total_dof, total_dof)
    )

    logger.info("Solving sparse system...")
    t1 = time.time()
    sol = spsolve(A_mat, rhs)
    t_solve = time.time() - t1
    logger.info(f"  Solved in {t_solve:.2f}s")

    phi1_grid = sol[:N_nodes].reshape(Nx, Ny)
    phi2_grid = sol[N_nodes:].reshape(Nx, Ny)

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
    """Bilinear interpolation of FEM solution at a point."""
    from scipy.interpolate import RegularGridInterpolator

    interp1 = RegularGridInterpolator(
        (result["x"], result["y"]), result["phi1"], method="cubic"
    )
    interp2 = RegularGridInterpolator(
        (result["x"], result["y"]), result["phi2"], method="cubic"
    )
    p1 = float(interp1(np.array([[x_eval, y_eval]]))[0])
    p2 = float(interp2(np.array([[x_eval, y_eval]]))[0])
    return p1, p2


def compute_pde_residual(
    result: Dict, x_eval: float, y_eval: float, h: float = 1e-4
) -> Tuple[float, float]:
    """Compute PDE residual at a point using FD on interpolated solution."""
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
    """Compute BC residuals at sample boundary points."""
    bc_res = {}
    h = 1e-4

    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        x_val = -0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val + h, y_val)
        p1_2h, p2_2h = interpolate_at(result, x_val + 2 * h, y_val)
        dx1 = (-3 * p1_0 + 4 * p1_h - p1_2h) / (2 * h)
        dx2 = (-3 * p2_0 + 4 * p2_h - p2_2h) / (2 * h)
        bc_res[f"left(x={x_val},y={y_val})"] = (-D1 * dx1 - y_val, -D2 * dx2 - y_val)

    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        x_val = 0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val - h, y_val)
        p1_2h, p2_2h = interpolate_at(result, x_val - 2 * h, y_val)
        dx1 = (3 * p1_0 - 4 * p1_h + p1_2h) / (2 * h)
        dx2 = (3 * p2_0 - 4 * p2_h + p2_2h) / (2 * h)
        bc_res[f"right(x={x_val},y={y_val})"] = (-D1 * dx1, -D2 * dx2)

    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        y_val = 0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val, y_val - h)
        p1_2h, p2_2h = interpolate_at(result, x_val, y_val - 2 * h)
        dy1 = (3 * p1_0 - 4 * p1_h + p1_2h) / (2 * h)
        dy2 = (3 * p2_0 - 4 * p2_h + p2_2h) / (2 * h)
        bc_res[f"top(x={x_val},y={y_val})"] = (-D1 * dy1, -D2 * dy2)

    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        y_val = -0.5
        p1_0, p2_0 = interpolate_at(result, x_val, y_val)
        p1_h, p2_h = interpolate_at(result, x_val, y_val + h)
        p1_2h, p2_2h = interpolate_at(result, x_val, y_val + 2 * h)
        dy1 = (-3 * p1_0 + 4 * p1_h - p1_2h) / (2 * h)
        dy2 = (-3 * p2_0 + 4 * p2_h - p2_2h) / (2 * h)
        bc_res[f"bottom(x={x_val},y={y_val})"] = (-D1 * dy1, -D2 * dy2)

    return bc_res


def main() -> None:
    """Run FEM solver and save results."""
    out_dir = Path(__file__).parent
    test_points = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]

    result = solve_fem(Nx=101, Ny=101)

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
        "method": "Finite Element Method (FEM) - Bilinear Q1",
        "grid": f"{result['Nx']}x{result['Ny']}",
        "dof": 2 * result["Nx"] * result["Ny"],
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
