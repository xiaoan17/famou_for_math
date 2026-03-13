# Literature Review: Analytical and Numerical Methods for Multi-Group Neutron Diffusion Equations

## 1. Multi-Group Neutron Diffusion: Historical Development and Analytical Solutions

### 1.1 Foundations

The multi-group neutron diffusion equation is the workhorse of nuclear reactor core analysis. Derived from the Boltzmann neutron transport equation under the assumptions of isotropic scattering and piecewise-homogeneous media, the diffusion approximation replaces the full angular dependence of the neutron flux with Fick's law, yielding a system of coupled elliptic PDEs---one per energy group (Duderstadt and Hamilton, 1976; Stacey, 2007). For G energy groups on a spatial domain $\Omega$, the steady-state system reads:

$$-\nabla \cdot (D_g \nabla \phi_g) + \Sigma_{r,g}\,\phi_g = \sum_{g'\neq g} \Sigma_{g'\to g}\,\phi_{g'} + \chi_g \sum_{g'} \nu \Sigma_{f,g'}\,\phi_{g'}, \quad g=1,\dots,G.$$

The two-group model ($G=2$: fast and thermal) captures the essential physics of thermal reactors while remaining tractable for analytical work (Lamarsh, 1966; Duderstadt and Hamilton, 1976, Ch. 5).

### 1.2 Classical Analytical Solutions

Closed-form solutions to the multi-group diffusion equation have been obtained primarily for one-dimensional and separable geometries:

- **1D slab geometry**: The Laplace Transform Technique was applied to the two-group diffusion equation in multilayered slabs by Lemos et al. (2008, *Annals of Nuclear Energy*), yielding analytical expressions for both forward and adjoint fluxes. The transformed scalar flux is recovered through Heaviside expansion.

- **1D eigenvalue problems**: Zanette et al. (2021, *Brazilian Journal of Radiation Sciences*) developed a modified power method that solves each iterate analytically using the Finite Fourier Sine Transform, obtaining the dominant eigenvalue ($k_\text{eff}$) and eigenfunction for multigroup slab problems.

- **2D rectangular geometry**: Fernandes, Bodmann, and Vilhena (Federal Univ. Rio Grande do Sul) used a two-step integral transform procedure with the Parseval identity to construct analytical solutions in rectangular 2D domains for multi-group problems. The Fictitious Borders Power Method (FBPM) of Zanette et al. (2018, *Annals of Nuclear Energy*) divides the domain into sub-regions and solves each analytically via Fourier Transform, reconstructing the global solution by polynomial interpolation.

- **Rectangular lattice cells**: Dion and Bhatt (2013, *Annals of Nuclear Energy*) solved the two-group diffusion and transport equations in a rectangular lattice cell with an elliptical fuel element using Fourier expansion methods, treating the lattice multiplication factor as the eigenvalue.

- **Cylindrical geometry**: The Laplace-Hankel transform approach extends the rectangular techniques to cylindrical coordinates for two-group kinetic problems (IAEA archives).

- **Residual Power Series Method (RPSM)**: El-Ajou et al. (2019, *Mathematics*) provided general solutions to multi-energy-group (2 and 4 groups) diffusion equations in rectangular, cylindrical, and spherical geometries without discretization.

### 1.3 Nodal and Semi-Analytical Methods

The Analytic Coarse-Mesh Finite Difference (ACMFD) method, implemented in the ANDES solver (Lozano et al., 2008, *Annals of Nuclear Energy*), derives its coarse-mesh discretization from the analytic solution of the 1D multi-group diffusion equation, achieving high accuracy with very coarse meshes. Nodal methods (NEM, ANM) exploit transverse integration to reduce 3D problems to coupled 1D problems solved analytically within each node (Smith, 1983).

### 1.4 Gap in Analytical Solutions

Despite these advances, *closed-form* analytical solutions for the **coupled two-group system in 2D with inhomogeneous Neumann boundary conditions** are absent from the literature. Existing Fourier-based methods either:
- treat homogeneous (zero-flux or zero-current) BCs,
- use iterative power methods that yield the solution only as the limit of an iteration, or
- address the criticality eigenvalue problem rather than a fixed-source/boundary-driven problem.

