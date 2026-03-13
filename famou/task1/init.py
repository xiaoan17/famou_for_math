"""
init.py — Initial candidate solution for FaMou evolution.

Implements a Finite Difference Method (FDM) solver for the 2D two-group
neutron diffusion equation. This is the baseline seed for evolution.

The script must implement solution() which returns (phi1_func, phi2_func),
two callables that accept (x: float, y: float) and return the flux values.
"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.interpolate import RegularGridInterpolator

# Physical constants
D1 = 1.0
D2 = 0.5
A11 = 0.0075   # Sigma_r - nu*Sigma_f1
A12 = -0.25    # -nu*Sigma_f2
A21 = -0.015   # -Sigma_12
A22 = 0.1      # Sigma_a2


def _build_and_solve(Nx: int = 101, Ny: int = 101):
    """Build and solve FDM system, return grid solution."""
    hx = 1.0 / (Nx - 1)
    hy = 1.0 / (Ny - 1)
    N = Nx * Ny

    rows, cols, vals = [], [], []
    rhs = np.zeros(2 * N)

    x_coords = np.linspace(-0.5, 0.5, Nx)
    y_coords = np.linspace(-0.5, 0.5, Ny)

    def i1(i, j): return i * Ny + j
    def i2(i, j): return N + i * Ny + j

    for i in range(Nx):
        for j in range(Ny):
            e1, e2 = i1(i, j), i2(i, j)
            yv = y_coords[j]

            if i == 0:  # Left BC: -D_g * dphi_g/dx = y
                for e, D, fn in [(e1, D1, i1), (e2, D2, i2)]:
                    rows += [e, e, e]
                    cols += [fn(0,j), fn(1,j), fn(2,j)]
                    vals += [D*3/(2*hx), -D*4/(2*hx), D*1/(2*hx)]
                    rhs[e] = yv
                continue

            if i == Nx - 1:  # Right BC: dphi_g/dx = 0
                for e, fn in [(e1, i1), (e2, i2)]:
                    rows += [e, e, e]
                    cols += [fn(Nx-1,j), fn(Nx-2,j), fn(Nx-3,j)]
                    vals += [3/(2*hx), -4/(2*hx), 1/(2*hx)]
                continue

            if j == 0:  # Bottom BC: dphi_g/dy = 0 (forward diff)
                for e, fn in [(e1, i1), (e2, i2)]:
                    rows += [e, e, e]
                    cols += [fn(i,0), fn(i,1), fn(i,2)]
                    vals += [-3/(2*hy), 4/(2*hy), -1/(2*hy)]
                continue

            if j == Ny - 1:  # Top BC: dphi_g/dy = 0 (backward diff)
                for e, fn in [(e1, i1), (e2, i2)]:
                    rows += [e, e, e]
                    cols += [fn(i,Ny-1), fn(i,Ny-2), fn(i,Ny-3)]
                    vals += [3/(2*hy), -4/(2*hy), 1/(2*hy)]
                continue

            # Interior: discretize PDEs
            cc1 = 2*D1/hx**2 + 2*D1/hy**2 + A11
            cc2 = 2*D2/hx**2 + 2*D2/hy**2 + A22

            # phi1 equation
            rows += [e1]*6; cols += [i1(i,j), i1(i-1,j), i1(i+1,j), i1(i,j-1), i1(i,j+1), i2(i,j)]
            vals += [cc1, -D1/hx**2, -D1/hx**2, -D1/hy**2, -D1/hy**2, A12]

            # phi2 equation
            rows += [e2]*6; cols += [i2(i,j), i2(i-1,j), i2(i+1,j), i2(i,j-1), i2(i,j+1), i1(i,j)]
            vals += [cc2, -D2/hx**2, -D2/hx**2, -D2/hy**2, -D2/hy**2, A21]

    A_mat = sparse.csr_matrix((vals, (rows, cols)), shape=(2*N, 2*N))
    sol = spsolve(A_mat, rhs)
    phi1_grid = sol[:N].reshape(Nx, Ny)
    phi2_grid = sol[N:].reshape(Nx, Ny)
    return phi1_grid, phi2_grid, x_coords, y_coords


def solution():
    """Return (phi1_func, phi2_func) callables for the neutron flux solution.

    Returns:
        phi1_func: callable(x, y) -> float, fast-group flux
        phi2_func: callable(x, y) -> float, thermal-group flux
    """
    phi1_grid, phi2_grid, x_coords, y_coords = _build_and_solve(Nx=101, Ny=101)

    interp1 = RegularGridInterpolator(
        (x_coords, y_coords), phi1_grid, method="cubic",
        bounds_error=False, fill_value=None,
    )
    interp2 = RegularGridInterpolator(
        (x_coords, y_coords), phi2_grid, method="cubic",
        bounds_error=False, fill_value=None,
    )

    def phi1_func(x: float, y: float) -> float:
        return float(interp1([[x, y]])[0])

    def phi2_func(x: float, y: float) -> float:
        return float(interp2([[x, y]])[0])

    return phi1_func, phi2_func


if __name__ == "__main__":
    import json
    phi1_f, phi2_f = solution()
    test_points = [(0.0, 0.0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]
    results = {}
    for x, y in test_points:
        results[f"({x},{y})"] = {"phi1": phi1_f(x, y), "phi2": phi2_f(x, y)}
    print(json.dumps(results, indent=2))
