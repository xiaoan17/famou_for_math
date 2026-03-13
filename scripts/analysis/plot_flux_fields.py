"""
Figure 1: Flux fields — 2x2 subplot with analytical phi1, phi2, FDM phi1, and error.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Add solver path
PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts" / "numerical_solver"))
sys.path.insert(0, str(PROJECT / "baselines" / "fdm"))

from analytical_solver import evaluate_flux
from fdm_solver import solve_fdm

FIGS = PROJECT / "paper" / "figs"


def main():
    # Publication style
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })

    N_grid = 100
    x1d = np.linspace(-0.5, 0.5, N_grid)
    y1d = np.linspace(-0.5, 0.5, N_grid)
    X, Y = np.meshgrid(x1d, y1d, indexing="ij")
    xf = X.ravel()
    yf = Y.ravel()

    # Analytical on 100x100
    print("Computing analytical solution on 100x100 grid...")
    phi1_ana, phi2_ana = evaluate_flux(xf, yf, N_terms=200)
    PHI1_ANA = phi1_ana.reshape(N_grid, N_grid)
    PHI2_ANA = phi2_ana.reshape(N_grid, N_grid)

    # FDM 101x101 then interpolate to same grid
    print("Computing FDM solution on 101x101 grid...")
    fdm = solve_fdm(Nx=101, Ny=101)
    from scipy.interpolate import RegularGridInterpolator
    interp1 = RegularGridInterpolator(
        (fdm["x"], fdm["y"]), fdm["phi1"], method="cubic"
    )
    pts = np.column_stack([xf, yf])
    PHI1_FDM = interp1(pts).reshape(N_grid, N_grid)

    # Error
    ERROR = np.abs(PHI1_ANA - PHI1_FDM)

    fig, axes = plt.subplots(2, 2, figsize=(9, 7.5))

    # Top-left: phi1 analytical
    im0 = axes[0, 0].pcolormesh(
        x1d, y1d, PHI1_ANA.T, cmap="viridis", shading="auto"
    )
    axes[0, 0].set_title(r"$\phi_1(x,y)$ — Analytical", fontsize=11)
    axes[0, 0].set_xlabel("$x$")
    axes[0, 0].set_ylabel("$y$")
    fig.colorbar(im0, ax=axes[0, 0], shrink=0.85)

    # Top-right: phi2 analytical
    im1 = axes[0, 1].pcolormesh(
        x1d, y1d, PHI2_ANA.T, cmap="viridis", shading="auto"
    )
    axes[0, 1].set_title(r"$\phi_2(x,y)$ — Analytical", fontsize=11)
    axes[0, 1].set_xlabel("$x$")
    axes[0, 1].set_ylabel("$y$")
    fig.colorbar(im1, ax=axes[0, 1], shrink=0.85)

    # Bottom-left: phi1 FDM
    im2 = axes[1, 0].pcolormesh(
        x1d, y1d, PHI1_FDM.T, cmap="viridis", shading="auto"
    )
    axes[1, 0].set_title(r"$\phi_1(x,y)$ — FDM (101$\times$101)", fontsize=11)
    axes[1, 0].set_xlabel("$x$")
    axes[1, 0].set_ylabel("$y$")
    fig.colorbar(im2, ax=axes[1, 0], shrink=0.85)

    # Bottom-right: error
    im3 = axes[1, 1].pcolormesh(
        x1d, y1d, ERROR.T, cmap="hot_r", shading="auto"
    )
    axes[1, 1].set_title(
        r"$|\phi_1^{\mathrm{ana}} - \phi_1^{\mathrm{FDM}}|$", fontsize=11
    )
    axes[1, 1].set_xlabel("$x$")
    axes[1, 1].set_ylabel("$y$")
    fig.colorbar(im3, ax=axes[1, 1], shrink=0.85, format="%.1e")

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = FIGS / f"flux_fields.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out} ({out.stat().st_size} bytes)")
    plt.close(fig)


if __name__ == "__main__":
    main()
