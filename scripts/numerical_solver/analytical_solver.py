"""
Analytical solution to 2D two-group neutron diffusion equations.

System:
  -D1 * lap(phi1) + Sigma_r * phi1 = nu*Sigma_f1*phi1 + nu*Sigma_f2*phi2
  -D2 * lap(phi2) + Sigma_a2 * phi2 = Sigma_12 * phi1

Rearranged (homogeneous form):
  -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
  -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

where:
  A11 = Sigma_r - nu*Sigma_f1 = 0.0075
  A12 = -nu*Sigma_f2 = -0.25
  A21 = -Sigma_12 = -0.015
  A22 = Sigma_a2 = 0.1

Domain: [-0.5, 0.5]^2
BCs:
  Left  (x=-0.5): -D_g * dphi_g/dx = y   for g=1,2
  Right (x=+0.5): -D_g * dphi_g/dx = 0   for g=1,2
  Top   (y=+0.5): -D_g * dphi_g/dy = 0   for g=1,2
  Bottom(y=-0.5): -D_g * dphi_g/dy = 0   for g=1,2

Method:
  1. Cosine expansion in y: cos(n*pi*(y+0.5)) for n=0,1,2,...
     (satisfies zero-Neumann at y = +/-0.5)
  2. Decouple via eigendecomposition of M = D^{-1}*A
  3. Solve x-ODE with cosh(alpha*(x-0.5)) to satisfy zero-Neumann at x=0.5
  4. Match left BC by expanding source function y in cosine basis
"""
import numpy as np
from typing import Tuple, Dict

# Physical constants
D1: float = 1.0
D2: float = 0.5
SIGMA_R: float = 0.02
SIGMA_A2: float = 0.1
NU: float = 2.5
SIGMA_F1: float = 0.005
SIGMA_F2: float = 0.1
SIGMA_12: float = 0.015

# Derived coupling matrix entries
A11: float = SIGMA_R - NU * SIGMA_F1   # 0.0075
A12: float = -NU * SIGMA_F2            # -0.25
A21: float = -SIGMA_12                 # -0.015
A22: float = SIGMA_A2                  # 0.1

# Matrix M = D^{-1} * A
M = np.array([
    [A11 / D1, A12 / D1],
    [A21 / D2, A22 / D2],
])
# M = [[0.0075, -0.25], [-0.03, 0.2]]


def _eigen_decomposition() -> Tuple[np.ndarray, np.ndarray]:
    """Compute eigenvalues and eigenvectors of M = D^{-1}*A.

    Returns:
        eigenvalues: shape (2,)
        eigenvectors: shape (2,2), columns are eigenvectors
    """
    eigenvalues, eigenvectors = np.linalg.eig(M)
    # Sort by eigenvalue for consistency
    idx = np.argsort(eigenvalues)
    return eigenvalues[idx], eigenvectors[:, idx]


# Precompute eigendecomposition
EIGENVALUES, EIGENVECTORS = _eigen_decomposition()
# P matrix: columns are eigenvectors of M
# M = P * diag(lambda) * P^{-1}
P = EIGENVECTORS
P_INV = np.linalg.inv(P)

# lambda_1, lambda_2 are the eigenvalues
LAMBDA1, LAMBDA2 = EIGENVALUES[0], EIGENVALUES[1]


def _cosine_coeffs_of_y(n: int) -> float:
    """Compute b_n = 2 * integral_{-0.5}^{0.5} y * cos(n*pi*(y+0.5)) dy.

    Using substitution u = y+0.5, y = u-0.5, u in [0,1]:
      integral = integral_0^1 (u - 0.5) * cos(n*pi*u) du

    For n=0: integral_0^1 (u-0.5) du = 0, so b_0 = 0.
    For n>=1:
      = [cos(n*pi) - 1] / (n*pi)^2  (from integration by parts)
      = [(-1)^n - 1] / (n*pi)^2

    b_n = 2 * [(-1)^n - 1] / (n*pi)^2
    Nonzero only for odd n: b_n = -4 / (n*pi)^2
    """
    if n == 0:
        return 0.0
    return 2.0 * ((-1.0)**n - 1.0) / (n * np.pi)**2


