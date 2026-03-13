"""
init.py — Initial candidate solution for FaMou evolution.

Implements a Finite Difference Method (FDM) solver for the 2D two-group
neutron diffusion equation. Baseline seed for evolution.

Must implement solution() -> (phi1_func, phi2_func).
"""
import numpy as np

# Physical constants
D1 = 1.0
D2 = 0.5
A11 = 0.0075   # Sigma_r - nu*Sigma_f1
A12 = -0.25    # -nu*Sigma_f2
A21 = -0.015   # -Sigma_12
A22 = 0.1      # Sigma_a2


def _bilinear_interp(phi_grid, x_coords, y_coords, x, y):
    """Bilinear interpolation on a regular grid."""
    x = float(np.clip(x, x_coords[0], x_coords[-1]))
    y = float(np.clip(y, y_coords[0], y_coords[-1]))
    i = int(np.searchsorted(x_coords, x)) - 1
    j = int(np.searchsorted(y_coords, y)) - 1
    i = int(np.clip(i, 0, len(x_coords) - 2))
    j = int(np.clip(j, 0, len(y_coords) - 2))
    tx = (x - x_coords[i]) / (x_coords[i+1] - x_coords[i])
    ty = (y - y_coords[j]) / (y_coords[j+1] - y_coords[j])
    return (phi_grid[i, j] * (1-tx)*(1-ty)
            + phi_grid[i+1, j] * tx*(1-ty)
            + phi_grid[i, j+1] * (1-tx)*ty
            + phi_grid[i+1, j+1] * tx*ty)


