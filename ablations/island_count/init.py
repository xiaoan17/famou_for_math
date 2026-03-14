"""
Island Count Ablation Study

Tests the effect of different island counts on evolutionary performance.
Uses the same init.py (Green's function solution) as the main experiment.
"""

import numpy as np
from typing import Tuple

# Physical constants
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015


def solution():
    """
    Returns two functions φ₁(x,y) and φ₂(x,y) using Green's function approach.
    This is the same solution used in the main Famou experiment.

    Returns:
        Tuple of (phi1_func, phi2_func)
        Each function returns: (value, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2)
    """
    # Precompute coefficients
    L1 = np.sqrt(D1/SIGMA_R)
    L2 = np.sqrt(D2/SIGMA_A2)

    # Number of Fourier terms to use
    N_terms = 20

    # Precompute Fourier coefficients
    n_values = np.arange(1, N_terms+1)
    lambda_n = (2*n_values - 1) * np.pi

    def phi1(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Fast group neutron flux using Green's function solution."""
        x = np.asarray(x)
        y = np.asarray(y)
        shape = x.shape

        val = np.zeros(shape)
        dphi_dx = np.zeros(shape)
        dphi_dy = np.zeros(shape)
        d2phi_dx2 = np.zeros(shape)
        d2phi_dy2 = np.zeros(shape)

        for n in n_values:
            lambda_n_val = (2*n - 1) * np.pi
            k_n = np.sqrt((lambda_n_val**2 + SIGMA_R/D1))

            cos_term = np.cos(lambda_n_val * (y + 0.5))
            A_n = 2 * (-1)**(n+1) / (lambda_n_val**2 * D1 * k_n * np.cosh(k_n))
            G_x = np.cosh(k_n * (x + 0.5)) / np.cosh(k_n)

            term = A_n * G_x * cos_term
            val += term

            dG_dx = k_n * np.sinh(k_n * (x + 0.5)) / np.cosh(k_n)
            dphi_dx += A_n * dG_dx * cos_term

            d2G_dx2 = k_n**2 * G_x
            d2phi_dx2 += A_n * d2G_dx2 * cos_term

            dphi_dy += -A_n * G_x * lambda_n_val * np.sin(lambda_n_val * (y + 0.5))
            d2phi_dy2 += -A_n * G_x * lambda_n_val**2 * cos_term

        return val, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2

    def phi2(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Thermal group neutron flux using Green's function solution."""
        x = np.asarray(x)
        y = np.asarray(y)
        shape = x.shape

        val = np.zeros(shape)
        dphi_dx = np.zeros(shape)
        dphi_dy = np.zeros(shape)
        d2phi_dx2 = np.zeros(shape)
        d2phi_dy2 = np.zeros(shape)

        for n in n_values:
            lambda_n_val = (2*n - 1) * np.pi
            k_n = np.sqrt((lambda_n_val**2 + SIGMA_R/D1))
            m_n = np.sqrt((lambda_n_val**2 + SIGMA_A2/D2))

            cos_term = np.cos(lambda_n_val * (y + 0.5))
            A_n = 2 * (-1)**(n+1) * SIGMA_12 / (lambda_n_val**2 * D1 * k_n * np.cosh(k_n))
            B_n = 1/(m_n**2 - k_n**2)
            G_x = B_n * (np.cosh(k_n * (x + 0.5))/np.cosh(k_n) - np.cosh(m_n * (x + 0.5))/np.cosh(m_n))

            term = A_n * G_x * cos_term
            val += term

            dG_dx = B_n * (k_n * np.sinh(k_n * (x + 0.5))/np.cosh(k_n) - m_n * np.sinh(m_n * (x + 0.5))/np.cosh(m_n))
            dphi_dx += A_n * dG_dx * cos_term

            d2G_dx2 = B_n * (k_n**2 * np.cosh(k_n * (x + 0.5))/np.cosh(k_n) - m_n**2 * np.cosh(m_n * (x + 0.5))/np.cosh(m_n))
            d2phi_dx2 += A_n * d2G_dx2 * cos_term

            dphi_dy += -A_n * G_x * lambda_n_val * np.sin(lambda_n_val * (y + 0.5))
            d2phi_dy2 += -A_n * G_x * lambda_n_val**2 * cos_term

        return val, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2

    return phi1, phi2


if __name__ == "__main__":
    phi1, phi2 = solution()
    X, Y = np.meshgrid(np.linspace(-0.4, 0.4, 5), np.linspace(-0.4, 0.4, 5))
    val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
    val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)
    print("Island Count Ablation - Base Solution Test:")
    print(f"phi1 at center: {val1[2,2]:.6f}")
    print(f"phi2 at center: {val2[2,2]:.6f}")
