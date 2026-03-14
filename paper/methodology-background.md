# Methodology Background: PDE Solution Methods

**For**: Model Developer Agent
**Project**: 2D Two-Group Neutron Diffusion Equation with Neumann Boundary Conditions
**Date**: 2026-03-14

---

## 1. Problem Formulation

### 1.1 Governing Equations

The two-group neutron diffusion equation describes steady-state neutron transport in nuclear reactors:

**Fast Group (Group 1):**
```
-D₁∇²φ₁ + Σᵣφ₁ = νΣf₁φ₁ + νΣf₂φ₂
```

**Thermal Group (Group 2):**
```
-D₂∇²φ₂ + Σₐ₂φ₂ = Σ₁→₂φ₁
```

Where:
- φ₁, φ₂: Neutron flux for fast and thermal groups
- D₁, D₂: Diffusion coefficients
- Σᵣ: Fast group removal cross-section
- Σₐ₂: Thermal group absorption cross-section
- ν: Average neutrons per fission
- Σf₁, Σf₂: Fission cross-sections
- Σ₁→₂: Group transfer cross-section

### 1.2 Domain and Boundary Conditions

**Domain**: Square region Ω = [-0.5, 0.5] × [-0.5, 0.5]

**Boundary Conditions (Neumann type):**

| Boundary | Position | Condition |
|----------|----------|-----------|
| Left | x = -0.5 | -D·∂φ/∂x = y (non-zero, spatially varying) |
| Right | x = 0.5 | -D·∂φ/∂x = 0 (zero Neumann) |
| Top | y = 0.5 | -D·∂φ/∂y = 0 (zero Neumann) |
| Bottom | y = -0.5 | -D·∂φ/∂y = 0 (zero Neumann) |

### 1.3 Physical Constants

| Symbol | Value | Unit | Description |
|--------|-------|------|-------------|
| D₁ | 1.0 | cm | Fast diffusion coefficient |
| D₂ | 0.5 | cm | Thermal diffusion coefficient |
| Σᵣ | 0.02 | cm⁻¹ | Fast removal cross-section |
| Σₐ₂ | 0.1 | cm⁻¹ | Thermal absorption cross-section |
| ν | 2.5 | - | Neutrons per fission |
| Σf₁ | 0.005 | cm⁻¹ | Fast fission cross-section |
| Σf₂ | 0.1 | cm⁻¹ | Thermal fission cross-section |
| Σ₁→₂ | 0.015 | cm⁻¹ | Group transfer cross-section |

---

## 2. Methodology Overview

### 2.1 Method Categories

```
PDE Solution Methods
├── Traditional Numerical
│   ├── Finite Difference Method (FDM)
│   ├── Finite Element Method (FEM)
│   └── Spectral Methods
├── Neural Network Based
│   ├── Physics-Informed Neural Networks (PINNs)
│   ├── Neural Operators (DeepONet, FNO, LNO)
│   └── Hybrid Approaches
└── Evolutionary/Search Based
    ├── FunSearch
    ├── Famou
    └── Genetic Programming
```

### 2.2 Method Selection Criteria

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| Accuracy | High | Must satisfy PDE and BCs with low residual |
| Efficiency | Medium | Training/evolution time should be reasonable |
| Generalization | Medium | Should handle similar problems |
| Interpretability | Low | Code-based solutions preferred |
| Implementation | High | Must be feasible within project timeline |

---

## 3. Traditional Numerical Methods

### 3.1 Finite Difference Method (FDM)

#### Discretization

For a uniform grid with spacing h:
```
∂²φ/∂x² ≈ (φ_{i+1,j} - 2φ_{i,j} + φ_{i-1,j}) / h²
∂²φ/∂y² ≈ (φ_{i,j+1} - 2φ_{i,j} + φ_{i,j-1}) / h²
```

#### Neumann Boundary Treatment

For left boundary (x = -0.5) with -D·∂φ/∂x = y:

**Ghost Point Method:**
```
(φ_{1,j} - φ_{-1,j}) / (2h) = -y_j / D
→ φ_{-1,j} = φ_{1,j} + 2h·y_j / D
```

**One-sided Difference (2nd order):**
```
(-3φ_{0,j} + 4φ_{1,j} - φ_{2,j}) / (2h) = -y_j / D
```

#### System Assembly

The discretized equations form a linear system:
```
A·Φ = b
```

Where A is a sparse matrix (block tridiagonal for 2D), Φ is the vector of unknown flux values, and b incorporates boundary conditions.

#### Implementation Notes

