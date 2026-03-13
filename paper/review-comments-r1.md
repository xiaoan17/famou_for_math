## Review Round 1 — 2026-03-13

### Reviewer A (Methodology)

- **Decision**: Major Revision

- **Summary**: The paper derives a Fourier-cosine + eigendecomposition analytical solution for the 2D two-group neutron diffusion equation with inhomogeneous Neumann boundary conditions on a square domain, and benchmarks it against FDM, FEM, spectral collocation, and PINN. The derivation is well-structured and the result is valuable as an exact benchmark for AI-for-science PDE solvers. However, there are mathematical errors in the eigenvalue analysis and several methodological gaps that must be addressed before the paper can be accepted.

- **Major Issues**:
  1. **Eigenvalue sign error (critical)**: The paper claims (Section 2, line following Eq. 9) that both eigenvalues of M = D^{-1}A are positive: mu_1 ~ 0.0262 and mu_2 ~ 0.1813. However, direct computation gives det(M) = 0.0075 * 0.2 - (-0.25)(-0.03) = 0.0015 - 0.0075 = -0.006 < 0. Since the determinant of a 2x2 matrix equals the product of its eigenvalues, one eigenvalue must be negative. The correct eigenvalues are approximately mu_1 ~ -0.0258 and mu_2 ~ 0.2333 (from the characteristic equation with tr(M)=0.2075). The stated claim "both are positive and real, confirming that the system is subcritical and well-posed" is incorrect. NOTE: The derivation may still be valid because only odd n >= 1 modes are used, and alpha_{p,n}^2 = mu_p + (n*pi)^2 remains positive for all n >= 1 even with mu_1 < 0 (since pi^2 ~ 9.87 >> 0.026). However, the eigenvalue values stated in the paper are wrong, and the subcriticality argument based on them is invalid. The authors must (a) correct the eigenvalue computation, (b) revise the well-posedness argument to show alpha_{p,n}^2 > 0 for all relevant n, and (c) discuss what happens at n=0 (alpha_{1,0}^2 < 0 would give cos/sin solutions instead of cosh/sinh, but this mode is not needed since b_0 = 0).

  2. **Novelty claim insufficiently supported**: The paper claims "first closed-form analytical solution" multiple times (abstract, contributions, conclusion). While the specific combination (2D, two-group, inhomogeneous Neumann, non-iterative) may indeed be novel, the Related Work does not systematically rule out all prior work. Specifically: (a) The GITT (Generalized Integral Transform Technique) literature is not discussed -- this is a major omission since GITT is the standard Brazilian school approach for exactly this class of problems, and several of the cited authors (Vilhena, Bodmann) are from that school. (b) The Adomian Decomposition Method and Homotopy Perturbation Method have also been applied to multi-group diffusion and should be discussed. (c) The paper should include a comparison table in Related Work explicitly listing what each prior method can and cannot handle (dimensionality, number of groups, BC type, iterative vs closed-form).

  3. **Subcriticality/physics interpretation incomplete**: The paper states the system is "subcritical" based on eigenvalue positivity (which is itself incorrect, see Issue 1). The actual criticality condition involves the effective multiplication factor k_eff, which is not computed or discussed. For the chosen parameters, the system with these BCs is a fixed-source problem (not an eigenvalue/criticality problem), so calling it "subcritical" requires justification. The paper should either (a) compute k_eff for this parameter set and verify subcriticality, or (b) reframe the well-posedness argument without reference to criticality.

  4. **Limitation discussion is superficial**: The Conclusion mentions three future extensions in one paragraph but does not formally discuss limitations. A dedicated Limitations subsection should address: (a) restriction to uniform (homogeneous) medium, (b) restriction to rectangular geometry, (c) restriction to the specific BC pattern (3 homogeneous + 1 inhomogeneous Neumann), (d) computational cost scaling with boundary data complexity (the current f(y)=y has very sparse Fourier coefficients -- what about more complex boundary data?), (e) extension to more than 2 energy groups (does the eigendecomposition generalize?).

  5. **Fair comparison with spectral method questioned**: The spectral method uses only N=30 collocation points. For smooth solutions on regular domains, Chebyshev spectral methods achieve exponential convergence, so increasing N to 50 or 100 should dramatically reduce the residual. The current comparison may understate the spectral method's capability. The authors should include a spectral convergence study analogous to the FDM convergence study, or justify why N=30 is representative.

