# Introduction (Draft)

## 1. Reactor Physics Context and Challenge

Accurate prediction of neutron flux distributions is fundamental to nuclear reactor design, safety analysis, and operational optimization. The spatial and energetic behavior of neutrons in a reactor core is governed by the Boltzmann transport equation, a seven-dimensional integro-differential equation whose direct solution remains computationally prohibitive for routine engineering analysis (Duderstadt and Hamilton, 1976; Stacey, 2007). The multi-group diffusion approximation---obtained by discretizing the energy variable into $G$ groups and invoking Fick's law for the angular dependence---reduces the problem to a system of $G$ coupled elliptic partial differential equations that retain the essential physics while becoming amenable to both analytical and numerical treatment (Lamarsh, 1966).

The two-group model, which distinguishes fast and thermal neutrons, captures the dominant physical mechanisms in thermal reactors: fast fission, slowing-down via scattering, and thermal absorption and fission. Despite more than six decades of study, closed-form analytical solutions to the two-group diffusion system remain confined to one-dimensional slab geometries and simple boundary conditions. The standard approach in both research and production codes relies on numerical discretization---finite difference, finite element, or nodal methods---which introduces mesh-dependent truncation errors that can obscure the accuracy assessment of other computational approaches (Han, 2009).

This limitation has become increasingly consequential as data-driven PDE solvers---physics-informed neural networks (PINNs), Fourier neural operators (FNO), and Deep Operator Networks (DeepONet)---enter the reactor physics arena (Yang et al., 2023; Huang et al., 2024; Zhang et al., 2026). Validating these methods requires reference solutions of known, controllable accuracy. Numerical benchmarks, however capable, always carry discretization artifacts, making it difficult to distinguish solver error from reference error. An analytical solution, exact up to floating-point arithmetic, eliminates this confound entirely.

## 2. Our Contribution: Analytical Closed-Form Solution

We present a closed-form analytical solution to the two-dimensional, two-group steady-state neutron diffusion equation on a rectangular domain $[-0.5, 0.5]^2$ with inhomogeneous Neumann boundary conditions. The left boundary prescribes a spatially varying incoming current ($-D_g\,\partial\phi_g/\partial x = y$), while the remaining three boundaries impose zero normal current (homogeneous Neumann). This configuration models a reactor face receiving an asymmetric external neutron source---a physically motivated and mathematically non-trivial boundary value problem.

The solution is constructed without iteration, linearization, or discretization. It is expressed as a Fourier-cosine series whose coefficients are determined in closed form through a sequence of exact algebraic operations. The resulting expressions for the fast and thermal fluxes $\phi_1(x,y)$ and $\phi_2(x,y)$ can be evaluated at arbitrary spatial points to any desired floating-point precision by including sufficiently many Fourier terms.

## 3. The Fourier-Cosine and Eigendecomposition Method

The analytical construction proceeds in four steps. First, the flux vector $\boldsymbol{\phi} = (\phi_1, \phi_2)^T$ is expanded in a Fourier-cosine series in the $y$-variable, whose basis functions $\cos(n\pi(y+0.5))$ automatically satisfy the homogeneous Neumann conditions on the top and bottom boundaries. This expansion converts the coupled 2D PDE system into a parametric family of coupled 1D ODE systems indexed by the Fourier mode number $n$.

Second, for each mode $n$, the $2\times 2$ group-coupling matrix $\mathbf{M}_n = \mathbf{D}^{-1}\mathbf{A} + (n\pi)^2\mathbf{I}$ is diagonalized by eigendecomposition, decoupling the fast and thermal equations into independent scalar ODEs. This step exploits the fact that the inter-group coupling---mediated by fission and scattering cross-sections---has a fixed linear structure that is diagonalizable for all physical parameter combinations.

Third, each decoupled ODE admits a hyperbolic cosine solution $\cosh(\sqrt{\lambda}\,(x - 0.5))$ that satisfies the homogeneous Neumann condition at the right boundary by construction. The remaining free coefficients are determined algebraically by matching the Fourier projection of the inhomogeneous left boundary condition.

