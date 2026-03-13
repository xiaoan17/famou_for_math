# Methodology Background: Fourier-Eigendecomposition for 2D Two-Group Neutron Diffusion

## 1. Problem Statement

Consider the steady-state two-group neutron diffusion system on the square domain $\Omega = [-0.5, 0.5]^2$:

$$-D_1 \nabla^2 \phi_1 + \Sigma_{r,1}\,\phi_1 = \nu\Sigma_{f,1}\,\phi_1 + \nu\Sigma_{f,2}\,\phi_2$$
$$-D_2 \nabla^2 \phi_2 + \Sigma_{a,2}\,\phi_2 = \Sigma_{1\to 2}\,\phi_1$$

where $\phi_1(x,y)$ and $\phi_2(x,y)$ are the fast and thermal neutron fluxes, respectively.

**Boundary conditions**:
- Left ($x = -0.5$): Inhomogeneous Neumann: $-D_g \frac{\partial \phi_g}{\partial x} = y$ for $g=1,2$
- Right ($x = 0.5$): Homogeneous Neumann: $\frac{\partial \phi_g}{\partial x} = 0$
- Bottom ($y = -0.5$): Homogeneous Neumann: $\frac{\partial \phi_g}{\partial y} = 0$
- Top ($y = 0.5$): Homogeneous Neumann: $\frac{\partial \phi_g}{\partial y} = 0$

**Physical parameters**: $D_1 = 1.0$, $D_2 = 0.5$, $\Sigma_{r,1} = 0.02$, $\Sigma_{a,2} = 0.1$, $\nu = 2.5$, $\Sigma_{f,1} = 0.005$, $\Sigma_{f,2} = 0.1$, $\Sigma_{1\to 2} = 0.015$.

## 2. Matrix Formulation

The system can be written compactly in matrix form. Define $\boldsymbol{\phi} = (\phi_1, \phi_2)^T$ and the matrices:

$$\mathbf{D} = \begin{pmatrix} D_1 & 0 \\ 0 & D_2 \end{pmatrix}, \quad \mathbf{A} = \begin{pmatrix} \Sigma_{r,1} - \nu\Sigma_{f,1} & -\nu\Sigma_{f,2} \\ -\Sigma_{1\to 2} & \Sigma_{a,2} \end{pmatrix}$$

The system becomes:

$$-\mathbf{D}\,\nabla^2 \boldsymbol{\phi} + \mathbf{A}\,\boldsymbol{\phi} = \mathbf{0}$$

or equivalently:

$$\nabla^2 \boldsymbol{\phi} = \mathbf{D}^{-1}\mathbf{A}\,\boldsymbol{\phi} \equiv \mathbf{M}\,\boldsymbol{\phi}$$

where $\mathbf{M} = \mathbf{D}^{-1}\mathbf{A}$ is the $2\times 2$ coupling matrix.

## 3. Fourier-Cosine Expansion in $y$

### 3.1 Why Cosine?

The three boundaries with homogeneous Neumann conditions ($\partial\phi/\partial n = 0$) on the top, bottom, and right sides suggest expanding in eigenfunctions of the Laplacian that naturally satisfy zero normal derivative. On the interval $[-0.5, 0.5]$ with homogeneous Neumann BCs at both endpoints, the complete orthogonal set is:

$$Y_n(y) = \cos\bigl(n\pi(y + 0.5)\bigr), \quad n = 0, 1, 2, \dots$$

These satisfy $Y_n'(-0.5) = Y_n'(0.5) = 0$ and form an orthogonal basis on $L^2([-0.5, 0.5])$.

### 3.2 Expansion

Expand the flux vector in this basis:

$$\boldsymbol{\phi}(x,y) = \sum_{n=0}^{\infty} \boldsymbol{\hat{\phi}}_n(x)\,Y_n(y)$$

where $\boldsymbol{\hat{\phi}}_n(x) = (\hat{\phi}_{1,n}(x), \hat{\phi}_{2,n}(x))^T$ are the Fourier coefficient vectors.

