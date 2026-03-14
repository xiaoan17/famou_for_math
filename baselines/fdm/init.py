"""
FDM baseline solution for two-group neutron diffusion equation.
This file provides the solution() interface required by the evaluator.
"""

import numpy as np
from scipy.sparse import csr_matrix, kron, diags, lil_matrix, bmat
from scipy.sparse.linalg import spsolve


# Physical constants
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015


class FDMSolver:
    """Finite Difference Method solver for 2D two-group neutron diffusion."""

    def __init__(self, nx=101, ny=101):
        """
        Initialize FDM solver.

        Args:
            nx: Number of grid points in x direction
            ny: Number of grid points in y direction
        """
        self.nx = nx
        self.ny = ny

        # Grid setup
        self.x = np.linspace(-0.5, 0.5, nx)
        self.y = np.linspace(-0.5, 0.5, ny)
        self.hx = self.x[1] - self.x[0]
        self.hy = self.y[1] - self.y[0]

        # Solutions
        self.phi1 = None
        self.phi2 = None

    def _build_laplacian_1d(self, n, h):
        """Build 1D Laplacian matrix with Neumann BC."""
        main_diag = -2.0 * np.ones(n) / (h ** 2)
        off_diag = np.ones(n - 1) / (h ** 2)

        L = diags([off_diag, main_diag, off_diag], [-1, 0, 1], format='lil')

        # Neumann BC: ghost point method for zero derivative
        L[0, 0] = -2.0 / (h ** 2)
        L[0, 1] = 2.0 / (h ** 2)

        L[-1, -1] = -2.0 / (h ** 2)
        L[-1, -2] = 2.0 / (h ** 2)

        return L

    def _build_system(self):
        """Build the coupled linear system for two-group diffusion."""
        nx, ny = self.nx, self.ny
        hx, hy = self.hx, self.hy
        N = nx * ny

        # Build 1D Laplacians
        Lx = self._build_laplacian_1d(nx, hx)
        Ly = self._build_laplacian_1d(ny, hy)

        # 2D Laplacian
        Ix = diags(np.ones(nx), format='csr')
        Iy = diags(np.ones(ny), format='csr')

        L2D = kron(Iy, Lx) + kron(Ly, Ix)

        # Build system matrices
        removal1 = SIGMA_R - NU * SIGMA_F1

        A11 = -D1 * L2D + removal1 * diags(np.ones(N), format='csr')
        A12 = -NU * SIGMA_F2 * diags(np.ones(N), format='csr')
        A21 = -SIGMA_12 * diags(np.ones(N), format='csr')
        A22 = -D2 * L2D + SIGMA_A2 * diags(np.ones(N), format='csr')

        # Assemble block matrix
        A = bmat([[A11, A12], [A21, A22]], format='csr')

        # Build RHS with boundary conditions and source
        b = np.zeros(2 * N)

        # Add external source to drive the system
        for j in range(ny):
            for i in range(nx):
                idx = j * nx + i
                x_val = self.x[i]
                y_val = self.y[j]
                source_val = np.exp(-20 * (x_val**2 + y_val**2))
                b[idx] = source_val
                b[N + idx] = 0.1 * source_val

        # Apply non-homogeneous Neumann BC on left boundary (x = -0.5)
        for j in range(ny):
            idx1 = j * nx
            idx2 = N + j * nx
            y_val = self.y[j]
            b[idx1] += 2 * y_val / hx
            b[idx2] += 2 * y_val / hx

        return A, b

    def solve(self):
        """Solve the linear system."""
        A, b = self._build_system()
        sol = spsolve(A, b)

        N = self.nx * self.ny
        self.phi1 = sol[:N].reshape((self.ny, self.nx))
        self.phi2 = sol[N:].reshape((self.ny, self.nx))

        return self.x, self.y, self.phi1, self.phi2

    def evaluate_at(self, x_query, y_query):
        """Evaluate solution at query points using bilinear interpolation."""
        if self.phi1 is None:
            self.solve()

        x_flat = np.atleast_1d(x_query).flatten()
        y_flat = np.atleast_1d(y_query).flatten()

        x_flat = np.clip(x_flat, -0.5, 0.5)
        y_flat = np.clip(y_flat, -0.5, 0.5)

        ix = np.floor((x_flat - self.x[0]) / self.hx).astype(int)
        iy = np.floor((y_flat - self.y[0]) / self.hy).astype(int)

        ix = np.clip(ix, 0, self.nx - 2)
        iy = np.clip(iy, 0, self.ny - 2)

        wx = (x_flat - self.x[ix]) / self.hx
        wy = (y_flat - self.y[iy]) / self.hy

        # Interpolate phi1
        phi1_val = (1 - wx) * (1 - wy) * self.phi1[iy, ix] + \
                   wx * (1 - wy) * self.phi1[iy, ix + 1] + \
                   (1 - wx) * wy * self.phi1[iy + 1, ix] + \
                   wx * wy * self.phi1[iy + 1, ix + 1]

        # Interpolate phi2
        phi2_val = (1 - wx) * (1 - wy) * self.phi2[iy, ix] + \
                   wx * (1 - wy) * self.phi2[iy, ix + 1] + \
                   (1 - wx) * wy * self.phi2[iy + 1, ix] + \
                   wx * wy * self.phi2[iy + 1, ix + 1]

        # Compute derivatives
        dphi1_dx = np.zeros_like(phi1_val)
        dphi2_dx = np.zeros_like(phi2_val)

        for i in range(len(x_flat)):
            ix_i, iy_i = ix[i], iy[i]
            if ix_i > 0 and ix_i < self.nx - 2:
                dphi1_dx[i] = (self.phi1[iy_i, ix_i + 1] - self.phi1[iy_i, ix_i - 1]) / (2 * self.hx)
                dphi2_dx[i] = (self.phi2[iy_i, ix_i + 1] - self.phi2[iy_i, ix_i - 1]) / (2 * self.hx)
            else:
                dphi1_dx[i] = (self.phi1[iy_i, ix_i + 1] - self.phi1[iy_i, ix_i]) / self.hx
                dphi2_dx[i] = (self.phi2[iy_i, ix_i + 1] - self.phi2[iy_i, ix_i]) / self.hx

        dphi1_dy = np.zeros_like(phi1_val)
        dphi2_dy = np.zeros_like(phi2_val)

        for i in range(len(y_flat)):
            ix_i, iy_i = ix[i], iy[i]
            if iy_i > 0 and iy_i < self.ny - 2:
                dphi1_dy[i] = (self.phi1[iy_i + 1, ix_i] - self.phi1[iy_i - 1, ix_i]) / (2 * self.hy)
                dphi2_dy[i] = (self.phi2[iy_i + 1, ix_i] - self.phi2[iy_i - 1, ix_i]) / (2 * self.hy)
            else:
                dphi1_dy[i] = (self.phi1[iy_i + 1, ix_i] - self.phi1[iy_i, ix_i]) / self.hy
                dphi2_dy[i] = (self.phi2[iy_i + 1, ix_i] - self.phi2[iy_i, ix_i]) / self.hy

        d2phi1_dx2 = np.zeros_like(phi1_val)
        d2phi2_dx2 = np.zeros_like(phi2_val)

        for i in range(len(x_flat)):
            ix_i, iy_i = ix[i], iy[i]
            if ix_i > 0 and ix_i < self.nx - 2:
                d2phi1_dx2[i] = (self.phi1[iy_i, ix_i + 1] - 2 * self.phi1[iy_i, ix_i] + self.phi1[iy_i, ix_i - 1]) / (self.hx ** 2)
                d2phi2_dx2[i] = (self.phi2[iy_i, ix_i + 1] - 2 * self.phi2[iy_i, ix_i] + self.phi2[iy_i, ix_i - 1]) / (self.hx ** 2)
            else:
                d2phi1_dx2[i] = (self.phi1[iy_i, ix_i + 1] - 2 * self.phi1[iy_i, ix_i] + self.phi1[iy_i, max(0, ix_i - 1)]) / (self.hx ** 2)
                d2phi2_dx2[i] = (self.phi2[iy_i, ix_i + 1] - 2 * self.phi2[iy_i, ix_i] + self.phi2[iy_i, max(0, ix_i - 1)]) / (self.hx ** 2)

        d2phi1_dy2 = np.zeros_like(phi1_val)
        d2phi2_dy2 = np.zeros_like(phi2_val)

        for i in range(len(y_flat)):
            ix_i, iy_i = ix[i], iy[i]
            if iy_i > 0 and iy_i < self.ny - 2:
                d2phi1_dy2[i] = (self.phi1[iy_i + 1, ix_i] - 2 * self.phi1[iy_i, ix_i] + self.phi1[iy_i - 1, ix_i]) / (self.hy ** 2)
                d2phi2_dy2[i] = (self.phi2[iy_i + 1, ix_i] - 2 * self.phi2[iy_i, ix_i] + self.phi2[iy_i - 1, ix_i]) / (self.hy ** 2)
            else:
                d2phi1_dy2[i] = (self.phi1[iy_i + 1, ix_i] - 2 * self.phi1[iy_i, ix_i] + self.phi1[max(0, iy_i - 1), ix_i]) / (self.hy ** 2)
                d2phi2_dy2[i] = (self.phi2[iy_i + 1, ix_i] - 2 * self.phi2[iy_i, ix_i] + self.phi2[max(0, iy_i - 1), ix_i]) / (self.hy ** 2)

        return (phi1_val.reshape(x_query.shape), dphi1_dx.reshape(x_query.shape),
                dphi1_dy.reshape(x_query.shape), d2phi1_dx2.reshape(x_query.shape),
                d2phi1_dy2.reshape(x_query.shape),
                phi2_val.reshape(x_query.shape), dphi2_dx.reshape(x_query.shape),
                dphi2_dy.reshape(x_query.shape), d2phi2_dx2.reshape(x_query.shape),
                d2phi2_dy2.reshape(x_query.shape))


# Global solver instance
_solver = None


def solution():
    """
    Return solution functions phi1 and phi2.

    Returns:
        tuple: (phi1_func, phi2_func)
               Each function takes (x, y) arrays and returns:
               (value, d_dx, d_dy, d2_dx2, d2_dy2)
    """
    global _solver

    if _solver is None:
        _solver = FDMSolver(nx=101, ny=101)
        _solver.solve()

    def phi1(x, y):
        """Fast group flux."""
        results = _solver.evaluate_at(x, y)
        return results[0], results[1], results[2], results[3], results[4]

    def phi2(x, y):
        """Thermal group flux."""
        results = _solver.evaluate_at(x, y)
        return results[5], results[6], results[7], results[8], results[9]

    return phi1, phi2


if __name__ == "__main__":
    phi1, phi2 = solution()
    X, Y = np.meshgrid(np.linspace(-0.4, 0.4, 5), np.linspace(-0.4, 0.4, 5))
    val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
    val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)
    print("FDM Baseline Test:")
    print(f"phi1 at center: {val1[2,2]:.6f}")
    print(f"phi2 at center: {val2[2,2]:.6f}")