- **Minor Issues**:
  1. **Abstract number stacking**: The abstract ends with five numerical residual values in one sentence, which is hard to parse. Consider summarizing as "outperforming all numerical methods by 10-13 orders of magnitude in PDE residual" and deferring specific numbers to Section 5.
  2. **Eq. 6 notation**: The left-hand side uses vector notation but the boundary condition Eq. 4 applies to each group independently with the same boundary data. It should be clarified why both groups receive the same inhomogeneous BC (i.e., the physical interpretation of the same incoming current for fast and thermal groups).
  3. **Unit of diffusion coefficient**: Table 1 lists the unit of D_1, D_2 as "cm". The diffusion coefficient has units of length (cm), not cm^{-1}. This is correct but could be confused with the cross-section units; adding a footnote clarifying D = 1/(3*Sigma_tr) and its dimension would help.
  4. **Missing DOF in Table 3**: The main results table lists "20,402 DOF" for FDM and FEM (101^2 * 2), but the comparison table markdown file says "10,201 DOF" (101^2). The LaTeX table uses the correct 2N^2 value, but this inconsistency between source files should be resolved.
  5. **Convergence rate computation**: The convergence rate formula in Section 5.3 uses R_h / R_{h/2} but the grid spacings are not exact factors of 2 (h goes from 0.05 to 0.02 to 0.01 to 0.005). The rate computation should use the actual ratio of grid spacings, not assume factor-of-2 refinement.

- **Required additions**:
  - Correct the eigenvalue computation and revise all statements depending on it
  - Add a Related Work comparison table (Method | Dim | Groups | BC type | Closed-form?)
  - Add a spectral convergence study or justify the single-N comparison
  - Add a dedicated Limitations subsection
  - Discuss the GITT literature and its relation to the proposed method

---

### Reviewer B (Experiments)

- **Decision**: Major Revision

- **Experimental Completeness Score**: 4/10

- **Summary**: The paper presents a clean comparison of five solution methods (analytical, FDM, FEM, spectral, PINN) for a specific 2D two-group neutron diffusion problem, with appropriate figures showing flux fields, profiles, residual distributions, and accuracy-efficiency tradeoffs. However, the experimental section is thin for a paper targeting ~16 pages: it lacks convergence studies for most methods, ablation on the analytical solution's own parameter (N_terms), proper error metrics beyond residuals, and several standard experiments expected in a benchmark paper.

- **Major Issues**:
  1. **Paper is critically short**: At 477 lines of LaTeX (approximately 8-9 pages compiled), the paper falls far short of the ~16-page target. The experimental section (Section 5) is the primary area needing expansion -- currently it occupies roughly 2.5 pages including figures. A benchmark paper of this nature should have at least 5-6 pages of experiments. Sections 1 (Introduction) and 6 (Related Work) could also be expanded.

  2. **No N_terms convergence study for analytical solution**: The paper mentions N=50, 200, 500 in passing (Section 3.7) but does not include a systematic study of how the analytical solution's accuracy depends on N_terms. This is essential for a benchmark paper -- users need to know the convergence rate (algebraic? exponential?) and the cost-accuracy tradeoff for the analytical solution itself. A table and figure showing max PDE residual, max BC residual, and wall time as a function of N_terms (e.g., N=10, 25, 50, 100, 200, 500, 1000) is required.

  3. **PINN baseline is unfairly weak**: The PINN uses only 5,000 Adam iterations with a simple 3x64 architecture. Modern PINN practice typically uses 10,000-50,000 iterations with learning rate scheduling, and often combines Adam with L-BFGS for fine-tuning. The 2,000 interior collocation points may also be insufficient for a coupled system. The paper should either (a) train the PINN to convergence (or near-convergence) so the comparison reflects the method's best achievable accuracy, or (b) include a PINN convergence study showing how residuals decrease with training iterations to demonstrate the PINN has plateaued.

  4. **No pointwise solution comparison**: The paper only evaluates PDE and BC residuals, but never compares the actual flux values phi_g(x,y) between methods. Since the analytical solution provides exact flux values, comparing numerical solution values against the analytical reference at test points (reporting L2 error, L-infinity error, relative error) is the most direct and informative metric. PDE residuals can be misleading -- a solution can have low PDE residual but be shifted by a constant (especially with pure Neumann BCs).

  5. **FDM BC residual anomaly not discussed**: The comparison table shows FDM BC residual INCREASING from 1.78e-4 (51x51) to 3.97e-4 (101x101) to 4.27e-4 (201x201) during grid refinement. This non-monotonic behavior is unexpected for a convergent method and suggests either (a) the BC residual evaluation methodology has a bug, or (b) the one-sided difference stencil at the boundary is not converging. This must be investigated and explained.

  6. **Missing convergence studies for FEM and Spectral**: Only FDM has a convergence study (Table 4 / Fig 1). For a comprehensive benchmark paper, FEM and Spectral should also have convergence studies showing how their residuals decrease with mesh refinement / polynomial degree. This would strengthen the claim that the analytical solution serves as a reliable reference.

  7. **Only 4 interior test points for PDE residual**: Evaluating PDE residuals at only 4 interior points is insufficient and potentially misleading. The maximum residual should be evaluated over a dense grid (e.g., 100x100 evaluation points) to capture the true worst-case error. The current 4-point evaluation could miss regions of high residual. Figure 6 (residual distribution) suggests a dense evaluation was done for the figure -- use the same dense evaluation for the reported numbers.