Substituting into $\nabla^2 \boldsymbol{\phi} = \mathbf{M}\,\boldsymbol{\phi}$ and using $Y_n''(y) = -(n\pi)^2 Y_n(y)$:

$$\boldsymbol{\hat{\phi}}_n''(x) - (n\pi)^2 \boldsymbol{\hat{\phi}}_n(x) = \mathbf{M}\,\boldsymbol{\hat{\phi}}_n(x)$$

$$\boldsymbol{\hat{\phi}}_n''(x) = \bigl(\mathbf{M} + (n\pi)^2 \mathbf{I}\bigr)\,\boldsymbol{\hat{\phi}}_n(x)$$

This reduces the 2D PDE system to a family of 1D ODE systems (one per Fourier mode $n$).

### 3.3 Fourier Coefficients of the Boundary Data

The inhomogeneous Neumann BC at $x=-0.5$ is $-D_g \partial\phi_g/\partial x = y$. Expanding $y$ in the cosine basis:

$$y = \sum_{n=0}^{\infty} c_n\,Y_n(y)$$

The coefficients $c_n$ are computed by the standard inner product:

$$c_n = \frac{\langle y, Y_n \rangle}{\langle Y_n, Y_n \rangle} = \frac{\int_{-0.5}^{0.5} y\,\cos(n\pi(y+0.5))\,dy}{\int_{-0.5}^{0.5} \cos^2(n\pi(y+0.5))\,dy}$$

The function $y$ is neither even nor odd about $y=0$ in the shifted coordinate $\xi = y+0.5 \in [0,1]$, so both even and odd $n$ contribute.

## 4. Eigendecomposition for Group Decoupling

### 4.1 The Key Step

For each Fourier mode $n$, define $\mathbf{M}_n = \mathbf{M} + (n\pi)^2 \mathbf{I}$. The ODE system is:

$$\boldsymbol{\hat{\phi}}_n''(x) = \mathbf{M}_n\,\boldsymbol{\hat{\phi}}_n(x)$$

This is a coupled system of two second-order ODEs. Eigendecomposition decouples it.

### 4.2 Diagonalization

Compute the eigenvalues $\lambda_1^{(n)}, \lambda_2^{(n)}$ and eigenvectors $\mathbf{v}_1^{(n)}, \mathbf{v}_2^{(n)}$ of $\mathbf{M}_n$:

$$\mathbf{M}_n = \mathbf{P}_n\,\boldsymbol{\Lambda}_n\,\mathbf{P}_n^{-1}$$

where $\boldsymbol{\Lambda}_n = \text{diag}(\lambda_1^{(n)}, \lambda_2^{(n)})$ and $\mathbf{P}_n = [\mathbf{v}_1^{(n)} \mid \mathbf{v}_2^{(n)}]$.

### 4.3 Decoupled Scalar ODEs

Define $\boldsymbol{\psi}_n(x) = \mathbf{P}_n^{-1}\,\boldsymbol{\hat{\phi}}_n(x)$. Then:

$$\psi_{k,n}''(x) = \lambda_k^{(n)}\,\psi_{k,n}(x), \quad k = 1, 2$$

These are independent second-order ODEs with constant coefficients.

### 4.4 Why Eigendecomposition Works

The coupling between energy groups in the neutron diffusion equation arises through fission and scattering cross-sections. The matrix $\mathbf{M} = \mathbf{D}^{-1}\mathbf{A}$ encodes this coupling. Eigendecomposition rotates the flux vector into a coordinate system aligned with the natural modes of the coupled system---analogous to normal modes in coupled oscillators. In the rotated coordinates, each mode diffuses independently with its own effective diffusion length, determined by $\lambda_k^{(n)}$.

For the two-group system, $\mathbf{M}_n$ is $2\times 2$ and generically has two distinct real eigenvalues (since the physical cross-sections produce a matrix with real, positive eigenvalues after the shift by $(n\pi)^2$). This guarantees diagonalizability.

## 5. Solution in the $x$-Direction

### 5.1 General Solution

For each eigenvalue $\lambda_k^{(n)} > 0$ (which holds for all physical parameter combinations with the $(n\pi)^2$ shift), the general solution is:

