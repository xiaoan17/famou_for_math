# Literature Review: Two-Group Neutron Diffusion Equation Numerical Solutions

**Project**: Analytical Solution of 2D Two-Group Neutron Diffusion Equation with Neumann Boundary Conditions
**Date**: 2026-03-14
**Researcher**: Background Researcher Agent

---

## 1. Research Scope and Keywords

### Core Research Questions
1. How to solve two-group neutron diffusion equations with mixed Neumann boundary conditions?
2. What are the state-of-the-art AI4S methods for PDE solving?
3. How does the Famou evolutionary framework compare to traditional and neural approaches?

### Search Keywords
- "Two-group neutron diffusion equation" + "analytical solution"
- "Physics-Informed Neural Networks" + "neutron diffusion"
- "FunSearch" + "evolutionary algorithm" + "PDE"
- "Helmholtz equation" + "Neumann boundary" + "finite difference"
- "Neural operator" + "DeepONet" + "FNO" + "AI4S"
- "Spectral method" + "Chebyshev" + "PDE boundary value problem"

---

## 2. Method Taxonomy and Comparison Matrix

### 2.1 Overview of PDE Solution Methods

| Method Category | Representative Methods | Key Characteristics | Typical Accuracy | Computational Cost |
|----------------|----------------------|---------------------|------------------|-------------------|
| **Traditional Numerical** | FDM, FEM, Spectral | Mesh-based, well-established | $O(h^p)$, $p=2-6$ | High for fine meshes |
| **Analytical Methods** | Laplace transform, Eigenfunction expansion | Exact when applicable | Exact | Low (when tractable) |
| **Neural Network Based** | PINNs, DeepONet, FNO | Mesh-free, data-driven | $10^{-3}-10^{-6}$ | High training cost |
| **Evolutionary Search** | FunSearch, Famou, Genetic Programming | Code evolution, interpretable | Problem-dependent | Moderate |
| **Hybrid Approaches** | CNN-PINN, Fourier-DeepONet | Combines strengths | Improved over baselines | Moderate to high |

### 2.2 Detailed Method Comparison

#### Traditional Numerical Methods

| Method | Strengths | Limitations | Best For |
|--------|-----------|-------------|----------|
| **Finite Difference (FDM)** | Simple implementation, efficient for regular domains | Accuracy limited by grid resolution, boundary condition handling | Regular geometries, quick prototyping |
| **Finite Element (FEM)** | Handles complex geometries, natural Neumann BC treatment | Requires mesh generation, assembly overhead | Complex domains, engineering applications |
| **Spectral (Chebyshev)** | Exponential convergence for smooth solutions | Global support, less flexible for complex geometries | Smooth solutions on simple domains |

#### Neural Network Methods

| Method | Key Innovation | Accuracy | Limitations |
|--------|---------------|----------|-------------|
| **PINNs** | Physics constraints in loss function | $10^{-3}-10^{-5}$ | Training instability, gradient conflicts |
| **CNN-PINN** | Convolutional architecture for spatial features | 0.63% flux error (vs 3.80% baseline) | Requires structured grids |
| **DeepONet** | Operator learning between function spaces | Good generalization | Needs training data ensemble |
| **FNO** | Fourier space operator learning | Fast inference | Limited to periodic/smooth problems |
| **Latent Neural Operator (LNO)** | Physics-Cross-Attention in latent space | SOTA on 4/6 benchmarks | Complex architecture |

#### Evolutionary Methods

| Method | Key Innovation | Application Domain | Performance |
|--------|---------------|-------------------|-------------|
| **FunSearch** | LLM-guided code evolution | Combinatorial optimization, PDEs | Cap set problem: first improvement in 20 years |
| **Famou** | Cloud-based evolutionary PDE solving | Helmholtz-type equations | Competitive with specialized solvers |
| **EvoKAN** | Evolutionary Kolmogorov-Arnold Networks | Allen-Cahn, Navier-Stokes | Energy-stable solutions |

