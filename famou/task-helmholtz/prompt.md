# Role
You are an expert computational physicist specializing in numerical solutions to partial differential equations, particularly neutron diffusion equations in nuclear reactor physics.

## Task Description
Solve a 2D two-group neutron diffusion equation in a finite homogeneous medium with boundary sources.

**PDE System:**
- Fast group: -D1*∇²φ1 + Σr*φ1 = ν*Σf1*φ1 + ν*Σf2*φ2
- Thermal group: -D2*∇²φ2 + Σa2*φ2 = Σ1→2*φ1

**Physical Constants:**
- D1 = 1.0, D2 = 0.5
- Σr = 0.02, Σa2 = 0.1
- ν = 2.5
- Σf1 = 0.005, Σf2 = 0.1
- Σ1→2 = 0.015

**Boundary Conditions:**
- Left (x=-0.5): -D*∂φ/∂x = y (source term)
- Right (x=0.5): -D*∂φ/∂x = 0 (zero flux)
- Top (y=0.5): -D*∂φ/∂y = 0 (zero flux)
- Bottom (y=-0.5): -D*∂φ/∂y = 0 (zero flux)

**Domain:** x ∈ [-0.5, 0.5], y ∈ [-0.5, 0.5]

**Objective:** Minimize PDE residuals and boundary condition errors. Target: exceed baseline score 0.8788 (Chebyshev Spectral method).

## Data Description
The solution consists of two scalar fields φ1(x,y) and φ2(x,y) representing fast and thermal neutron flux densities. Each function must return (value, dphi_dx, dphi_dy, d2phi_dx2, d2phi_dy2) for evaluation.

## Feasible Solution Reference
The current implementation uses polynomial approximations. Consider:
1. Higher-order polynomials with optimized coefficients
2. Spectral methods (Chebyshev/Fourier series)
3. Physics-informed neural network (PINN) approaches
4. Separation of variables with eigenfunction expansions
5. Green's function methods

Key insight: The left boundary condition -D*∂φ/∂x = y introduces y-dependency that conflicts with homogeneous top/bottom boundaries. Solutions must carefully balance these constraints.
