# Baseline Candidates for Two-Group Neutron Diffusion Equation

**Project**: Analytical Solution of 2D Two-Group Neutron Diffusion Equation
**Date**: 2026-03-14
**For**: Experiment Runner and Model Developer Agents

---

## Executive Summary

This document recommends 5 baseline methods for comparison against the Famou evolutionary framework. The baselines span traditional numerical methods, neural network approaches, and hybrid methods to provide comprehensive evaluation coverage.

| Rank | Method | Category | Priority | Effort | Expected Accuracy |
|------|--------|----------|----------|--------|-------------------|
| 1 | Finite Difference Method (FDM) | Traditional | Must-have | Low | High (with fine grid) |
| 2 | Physics-Informed Neural Network (PINN) | Neural | Must-have | Medium | Medium-High |
| 3 | Chebyshev Spectral Method | Traditional | High | Medium | Very High |
| 4 | Finite Element Method (FEM) | Traditional | Medium | High | High |
| 5 | Analytical Eigenfunction Expansion | Analytical | Low | Variable | Exact (if tractable) |

---

## Baseline 1: Finite Difference Method (FDM)

### Overview

The Finite Difference Method discretizes the PDE on a regular grid, approximating derivatives using finite differences. It is the gold standard for simple geometries and provides a reliable accuracy reference.

### Mathematical Formulation

**Interior Points (5-point stencil):**
```
∇²φ ≈ (φ_{i+1,j} + φ_{i-1,j} + φ_{i,j+1} + φ_{i,j-1} - 4φ_{i,j}) / h²
```

**Left Boundary (Ghost Point Method):**
```
(φ_{1,j} - φ_{-1,j}) / (2h) = -y_j / D
→ φ_{-1,j} = φ_{1,j} + 2h·y_j / D
```

**Other Boundaries (Zero Neumann):**
```
φ_{-1,j} = φ_{1,j}  (left ghost for right boundary)
φ_{i,-1} = φ_{i,1}  (bottom ghost)
φ_{i,N+1} = φ_{i,N-1}  (top ghost)
```

### Implementation Plan

```python
import numpy as np
from scipy.sparse import csr_matrix, kron, diags
from scipy.sparse.linalg import spsolve

def solve_fdm_two_group(nx=101, ny=101):
    """
    Solve two-group neutron diffusion equation using FDM.

    Args:
        nx, ny: Number of grid points in x and y directions

    Returns:
        x, y: Grid coordinates
        phi1, phi2: Solution arrays (ny, nx)
    """
    # Grid setup
    x = np.linspace(-0.5, 0.5, nx)
    y = np.linspace(-0.5, 0.5, ny)
    hx, hy = x[1] - x[0], y[1] - y[0]

    # Physical constants
    D1, D2 = 1.0, 0.5
    Sr, Sa2 = 0.02, 0.1
    nu, Sf1, Sf2 = 2.5, 0.005, 0.1
    S12 = 0.015

    # Build 2D Laplacian using Kronecker products
    # ... (implementation)

    # Assemble coupled system
    # [A11  A12] [phi1] = [b1]
    # [A21  A22] [phi2]   [b2]

    # Solve and return
    return x, y, phi1, phi2
```

### Pros and Cons

**Pros:**
- Simple to implement and verify
- Well-understood convergence properties
- Easy to achieve high accuracy with fine grids
- Fast solution with sparse linear solvers

**Cons:**
- Accuracy limited by grid resolution
- Requires structured grid
- Boundary condition implementation can be tricky

### Expected Performance

- **Grid 51×51**: ~1% error
- **Grid 101×101**: ~0.1% error
- **Grid 201×201**: ~0.01% error
- **Runtime**: < 1 second for 101×101 grid

### Resources

- Reference: LeVeque, R.J. (2007). Finite Difference Methods for ODE and PDE. SIAM.
- Implementation guidance: See methodology-background.md Section 3.1

---

## Baseline 2: Physics-Informed Neural Network (PINN)

### Overview

PINNs embed the PDE and boundary conditions into the neural network loss function, enabling mesh-free solutions. They represent the state-of-the-art ML approach for PDE solving.

