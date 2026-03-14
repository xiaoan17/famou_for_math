"""
2D Two-Group Neutron Diffusion Solver using Green's Function and Fourier Series
"""

import numpy as np
from typing import Tuple, Callable


def solution():
    """
    Returns two functions φ₁(x,y) and φ₂(x,y) using Green's function approach
    
    Returns:
        Tuple of (phi1_func, phi2_func)
        Each function returns: (value, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2)
    """
    # Physical constants
    D1 = 1.0
    D2 = 0.5
    SIGMA_R = 0.02
    SIGMA_A2 = 0.1
    NU = 2.5
    SIGMA_F1 = 0.005
    SIGMA_F2 = 0.1
    SIGMA_12 = 0.015
    
    # Precompute coefficients
    L1 = np.sqrt(D1/SIGMA_R)
    L2 = np.sqrt(D2/SIGMA_A2)
    
    # Number of Fourier terms to use (more terms = better accuracy)
    N_terms = 20
    
    # Precompute Fourier coefficients
    n_values = np.arange(1, N_terms+1)
    lambda_n = (2*n_values - 1) * np.pi  # Eigenvalues for y-direction
    
    def phi1(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Fast group neutron flux using Green's function solution
        """
        x = np.asarray(x)
        y = np.asarray(y)
        shape = x.shape
        
        # Initialize all return arrays
        val = np.zeros(shape)
        dphi_dx = np.zeros(shape)
        dphi_dy = np.zeros(shape)
        d2phi_dx2 = np.zeros(shape)
        d2phi_dy2 = np.zeros(shape)
        
        # Compute solution as a series expansion
        for n in n_values:
            lambda_n = (2*n - 1) * np.pi
            k_n = np.sqrt((lambda_n**2 + SIGMA_R/D1))
            
            # Compute the y-dependent part
            cos_term = np.cos(lambda_n * (y + 0.5))
            
            # Compute the x-dependent Green's function part
            A_n = 2 * (-1)**(n+1) / (lambda_n**2 * D1 * k_n * np.cosh(k_n))
            G_x = np.cosh(k_n * (x + 0.5)) / np.cosh(k_n)
            
            # Value and derivatives
            term = A_n * G_x * cos_term
            val += term
            
            # x derivatives
            dG_dx = k_n * np.sinh(k_n * (x + 0.5)) / np.cosh(k_n)
            dphi_dx += A_n * dG_dx * cos_term
            
            d2G_dx2 = k_n**2 * G_x
            d2phi_dx2 += A_n * d2G_dx2 * cos_term
            
            # y derivatives
            dphi_dy += -A_n * G_x * lambda_n * np.sin(lambda_n * (y + 0.5))
            d2phi_dy2 += -A_n * G_x * lambda_n**2 * cos_term
        
        return val, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2
    
    def phi2(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Thermal group neutron flux using Green's function solution
        """
        x = np.asarray(x)
        y = np.asarray(y)
        shape = x.shape
        
        # Initialize all return arrays
        val = np.zeros(shape)
        dphi_dx = np.zeros(shape)
        dphi_dy = np.zeros(shape)
        d2phi_dx2 = np.zeros(shape)
        d2phi_dy2 = np.zeros(shape)
        
        # Compute solution as a series expansion
        for n in n_values:
            lambda_n = (2*n - 1) * np.pi
            k_n = np.sqrt((lambda_n**2 + SIGMA_R/D1))
            m_n = np.sqrt((lambda_n**2 + SIGMA_A2/D2))
            
            # Compute the y-dependent part
            cos_term = np.cos(lambda_n * (y + 0.5))
            
            # Compute the x-dependent Green's function part
            A_n = 2 * (-1)**(n+1) * SIGMA_12 / (lambda_n**2 * D1 * k_n * np.cosh(k_n))
            B_n = 1/(m_n**2 - k_n**2)
            G_x = B_n * (np.cosh(k_n * (x + 0.5))/np.cosh(k_n) - np.cosh(m_n * (x + 0.5))/np.cosh(m_n))
            
            # Value and derivatives
            term = A_n * G_x * cos_term
            val += term
            
            # x derivatives
            dG_dx = B_n * (k_n * np.sinh(k_n * (x + 0.5))/np.cosh(k_n) - m_n * np.sinh(m_n * (x + 0.5))/np.cosh(m_n))
            dphi_dx += A_n * dG_dx * cos_term
            
            d2G_dx2 = B_n * (k_n**2 * np.cosh(k_n * (x + 0.5))/np.cosh(k_n) - m_n**2 * np.cosh(m_n * (x + 0.5))/np.cosh(m_n))
            d2phi_dx2 += A_n * d2G_dx2 * cos_term
            
            # y derivatives
            dphi_dy += -A_n * G_x * lambda_n * np.sin(lambda_n * (y + 0.5))
            d2phi_dy2 += -A_n * G_x * lambda_n**2 * cos_term
        
        return val, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2
    
    return phi1, phi2


def verify_solution():
    """
    验证解的正确性：检查PDE残差和边界条件
    """
    phi1, phi2 = solution()

    # 物理常数
    D1 = 1.0
    D2 = 0.5
    SIGMA_R = 0.02
    SIGMA_A2 = 0.1
    NU = 2.5
    SIGMA_F1 = 0.005
    SIGMA_F2 = 0.1
    SIGMA_12 = 0.015

    print("=== Verification Report ===\n")

    # 测试内部点
    x_test = np.linspace(-0.4, 0.4, 9)
    y_test = np.linspace(-0.4, 0.4, 9)
    X, Y = np.meshgrid(x_test, y_test)

    val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
    val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)

    # 计算PDE残差
    res1 = -D1*(d2_1_dx2 + d2_1_dy2) + SIGMA_R*val1 - (NU*SIGMA_F1*val1 + NU*SIGMA_F2*val2)
    res2 = -D2*(d2_2_dx2 + d2_2_dy2) + SIGMA_A2*val2 - SIGMA_12*val1

    print("PDE Residuals (interior points):")
    print(f"  Res1 max abs: {np.max(np.abs(res1)):.6f}")
    print(f"  Res2 max abs: {np.max(np.abs(res2)):.6f}")

    # 测试边界条件
    y_grid = np.linspace(-0.5, 0.5, 21)
    x_grid = np.linspace(-0.5, 0.5, 21)

    # 左边界 x = -0.5: -D * dphi/dx = y
    x_left = np.full_like(y_grid, -0.5)
    _, d1_dx_left, _, _, _ = phi1(x_left, y_grid)
    _, d2_dx_left, _, _, _ = phi2(x_left, y_grid)
    bc1_left = -D1 * d1_dx_left - y_grid
    bc2_left = -D2 * d2_dx_left - y_grid

    print(f"\nLeft Boundary (x=-0.5):")
    print(f"  BC1 residual max abs: {np.max(np.abs(bc1_left)):.6f}")
    print(f"  BC2 residual max abs: {np.max(np.abs(bc2_left)):.6f}")

    # 右边界 x = 0.5: -D * dphi/dx = 0
    x_right = np.full_like(y_grid, 0.5)
    _, d1_dx_right, _, _, _ = phi1(x_right, y_grid)
    _, d2_dx_right, _, _, _ = phi2(x_right, y_grid)
    bc1_right = -D1 * d1_dx_right
    bc2_right = -D2 * d2_dx_right

    print(f"\nRight Boundary (x=0.5):")
    print(f"  BC1 residual max abs: {np.max(np.abs(bc1_right)):.6f}")
    print(f"  BC2 residual max abs: {np.max(np.abs(bc2_right)):.6f}")

    # 上边界 y = 0.5: -D * dphi/dy = 0
    y_top = np.full_like(x_grid, 0.5)
    _, _, d1_dy_top, _, _ = phi1(x_grid, y_top)
    _, _, d2_dy_top, _, _ = phi2(x_grid, y_top)
    bc1_top = -D1 * d1_dy_top
    bc2_top = -D2 * d2_dy_top

    print(f"\nTop Boundary (y=0.5):")
    print(f"  BC1 residual max abs: {np.max(np.abs(bc1_top)):.6f}")
    print(f"  BC2 residual max abs: {np.max(np.abs(bc2_top)):.6f}")

    # 下边界 y = -0.5: -D * dphi/dy = 0
    y_bottom = np.full_like(x_grid, -0.5)
    _, _, d1_dy_bottom, _, _ = phi1(x_grid, y_bottom)
    _, _, d2_dy_bottom, _, _ = phi2(x_grid, y_bottom)
    bc1_bottom = -D1 * d1_dy_bottom
    bc2_bottom = -D2 * d2_dy_bottom

    print(f"\nBottom Boundary (y=-0.5):")
    print(f"  BC1 residual max abs: {np.max(np.abs(bc1_bottom)):.6f}")
    print(f"  BC2 residual max abs: {np.max(np.abs(bc2_bottom)):.6f}")

    return {
        'res1_max': np.max(np.abs(res1)),
        'res2_max': np.max(np.abs(res2)),
        'bc_left_max': max(np.max(np.abs(bc1_left)), np.max(np.abs(bc2_left))),
        'bc_right_max': max(np.max(np.abs(bc1_right)), np.max(np.abs(bc2_right))),
        'bc_top_max': max(np.max(np.abs(bc1_top)), np.max(np.abs(bc2_top))),
        'bc_bottom_max': max(np.max(np.abs(bc1_bottom)), np.max(np.abs(bc2_bottom)))
    }


if __name__ == "__main__":
    results = verify_solution()
    print("\n=== Summary ===")
    for key, val in results.items():
        print(f"{key}: {val:.6f}")