---

## 3. Key Literature Analysis

### 3.1 Core Papers on Neutron Diffusion Equations

#### 1. CNN-Based PINNs for Neutron Diffusion (Seoul National University, 2025)
- **Title**: "A CNN-Based Physics-Informed Neural Networks for Solving the Neutron Diffusion Equation"
- **Innovation**: Replaces fully-connected networks with CNNs for spatial feature extraction
- **Results**: 11.24% flux RMS error (single reactor), 7.61% (multiple patterns)
- **Significance**: Enables inference on unseen reactor configurations

#### 2. FC-PINNs for Eigenvalue Problems (JCP, 2025)
- **Title**: "FC-PINNs: Physics-informed neural networks for solving neutron diffusion eigenvalue problem with interface considerations"
- **Authors**: Song, Zhang, Liu
- **Innovation**: Fixed-point transformation for eigenvalue problems; domain concatenation for interfaces
- **Results**: All test cases below 0.3% error
- **DOI**: 10.1016/j.jcp.2025.114311

#### 3. Analytical Solutions via Laplace Transform
- **Title**: "Analytical solutions to the coupled fractional neutron diffusion equations with delayed neutrons"
- **Method**: Laplace transform for time-dependent problems
- **Application**: Fractional-order neutron diffusion

### 3.2 Core Papers on FunSearch and Evolutionary PDE Solving

#### 1. FunSearch (DeepMind, Nature 2023)
- **Title**: "Mathematical discoveries from program search with large language models"
- **Authors**: Romera-Paredes et al.
- **Key Innovation**: LLM-guided evolutionary search with island-based selection
- **Achievements**:
  - Cap set problem: First improvement in 20 years
  - Online bin packing: New state-of-the-art heuristics
  - Interpretable program outputs

#### 2. Evolutionary Algorithms for PDEs
- **Title**: "Solving Partial Differential Equations Using a New Differential Evolution Algorithm"
- **Method**: DE-New with adaptive population sizing
- **Test Cases**: Laplace, Helmholtz, Poisson equations
- **Approach**: Converts PDE to optimization with equality constraints

### 3.3 Core Papers on Neural Operators (AI4S)

#### 1. Latent Neural Operator (NeurIPS 2024)
- **Title**: "Latent Neural Operator for Solving Forward and Inverse PDE Problems"
- **Authors**: Wang & Wang (Chinese Academy of Sciences)
- **Innovation**: Physics-Cross-Attention (PhCA) for geometric/latent space transformation
- **Performance**: 50% GPU memory reduction, 1.8x training speedup
- **Code**: https://github.com/L-I-M-I-T/LatentNeuralOperator

#### 2. DiffusionPDE (NeurIPS 2024)
- **Title**: "DiffusionPDE: Solving Partial Differential Equations under Partial Observations"
- **Method**: Generative diffusion models for PDE solving
- **Application**: Partial observations, inverse problems

#### 3. DGenNO (JCP 2025)
- **Title**: "DGenNO: a novel physics-aware neural operator for solving forward and inverse PDE problems"
- **Innovation**: MultiONet generalization of DeepONet; uses unlabeled data via weak-form residuals

### 3.4 Core Papers on Helmholtz/Neumann Boundary Problems

#### 1. High-Order Compact Finite Difference
- **Title**: "A new 9-point sixth-order accurate compact finite difference method for the Helmholtz equation"
- **Author**: Nabavi et al.
- **Innovation**: Sixth-order accuracy with special Neumann boundary treatment

#### 2. Method of Fundamental Solutions
- **Title**: "Method of fundamental solutions for Neumann problems of the modified Helmholtz equation in disk domains"
- **Method**: MFS with exponential convergence for disk domains

#### 3. Difference Potentials Method
- **Developer**: Ryaben'kii
- **Advantage**: Universal boundary condition treatment on regular grids
- **Capability**: Handles Dirichlet, Neumann, Robin without boundary approximation