Fourth, the physical flux is reconstructed by applying the inverse eigenvector transformation and summing the Fourier series. The exponential convergence of the cosine expansion for smooth solutions ensures that $N = 50$--$500$ terms suffice for residuals at or below machine epsilon ($\sim 10^{-15}$).

## 4. Validation and Benchmarking

We validate the analytical solution by computing PDE residuals and boundary condition residuals on dense evaluation grids, demonstrating that the method achieves machine-precision accuracy with modest computational cost. We then deploy the analytical solution as a benchmark to evaluate four representative numerical and data-driven solvers: a second-order finite difference method (FDM) on a $101\times 101$ grid, a finite element method (FEM) with linear triangular elements, a Chebyshev spectral collocation method, and a physics-informed neural network (PINN). The comparison reveals the convergence characteristics and practical accuracy limits of each approach, providing the first rigorous, analytically grounded benchmark for coupled multi-group neutron diffusion solvers.

## 5. Related Work

Analytical solutions for multi-group neutron diffusion have been developed primarily in one spatial dimension. Lemos et al. (2008) applied the Laplace Transform to two-group problems in multilayered slabs. Zanette et al. (2018, 2021) combined modified power iteration with Finite Fourier Transforms for multigroup eigenvalue problems in 1D and 2D Cartesian geometries, though their approach yields the solution as the limit of an iterative sequence rather than in closed form. Fernandes et al. used the Parseval identity for analytical solutions in rectangular 2D geometry but focused on the criticality eigenvalue rather than boundary-driven source problems. El-Ajou et al. (2019) applied the Residual Power Series Method to multi-group diffusion in various geometries without spatial discretization.

On the numerical side, finite element methods for neutron diffusion are well established (Cho et al., 2016), and nodal methods with analytical basis functions (ANDES; Lozano et al., 2008) achieve high accuracy on coarse meshes. The application of PINNs to neutron diffusion has accelerated since 2022, with contributions addressing eigenvalue problems (Yang et al., 2023), material interface conditions (Liu et al., 2023), multi-group decoupling (Huang et al., 2024), and improved architectures (Zhang et al., 2026). Neural operators (FNO: Li et al., 2021; DeepONet: Lu et al., 2021) have been benchmarked extensively against each other (Lu et al., 2022) but not yet against analytical multi-group diffusion solutions.

The Helmholtz equation---the scalar analogue of the diffusion equation---admits well-known cosine-eigenfunction solutions on rectangular domains with Neumann boundary conditions (cf. Ihlenburg, 1998). Our method generalizes this classical construction to the coupled multi-group setting through eigendecomposition of the group-coupling matrix, a step that has no precedent in the analytical neutron diffusion literature.

## 6. Contributions

The principal contributions of this work are:

- **Closed-form analytical solution**: We derive the first non-iterative, closed-form solution to the 2D two-group neutron diffusion equation with inhomogeneous Neumann boundary conditions, expressed as a Fourier-cosine series with algebraically determined coefficients.

- **Machine-precision benchmark**: The analytical solution achieves PDE residuals at the level of floating-point roundoff ($\sim 10^{-15}$), providing an exact reference for validating numerical and data-driven PDE solvers in the multi-group diffusion setting.

- **Systematic solver comparison**: We benchmark FDM, FEM, spectral collocation, and PINN solvers against the analytical reference, quantifying their convergence rates, accuracy limits, and computational costs in a unified framework.

- **Eigendecomposition decoupling technique**: We demonstrate that eigendecomposition of the diffusion-weighted coupling matrix $\mathbf{D}^{-1}\mathbf{A}$ combined with Fourier expansion provides a general strategy for constructing analytical solutions to coupled elliptic PDE systems with compatible boundary conditions, applicable beyond the specific reactor physics context.
