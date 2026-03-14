"""
Finite Element Method (FEM) baseline for two-group neutron diffusion equation.

Simplified implementation using finite difference approximation on a mesh.
"""

import numpy as np
from scipy.sparse import csr_matrix, diags, bmat
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


class FEMSolver:
    """Simplified FEM solver using finite element-like discretization."""

    def __init__(self, nx=65, ny=65):
        """Initialize FEM solver with mesh size."""
        self.nx = nx
        self.ny = ny

        # Mesh coordinates
        self.x = np.linspace(-0.5, 0.5, nx)
        self.y = np.linspace(-0.5, 0.5, ny)
        self.hx = self.x[1] - self.x[0]
        self.hy = self.y[1] - self.y[0]

        # Solutions
        self.phi1 = None
        self.phi2 = None

    def _build_stiffness_matrix(self):
        """Build stiffness matrix using bilinear elements."""
        nx, ny = self.nx, self.ny
        N = nx * ny

        # Assemble matrix using finite element approach
        # For each node, compute contributions from surrounding elements

        data = []
        row_idx = []
        col_idx = []

        for j in range(ny):
            for i in range(nx):
                idx = j * nx + i

                # Diagonal entry
                diag_val = 0.0

                # Check if node has left neighbor
                if i > 0:
                    diag_val += D1 / self.hx**2
                    row_idx.append(idx)
                    col_idx.append(idx - 1)
                    data.append(-D1 / self.hx**2)

                # Check if node has right neighbor
                if i < nx - 1:
                    diag_val += D1 / self.hx**2
                    row_idx.append(idx)
                    col_idx.append(idx + 1)
                    data.append(-D1 / self.hx**2)

                # Check if node has bottom neighbor
                if j > 0:
                    diag_val += D1 / self.hy**2
                    row_idx.append(idx)
                    col_idx.append(idx - nx)
                    data.append(-D1 / self.hy**2)

                # Check if node has top neighbor
                if j < ny - 1:
                    diag_val += D1 / self.hy**2
                    row_idx.append(idx)
                    col_idx.append(idx + nx)
                    data.append(-D1 / self.hy**2)

                # Add diagonal
                row_idx.append(idx)
                col_idx.append(idx)
                data.append(diag_val)

        K = csr_matrix((data, (row_idx, col_idx)), shape=(N, N))
        return K

    def solve(self):
        """Solve the FEM system."""
        nx, ny = self.nx, self.ny
        N = nx * ny

        # Build stiffness matrix
        K = self._build_stiffness_matrix()

        # Mass matrix (lumped)
        M = diags(np.ones(N) * self.hx * self.hy, format='csr')

        # System matrices
        removal1 = SIGMA_R - NU * SIGMA_F1

        A11 = K + removal1 * M
        A12 = -NU * SIGMA_F2 * M
        A21 = -SIGMA_12 * M
        A22 = (D2/D1) * K + SIGMA_A2 * M  # Scale K by D2/D1 for group 2

        # Assemble block matrix
        A = bmat([[A11, A12], [A21, A22]], format='csr')

        # RHS with source and BC
        b = np.zeros(2 * N)

        # Source term
        for j in range(ny):
            for i in range(nx):
                idx = j * nx + i
                x_val = self.x[i]
                y_val = self.y[j]
                src = np.exp(-12 * (x_val**2 + y_val**2))
                b[idx] = src * self.hx * self.hy
                b[N + idx] = 0.1 * src * self.hx * self.hy

        # Apply boundary conditions
        # Left boundary (x=-0.5): -D*dphi/dx = y
        for j in range(ny):
            idx1 = j * nx
            idx2 = N + j * nx
            y_val = self.y[j]

            # Neumann BC contribution
            b[idx1] += 2 * y_val * self.hy
            b[idx2] += 2 * y_val * self.hy

        # Solve
        sol = spsolve(A, b)

        self.phi1 = sol[:N].reshape((ny, nx))
        self.phi2 = sol[N:].reshape((ny, nx))

        return self.x, self.y, self.phi1, self.phi2

    def evaluate_at(self, x_query, y_query):
        """Evaluate solution using bilinear interpolation."""
        if self.phi1 is None:
            self.solve()

        x_flat = np.atleast_1d(x_query).flatten()
        y_flat = np.atleast_1d(y_query).flatten()

        x_flat = np.clip(x_flat, -0.5, 0.5)
        y_flat = np.clip(y_flat, -0.5, 0.5)

        # Find indices
        ix = np.floor((x_flat - self.x[0]) / self.hx).astype(int)
        iy = np.floor((y_flat - self.y[0]) / self.hy).astype(int)

        ix = np.clip(ix, 0, self.nx - 2)
        iy = np.clip(iy, 0, self.ny - 2)

        # Weights
        wx = (x_flat - self.x[ix]) / self.hx
        wy = (y_flat - self.y[iy]) / self.hy

        # Interpolate
        phi1_val = (1-wx)*(1-wy)*self.phi1[iy, ix] + wx*(1-wy)*self.phi1[iy, ix+1] + \
                   (1-wx)*wy*self.phi1[iy+1, ix] + wx*wy*self.phi1[iy+1, ix+1]

        phi2_val = (1-wx)*(1-wy)*self.phi2[iy, ix] + wx*(1-wy)*self.phi2[iy, ix+1] + \
                   (1-wx)*wy*self.phi2[iy+1, ix] + wx*wy*self.phi2[iy+1, ix+1]

        # Derivatives via FD
        eps = 1e-6

        def get_phi1(x, y):
            xf = np.atleast_1d(x).flatten()
            yf = np.atleast_1d(y).flatten()
            i = np.clip(np.floor((xf - self.x[0]) / self.hx).astype(int), 0, self.nx - 2)
            j = np.clip(np.floor((yf - self.y[0]) / self.hy).astype(int), 0, self.ny - 2)
            w = (xf - self.x[i]) / self.hx
            z = (yf - self.y[j]) / self.hy
            return (1-w)*(1-z)*self.phi1[j, i] + w*(1-z)*self.phi1[j, i+1] + \
                   (1-w)*z*self.phi1[j+1, i] + w*z*self.phi1[j+1, i+1]

        def get_phi2(x, y):
            xf = np.atleast_1d(x).flatten()
            yf = np.atleast_1d(y).flatten()
            i = np.clip(np.floor((xf - self.x[0]) / self.hx).astype(int), 0, self.nx - 2)
            j = np.clip(np.floor((yf - self.y[0]) / self.hy).astype(int), 0, self.ny - 2)
            w = (xf - self.x[i]) / self.hx
            z = (yf - self.y[j]) / self.hy
            return (1-w)*(1-z)*self.phi2[j, i] + w*(1-z)*self.phi2[j, i+1] + \
                   (1-w)*z*self.phi2[j+1, i] + w*z*self.phi2[j+1, i+1]

        phi1_xp = get_phi1(x_flat + eps, y_flat)
        phi1_xm = get_phi1(x_flat - eps, y_flat)
        phi1_yp = get_phi1(x_flat, y_flat + eps)
        phi1_ym = get_phi1(x_flat, y_flat - eps)

        phi2_xp = get_phi2(x_flat + eps, y_flat)
        phi2_xm = get_phi2(x_flat - eps, y_flat)
        phi2_yp = get_phi2(x_flat, y_flat + eps)
        phi2_ym = get_phi2(x_flat, y_flat - eps)

        dphi1_dx = (phi1_xp - phi1_xm) / (2 * eps)
        dphi1_dy = (phi1_yp - phi1_ym) / (2 * eps)
        dphi2_dx = (phi2_xp - phi2_xm) / (2 * eps)
        dphi2_dy = (phi2_yp - phi2_ym) / (2 * eps)

        d2phi1_dx2 = (phi1_xp - 2*phi1_val + phi1_xm) / (eps**2)
        d2phi1_dy2 = (phi1_yp - 2*phi1_val + phi1_ym) / (eps**2)
        d2phi2_dx2 = (phi2_xp - 2*phi2_val + phi2_xm) / (eps**2)
        d2phi2_dy2 = (phi2_yp - 2*phi2_val + phi2_ym) / (eps**2)

        return (phi1_val.reshape(x_query.shape), dphi1_dx.reshape(x_query.shape),
                dphi1_dy.reshape(x_query.shape), d2phi1_dx2.reshape(x_query.shape),
                d2phi1_dy2.reshape(x_query.shape),
                phi2_val.reshape(x_query.shape), dphi2_dx.reshape(x_query.shape),
                dphi2_dy.reshape(x_query.shape), d2phi2_dx2.reshape(x_query.shape),
                d2phi2_dy2.reshape(x_query.shape))


# Global solver
_solver = None


def solution():
    """Return solution functions."""
    global _solver

    if _solver is None:
        _solver = FEMSolver(nx=65, ny=65)
        _solver.solve()

    def phi1(x, y):
        r = _solver.evaluate_at(x, y)
        return r[0], r[1], r[2], r[3], r[4]

    def phi2(x, y):
        r = _solver.evaluate_at(x, y)
        return r[5], r[6], r[7], r[8], r[9]

    return phi1, phi2


if __name__ == "__main__":
    phi1, phi2 = solution()
    X, Y = np.meshgrid(np.linspace(-0.4, 0.4, 5), np.linspace(-0.4, 0.4, 5))
    val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
    val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)
    print("FEM Baseline Test:")
    print(f"phi1 at center: {val1[2,2]:.6f}")
    print(f"phi2 at center: {val2[2,2]:.6f}")