def _compute_solution_modes(N_terms: int) -> list:
    """Precompute coefficients for all Fourier modes.

    For each mode n, we have wavenumber k_n = n*pi.
    The decoupled x-equation for eigenmode p is:
      X_p'' - (lambda_p + k_n^2) * X_p = 0

    Solution satisfying dX/dx = 0 at x=0.5:
      X_{p,n}(x) = cosh(alpha_{p,n} * (x - 0.5))
    where alpha_{p,n} = sqrt(lambda_p + k_n^2).

    The physical solution is:
      [phi1, phi2]^T = sum_n sum_p c_{p,n} * P[:,p] * X_{p,n}(x) * cos(k_n*(y+0.5))

    Left BC at x=-0.5: -D_g * dphi_g/dx = y for g=1,2
    dphi_g/dx|_{x=-0.5} = sum_n sum_p c_{p,n} * P[g-1,p] * alpha_{p,n}
                           * sinh(alpha_{p,n}*(-1)) * cos(k_n*(y+0.5))
                         = -sum_n sum_p c_{p,n} * P[g-1,p] * alpha_{p,n}
                           * sinh(alpha_{p,n}) * cos(k_n*(y+0.5))

    So: -D_g * dphi_g/dx|_{x=-0.5}
      = sum_n sum_p c_{p,n} * D_g * P[g-1,p] * alpha_{p,n} * sinh(alpha_{p,n})
        * cos(k_n*(y+0.5))
      = b_n * cos(k_n*(y+0.5)) for each n

    This gives for each n a 2x2 system (for g=1,2):
      sum_p c_{p,n} * D_g * P[g-1,p] * alpha_{p,n} * sinh(alpha_{p,n}) = b_n

    Written as matrix equation:
      Q_n * [c_{1,n}, c_{2,n}]^T = [b_n, b_n]^T
    where Q_n[g,p] = D_g * P[g,p] * alpha_{p,n} * sinh(alpha_{p,n})
    (using 0-indexed g and p)

    Returns:
        List of (alpha_1n, alpha_2n, c_1n, c_2n) for n=0,...,N_terms
    """
    D_vec = np.array([D1, D2])
    modes = []

    for n in range(N_terms + 1):
        kn = n * np.pi
        kn_sq = kn**2
        bn = _cosine_coeffs_of_y(n)

        if abs(bn) < 1e-30:
            # Zero coefficient, skip (n=0 and even n)
            modes.append(None)
            continue

        # Compute alpha for each eigenmode
        alphas = np.zeros(2)
        for p in range(2):
            val = EIGENVALUES[p] + kn_sq
            if val < 0:
                # This would give imaginary alpha; shouldn't happen for
                # physical parameters but handle gracefully
                raise ValueError(
                    f"Negative argument for sqrt: lambda_{p}={EIGENVALUES[p]}, "
                    f"k_n^2={kn_sq}"
                )
            alphas[p] = np.sqrt(val)

        # Build the 2x2 system Q_n * c_n = [bn, bn]
        Q = np.zeros((2, 2))
        for g in range(2):
            for p in range(2):
                Q[g, p] = D_vec[g] * P[g, p] * alphas[p] * np.sinh(alphas[p])

        rhs = np.array([bn, bn])
        c_n = np.linalg.solve(Q, rhs)

        modes.append((alphas[0], alphas[1], c_n[0], c_n[1]))

    return modes


