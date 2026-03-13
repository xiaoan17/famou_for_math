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
(To be filled by Background Researcher)

## conda environment
- `base` environment (default), Python 3.x
- Dependencies: numpy, scipy, matplotlib available

## Important Notes
- No GPU required — all solvers CPU-based
- Analytical solution uses N_terms=50–500 Fourier modes
- FDM uses 101×101 sparse grid (scipy)
- Paper: NeurIPS LaTeX template
