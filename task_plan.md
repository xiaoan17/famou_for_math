# Task Plan: 2D Two-Group Neutron Diffusion — Full Paper Pipeline

## Goal
Deliver a publication-ready ~16-page PDF paper on analytical + numerical solution of 2D two-group neutron diffusion equations, suitable for a top venue (NeurIPS/ICLR/ICML style).

## Project Summary
- **Physics**: Coupled fast/thermal neutron flux PDEs on [-0.5,0.5]^2 with mixed Neumann BCs
- **Method**: Analytical (Fourier-cosine + eigendecomposition) + numerical comparison
- **Working dir**: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/`
- **Existing code**:
  - `scripts/numerical_solver/analytical_solver.py` — complete analytical solution
  - `baselines/fdm/fdm_solver.py` — FDM baseline (101×101 grid)
  - `baselines/{fem,pinn,spectral}/` — directories exist, no code yet

## Phases

### Phase 1: Background Research + Codebase Assessment [IN PROGRESS]
- [x] Read task description
- [x] Read agent team config
- [x] Audit existing code (analytical_solver.py, fdm_solver.py)
- [ ] Background Researcher: literature survey on AI4S + neutron diffusion solvers
- [ ] Assess what baselines need implementing

### Phase 2: Numerical Experiments
- [ ] Run analytical solver — compute residuals at test points (validation)
- [ ] Run FDM baseline — get results.json
- [ ] Implement FEM baseline (FEniCS or scipy-based)
- [ ] Implement Spectral (Chebyshev) baseline
- [ ] Implement PINN baseline (PyTorch)
- [ ] Generate comparison table (analytical vs FDM vs FEM vs Spectral vs PINN)

### Phase 3: Visualization & Analysis
- [ ] Evaluator: flux field heatmaps (phi1, phi2)
- [ ] Evaluator: convergence curves (error vs grid size / iterations)
- [ ] Evaluator: BC residual comparison across methods
- [ ] Evaluator: computational cost comparison
- [ ] Generate paper_results_registry.json

### Phase 4: Paper Writing
- [ ] Paper Writer: draft Introduction (with research gap)
- [ ] Paper Writer: Method section (analytical derivation in full)
- [ ] Paper Writer: Experiments section
- [ ] Paper Writer: Related Work
- [ ] Paper Writer: Conclusion
- [ ] Assemble LaTeX (NeurIPS template)
- [ ] Compile to PDF

### Phase 5: Review & Iteration
- [ ] Strict Reviewer Round 1 — Reviewer A + B
- [ ] Paper Writer: revisions
- [ ] Strict Reviewer Round 2 — must both Accept
- [ ] Final PDF delivery

## Key Decisions Made
- **Analytical method**: Fourier-cosine expansion in y + eigendecomposition decoupling (implemented)
- **Baselines**: FDM (done), FEM, Spectral, PINN (to implement)
- **Paper venue**: NeurIPS-style (use NeurIPS LaTeX template)
- **Paper length**: ~16 pages
- **No GPU needed**: all solvers are CPU-based (pure math/scipy)

## Status
**Currently in Phase 1** — Team Lead assessing codebase, about to spawn team

## CONTEXT.md path
`/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/CONTEXT.md`