def evaluate_flux(
    x: np.ndarray,
    y: np.ndarray,
    N_terms: int = 50,
) -> Tuple[np.ndarray, np.ndarray]:
    """Evaluate both flux components at given (x,y) points.

    Args:
        x: x-coordinates, shape (N,) or scalar
        y: y-coordinates, shape (N,) or scalar
        N_terms: number of Fourier modes

    Returns:
        phi1, phi2: flux values at the given points
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    y = np.atleast_1d(np.asarray(y, dtype=float))

    modes = _compute_solution_modes(N_terms)

    phi1 = np.zeros_like(x)
    phi2 = np.zeros_like(x)

    for n in range(N_terms + 1):
        if modes[n] is None:
            continue

        alpha1, alpha2, c1, c2 = modes[n]
        kn = n * np.pi
        cos_y = np.cos(kn * (y + 0.5))

        # X_{p,n}(x) = cosh(alpha_{p,n} * (x - 0.5))
        X1 = np.cosh(alpha1 * (x - 0.5))
        X2 = np.cosh(alpha2 * (x - 0.5))

        # Contribution from eigenmode p=0 and p=1
        # [phi1_contrib, phi2_contrib] = c1*P[:,0]*X1 + c2*P[:,1]*X2
        phi1 += (c1 * P[0, 0] * X1 + c2 * P[0, 1] * X2) * cos_y
        phi2 += (c1 * P[1, 0] * X1 + c2 * P[1, 1] * X2) * cos_y

    return phi1, phi2


def evaluate_derivatives(
    x: np.ndarray,
    y: np.ndarray,
    N_terms: int = 50,
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """Compute analytical derivatives of both flux components.

    Returns dict with keys: 'dx', 'dy', 'dxx', 'dyy' (partial derivatives),
    each mapping to (deriv_phi1, deriv_phi2).
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    y = np.atleast_1d(np.asarray(y, dtype=float))

    modes = _compute_solution_modes(N_terms)

    # Initialize all derivative arrays
    dx1 = np.zeros_like(x)
    dx2 = np.zeros_like(x)
    dy1 = np.zeros_like(x)
    dy2 = np.zeros_like(x)
    dxx1 = np.zeros_like(x)
    dxx2 = np.zeros_like(x)
    dyy1 = np.zeros_like(x)
    dyy2 = np.zeros_like(x)

    for n in range(N_terms + 1):
        if modes[n] is None:
            continue

        alpha1, alpha2, c1, c2 = modes[n]
        kn = n * np.pi
        cos_y = np.cos(kn * (y + 0.5))
        sin_y = np.sin(kn * (y + 0.5))

        arg1 = alpha1 * (x - 0.5)
        arg2 = alpha2 * (x - 0.5)

        cosh1 = np.cosh(arg1)
        sinh1 = np.sinh(arg1)
        cosh2 = np.cosh(arg2)
        sinh2 = np.sinh(arg2)

        # f_g(x,y) = sum_n (c1*P[g,0]*cosh(a1*(x-0.5)) + c2*P[g,1]*cosh(a2*(x-0.5)))
        #            * cos(kn*(y+0.5))

        # df/dx: sinh * alpha * cos_y
        for g_idx, (dx_arr, dxx_arr, dy_arr, dyy_arr) in enumerate([
            (dx1, dxx1, dy1, dyy1), (dx2, dxx2, dy2, dyy2)
        ]):
            coeff1 = c1 * P[g_idx, 0]
            coeff2 = c2 * P[g_idx, 1]

            dx_arr += (coeff1 * alpha1 * sinh1 + coeff2 * alpha2 * sinh2) * cos_y
            dxx_arr += (coeff1 * alpha1**2 * cosh1 + coeff2 * alpha2**2 * cosh2) * cos_y
            dy_arr += (coeff1 * cosh1 + coeff2 * cosh2) * (-kn * sin_y)
            dyy_arr += (coeff1 * cosh1 + coeff2 * cosh2) * (-kn**2 * cos_y)

    return {
        "dx": (dx1, dx2),
        "dy": (dy1, dy2),
        "dxx": (dxx1, dxx2),
        "dyy": (dyy1, dyy2),
    }


def phi1(x: float, y: float, N_terms: int = 50) -> float:
    """Fast-group neutron flux at a single point."""
    p1, _ = evaluate_flux(np.array([x]), np.array([y]), N_terms)
    return float(p1[0])


def phi2(x: float, y: float, N_terms: int = 50) -> float:
    """Thermal-group neutron flux at a single point."""
    _, p2 = evaluate_flux(np.array([x]), np.array([y]), N_terms)
    return float(p2[0])


def _numerical_laplacian(
    func, x: float, y: float, h: float = 1e-5, N_terms: int = 50,
) -> float:
    """Compute Laplacian using central finite differences.

    Args:
        func: callable(x, y, N_terms) -> float
        x, y: evaluation point
        h: step size
        N_terms: Fourier terms

    Returns:
        Approximation of d^2f/dx^2 + d^2f/dy^2
    """
    fxx = (func(x + h, y, N_terms) - 2 * func(x, y, N_terms)
           + func(x - h, y, N_terms)) / h**2
    fyy = (func(x, y + h, N_terms) - 2 * func(x, y, N_terms)
           + func(x, y - h, N_terms)) / h**2
    return fxx + fyy


def _numerical_dx(
    func, x: float, y: float, h: float = 1e-5, N_terms: int = 50,
) -> float:
    """Compute df/dx using central differences."""
    return (func(x + h, y, N_terms) - func(x - h, y, N_terms)) / (2 * h)


def _numerical_dy(
    func, x: float, y: float, h: float = 1e-5, N_terms: int = 50,
) -> float:
    """Compute df/dy using central differences."""
    return (func(x, y + h, N_terms) - func(x, y - h, N_terms)) / (2 * h)