The present work fills this gap by constructing a direct, non-iterative closed-form solution via Fourier-cosine expansion combined with matrix eigendecomposition.

---

## 2. Classical Numerical Methods for Neutron Diffusion

### 2.1 Finite Difference Method (FDM)

FDM discretizes the spatial domain on a structured grid and approximates differential operators by central differences. For neutron diffusion, the resulting sparse linear system (or generalized eigenvalue problem) is solved by direct or iterative methods. FDM is straightforward to implement but suffers from low-order convergence ($O(h^2)$ for second-order schemes) and inflexibility with complex geometries. It remains widely used as a reference method for benchmarking (Han, 2009, *Science and Technology of Nuclear Installations*).

### 2.2 Finite Element Method (FEM)

FEM employs local polynomial basis functions on unstructured meshes, producing sparse algebraic systems. Galerkin FEM for multi-group neutron diffusion has been applied extensively to both rectangular and hexagonal cores (Cho et al., 2016, *Nuclear Engineering and Technology*). Higher-order FEM ($p$-refinement) and $hp$-adaptive methods achieve algebraic convergence rates that can be tuned by increasing either mesh density or polynomial degree. FEM handles complex geometries and material interfaces naturally but requires mesh generation and careful treatment of multi-group coupling.

The SP3 approximation of neutron transport, discretized by FEM, offers improved accuracy over diffusion theory at moderate additional cost (Abreu et al., 2019, arXiv:1903.11502).

### 2.3 Spectral Methods

Spectral methods expand the solution in global orthogonal basis functions (typically Fourier or Chebyshev polynomials), achieving exponential convergence for smooth solutions. The Spectral Green's Function (SGF) method (Cabral da Silva et al., TEMA 2023) solves the 1D diffusion equation exactly within each spatial cell and couples cells via interface conditions, yielding solutions free of truncation error on coarse meshes. The spectral finite element method (SFEM) combines spectral accuracy with FEM flexibility, using high-order Gauss-Lobatto-Legendre polynomials as basis functions.

For smooth problems on regular domains---precisely the setting of the present work---spectral methods offer the fastest convergence per degree of freedom. However, their global basis functions make them less suitable for heterogeneous cores with material discontinuities.

### 2.4 Comparison Matrix

| Method | Convergence Rate | Geometry Flexibility | Matrix Structure | Analytical Availability | Typical Use Case |
|--------|-----------------|---------------------|------------------|------------------------|------------------|
| **Analytical (Fourier-Eigen)** | Exact (N-term truncation) | Rectangular only | Dense (small) | Yes---closed form | Benchmarking, verification |
| **FDM** | $O(h^2)$ | Structured grids | Sparse | No | Quick prototyping, reference |
| **FEM (linear)** | $O(h^2)$ | Unstructured meshes | Sparse | No | Production reactor codes |
| **FEM (high-order)** | $O(h^{p+1})$ | Unstructured meshes | Sparse (wider bandwidth) | No | High-accuracy simulations |
| **Spectral** | Exponential (smooth) | Regular domains | Dense | No | Research, smooth benchmarks |
| **SGF (coarse mesh)** | Exact per cell | 1D / structured | Sparse | Semi-analytical | Coarse-mesh reactor codes |
| **PINN** | Problem-dependent | Mesh-free | Dense (NN weights) | No | Data-scarce, inverse problems |
| **FNO / DeepONet** | Data-dependent | Varies | Dense (NN weights) | No | Parametric studies, surrogate models |

---

## 3. AI for Science: Neural PDE Solvers

### 3.1 Physics-Informed Neural Networks (PINNs)

Raissi, Perdikaris, and Karniadakis (2019, *Journal of Computational Physics*, 378:686--707) introduced PINNs, which embed PDE residuals into the loss function of a neural network, enabling mesh-free solution of forward and inverse problems. PINNs have been applied to neutron diffusion in several recent works:

- **DEPINN** (Data-Enabled PINN): Yang et al. (2023, *Annals of Nuclear Energy*) combined small amounts of simulation data with physics constraints to achieve engineering-acceptable accuracy on neutron diffusion eigenvalue problems, providing systematic performance analysis.