### Architecture

```
Input: (x, y) → Hidden Layers (64-128 units, 4-6 layers, Tanh) → Output: (φ₁, φ₂)
```

### Loss Function

```python
def pinn_loss(model, x_interior, y_interior, x_boundary, y_boundary, bc_values):
    """Compute PINN loss."""
    # PDE residuals
    res1, res2 = compute_pde_residual(model, x_interior, y_interior)
    loss_pde = torch.mean(res1**2) + torch.mean(res2**2)

    # Boundary residuals
    bc_pred = model(x_boundary, y_boundary)
    bc_residual = compute_neumann_residual(bc_pred, x_boundary, y_boundary, bc_values)
    loss_bc = torch.mean(bc_residual**2)

    # Total loss with weighting
    return loss_pde + lambda_bc * loss_bc
```

### Implementation Plan

```python
import torch
import torch.nn as nn

class TwoGroupPINN(nn.Module):
    def __init__(self, hidden_dim=64, num_layers=4):
        super().__init__()
        layers = [nn.Linear(2, hidden_dim), nn.Tanh()]
        for _ in range(num_layers - 1):
            layers.extend([nn.Linear(hidden_dim, hidden_dim), nn.Tanh()])
        layers.append(nn.Linear(hidden_dim, 2))
        self.net = nn.Sequential(*layers)

    def forward(self, x, y):
        xy = torch.stack([x, y], dim=-1)
        return self.net(xy)

def train_pinn(model, n_epochs=10000):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2000, gamma=0.5)

    for epoch in range(n_epochs):
        optimizer.zero_grad()
        loss = compute_total_loss(model)
        loss.backward()
        optimizer.step()
        scheduler.step()
```

### Training Strategy

1. **Adaptive Weighting**: Use gradient statistics to balance PDE and BC losses
2. **Curriculum Learning**: Start with simpler problem (e.g., single group)
3. **Residual Resampling**: Dynamically adjust collocation points

### Pros and Cons

**Pros:**
- Mesh-free evaluation
- Can handle complex geometries
- Differentiation via autograd
- Active research area

**Cons:**
- Training can be unstable
- Requires careful hyperparameter tuning
- May struggle with high-frequency solutions
- No convergence guarantees

### Expected Performance

- **Training time**: 10-30 minutes on GPU
- **Accuracy**: 10⁻³ to 10⁻⁵ residual (depending on training)
- **Inference**: Fast once trained

### Resources

- Reference: Raissi et al. (2019). Physics-informed neural networks. JCP, 378, 686-707.
- Code reference: https://github.com/maziarraissi/PINNs

---

## Baseline 3: Chebyshev Spectral Method

### Overview

Spectral methods using Chebyshev polynomials achieve exponential convergence for smooth solutions. They provide the highest accuracy among traditional methods for problems on simple domains.

### Mathematical Formulation

**Chebyshev-Gauss-Lobatto Points:**
```
x_i = cos(πi/N), i = 0, 1, ..., N
```

**Differentiation Matrix:**
```
(D_N)_{ij} = (c_i / c_j) * (-1)^{i+j} / (x_i - x_j), i ≠ j
(D_N)_{ii} = -x_i / (2(1 - x_i²)), i ≠ 0, N
(D_N)_{00} = -(2N² + 1) / 6
(D_N)_{NN} = (2N² + 1) / 6
```

**2D Laplacian:**
```
∇² ≈ I ⊗ D² + D² ⊗ I
```

### Implementation Plan

```python
import numpy as np
from numpy.polynomial.chebyshev import chebder

def cheb_diff_matrix(N):
    """Generate Chebyshev differentiation matrix."""
    x = np.cos(np.pi * np.arange(N+1) / N)
    c = np.ones(N+1)
    c[0], c[N] = 2, 2
    c *= (-1)**np.arange(N+1)

    X = np.outer(x, np.ones(N+1))
    dX = X - X.T + np.eye(N+1)
    D = np.outer(c, 1/c) / dX
    D -= np.diag(np.sum(D, axis=1))
    return D, x

def solve_spectral_two_group(N=50):
    """Solve using Chebyshev spectral method."""
    D, x = cheb_diff_matrix(N)
    D2 = D @ D

    # 2D operators via Kronecker product
    I = np.eye(N+1)
    L = np.kron(I, D2) + np.kron(D2, I)

    # Apply boundary conditions and solve
    # ...

    return phi1, phi2
```