```python
import numpy as np
from scipy.sparse import diags, kron, eye
from scipy.sparse.linalg import spsolve

def solve_fdm(nx, ny, constants):
    """
    Solve two-group diffusion equation using FDM.

    Args:
        nx, ny: Number of grid points in x and y
        constants: Dict with D1, D2, Sr, Sa2, nu, Sf1, Sf2, S12

    Returns:
        phi1, phi2: Solution arrays (ny, nx)
    """
    # Grid setup
    x = np.linspace(-0.5, 0.5, nx)
    y = np.linspace(-0.5, 0.5, ny)
    hx, hy = x[1] - x[0], y[1] - y[0]

    # Build Laplacian matrix
    # ... (implementation details)

    # Apply boundary conditions
    # Left: -D*dphi/dx = y
    # Others: -D*dphi/dx or dphi/dy = 0

    # Solve coupled system
    # ...

    return phi1, phi2
```

### 3.2 Spectral Methods (Chebyshev)

#### Chebyshev Polynomials

Defined on [-1, 1]:
```
T_n(x) = cos(n·arccos(x))
```

Recurrence relation:
```
T_{n+1}(x) = 2x·T_n(x) - T_{n-1}(x)
T_0(x) = 1, T_1(x) = x
```

#### Collocation Points

Chebyshev-Gauss-Lobatto points:
```
x_j = cos(πj/N), j = 0, 1, ..., N
```

#### Differentiation Matrix

The derivative at collocation points:
```
dφ/dx|_{x_i} ≈ Σ_j D_{ij} φ(x_j)
```

Where D is the Chebyshev differentiation matrix.

#### Advantages for This Problem

1. **Exponential convergence**: For smooth solutions, error decreases as O(e^{-cN})
2. **Boundary clustering**: Natural resolution of boundary layers
3. **Efficient**: O(N log N) operations with FFT

#### Implementation Sketch

```python
import numpy as np
from numpy.polynomial.chebyshev import chebder, chebval

def cheb_diff_matrix(N):
    """Generate Chebyshev differentiation matrix."""
    x = np.cos(np.pi * np.arange(N+1) / N)
    c = np.ones(N+1)
    c[0], c[N] = 2, 2
    c = c * (-1)**np.arange(N+1)
    X = np.tile(x, (N+1, 1))
    dX = X - X.T
    D = (c[:, None] / c[None, :]) / (dX + np.eye(N+1))
    D = D - np.diag(np.sum(D, axis=1))
    return D, x

def solve_spectral(N, constants):
    """Solve using Chebyshev spectral method."""
    # 2D: Use tensor product of 1D Chebyshev grids
    # Build 2D differentiation matrices via Kronecker products
    # Apply boundary conditions
    # Solve system
    pass
```

### 3.3 Finite Element Method (FEM)

#### Variational Formulation

For the fast group equation:
```
∫_Ω (D₁∇φ₁·∇v + Σᵣφ₁v) dΩ = ∫_Ω (νΣf₁φ₁ + νΣf₂φ₂)v dΩ + ∫_Γ y·v dΓ
```

**Key insight**: Neumann boundary conditions appear naturally in the variational form after integration by parts.

#### Weak Form Derivation

Starting from:
```
-D₁∇²φ₁ + Σᵣφ₁ = νΣf₁φ₁ + νΣf₂φ₂
```

Multiply by test function v and integrate:
```
∫_Ω (-D₁∇²φ₁)v dΩ + ∫_Ω Σᵣφ₁v dΩ = ∫_Ω (νΣf₁φ₁ + νΣf₂φ₂)v dΩ
```

Integration by parts on first term:
```
∫_Ω D₁∇φ₁·∇v dΩ - ∫_Γ D₁(∂φ₁/∂n)v dΓ + ∫_Ω Σᵣφ₁v dΩ = RHS
```

Apply Neumann BC (-D₁∂φ₁/∂n = y on left, 0 elsewhere):
```
∫_Ω (D₁∇φ₁·∇v + Σᵣφ₁v) dΩ = RHS + ∫_{Γ_left} y·v dΓ
```

#### Implementation with FEniCS

```python
from fenics import *

# Mesh
mesh = UnitSquareMesh(64, 64)
V = FunctionSpace(mesh, 'P', 1)

# Boundary markers
left_boundary = CompiledSubDomain('near(x[0], -0.5)')
# ... other boundaries

# Variational problem
phi1 = TrialFunction(V)
v = TestFunction(V)

a = (D1*dot(grad(phi1), grad(v)) + Sr*phi1*v)*dx
L = (nu*Sf1*phi1 + nu*Sf2*phi2)*v*dx + y*v*ds(1)  # ds(1) = left boundary

# Solve
phi1 = Function(V)
solve(a == L, phi1)
```

