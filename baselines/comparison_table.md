| Method | Max PDE Residual | Max BC Residual | Solve Time (s) | Parameters/Grid |
|--------|-----------------|-----------------|----------------|-----------------|
| Analytical (N=200) | 2.81e-16 | 5.03e-07 | 0.017 | 200 Fourier modes |
| FDM 101x101 | 9.07e-05 | 3.97e-04 | 0.134 | 101x101 = 10201 DOF |
| FEM 101x101 (Q1) | 9.20e-07 | 4.05e-04 | 0.824 | 101x101 = 10201 DOF |
| Spectral N=30 | 7.23e-06 | 6.04e-05 | 0.079 | 30x30 = 900 DOF |
| PINN (3x64 MLP) | 9.54e-03 | 9.13e-03 | 98.624 | 8,706 parameters |

## Notes

- **Analytical**: Fourier-cosine eigendecomposition, essentially exact (machine epsilon PDE residual). BC residual limited by truncation of Fourier series.
- **FDM**: 2nd-order centered finite differences with 2nd-order one-sided stencils at boundaries. Sparse direct solve (scipy spsolve).
- **FEM**: Bilinear Q1 Galerkin FEM with 2x2 Gauss quadrature. Neumann BC imposed naturally via boundary integral. BC residual evaluated via FD on interpolated solution.
- **Spectral**: Chebyshev-Gauss-Lobatto collocation, dense direct solve. Residuals evaluated using spectral differentiation matrices + barycentric interpolation.
- **PINN**: 2-64-64-64-2 MLP with tanh activation, trained 5000 Adam iterations on 2000 interior + 400 BC points. Highest residuals among all methods.

## Convergence (FDM)

| Grid | Max PDE Residual | Max BC Residual | Time (s) | h |
|------|-----------------|-----------------|----------|---|
| 21x21 | 2.86e-03 | 2.59e-03 | 0.006 | 0.05 |
| 51x51 | 3.64e-04 | 1.78e-04 | 0.024 | 0.02 |
| 101x101 | 9.07e-05 | 3.97e-04 | 0.132 | 0.01 |
| 201x201 | 2.25e-05 | 4.27e-04 | 1.108 | 0.005 |

FDM PDE residual decreases approximately as O(h^2), confirming 2nd-order convergence.