- **PC-GIPMNN** (Physics-Constrained Generalized Inverse Power Method NN): Liu et al. (2023, *Nuclear Science and Techniques*) enforced conservative interface conditions for the neutron flux at material discontinuities, solving $k$-eigenvalue problems with heterogeneous coefficients.

- **R$^2$-PINN**: Zhang et al. (2026, *Nuclear Science and Techniques*) replaced the standard fully connected architecture with a shortcut CNN (S-CNN) and introduced Residual Adaptive Resampling (RAR) for dynamic collocation point placement, improving accuracy for neutron diffusion.

- **Mixed Dual Form PINN**: Do et al. (2025, SSRN preprint) trained networks for both neutron flux and current simultaneously, demonstrating improved performance in heterogeneous media.

- **Multi-Group Decoupling Loss**: Huang et al. (2024, arXiv:2411.15693) introduced a decoupling loss function to handle the ill-conditioned coupling structure of multi-group diffusion, achieving the first neural-network-based solutions for 3D multi-group problems in realistic reactor geometries.

**Limitations of PINNs for neutron diffusion**: convergence is slow when the dominance ratio is high (typical of large reactor cores); accuracy generally falls short of high-order numerical methods; and each new problem instance requires retraining from scratch.

### 3.2 Neural Operators: DeepONet and FNO

Neural operators learn mappings between function spaces, enabling generalization across parameter families without retraining:

- **DeepONet** (Lu et al., 2021, *Nature Machine Intelligence*): Based on the universal approximation theorem for operators (Chen and Chen, 1995), DeepONet uses a branch-trunk architecture. It handles non-uniform meshes and complex geometries naturally.

- **Fourier Neural Operator (FNO)** (Li et al., 2021, ICLR): Parameterizes the integral kernel in Fourier space, achieving strong performance on problems with smooth solutions on regular grids. Kovachki et al. (2021) showed FNO can be viewed as a special case of DeepONet with trigonometric trunk functions.

- **Comparative benchmark**: Lu et al. (2022, *Computer Methods in Applied Mechanics and Engineering*) compared DeepONet and FNO across 16 benchmarks. DeepONet proved more robust to noisy data (FNO error increased 10,000x with 0.1% noise in one test), while FNO excelled on regular domains with strong spectral content.

**Application to reactor physics**: Neural operators have been explored primarily for surrogate modeling of parametric reactor simulations but have not yet been applied to produce benchmark-quality solutions for coupled multi-group diffusion systems.

### 3.3 Summary of AI Methods

| Method | Data Requirement | Mesh | Generalization | Accuracy vs. Classical | Key Reference |
|--------|-----------------|------|---------------|----------------------|---------------|
| **PINN** | Zero (physics only) | Free | Per-instance | Low--moderate | Raissi et al. (2019) |
| **DEPINN** | Small dataset | Free | Per-instance | Moderate | Yang et al. (2023) |
| **FNO** | Large dataset | Uniform grid | Across parameters | Moderate--high | Li et al. (2021) |
| **DeepONet** | Large dataset | Flexible | Across parameters | Moderate--high | Lu et al. (2021) |
| **PI-DeepONet** | Small dataset | Flexible | Across parameters | Moderate | Wang et al. (2021) |

---

## 4. Research Gap and Contribution

The literature reveals a clear gap at the intersection of analytical methods and modern benchmarking needs:

1. **No closed-form 2D two-group solution with inhomogeneous Neumann BCs**: Existing analytical results either treat homogeneous BCs, 1D geometries, or rely on iterative schemes that converge to the solution rather than expressing it directly.

2. **Lack of machine-precision benchmarks for AI4S PDE solvers**: Neural PDE solvers (PINNs, FNO, DeepONet) are typically validated against numerical references (FDM, FEM) that carry their own discretization errors. An analytical solution provides a ground-truth reference with controllable precision.

3. **Eigendecomposition for group decoupling is underexploited**: While eigenvalue decomposition of the group transfer matrix $D^{-1}A$ is a standard technique in reactor physics (Duderstadt and Hamilton, 1976, Ch. 5), its combination with Fourier-cosine expansion to handle inhomogeneous Neumann BCs in 2D has not been documented.