---

## 4. Neural Network Methods

### 4.1 Physics-Informed Neural Networks (PINNs)

#### Architecture

```
Input: (x, y)
    ↓
[Fully Connected Layers]
    ↓
Output: (φ₁, φ₂)
```

#### Loss Function

**PDE Residual:**
```
L_PDE1 = || -D₁(φ₁,xx + φ₁,yy) + Σᵣφ₁ - (νΣf₁φ₁ + νΣf₂φ₂) ||²
L_PDE2 = || -D₂(φ₂,xx + φ₂,yy) + Σₐ₂φ₂ - Σ₁→₂φ₁ ||²
```

**Boundary Residual:**
```
L_BC_left = || -D·∂φ/∂x - y ||²_{x=-0.5}
L_BC_right = || -D·∂φ/∂x ||²_{x=0.5}
L_BC_top = || -D·∂φ/∂y ||²_{y=0.5}
L_BC_bottom = || -D·∂φ/∂y ||²_{y=-0.5}
```

**Total Loss:**
```
L_total = λ₁L_PDE1 + λ₂L_PDE2 + λ_bc(L_BC_left + L_BC_right + L_BC_top + L_BC_bottom)
```

#### Implementation

```python
import torch
import torch.nn as nn

class PINN(nn.Module):
    def __init__(self, hidden_dim=64, num_layers=4):
        super().__init__()
        layers = []
        layers.append(nn.Linear(2, hidden_dim))
        layers.append(nn.Tanh())
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.Tanh())
        layers.append(nn.Linear(hidden_dim, 2))  # φ₁, φ₂
        self.net = nn.Sequential(*layers)

    def forward(self, x, y):
        xy = torch.stack([x, y], dim=-1)
        return self.net(xy)

    def pde_residual(self, x, y, constants):
        """Compute PDE residuals."""
        x.requires_grad_(True)
        y.requires_grad_(True)

        phi = self.forward(x, y)
        phi1, phi2 = phi[..., 0], phi[..., 1]

        # Compute derivatives
        phi1_x = torch.autograd.grad(phi1, x, grad_outputs=torch.ones_like(phi1),
                                     create_graph=True)[0]
        phi1_xx = torch.autograd.grad(phi1_x, x, grad_outputs=torch.ones_like(phi1_x),
                                      create_graph=True)[0]
        # ... similar for yy and phi2

        # Compute residuals
        res1 = -constants['D1']*(phi1_xx + phi1_yy) + constants['Sr']*phi1 - \
               (constants['nu']*constants['Sf1']*phi1 + constants['nu']*constants['Sf2']*phi2)
        # ... res2

        return res1, res2
```

#### Training Challenges

1. **Gradient conflicts**: PDE and BC losses may compete
   - Solution: Gradient harmonization, adaptive weighting

2. **Spectral bias**: Neural networks learn low frequencies first
   - Solution: Fourier features, multi-scale networks

3. **Training instability**: Sensitive to initialization and learning rate
   - Solution: Curriculum learning, residual resampling

### 4.2 Neural Operators

#### DeepONet

Learns operator G: u → φ where u is input function (e.g., source term).

**Architecture:**
```
Branch net: u → (b₁, b₂, ..., b_p)
Trunk net: (x, y) → (t₁, t₂, ..., t_p)
Output: φ(x, y) = Σ_i b_i·t_i
```

#### Fourier Neural Operator (FNO)

**Key idea**: Learn in Fourier space
```
φ_{l+1} = σ(W_l·φ_l + F^{-1}(R_l·F(φ_l)))
```

Where F is FFT, R_l is learnable complex weight matrix.

**Advantage**: Fast, mesh-independent inference

---

## 5. Evolutionary Methods

### 5.1 FunSearch Framework

#### Core Concept

FunSearch combines LLMs with evolutionary algorithms to discover programs.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Prompt    │────→│     LLM     │────→│  Candidate  │
│  (examples) │     │   (PaLM 2)  │     │   Program   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                                ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Islands   │←────│   Scoring   │←────│  Evaluation │
│  (programs) │     │   (fitness) │     │  (execute)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

#### Island-Based Evolution

- Multiple subpopulations (islands) maintain diversity
- Periodic migration of elite solutions
- Prevents premature convergence

#### Key Components

1. **Program Database**: Stores scored programs
2. **LLM Prompt Construction**: Samples high-performing programs
3. **Sandboxed Execution**: Safe evaluation
4. **Deduplication**: Behavioral hashing

