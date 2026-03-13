# Experiments Index

## 2D Two-Group Neutron Diffusion — Method Comparison

| Exp ID | Method | Max PDE Residual | Max BC Residual | Time (s) | Grid/Params | Status |
|--------|--------|-----------------|-----------------|----------|-------------|--------|
| exp-001 | Analytical (N=200) | 2.81e-16 | 5.03e-07 | 0.017 | 200 Fourier modes | **complete** |
| exp-002 | FDM 101×101 | 9.07e-05 | 3.97e-04 | 0.134 | 10201 DOF | **complete** |
| exp-003 | FEM 101×101 | TBD | TBD | TBD | ~20000 DOF | pending |
| exp-004 | Spectral N=30 | TBD | TBD | TBD | 900 DOF | pending |
| exp-005 | PINN | TBD | TBD | TBD | 3×64 MLP | pending |

## Experiment Details

### exp-001: Analytical Solution (Fourier-Cosine Eigendecomposition)
- **Script**: `scripts/numerical_solver/analytical_solver.py`
- **Method**: Fourier cosine series expansion with eigendecomposition for coupled 2-group system
- **Parameters**: N_terms=500 Fourier modes
- **Expected**: Machine-precision PDE residual, exact BC satisfaction

### exp-002: Finite Difference Method (FDM)
- **Script**: `baselines/fdm/fdm_solver.py`
- **Method**: 2nd-order central differences, sparse direct solve (scipy)
- **Parameters**: 101×101 uniform grid, 10201 DOF per group
- **Expected**: O(h^2) convergence

### exp-003: Finite Element Method (FEM)
- **Script**: `baselines/fem/fem_solver.py`
- **Method**: Linear triangular elements, Galerkin formulation
- **Parameters**: 101×101 node grid, ~20000 triangular elements
- **Expected**: O(h^2) convergence for linear elements

### exp-004: Spectral Method
- **Script**: `baselines/spectral/spectral_solver.py`
- **Method**: Chebyshev collocation
- **Parameters**: N=30 (900 DOF per group)
- **Expected**: Exponential convergence for smooth solutions

### exp-005: Physics-Informed Neural Network (PINN)
- **Script**: `baselines/pinn/pinn_solver.py`
- **Method**: MLP with PDE residual loss + BC loss
- **Parameters**: 3 hidden layers × 64 neurons, Adam optimizer
- **Expected**: Moderate accuracy, longer training time

## Update Log

- 2026-03-13: Initial experiment plan created
- 2026-03-13: exp-001 (Analytical N=200) complete — max PDE res 2.81e-16, max BC res 5.03e-07, 0.017s
- 2026-03-13: exp-002 (FDM 101x101) complete — max PDE res 9.07e-05, max BC res 3.97e-04, 0.134s
