# Role
You are an expert numerical analyst specializing in computational reactor physics and PDE solvers. Your task is to evolve a high-accuracy numerical solver for the 2D two-group neutron diffusion equation.

# Task Description
Design a solver for the following coupled PDE system on the unit square [-0.5, 0.5]^2:

Fast group:   -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
Thermal group: -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

Parameters: D1=1.0, D2=0.5, A11=0.0075, A12=-0.25, A21=-0.015, A22=0.1

Boundary conditions (Neumann):
- Left   x=-0.5: -D_g * dphi_g/dx = y   (non-zero, linear in y)
- Right  x=+0.5: -D_g * dphi_g/dx = 0
- Top    y=+0.5: -D_g * dphi_g/dy = 0
- Bottom y=-0.5: -D_g * dphi_g/dy = 0

The script must implement:
    def solution() -> (phi1_func, phi2_func)
where phi1_func(x, y) and phi2_func(x, y) are callables returning float values.

# Data Description
No external data files. All parameters are defined inline in the script.
Dependencies allowed: numpy, scipy, torch (optional).

# Reference Solution (Initial Approach)
The current baseline uses FDM (finite difference method) with a 101x101 grid and scipy sparse solver. It achieves moderate accuracy but may be improved by:

1. Higher-order discretization (4th-order FD, spectral methods)
2. Adaptive mesh refinement near left boundary (where source varies as y)
3. Fourier series approach: expand in cosine basis for y, solve 1D ODE in x
4. Spectral collocation (Chebyshev polynomials in both directions)
5. Hybrid analytical-numerical: use known eigenstructure of D^{-1}A matrix

Key insight: the coupling matrix M = D^{-1}A = [[0.0075, -0.25], [-0.03, 0.2]]
has eigenvalues ~0.0262 and ~0.1813. Decoupling via eigendecomposition may
yield cleaner x-direction ODEs.

Target: minimize mean relative error vs. analytical reference at test points
(0,0), (0.2,0.2), (-0.2,-0.3), (0.4,-0.4). PDE residual < 1e-6 is excellent.