### 5.2 Famou for PDE Solving

#### Adaptation for PDEs

**Individual Representation:**
```python
def solve_neutron_diffusion(x, y):
    """
    Compute φ₁(x,y) and φ₂(x,y).

    Args:
        x, y: Spatial coordinates (scalars or arrays)

    Returns:
        phi1, phi2: Neutron flux values
    """
    # Candidate solution code (evolved)
    phi1 = ...
    phi2 = ...
    return phi1, phi2
```

**Fitness Function:**
```python
def evaluate(program):
    """Score a candidate solution."""
    # PDE residual at test points
    res1, res2 = compute_pde_residual(program, test_points)

    # BC residual at boundary points
    bc_res = compute_bc_residual(program, boundary_points)

    # Combined score (lower is better)
    score = - (||res1|| + ||res2|| + λ·||bc_res||)

    return score
```

#### Evolution Loop

```python
def famou_evolution(problem_spec, num_rounds=100):
    """
    Main Famou evolution loop.

    Args:
        problem_spec: Contains evaluate() and seed programs
        num_rounds: Number of evolution rounds
    """
    islands = initialize_islands(problem_spec.seeds)

    for round in range(num_rounds):
        for island in islands:
            # Select parents
            parents = island.sample_high_scoring(k=3)

            # Generate candidate via LLM
            prompt = build_prompt(parents, problem_spec)
            candidate = llm_generate(prompt)

            # Evaluate
            score = problem_spec.evaluate(candidate)

            # Add to island if improved
            if score > island.worst_score():
                island.add(candidate, score)

        # Periodic migration
        if round % 10 == 0:
            migrate_elites(islands)

    return best_program(islands)
```

### 5.3 Advantages for This Problem

1. **Interpretability**: Solutions are explicit Python functions
2. **No training data needed**: Self-supervised via PDE residual
3. **Handles boundary conditions naturally**: Enforced in evaluation
4. **Coupled system friendly**: Can evolve φ₁ and φ₂ simultaneously

---

## 6. Method Comparison for This Project

### 6.1 Suitability Analysis

| Method | PDE Handling | BC Handling | Coupled System | Implementation |
|--------|-------------|-------------|----------------|----------------|
| FDM | Excellent | Good (ghost points) | Good | Easy |
| Spectral | Excellent | Moderate | Moderate | Moderate |
| FEM | Excellent | Excellent (natural) | Good | Complex |
| PINN | Good | Good (soft constraints) | Good | Moderate |
| Famou | Good | Good (evaluation) | Good | Moderate |

### 6.2 Recommended Approach

**Primary**: Famou evolutionary framework
- Novel application to neutron diffusion
- Interpretable solutions
- Natural handling of coupled system

**Baselines**:
1. FDM: Reliable reference solution
2. PINN: State-of-the-art ML comparison
3. Spectral: High-accuracy benchmark

---

## 7. Implementation Guidelines

### 7.1 Famou Implementation Checklist

- [ ] Define `evaluate()` function for PDE + BC residuals
- [ ] Create seed programs (simple analytical guesses)
- [ ] Set up island-based evolution parameters
- [ ] Implement LLM prompt construction
- [ ] Configure scoring weights (PDE vs BC balance)
- [ ] Add derivative computation (analytical or numerical)

### 7.2 FDM Baseline Checklist

- [ ] Implement 2D Laplacian discretization
- [ ] Handle Neumann BCs (ghost points or one-sided)
- [ ] Assemble coupled system matrix
- [ ] Solve linear system (direct or iterative)
- [ ] Verify convergence with grid refinement

### 7.3 PINN Baseline Checklist

- [ ] Design network architecture (width, depth, activation)
- [ ] Implement PDE residual computation (autograd)
- [ ] Implement BC residual computation
- [ ] Set up training loop with adaptive weighting
- [ ] Monitor loss components separately

---

## 8. References

1. Raissi, M., et al. (2019). Physics-informed neural networks. *JCP*, 378, 686-707.
2. Romera-Paredes, B., et al. (2023). Mathematical discoveries from program search with LLMs. *Nature*.
3. Trefethen, L.N. (2000). Spectral Methods in MATLAB. SIAM.
4. Brenner, S.C., & Scott, L.R. (2008). The Mathematical Theory of FEM. Springer.
5. Duderstadt, J.J., & Hamilton, L.J. (1976). Nuclear Reactor Analysis. Wiley.

---

*Document for Model Developer Agent*
*Last updated: 2026-03-14*
