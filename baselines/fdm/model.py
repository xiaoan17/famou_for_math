"""
Finite Difference Method (FDM) solver for two-group neutron diffusion equation.

Equation system:
    -D1 * nabla^2(phi1) + Sigma_r * phi1 = nu*Sigma_f1*phi1 + nu*Sigma_f2*phi2 + S1_ext
    -D2 * nabla^2(phi2) + Sigma_a2 * phi2 = Sigma_12 * phi1 + S2_ext

Boundary conditions:
    Left (x=-0.5):  -D * dphi/dx = y
    Right (x=0.5):  -D * dphi/dx = 0
    Top (y=0.5):    -D * dphi/dy = 0
    Bottom (y=-0.5): -D * dphi/dy = 0
"""

import numpy as np
from scipy.sparse import csr_matrix, kron, diags, lil_matrix, bmat
from scipy.sparse.linalg import spsolve


class FDMSolver:
    """Finite Difference Method solver for 2D two-group neutron diffusion."""

    # Physical constants
    D1 = 1.0
    D2 = 0.5
    SIGMA_R = 0.02
    SIGMA_A2 = 0.1
    NU = 2.5
    SIGMA_F1 = 0.005
    SIGMA_F2 = 0.1
    SIGMA_12 = 0.015

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
        # Interior: standard stencil
        main_diag = -2.0 * np.ones(n) / (h ** 2)
        off_diag = np.ones(n - 1) / (h ** 2)

        L = diags([off_diag, main_diag, off_diag], [-1, 0, 1], format='lil')

        # Neumann BC: ghost point method for zero derivative
        # For zero Neumann at left: (u[1] - u[-1])/(2h) = 0 => u[-1] = u[1]
        # Modified equation at boundary: (u[1] - 2*u[0] + u[-1])/h^2 = (2*u[1] - 2*u[0])/h^2
        L[0, 0] = -2.0 / (h ** 2)
        L[0, 1] = 2.0 / (h ** 2)

        # At right boundary
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

        # 2D Laplacian: L = kron(I_y, L_x) + kron(L_y, I_x)
        Ix = diags(np.ones(nx), format='csr')
        Iy = diags(np.ones(ny), format='csr')

        L2D = kron(Iy, Lx) + kron(Ly, Ix)

        # Build system matrices for each group
        # Group 1: -D1 * nabla^2(phi1) + (Sigma_r - nu*Sigma_f1)*phi1 - nu*Sigma_f2*phi2 = S1
        # Group 2: -D2 * nabla^2(phi2) + Sigma_a2*phi2 - Sigma_12*phi1 = S2

        removal1 = self.SIGMA_R - self.NU * self.SIGMA_F1  # 0.02 - 0.0125 = 0.0075

        A11 = -self.D1 * L2D + removal1 * diags(np.ones(N), format='csr')
        A12 = -self.NU * self.SIGMA_F2 * diags(np.ones(N), format='csr')
        A21 = -self.SIGMA_12 * diags(np.ones(N), format='csr')
        A22 = -self.D2 * L2D + self.SIGMA_A2 * diags(np.ones(N), format='csr')

        # Assemble block matrix
        A = bmat([[A11, A12], [A21, A22]], format='csr')

        # Build RHS with boundary conditions and source
        b = np.zeros(2 * N)

        # Add external source to drive the system (to avoid trivial solution)
        # Place a source in the center region
        for j in range(ny):
            for i in range(nx):
                idx = j * nx + i
                x_val = self.x[i]
                y_val = self.y[j]
                # Gaussian source in center
                source_val = np.exp(-20 * (x_val**2 + y_val**2))
                b[idx] = source_val  # Source for group 1
                b[N + idx] = 0.1 * source_val  # Source for group 2

        # Apply non-homogeneous Neumann BC on left boundary (x = -0.5)
        # For Neumann BC: -D * dphi/dx = g(y)
        # Using ghost point: (phi[1,j] - phi[-1,j])/(2*hx) = -g(y)/D
        # So: phi[-1,j] = phi[1,j] + 2*hx*g(y)/D
        # The Laplacian at boundary: (phi[1,j] - 2*phi[0,j] + phi[-1,j])/hx^2
        #                          = (2*phi[1,j] - 2*phi[0,j] + 2*hx*g(y)/D)/hx^2
        # The standard Neumann modification gives: (2*phi[1,j] - 2*phi[0,j])/hx^2
        # So we need to add 2*g(y)/(D*hx) to the RHS

        for j in range(ny):
            idx1 = j * nx  # Left boundary index for phi1
            idx2 = N + j * nx  # Left boundary index for phi2
            y_val = self.y[j]

            # BC: -D * dphi/dx = y_val, so g(y) = y_val
            # Ghost point contribution: 2*y_val / (D * hx)
            # But we need to account for the -D factor in front of Laplacian
            # The equation has -D1 * (Laplacian), so the RHS contribution is:
            b[idx1] += 2 * y_val / hx
            b[idx2] += 2 * y_val / hx

        return A, b

    def solve(self):
        """Solve the linear system."""
        A, b = self._build_system()

        # Solve
        sol = spsolve(A, b)

        N = self.nx * self.ny
        self.phi1 = sol[:N].reshape((self.ny, self.nx))
        self.phi2 = sol[N:].reshape((self.ny, self.nx))

        return self.x, self.y, self.phi1, self.phi2

    def evaluate_at(self, x_query, y_query):
        """
        Evaluate solution at query points using bilinear interpolation.

        Returns:
            phi1, dphi1_dx, dphi1_dy, d2phi1_dx2, d2phi1_dy2
            phi2, dphi2_dx, dphi2_dy, d2phi2_dx2, d2phi2_dy2
        """
        if self.phi1 is None:
            self.solve()

        # Flatten inputs
        x_flat = np.atleast_1d(x_query).flatten()
        y_flat = np.atleast_1d(y_query).flatten()

        # Clip to domain
        x_flat = np.clip(x_flat, -0.5, 0.5)
        y_flat = np.clip(y_flat, -0.5, 0.5)

        # Find indices
        ix = np.floor((x_flat - self.x[0]) / self.hx).astype(int)
        iy = np.floor((y_flat - self.y[0]) / self.hy).astype(int)

        # Clip indices
        ix = np.clip(ix, 0, self.nx - 2)
        iy = np.clip(iy, 0, self.ny - 2)

        # Bilinear interpolation weights
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

        # Compute derivatives using central differences on grid
        # dphi/dx
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

        # dphi/dy
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

        # d2phi/dx2
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

        # d2phi/dy2
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


def solve_fdm(nx=101, ny=101):
    """Convenience function to solve using FDM."""
    solver = FDMSolver(nx, ny)
    return solver.solve()


if __name__ == "__main__":
    # Test the solver
    solver = FDMSolver(nx=51, ny=51)
    x, y, phi1, phi2 = solver.solve()

    print(f"FDM Solution:")
    print(f"  Grid: {len(x)} x {len(y)}")
    print(f"  phi1 range: [{phi1.min():.4f}, {phi1.max():.4f}]")
    print(f"  phi2 range: [{phi2.min():.4f}, {phi2.max():.4f}]")

    # Test evaluation at points
    X, Y = np.meshgrid(np.linspace(-0.4, 0.4, 5), np.linspace(-0.4, 0.4, 5))
    results = solver.evaluate_at(X, Y)
    print(f"\nEvaluation at test points:")
    print(f"  phi1[0,0] = {results[0][0,0]:.4f}")
    print(f"  phi2[0,0] = {results[5][0,0]:.4f}")