$$\psi_{k,n}(x) = A_{k,n}\,\cosh\bigl(\sqrt{\lambda_k^{(n)}}\,(x - 0.5)\bigr) + B_{k,n}\,\sinh\bigl(\sqrt{\lambda_k^{(n)}}\,(x - 0.5)\bigr)$$

### 5.2 Right Boundary Condition

The homogeneous Neumann condition at $x = 0.5$ requires $\psi_{k,n}'(0.5) = 0$ (after accounting for the eigenvector transformation). This immediately gives $B_{k,n} = 0$, simplifying to:

$$\psi_{k,n}(x) = A_{k,n}\,\cosh\bigl(\sqrt{\lambda_k^{(n)}}\,(x - 0.5)\bigr)$$

The $\cosh$ centered at the right boundary is the natural choice---its derivative vanishes at $x=0.5$ by symmetry of $\cosh$.

### 5.3 Left Boundary Condition (Coefficient Matching)

At $x = -0.5$, the inhomogeneous Neumann BC provides:

$$-\mathbf{D}\,\boldsymbol{\hat{\phi}}_n'(-0.5) = c_n\,\mathbf{e}$$

where $\mathbf{e} = (1, 1)^T$ (both groups receive the same boundary flux $y$, after Fourier projection).

Transforming to the decoupled coordinates and evaluating the $\cosh'$ derivative at $x=-0.5$:

$$A_{k,n} = \frac{(\text{transformed BC coefficient})_k}{-\sqrt{\lambda_k^{(n)}}\,\sinh\bigl(-\sqrt{\lambda_k^{(n)}}\bigr)}$$

This is a direct algebraic expression---no iteration or nonlinear solve is required.

### 5.4 Reconstruction

The physical flux is reconstructed by:

$$\boldsymbol{\hat{\phi}}_n(x) = \mathbf{P}_n\,\boldsymbol{\psi}_n(x)$$

$$\boldsymbol{\phi}(x,y) = \sum_{n=0}^{N} \boldsymbol{\hat{\phi}}_n(x)\,\cos\bigl(n\pi(y+0.5)\bigr)$$

where $N$ is the truncation order. The Fourier-cosine series converges exponentially fast for smooth solutions, so $N = 50$--$500$ typically suffices for machine-precision accuracy.

## 6. Summary of the Method

| Step | Operation | Dimension Reduction |
|------|-----------|-------------------|
| 1. Fourier-cosine expansion in $y$ | $2\text{D PDE} \to$ family of $1\text{D ODE systems}$ | Eliminates $y$-dependence |
| 2. Eigendecomposition of $\mathbf{M}_n$ | Coupled $2\times 2$ ODE $\to$ two scalar ODEs | Decouples energy groups |
| 3. Solve scalar ODEs ($\cosh$ solutions) | Closed-form $x$-dependence | Eliminates $x$-dependence |
| 4. Match coefficients at left BC | Algebraic system for $A_{k,n}$ | Determines all free constants |
| 5. Reconstruct: eigenvectors $\times$ Fourier sum | Assemble the physical flux field | --- |

The entire procedure is non-iterative and yields an analytical expression for $\phi_1(x,y)$ and $\phi_2(x,y)$ as a truncated Fourier series whose coefficients are given in closed form. The only approximation is the truncation of the Fourier series, which converges exponentially.

## 7. Advantages Over Numerical Methods

1. **Machine precision**: The solution is exact up to floating-point evaluation of elementary functions ($\cosh$, $\cos$, eigenvalues). No discretization error.
2. **No mesh dependence**: The solution does not depend on a spatial grid. It can be evaluated at arbitrary $(x,y)$ points.
3. **Benchmark quality**: Provides a ground-truth reference for validating numerical and neural PDE solvers.
4. **Computational efficiency**: For moderate $N$ (50--500 terms), evaluation is $O(N \times N_\text{eval})$ where $N_\text{eval}$ is the number of evaluation points. No large sparse system solve is required.
5. **Physical transparency**: Each Fourier mode and eigenmode has a clear physical interpretation (spatial frequency in $y$; fast/thermal coupling mode).