def _build_and_solve(Nx=101, Ny=101):
    """Build sparse FDM system and solve via numpy for 2-group diffusion."""
    try:
        from scipy import sparse
        from scipy.sparse.linalg import spsolve
        _scipy = True
    except Exception:
        _scipy = False

    hx = 1.0 / (Nx - 1)
    hy = 1.0 / (Ny - 1)
    N = Nx * Ny

    x_coords = np.linspace(-0.5, 0.5, Nx)
    y_coords = np.linspace(-0.5, 0.5, Ny)

    def i1(i, j): return i * Ny + j
    def i2(i, j): return N + i * Ny + j

    if _scipy:
        rows, cols, vals = [], [], []
        rhs = np.zeros(2 * N)

        for i in range(Nx):
            for j in range(Ny):
                e1, e2 = i1(i, j), i2(i, j)
                yv = y_coords[j]

                if i == 0:
                    for e, D, fn in [(e1, D1, i1), (e2, D2, i2)]:
                        rows += [e, e, e]
                        cols += [fn(0,j), fn(1,j), fn(2,j)]
                        vals += [D*3/(2*hx), -D*4/(2*hx), D/(2*hx)]
                        rhs[e] = yv
                    continue

                if i == Nx - 1:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        rows += [e, e, e]
                        cols += [fn(Nx-1,j), fn(Nx-2,j), fn(Nx-3,j)]
                        vals += [3/(2*hx), -4/(2*hx), 1/(2*hx)]
                    continue

                if j == 0:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        rows += [e, e, e]
                        cols += [fn(i,0), fn(i,1), fn(i,2)]
                        vals += [-3/(2*hy), 4/(2*hy), -1/(2*hy)]
                    continue

                if j == Ny - 1:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        rows += [e, e, e]
                        cols += [fn(i,Ny-1), fn(i,Ny-2), fn(i,Ny-3)]
                        vals += [3/(2*hy), -4/(2*hy), 1/(2*hy)]
                    continue

                cc1 = 2*D1/hx**2 + 2*D1/hy**2 + A11
                cc2 = 2*D2/hx**2 + 2*D2/hy**2 + A22

                rows += [e1]*6
                cols += [i1(i,j), i1(i-1,j), i1(i+1,j), i1(i,j-1), i1(i,j+1), i2(i,j)]
                vals += [cc1, -D1/hx**2, -D1/hx**2, -D1/hy**2, -D1/hy**2, A12]

                rows += [e2]*6
                cols += [i2(i,j), i2(i-1,j), i2(i+1,j), i2(i,j-1), i2(i,j+1), i1(i,j)]
                vals += [cc2, -D2/hx**2, -D2/hx**2, -D2/hy**2, -D2/hy**2, A21]

        A_mat = sparse.csr_matrix((vals, (rows, cols)), shape=(2*N, 2*N))
        sol = spsolve(A_mat, rhs)
    else:
        # Fallback: dense numpy (only feasible for small grids)
        Nx, Ny = min(Nx, 31), min(Ny, 31)
        hx = 1.0 / (Nx - 1)
        hy = 1.0 / (Ny - 1)
        N = Nx * Ny
        x_coords = np.linspace(-0.5, 0.5, Nx)
        y_coords = np.linspace(-0.5, 0.5, Ny)
        A_dense = np.zeros((2*N, 2*N))
        rhs = np.zeros(2*N)
        for i in range(Nx):
            for j in range(Ny):
                e1, e2 = i1(i, j), i2(i, j)
                yv = y_coords[j]
                if i == 0:
                    for e, D, fn in [(e1, D1, i1), (e2, D2, i2)]:
                        A_dense[e, fn(0,j)] = D*3/(2*hx)
                        A_dense[e, fn(1,j)] = -D*4/(2*hx)
                        A_dense[e, fn(2,j)] = D/(2*hx)
                        rhs[e] = yv
                    continue
                if i == Nx-1:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        A_dense[e, fn(Nx-1,j)] = 3/(2*hx)
                        A_dense[e, fn(Nx-2,j)] = -4/(2*hx)
                        A_dense[e, fn(Nx-3,j)] = 1/(2*hx)
                    continue
                if j == 0:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        A_dense[e, fn(i,0)] = -3/(2*hy)
                        A_dense[e, fn(i,1)] = 4/(2*hy)
                        A_dense[e, fn(i,2)] = -1/(2*hy)
                    continue
                if j == Ny-1:
                    for e, fn in [(e1, i1), (e2, i2)]:
                        A_dense[e, fn(i,Ny-1)] = 3/(2*hy)
                        A_dense[e, fn(i,Ny-2)] = -4/(2*hy)
                        A_dense[e, fn(i,Ny-3)] = 1/(2*hy)
                    continue
                cc1 = 2*D1/hx**2 + 2*D1/hy**2 + A11
                cc2 = 2*D2/hx**2 + 2*D2/hy**2 + A22
                A_dense[e1, i1(i,j)] = cc1
                A_dense[e1, i1(i-1,j)] = -D1/hx**2
                A_dense[e1, i1(i+1,j)] = -D1/hx**2
                A_dense[e1, i1(i,j-1)] = -D1/hy**2
                A_dense[e1, i1(i,j+1)] = -D1/hy**2
                A_dense[e1, i2(i,j)] = A12
                A_dense[e2, i2(i,j)] = cc2
                A_dense[e2, i2(i-1,j)] = -D2/hx**2
                A_dense[e2, i2(i+1,j)] = -D2/hx**2
                A_dense[e2, i2(i,j-1)] = -D2/hy**2
                A_dense[e2, i2(i,j+1)] = -D2/hy**2
                A_dense[e2, i1(i,j)] = A21
        sol = np.linalg.solve(A_dense, rhs)

    phi1_grid = sol[:N].reshape(Nx, Ny)
    phi2_grid = sol[N:].reshape(Nx, Ny)
    return phi1_grid, phi2_grid, x_coords, y_coords


def solution():
    """Return (phi1_func, phi2_func) callables for the neutron flux solution."""
    phi1_grid, phi2_grid, x_coords, y_coords = _build_and_solve(Nx=101, Ny=101)

    def phi1_func(x: float, y: float) -> float:
        return float(_bilinear_interp(phi1_grid, x_coords, y_coords, x, y))

    def phi2_func(x: float, y: float) -> float:
        return float(_bilinear_interp(phi2_grid, x_coords, y_coords, x, y))

    return phi1_func, phi2_func


if __name__ == "__main__":
    import json
    phi1_f, phi2_f = solution()
    test_points = [(0.0, 0.0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]
    results = {}
    for x, y in test_points:
        results[f"({x},{y})"] = {"phi1": phi1_f(x, y), "phi2": phi2_f(x, y)}
    print(json.dumps(results, indent=2))
