# CONTEXT.md — 2D Two-Group Neutron Diffusion Paper Project

## Project Overview
- **Title (draft)**: *Analytical and Numerical Solution of 2D Two-Group Neutron Diffusion Equations with Inhomogeneous Neumann Boundary Conditions*
- **Date**: 2026-03-13
- **Working directory**: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/`
- **Target**: ~16-page publication-ready paper (NeurIPS style), PDF delivery

## Physics Problem
- **PDE system**: Coupled 2-group neutron diffusion (fast + thermal) on [-0.5,0.5]^2
- **BCs**: Non-zero Neumann at x=-0.5 (`-D∂φ/∂x = y`), zero Neumann on 3 other sides
- **Parameters**: D1=1.0, D2=0.5, Σ_r=0.02, Σ_a2=0.1, ν=2.5, Σ_f1=0.005, Σ_f2=0.1, Σ_12=0.015
- **Task ID**: Analytical Solution Helmholtz

## Existing Code Assets
| File | Status | Description |
|------|--------|-------------|
| `scripts/numerical_solver/analytical_solver.py` | ✅ Complete | Fourier-cosine + eigendecomposition analytical solution |
| `scripts/numerical_solver/run_analytical.py` | ✅ Complete | Runner script, saves analytical_results.json |
| `baselines/fdm/fdm_solver.py` | ✅ Complete | FDM 101×101, sparse solve |
| `baselines/fdm/run_convergence.py` | ✅ Complete | FDM convergence study (N=21,51,101,201) |
| `baselines/fem/fem_solver.py` | ✅ Complete | Bilinear Q1 Galerkin FEM, sparse solve |
| `baselines/spectral/spectral_solver.py` | ✅ Complete | Chebyshev spectral collocation N=30 |
| `baselines/pinn/pinn_solver.py` | ✅ Complete | PINN 2-64-64-64-2 MLP, PyTorch |

## Current Results
| Method | Max PDE Residual | Max BC Residual | Time (s) | Status |
|--------|-----------------|-----------------|----------|--------|
| Analytical (N=200) | 2.81e-16 | 5.03e-07 | 0.017 | DONE |
| FDM 101×101 | 9.07e-05 | 3.97e-04 | 0.134 | DONE |
| FEM 101×101 (Q1) | 9.20e-07 | 4.05e-04 | 0.824 | DONE |
| Spectral N=30 | 7.23e-06 | 6.04e-05 | 0.079 | DONE |
| PINN (3×64 MLP) | 9.54e-03 | 9.13e-03 | 98.624 | DONE |

## Famou Experiment
- **Experiment ID**: exp-20260313202324-i5445e
- **Name**: neutron_t1_r1
- **Status**: CREATED → evolving
- **Task dir**: `famou/task1/`
- **Seed score**: validity=1.0, combined_score=0.071 (FDM 101×101)
- **Target**: combined_score > 0.95
- **Monitor**: `famou-ctl experiment status exp-20260313202324-i5445e --api-url https://pro-service.famou.com --json`

## Team Status
| Agent | Status | Current Task |
|-------|--------|--------------|
| Team Lead | Active | Orchestrating |
| Background Researcher | Done | Literature survey complete |
| Experiment Runner | Done | All 5 solvers run |
| Git & Doc Manager | Active | Commits & GitHub push |
| Paper Writer | Pending | Awaiting Famou results |
| Strict Reviewer | Pending | Awaiting draft |

## Key Milestones
- [x] All solvers run + results.json saved
- [x] Comparison table complete
- [ ] Figures generated (flux fields, convergence, BC residuals)
- [ ] Paper draft v1 complete
- [ ] Review Round 1 complete
- [ ] Review Round 2 complete (both Accept)
- [ ] PDF compiled and delivered

## Research Background

### Key References
- **Foundational textbooks**: Duderstadt & Hamilton (1976) *Nuclear Reactor Analysis*; Stacey (2007) *Nuclear Reactor Physics*; Lamarsh (1966) *Introduction to Nuclear Engineering*
- **1D analytical solutions**: Lemos et al. (2008) Laplace Transform for two-group slab; Zanette et al. (2018, 2021) modified power method + Fourier sine transform for multigroup 1D/2D eigenvalue problems
- **2D analytical methods**: Fernandes et al. (Parseval identity, rectangular 2D); El-Ajou et al. (2019) RPSM for multi-group in various geometries; Dion & Bhatt (2013) Fourier expansion for lattice cells
- **Nodal/semi-analytical**: ANDES solver (Lozano et al., 2008) with ACMFD method; Smith (1983) nodal methods
- **PINNs for neutron diffusion**: Yang et al. (2023) DEPINN; Liu et al. (2023) PC-GIPMNN; Huang et al. (2024) multi-group decoupling loss; Zhang et al. (2026) R2-PINN; Do et al. (2025) mixed dual form
- **Neural operators**: Raissi et al. (2019) PINNs foundational paper; Li et al. (2021) FNO; Lu et al. (2021) DeepONet; Lu et al. (2022) comprehensive FNO vs DeepONet comparison
- **Helmholtz/spectral**: Cosine eigenfunctions for Neumann BCs on rectangular domains (classical); SGF method (Cabral da Silva et al., 2023)

### Research Gap
No closed-form (non-iterative) analytical solution exists for the **2D coupled two-group neutron diffusion equation with inhomogeneous Neumann boundary conditions**. Existing analytical work is limited to 1D slabs, homogeneous BCs, or iterative power-method schemes. AI4S solvers (PINNs, FNO, DeepONet) lack exact multi-group diffusion benchmarks---they are validated only against numerical references carrying discretization error.

### Technical Approach Summary
**Fourier-cosine expansion in y** (satisfies homogeneous Neumann on top/bottom) + **eigendecomposition of D^{-1}A** (decouples fast/thermal groups) + **cosh(x) solutions** (satisfies right Neumann BC) + **algebraic coefficient matching at left BC** (inhomogeneous Neumann). Non-iterative, yields machine-precision residuals with N=50-500 Fourier terms.

### Output Files
- `literature-review.md` — Full structured survey with method comparison matrix
- `methodology-background.md` — Technical background on Fourier-eigendecomposition derivation
- `introduction-draft.md` — Introduction section draft (~2 pages, academic style)

## GitHub Repository
- **Remote**: `git@github.com:xiaoan17/famou_for_math.git`
- **Branch**: `main`
- **Scope**: ONLY push contents of `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/`
- **Push command**: `git push -u origin main` (from inside the working dir)
- **Initial commit done**: ✅ 4caad5c

## conda environment
- `ml_env` environment for all solvers (scipy, PyTorch available)
- Run command: `conda run -n ml_env python <script>`
- Dependencies: numpy, scipy, matplotlib, torch available

## Important Notes
- No GPU required — all solvers CPU-based
- Analytical solution uses N_terms=50–500 Fourier modes
- FDM uses 101×101 sparse grid (scipy)
- Paper: NeurIPS LaTeX template