### Boundary Condition Treatment

**Dirichlet**: Remove boundary rows/columns
**Neumann**: Replace boundary rows with derivative conditions

```python
# For Neumann BC at left boundary (x = -1 in Chebyshev domain)
# Replace row with: D[0, :] @ u = g
```

### Pros and Cons

**Pros:**
- Exponential convergence for smooth solutions
- Very high accuracy with moderate N
- Efficient with FFT for large N
- Elegant mathematical foundation

**Cons:**
- Global support (dense matrices)
- Less flexible for complex geometries
- Requires solution smoothness
- Boundary condition implementation can be complex

### Expected Performance

- **N = 30**: ~10⁻⁶ error
- **N = 50**: ~10⁻¹⁰ error (machine precision limited)
- **Runtime**: < 1 second

### Resources

- Reference: Trefethen, L.N. (2000). Spectral Methods in MATLAB. SIAM.
- Code: https://github.com/Trefethen/spectral-methods-matlab

---

## Baseline 4: Finite Element Method (FEM)

### Overview

FEM provides natural treatment of Neumann boundary conditions through variational formulation. It is the industry standard for complex engineering problems.

### Variational Formulation

**Weak Form for Fast Group:**
```
∫_Ω (D₁∇φ₁·∇v + Σᵣφ₁v) dΩ = ∫_Ω (νΣf₁φ₁ + νΣf₂φ₂)v dΩ + ∫_{Γ_left} y·v dΓ
```

**Key Advantage**: Neumann BCs appear naturally after integration by parts.

### Implementation Plan

Using FEniCS (Python):

```python
from fenics import *

# Mesh
mesh = RectangleMesh(Point(-0.5, -0.5), Point(0.5, 0.5), 64, 64)
V = FunctionSpace(mesh, 'P', 2)  # Quadratic elements

# Define boundaries
class LeftBoundary(SubDomain):
    def inside(self, x, on_boundary):
        return near(x[0], -0.5) and on_boundary

# Mark boundaries
# ...

# Variational problem
phi1 = TrialFunction(V)
phi2 = TrialFunction(V)
v1 = TestFunction(V)
v2 = TestFunction(V)

# Bilinear forms
a1 = (D1*dot(grad(phi1), grad(v1)) + Sr*phi1*v1)*dx
a2 = (D2*dot(grad(phi2), grad(v2)) + Sa2*phi2*v2)*dx

# Linear forms (coupled)
L1 = (nu*Sf1*phi1 + nu*Sf2*phi2)*v1*dx + y*v1*ds(1)
L2 = S12*phi1*v2*dx

# Solve coupled system
# ...
```

### Pros and Cons

**Pros:**
- Natural Neumann BC handling
- Handles complex geometries
- Rich mathematical theory
- Industry standard

**Cons:**
- Requires mesh generation
- Assembly overhead
- More complex implementation
- Overkill for simple square domain

### Expected Performance

- **Mesh 64×64 (P1)**: ~1% error
- **Mesh 64×64 (P2)**: ~0.01% error
- **Runtime**: 1-5 seconds

### Resources

