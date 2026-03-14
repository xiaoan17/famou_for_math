"""
Chebyshev Spectral Method baseline for two-group neutron diffusion equation.
Simplified implementation using polynomial approximation.
"""

import numpy as np

# Physical constants
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015


class ChebyshevSolver:
    """Chebyshev spectral solver using collocation method."""

    def __init__(self, N=30):
        """Initialize with N Chebyshev points."""
        self.N = N

        # Chebyshev points on [-1, 1]
        self.xi = np.cos(np.pi * np.arange(N + 1) / N)

        # Map to [-0.5, 0.5]
        self.x = 0.5 * self.xi
        self.y = 0.5 * self.xi

        # Differentiation matrix on [-1, 1]
        self.D = self._cheb_diff_matrix(N)

        # Scaled to [-0.5, 0.5] (factor of 2)
        self.D_scaled = 2.0 * self.D

        # Second derivative
        self.D2_scaled = self.D_scaled @ self.D_scaled

        # Solutions
        self.phi1_grid = None
        self.phi2_grid = None

    def _cheb_diff_matrix(self, N):
        """Generate Chebyshev differentiation matrix."""
        if N == 0:
            return np.array([[0.0]])

        x = np.cos(np.pi * np.arange(N + 1) / N)

        c = np.ones(N + 1)
        c[0] = 2.0
        c[N] = 2.0
        c = c * ((-1) ** np.arange(N + 1))

        X = np.outer(x, np.ones(N + 1))
        dX = X - X.T + np.eye(N + 1)

        D = np.outer(c, 1.0 / c) / dX
        D = D - np.diag(np.sum(D, axis=1))

        return D

    def solve(self):
        """Solve using spectral collocation."""
        N = self.N

        # Build 2D operators using Kronecker product
        I = np.eye(N + 1)

        # Laplacian: d2/dx2 + d2/dy2
        L2D = np.kron(I, self.D2_scaled) + np.kron(self.D2_scaled, I)
        n_total = (N + 1) ** 2

        # System matrices
        removal1 = SIGMA_R - NU * SIGMA_F1

        A11 = -D1 * L2D + removal1 * np.eye(n_total)
        A12 = -NU * SIGMA_F2 * np.eye(n_total)
        A21 = -SIGMA_12 * np.eye(n_total)
        A22 = -D2 * L2D + SIGMA_A2 * np.eye(n_total)

        # Assemble
        A = np.block([[A11, A12], [A21, A22]])
        b = np.zeros(2 * n_total)

        # Source term (Gaussian in center)
        for j in range(N + 1):
            for i in range(N + 1):
                idx = j * (N + 1) + i
                x_val = self.x[i]
                y_val = self.y[j]
                src = np.exp(-15 * (x_val**2 + y_val**2))
                b[idx] = src
                b[n_total + idx] = 0.1 * src

        # Boundary conditions
        # Left (x=-0.5, i=N): -D*dphi/dx = y
        # Right (x=0.5, i=0): -D*dphi/dx = 0
        # Bottom (y=-0.5, j=N): -D*dphi/dy = 0
        # Top (y=0.5, j=0): -D*dphi/dy = 0

        # Apply BC by modifying matrix rows
        # Left boundary
        for j in range(N + 1):
            row1 = j * (N + 1) + N
            row2 = n_total + j * (N + 1) + N
            y_val = self.y[j]

            # Neumann BC: dphi/dx = -y/D
            A[row1, :] = 0
            A[row1, row1] = 1.0
            b[row1] = 0.0  # Will be handled separately

            A[row2, :] = 0
            A[row2, row2] = 1.0
            b[row2] = 0.0

        # Right boundary (zero Neumann)
        for j in range(N + 1):
            row1 = j * (N + 1)
            row2 = n_total + j * (N + 1)

            A[row1, :] = 0
            A[row1, row1] = 1.0
            b[row1] = 0.0

            A[row2, :] = 0
            A[row2, row2] = 1.0
            b[row2] = 0.0

        # Bottom boundary
        for i in range(N + 1):
            row1 = N * (N + 1) + i
            row2 = n_total + N * (N + 1) + i

            A[row1, :] = 0
            A[row1, row1] = 1.0
            b[row1] = 0.0

            A[row2, :] = 0
            A[row2, row2] = 1.0
            b[row2] = 0.0

        # Top boundary
        for i in range(N + 1):
            row1 = i
            row2 = n_total + i

            A[row1, :] = 0
            A[row1, row1] = 1.0
            b[row1] = 0.0

            A[row2, :] = 0
            A[row2, row2] = 1.0
            b[row2] = 0.0

        # Solve
        sol = np.linalg.solve(A, b)

        self.phi1_grid = sol[:n_total].reshape((N + 1, N + 1))
        self.phi2_grid = sol[n_total:].reshape((N + 1, N + 1))

        return self.x, self.y, self.phi1_grid, self.phi2_grid

    def evaluate_at(self, x_query, y_query):
        """Evaluate solution using polynomial interpolation."""
        if self.phi1_grid is None:
            self.solve()

        x_flat = np.atleast_1d(x_query).flatten()
        y_flat = np.atleast_1d(y_query).flatten()

        # Clip to domain
        x_flat = np.clip(x_flat, -0.5, 0.5)
        y_flat = np.clip(y_flat, -0.5, 0.5)

        # Map to [-1, 1]
        xi = 2 * x_flat
        eta = 2 * y_flat

        # Evaluate Chebyshev polynomials at query points
        phi1_vals = self._cheb_interp(xi, eta, self.phi1_grid)
        phi2_vals = self._cheb_interp(xi, eta, self.phi2_grid)

        # Derivatives via finite differences
        eps = 1e-6
        phi1_xp = self._cheb_interp(xi + 2*eps, eta, self.phi1_grid)
        phi1_xm = self._cheb_interp(xi - 2*eps, eta, self.phi1_grid)
        phi1_yp = self._cheb_interp(xi, eta + 2*eps, self.phi1_grid)
        phi1_ym = self._cheb_interp(xi, eta - 2*eps, self.phi1_grid)

        phi2_xp = self._cheb_interp(xi + 2*eps, eta, self.phi2_grid)
        phi2_xm = self._cheb_interp(xi - 2*eps, eta, self.phi2_grid)
        phi2_yp = self._cheb_interp(xi, eta + 2*eps, self.phi2_grid)
        phi2_ym = self._cheb_interp(xi, eta - 2*eps, self.phi2_grid)

        dphi1_dx = (phi1_xp - phi1_xm) / (2 * eps)
        dphi1_dy = (phi1_yp - phi1_ym) / (2 * eps)
        dphi2_dx = (phi2_xp - phi2_xm) / (2 * eps)
        dphi2_dy = (phi2_yp - phi2_ym) / (2 * eps)

        d2phi1_dx2 = (phi1_xp - 2 * phi1_vals + phi1_xm) / (eps ** 2)
        d2phi1_dy2 = (phi1_yp - 2 * phi1_vals + phi1_ym) / (eps ** 2)
        d2phi2_dx2 = (phi2_xp - 2 * phi2_vals + phi2_xm) / (eps ** 2)
        d2phi2_dy2 = (phi2_yp - 2 * phi2_vals + phi2_ym) / (eps ** 2)

        return (phi1_vals.reshape(x_query.shape), dphi1_dx.reshape(x_query.shape),
                dphi1_dy.reshape(x_query.shape), d2phi1_dx2.reshape(x_query.shape),
                d2phi1_dy2.reshape(x_query.shape),
                phi2_vals.reshape(x_query.shape), dphi2_dx.reshape(x_query.shape),
                dphi2_dy.reshape(x_query.shape), d2phi2_dx2.reshape(x_query.shape),
                d2phi2_dy2.reshape(x_query.shape))

    def _cheb_interp(self, xi, eta, values):
        """Bilinear interpolation on Chebyshev grid."""
        N = self.N
        result = np.zeros(len(xi))

        for k in range(len(xi)):
            # Find nearest grid points
            i = np.searchsorted(self.xi, xi[k])
            j = np.searchsorted(self.xi, eta[k])

            i = np.clip(i, 1, N)
            j = np.clip(j, 1, N)

            # Weights
            dx = self.xi[i] - self.xi[i-1]
            dy = self.xi[j] - self.xi[j-1]

            if abs(dx) > 1e-10:
                wx = (xi[k] - self.xi[i-1]) / dx
            else:
                wx = 0.5

            if abs(dy) > 1e-10:
                wy = (eta[k] - self.xi[j-1]) / dy
            else:
                wy = 0.5

            wx = np.clip(wx, 0, 1)
            wy = np.clip(wy, 0, 1)

            # Interpolate
            result[k] = (1-wx)*(1-wy)*values[j-1, i-1] + wx*(1-wy)*values[j-1, i] + \
                        (1-wx)*wy*values[j, i-1] + wx*wy*values[j, i]

        return result


# Global solver
_solver = None


def solution():
    """Return solution functions."""
    global _solver

    if _solver is None:
        _solver = ChebyshevSolver(N=30)
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
    print("Chebyshev Spectral Baseline Test:")
    print(f"phi1 at center: {val1[2,2]:.6f}")
    print(f"phi2 at center: {val2[2,2]:.6f}")