The present work addresses all three gaps by constructing a direct closed-form solution via:
- Fourier-cosine expansion in the $y$-direction (natural for homogeneous Neumann BCs on $y$-boundaries),
- Eigendecomposition of the $2\times 2$ group coupling matrix to decouple the fast and thermal equations,
- Hyperbolic cosine solutions in the $x$-direction for each decoupled mode,
- Fourier coefficient matching at the inhomogeneous left boundary ($x=-0.5$).

This solution serves as an exact benchmark against which FDM, FEM, spectral, and PINN solvers are compared.

---

## References

- Cabral da Silva, A.C. et al. (2023). FEM with Spectral Green's Function for Neutron Diffusion. *TEMA*.
- Chen, T. and Chen, H. (1995). Universal approximation to nonlinear operators. *Mathematics of Control, Signals and Systems*, 8(3):246--257.
- Cho, N.Z. et al. (2016). Sensitivity analysis of Galerkin FEM neutron diffusion solver. *Nuclear Engineering and Technology*, 48(2):402--411.
- Dion, M. and Bhatt, S.M. (2013). Fourier transform methods for 2D lattice diffusion. *Annals of Nuclear Energy*, 62:76--84.
- Do, M.-H. et al. (2025). PINNs for the mixed dual form of the neutron diffusion equation. SSRN preprint.
- Duderstadt, J.J. and Hamilton, L.J. (1976). *Nuclear Reactor Analysis*. Wiley.
- El-Ajou, A. et al. (2019). Analytical solution for multi-energy groups by RPSM. *Mathematics*, 7(7):633.
- Fernandes, H.A., Bodmann, B.E.J., and Vilhena, M.T. Multi-group neutron diffusion using the Parseval identity. ResearchGate/Springer.
- Han, G. (2009). Computational methods for multidimensional neutron diffusion problems. *Science and Technology of Nuclear Installations*.
- Huang, Y. et al. (2024). Decoupling residual loss function for multi-group neutron diffusion. arXiv:2411.15693.
- Lamarsh, J.R. (1966). *Introduction to Nuclear Engineering*. Addison-Wesley.
- Lemos, R.S. et al. (2008). Analytical solution for two-group diffusion via Laplace Transform. *Annals of Nuclear Energy*, 35(2):169--176.
- Li, Z. et al. (2021). Fourier Neural Operator for parametric PDEs. ICLR 2021.
- Liu, X. et al. (2023). Physics-constrained NN for discontinuous interface K-eigenvalue. *Nuclear Science and Techniques*, 34:163.
- Lozano, J.A. et al. (2008). The ANDES analytic nodal diffusion solver. *Annals of Nuclear Energy*, 35(12):2365--2374.
- Lu, L. et al. (2021). Learning nonlinear operators via DeepONet. *Nature Machine Intelligence*, 3:218--229.
- Lu, L. et al. (2022). Comprehensive comparison of DeepONet and FNO. *Computer Methods in Applied Mechanics and Engineering*, 393:114778.
- Raissi, M., Perdikaris, P., and Karniadakis, G.E. (2019). Physics-informed neural networks. *Journal of Computational Physics*, 378:686--707.
- Smith, K.S. (1983). Nodal method storage reduction by nonlinear iteration. *Transactions of the American Nuclear Society*, 44.
- Stacey, W.M. (2007). *Nuclear Reactor Physics* (2nd ed.). Wiley.
- Wang, S. et al. (2021). Learning the solution operator of parametric PDEs with physics-informed DeepONets. *Science Advances*, 7(40).
- Yang, Y. et al. (2023). DEPINN for neutron diffusion eigenvalue problems. *Annals of Nuclear Energy*, 183:109656.
- Zanette, R. et al. (2018). Modified power method for 2D multigroup neutron diffusion. *Annals of Nuclear Energy*, 111:136--145.
- Zanette, R. et al. (2021). Modified power method with Fourier sine transform. *Brazilian Journal of Radiation Sciences*, 9(1).
- Zhang, Y. et al. (2026). R$^2$-PINN for neutron diffusion equations. *Nuclear Science and Techniques*.
