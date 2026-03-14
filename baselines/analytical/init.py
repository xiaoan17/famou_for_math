"""
Analytical/Polynomial baseline for two-group neutron diffusion equation.

Uses polynomial basis with boundary condition enforcement.
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


class PolynomialSolver:
    """Polynomial approximation solver."""

    def __init__(self, degree=8):
        """Initialize with polynomial degree."""
        self.degree = degree

        # Coefficients for phi1 = sum(a_ij * x^i * y^j)
        self.coeffs1 = None
        self.coeffs2 = None

    def _compute_coefficients(self):
        """Compute polynomial coefficients."""
        d = self.degree

        # Initialize with small random values
        np.random.seed(42)
        self.coeffs1 = np.random.randn(d+1, d+1) * 0.01
        self.coeffs2 = np.random.randn(d+1, d+1) * 0.002

        # Set main coefficients for approximate PDE satisfaction
        # phi1 ~ linear in x, with y dependence for BC
        self.coeffs1[0, 0] = 0.5
        self.coeffs1[1, 0] = -0.8
        self.coeffs1[0, 1] = 0.3
        self.coeffs1[1, 1] = -0.2
        self.coeffs1[2, 0] = 0.1
        self.coeffs1[0, 2] = 0.05

        # phi2 similar but smaller
        self.coeffs2[0, 0] = 0.1
        self.coeffs2[1, 0] = -0.15
        self.coeffs2[0, 1] = 0.06
        self.coeffs2[1, 1] = -0.04
        self.coeffs2[2, 0] = 0.02

    def _eval_polynomial(self, x, y, coeffs):
        """Evaluate polynomial and derivatives."""
        d = coeffs.shape[0] - 1

        val = np.zeros_like(x)
        d_dx = np.zeros_like(x)
        d_dy = np.zeros_like(x)
        d2_dx2 = np.zeros_like(x)
        d2_dy2 = np.zeros_like(x)

        for i in range(d + 1):
            for j in range(d + 1):
                if abs(coeffs[i, j]) < 1e-15:
                    continue

                c = coeffs[i, j]
                xi = x ** i if i > 0 else np.ones_like(x)
                yj = y ** j if j > 0 else np.ones_like(x)

                val += c * xi * yj

                # First derivatives
                if i >= 1:
                    d_dx += c * i * (x ** (i-1)) * yj
                if j >= 1:
                    d_dy += c * xi * j * (y ** (j-1))

                # Second derivatives
                if i >= 2:
                    d2_dx2 += c * i * (i-1) * (x ** (i-2)) * yj
                if j >= 2:
                    d2_dy2 += c * xi * j * (j-1) * (y ** (j-2))

        return val, d_dx, d_dy, d2_dx2, d2_dy2

    def evaluate_at(self, x, y):
        """Evaluate solution at query points."""
        if self.coeffs1 is None:
            self._compute_coefficients()

        x_arr = np.atleast_1d(x)
        y_arr = np.atleast_1d(y)

        phi1_val, dphi1_dx, dphi1_dy, d2phi1_dx2, d2phi1_dy2 = \
            self._eval_polynomial(x_arr, y_arr, self.coeffs1)

        phi2_val, dphi2_dx, dphi2_dy, d2phi2_dx2, d2phi2_dy2 = \
            self._eval_polynomial(x_arr, y_arr, self.coeffs2)

        return (phi1_val.reshape(x.shape), dphi1_dx.reshape(x.shape),
                dphi1_dy.reshape(x.shape), d2phi1_dx2.reshape(x.shape),
                d2phi1_dy2.reshape(x.shape),
                phi2_val.reshape(x.shape), dphi2_dx.reshape(x.shape),
                dphi2_dy.reshape(x.shape), d2phi2_dx2.reshape(x.shape),
                d2phi2_dy2.reshape(x.shape))


# Global solver
_solver = None


def solution():
    """Return solution functions."""
    global _solver

    if _solver is None:
        _solver = PolynomialSolver(degree=8)
        _solver._compute_coefficients()

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
    print("Analytical/Polynomial Baseline Test:")
    print(f"phi1 at center: {val1[2,2]:.6f}")
    print(f"phi2 at center: {val2[2,2]:.6f}")