- Reference: Brenner & Scott (2008). The Mathematical Theory of FEM. Springer.
- Software: FEniCS Project (https://fenicsproject.org)

---

## Baseline 5: Analytical Eigenfunction Expansion

### Overview

For simple geometries and constant coefficients, analytical solutions via eigenfunction expansion provide exact reference solutions.

### Mathematical Approach

**Step 1**: Solve eigenvalue problem for Laplacian on square with Neumann BCs:
```
∇²ψ + λψ = 0
∂ψ/∂n = 0 on boundaries
```

Eigenfunctions:
```
ψ_{mn}(x,y) = cos(mπ(x+0.5)) * cos(nπ(y+0.5))
λ_{mn} = π²(m² + n²)
```

**Step 2**: Expand solution:
```
φ₁ = Σ_{m,n} a_{mn} ψ_{mn}
φ₂ = Σ_{m,n} b_{mn} ψ_{mn}
```

**Step 3**: Solve for coefficients using orthogonality.

### Challenges

- Non-homogeneous Neumann BC on left boundary complicates expansion
- Coupled equations require simultaneous solution
- May require many terms for convergence

### Implementation Plan

```python
def solve_analytical_expansion(M=20, N=20):
    """
    Solve using eigenfunction expansion.

    Args:
        M, N: Number of modes in x and y

    Returns:
        phi1_func, phi2_func: Callable functions
    """
    # Compute expansion coefficients
    # Handle non-homogeneous BC via superposition or special treatment
    # ...

    def phi1(x, y):
        result = 0
        for m in range(M):
            for n in range(N):
                result += a[m,n] * np.cos(m*np.pi*(x+0.5)) * np.cos(n*np.pi*(y+0.5))
        return result

    return phi1, phi2
```

### Pros and Cons

**Pros:**
- Exact solution (infinite series limit)
- Provides theoretical insight
- No discretization error

**Cons:**
- Complex for mixed BCs
- Slow convergence for some problems
- Limited to simple geometries

### Expected Performance

- **20×20 modes**: ~0.1% error
- **50×50 modes**: ~0.001% error
- **Runtime**: Fast evaluation once coefficients computed

### Resources

- Reference: Haberman, R. (2013). Applied PDE with Fourier Series. Pearson.
- Reference: Duderstadt & Hamilton (1976). Nuclear Reactor Analysis. Wiley.

---

## Implementation Priority

### Phase 1: Essential Baselines (Must Implement)

1. **FDM**: Quick to implement, reliable reference
2. **PINN**: State-of-the-art ML comparison

### Phase 2: High-Value Baselines (Strongly Recommended)

3. **Chebyshev Spectral**: Demonstrates accuracy upper bound

### Phase 3: Optional Baselines (If Time Permits)

4. **FEM**: Industry standard validation
5. **Analytical**: Theoretical ground truth

---

## Comparison Metrics

### Accuracy Metrics

1. **PDE Residual**: L2 norm of PDE residual at test points
2. **BC Residual**: L2 norm of boundary condition residual
3. **Solution Difference**: ||φ_famou - φ_baseline||₂

### Efficiency Metrics

1. **Setup Time**: Implementation effort
2. **Training/Solution Time**: Wall-clock time
3. **Memory Usage**: Peak memory consumption
4. **Inference Time**: Evaluation speed

### Robustness Metrics

1. **Convergence**: Stability across runs
2. **Generalization**: Performance on unseen points
3. **Hyperparameter Sensitivity**: Tuning difficulty

---

## Expected Results Summary

| Method | PDE Residual | BC Residual | Setup Effort | Runtime |
|--------|-------------|-------------|--------------|---------|
| FDM (101×101) | ~10⁻⁴ | ~10⁻⁴ | Low | <1s |
| PINN (well-trained) | ~10⁻⁵ | ~10⁻⁵ | Medium | 10-30min train |
| Chebyshev (N=50) | ~10⁻¹⁰ | ~10⁻¹⁰ | Medium | <1s |
| FEM (P2, 64×64) | ~10⁻⁶ | ~10⁻⁶ | High | 1-5s |
| Famou (target) | <10⁻⁴ | <10⁻⁴ | Medium | Variable |

---

## References

1. Raissi, M., et al. (2019). Physics-informed neural networks. JCP, 378, 686-707.
2. Trefethen, L.N. (2000). Spectral Methods in MATLAB. SIAM.
3. LeVeque, R.J. (2007). Finite Difference Methods. SIAM.
4. Brenner, S.C., & Scott, L.R. (2008). The Mathematical Theory of FEM. Springer.
5. Duderstadt, J.J., & Hamilton, L.J. (1976). Nuclear Reactor Analysis. Wiley.

---

*Document prepared by Background Researcher Agent*
*Last updated: 2026-03-14*