- **Minor Issues**:
  1. **No error bars or statistical analysis for PINN**: Neural network training is stochastic. The PINN results should report mean and standard deviation over multiple random seeds (at least 3-5 runs).
  2. **Timing comparison is on a single platform**: All timing is on "Apple M-series" without specifying the exact chip (M1/M2/M3). For reproducibility, report exact hardware, NumPy/SciPy/PyTorch versions, and whether BLAS/LAPACK is MKL or Accelerate.
  3. **Figure 5 (flux profiles) lacks error subplot**: The flux profiles appear visually identical for analytical/FDM/FEM/Spectral. Adding a subplot showing the pointwise difference from the analytical solution would make the comparison quantitative rather than qualitative.
  4. **No discussion of spectral method's Runge phenomenon or edge effects**: Section 5.6 mentions "Gibbs-like effect at the edges of the Chebyshev grid" for the spectral residual. This deserves more discussion -- is this a fundamental limitation of spectral collocation for Neumann problems?
  5. **Missing Appendix**: The paper would benefit from an appendix containing (a) the explicit eigenvector matrix P and its inverse, (b) a few representative c_{p,n} coefficients, and (c) the full derivation of the b_n Fourier coefficients. This aids reproducibility.
  6. **Table formatting**: Tables 3 and 4 use `lllll` column alignment; numeric columns should use `S` (siunitx) or `r` alignment for readability.

- **Missing experiments**:
  - N_terms convergence study for the analytical solution (Table + Figure)
  - Pointwise flux comparison: L2 and L-infinity errors of numerical solutions vs. analytical reference
  - FEM convergence study (varying mesh size)
  - Spectral convergence study (varying N)
  - PINN training convergence curve (residual vs. iteration)
  - PINN sensitivity to architecture and hyperparameters (at least 2-3 configurations)
  - Investigation of the FDM BC residual anomaly
  - Dense-grid max residual evaluation (not just 4 points)

---

### Round 1 Verdict

- **Can paper be released?**: NO (Round 2 required regardless)

- **Paper Writer action items** (prioritized):

  1. **[CRITICAL] Fix eigenvalue computation error**: Recompute eigenvalues of M = D^{-1}A. det(M) = -0.006 < 0, so one eigenvalue is negative (~-0.026). Correct all text, verify the derivation still holds for odd n >= 1, and revise the subcriticality/well-posedness argument.

  2. **[CRITICAL] Expand paper to ~16 pages**: The paper is currently ~8-9 pages, far below the ~16-page target. Add: (a) N_terms convergence study for analytical solution, (b) pointwise solution error comparison (L2, L-inf vs. analytical), (c) FEM and Spectral convergence studies, (d) PINN training curve, (e) dedicated Limitations subsection, (f) Related Work comparison table, (g) Appendix with explicit eigenvectors and representative coefficients.

  3. **[HIGH] Add pointwise flux value comparison**: Currently only PDE/BC residuals are reported. Add L2-norm and L-infinity-norm error of numerical solutions compared to the analytical reference. This is the most direct benchmark metric and addresses the pure-Neumann uniqueness concern.

  4. **[HIGH] Strengthen PINN baseline**: Either increase training iterations to 20,000+ with L-BFGS fine-tuning, or include a training convergence curve demonstrating plateau. Report over 3+ random seeds.

  5. **[HIGH] Investigate FDM BC residual non-convergence**: The BC residual increases with grid refinement beyond 51x51 -- this is anomalous. Diagnose whether it is an evaluation artifact or an implementation issue.

  6. **[MEDIUM] Revise abstract to reduce number stacking**: Summarize residual comparison qualitatively in the abstract; defer specific numbers to Section 5.

  7. **[MEDIUM] Add GITT discussion to Related Work**: The Generalized Integral Transform Technique is the most directly relevant prior methodology and is not cited.

  8. **[MEDIUM] Add spectral convergence study**: Show how spectral residual decreases with N to demonstrate the current N=30 comparison is fair.

  9. **[LOW] Expand test point set**: Use dense grid evaluation (100x100) for reported max residuals, not just 4 interior points.

  10. **[LOW] Add error bars for PINN results**: Report mean +/- std over multiple random seeds.