---

## 4. Research Gap Analysis

### 4.1 Identified Gaps

| Gap Category | Description | Opportunity |
|--------------|-------------|-------------|
| **Methodological** | Limited work on evolutionary methods for coupled PDE systems | Apply Famou to two-group neutron diffusion |
| **Application** | Most PINN work focuses on single-group or time-dependent problems | Steady-state two-group with mixed Neumann BCs |
| **Boundary Treatment** | Non-homogeneous Neumann conditions with spatial variation ($y$) | Left boundary $-D\partial\phi/\partial x = y$ |
| **Coupled Systems** | Fast-thermal coupling in evolutionary frameworks | Simultaneous evolution of $\phi_1$ and $\phi_2$ |

### 4.2 Positioning of This Research

This project addresses the intersection of:
1. **Nuclear engineering**: Two-group neutron diffusion (industry-relevant)
2. **AI4S**: Evolutionary PDE solving via Famou
3. **Numerical analysis**: Mixed Neumann boundary conditions

**Novelty**: First application of LLM-guided evolutionary search to coupled-group neutron diffusion with non-trivial Neumann boundary conditions.

---

## 5. Baseline Method Candidates

### 5.1 Recommended Baselines

| Rank | Method | Rationale | Implementation Complexity |
|------|--------|-----------|--------------------------|
| 1 | **Finite Difference (FDM)** | Gold standard, easy to verify | Low |
| 2 | **Physics-Informed Neural Network (PINN)** | State-of-the-art AI4S approach | Medium |
| 3 | **Spectral Method (Chebyshev)** | Exponential accuracy for smooth solutions | Medium |
| 4 | **Finite Element (FEM)** | Natural Neumann BC handling | Medium-High |
| 5 | **Analytical (Eigenfunction Expansion)** | Ground truth when available | Problem-dependent |

### 5.2 Baseline Selection Justification

**Primary Baseline: FDM**
- Well-understood, easy to implement correctly
- Provides reliable accuracy reference
- Can achieve high accuracy with fine grids

**AI4S Baseline: PINN**
- Represents current ML approach
- Direct comparison with evolutionary method
- Highlights trade-offs between training and evolution

**High-Accuracy Baseline: Spectral Method**
- Exponential convergence for smooth solutions
- Demonstrates upper bound of numerical accuracy
- Validates if solution is sufficiently smooth

---

## 6. References

### Key Papers

1. Romera-Paredes, B., et al. (2023). Mathematical discoveries from program search with large language models. *Nature*.

2. Wang, T., & Wang, C. (2024). Latent Neural Operator for Solving Forward and Inverse PDE Problems. *NeurIPS 2024*.

3. Song, M., Zhang, T., & Liu, X. (2025). FC-PINNs: Physics-informed neural networks for solving neutron diffusion eigenvalue problem with interface considerations. *Journal of Computational Physics*, 541, 114311.

4. Raissi, M., Perdikaris, P., & Karniadakis, G.E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *Journal of Computational Physics*, 378, 686-707.

5. Li, Z., et al. (2021). Fourier Neural Operator for Parametric Partial Differential Equations. *ICLR 2021*.

6. Lu, L., et al. (2021). Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators. *Nature Machine Intelligence*, 3(3), 218-229.

7. Trefethen, L.N. (2000). Spectral Methods in MATLAB. SIAM.

8. Duderstadt, J.J., & Hamilton, L.J. (1976). Nuclear Reactor Analysis. Wiley.

### Online Resources

- FunSearch GitHub: https://github.com/google-deepmind/funsearch
- Latent Neural Operator: https://github.com/L-I-M-I-T/LatentNeuralOperator
- DeepMind FunSearch Blog: https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/

---

*Document generated by Background Researcher Agent*
*Last updated: 2026-03-14*