def compute_residuals(
    N_terms: int = 100,
) -> Dict[str, Dict[str, float]]:
    """Compute PDE and BC residuals using analytical derivatives.

    PDE residuals:
      R1 = -D1*lap(phi1) + A11*phi1 + A12*phi2
      R2 = -D2*lap(phi2) + A21*phi1 + A22*phi2

    Returns:
        Dictionary with PDE and BC residuals.
    """
    results: Dict[str, Dict[str, float]] = {"pde": {}, "bc": {}}

    # PDE residuals at interior test points (using analytical derivatives)
    test_points = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]
    xp = np.array([p[0] for p in test_points])
    yp = np.array([p[1] for p in test_points])

    p1_vals, p2_vals = evaluate_flux(xp, yp, N_terms)
    derivs = evaluate_derivatives(xp, yp, N_terms)
    dxx1, dxx2 = derivs["dxx"]
    dyy1, dyy2 = derivs["dyy"]

    for i, (x, y) in enumerate(test_points):
        lap1 = dxx1[i] + dyy1[i]
        lap2 = dxx2[i] + dyy2[i]
        R1 = -D1 * lap1 + A11 * p1_vals[i] + A12 * p2_vals[i]
        R2 = -D2 * lap2 + A21 * p1_vals[i] + A22 * p2_vals[i]
        results["pde"][f"({x},{y})"] = {"R1": float(R1), "R2": float(R2)}

    # BC residuals using analytical derivatives
    # Left BC: -D_g * dphi_g/dx = y
    bc_y_vals = np.array([-0.3, 0.0, 0.2, 0.4])
    bc_x_left = np.full_like(bc_y_vals, -0.5)
    derivs_left = evaluate_derivatives(bc_x_left, bc_y_vals, N_terms)
    dx1_left, dx2_left = derivs_left["dx"]
    for i, yv in enumerate(bc_y_vals):
        R1 = -D1 * dx1_left[i] - yv
        R2 = -D2 * dx2_left[i] - yv
        results["bc"][f"left(-0.5,{yv})"] = {"R1": float(R1), "R2": float(R2)}

    # Right BC: -D_g * dphi_g/dx = 0
    bc_x_right = np.full_like(bc_y_vals, 0.5)
    derivs_right = evaluate_derivatives(bc_x_right, bc_y_vals, N_terms)
    dx1_right, dx2_right = derivs_right["dx"]
    for i, yv in enumerate(bc_y_vals):
        R1 = -D1 * dx1_right[i]
        R2 = -D2 * dx2_right[i]
        results["bc"][f"right(0.5,{yv})"] = {"R1": float(R1), "R2": float(R2)}

    # Top BC: -D_g * dphi_g/dy = 0
    bc_x_vals = np.array([-0.3, 0.0, 0.2, 0.4])
    bc_y_top = np.full_like(bc_x_vals, 0.5)
    derivs_top = evaluate_derivatives(bc_x_vals, bc_y_top, N_terms)
    dy1_top, dy2_top = derivs_top["dy"]
    for i, xv in enumerate(bc_x_vals):
        R1 = -D1 * dy1_top[i]
        R2 = -D2 * dy2_top[i]
        results["bc"][f"top({xv},0.5)"] = {"R1": float(R1), "R2": float(R2)}

    # Bottom BC: -D_g * dphi_g/dy = 0
    bc_y_bot = np.full_like(bc_x_vals, -0.5)
    derivs_bot = evaluate_derivatives(bc_x_vals, bc_y_bot, N_terms)
    dy1_bot, dy2_bot = derivs_bot["dy"]
    for i, xv in enumerate(bc_x_vals):
        R1 = -D1 * dy1_bot[i]
        R2 = -D2 * dy2_bot[i]
        results["bc"][f"bottom({xv},-0.5)"] = {"R1": float(R1), "R2": float(R2)}

    return results


def print_residuals(results: Dict) -> None:
    """Pretty-print residual results."""
    print("=" * 70)
    print("PDE RESIDUALS (should be ~ 0)")
    print("=" * 70)
    for point, res in results["pde"].items():
        print(f"  Point {point:>15s}:  R1 = {res['R1']:+.6e},  R2 = {res['R2']:+.6e}")

    print()
    print("=" * 70)
    print("BOUNDARY CONDITION RESIDUALS (should be ~ 0)")
    print("=" * 70)
    for loc, res in results["bc"].items():
        print(f"  {loc:>25s}:  R1 = {res['R1']:+.6e},  R2 = {res['R2']:+.6e}")

    # Summary statistics
    all_pde = []
    for res in results["pde"].values():
        all_pde.extend([abs(res["R1"]), abs(res["R2"])])
    all_bc = []
    for res in results["bc"].values():
        all_bc.extend([abs(res["R1"]), abs(res["R2"])])

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Max |PDE residual|: {max(all_pde):.6e}")
    print(f"  Max |BC  residual|: {max(all_bc):.6e}")


if __name__ == "__main__":
    print("Eigenvalues of M:", EIGENVALUES)
    print("Eigenvectors (columns):")
    print(P)
    print()

    results = compute_residuals(N_terms=500)
    print_residuals(results)
