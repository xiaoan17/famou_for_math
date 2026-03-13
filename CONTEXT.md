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
| `baselines/fdm/fdm_solver.py` | ✅ Complete | FDM 101×101, sparse solve |
| `baselines/fem/` | ❌ Empty | To implement |
| `baselines/spectral/` | ❌ Empty | To implement |
| `baselines/pinn/` | ❌ Empty | To implement |

## Current Results
| Method | Max PDE Residual | Max BC Residual | Time (s) | Status |
|--------|-----------------|-----------------|----------|--------|
| Analytical | TBD | TBD | TBD | needs run |
| FDM 101×101 | TBD | TBD | TBD | needs run |
| FEM | TBD | TBD | TBD | not impl |
| Spectral | TBD | TBD | TBD | not impl |
| PINN | TBD | TBD | TBD | not impl |

## Team Status
| Agent | Status | Current Task |
|-------|--------|--------------|
| Team Lead (you) | Active | Orchestrating |
| Background Researcher | Spawning | Literature survey |
| Experiment Runner | Spawning | Run solvers |
| Paper Writer | Pending | Awaiting results |
| Strict Reviewer | Pending | Awaiting draft |

## Key Milestones
- [ ] All solvers run + results.json saved
- [ ] Comparison table complete
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
- `base` environment (default), Python 3.x
- Dependencies: numpy, scipy, matplotlib available

## Important Notes
- No GPU required — all solvers CPU-based
- Analytical solution uses N_terms=50–500 Fourier modes
- FDM uses 101×101 sparse grid (scipy)
- Paper: NeurIPS LaTeX template
