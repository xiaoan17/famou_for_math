"""
Figure 5: Flux profiles — line plots of phi1 along x-slice (y=0) and y-slice (x=0).
Compares Analytical, FDM, Spectral.
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts" / "numerical_solver"))
sys.path.insert(0, str(PROJECT / "baselines" / "fdm"))
sys.path.insert(0, str(PROJECT / "baselines" / "spectral"))

from analytical_solver import evaluate_flux
from fdm_solver import solve_fdm

FIGS = PROJECT / "paper" / "figs"


def main():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })

    N_pts = 200
    x_line = np.linspace(-0.5, 0.5, N_pts)
    y_line = np.linspace(-0.5, 0.5, N_pts)

    # --- Analytical ---
    # x-slice at y=0
    phi1_ana_x, phi2_ana_x = evaluate_flux(x_line, np.zeros(N_pts), N_terms=200)
    # y-slice at x=0
    phi1_ana_y, phi2_ana_y = evaluate_flux(np.zeros(N_pts), y_line, N_terms=200)

    # --- FDM ---
    print("Computing FDM solution...")
    fdm = solve_fdm(Nx=101, Ny=101)
    from scipy.interpolate import RegularGridInterpolator
    interp1_fdm = RegularGridInterpolator(
        (fdm["x"], fdm["y"]), fdm["phi1"], method="cubic"
    )
    interp2_fdm = RegularGridInterpolator(
        (fdm["x"], fdm["y"]), fdm["phi2"], method="cubic"
    )
    pts_x = np.column_stack([x_line, np.zeros(N_pts)])
    pts_y = np.column_stack([np.zeros(N_pts), y_line])
    phi1_fdm_x = interp1_fdm(pts_x)
    phi1_fdm_y = interp1_fdm(pts_y)

    # --- Spectral ---
    # Import and run spectral solver
    from spectral_solver import solve_spectral
    print("Computing Spectral solution...")
    spec = solve_spectral(N=30)
    # Spectral returns on Chebyshev nodes; interpolate
    interp1_spec = RegularGridInterpolator(
        (spec["x"], spec["y"]), spec["phi1"], method="cubic",
        bounds_error=False, fill_value=None
    )
    phi1_spec_x = interp1_spec(pts_x)
    phi1_spec_y = interp1_spec(pts_y)

    colors = plt.cm.tab10.colors
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: x-slice at y=0
    ax = axes[0]
    ax.plot(x_line, phi1_ana_x, "-", color=colors[0], linewidth=1.8, label="Analytical")
    ax.plot(x_line, phi1_fdm_x, "--", color=colors[1], linewidth=1.5, label="FDM")
    ax.plot(x_line, phi1_spec_x, ":", color=colors[2], linewidth=1.5, label="Spectral")
    ax.set_xlabel("$x$", fontsize=11)
    ax.set_ylabel(r"$\phi_1(x, 0)$", fontsize=11)
    ax.set_title(r"$\phi_1$ along $y=0$", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, linewidth=0.3, alpha=0.5)

    # Right: y-slice at x=0
    ax = axes[1]
    ax.plot(y_line, phi1_ana_y, "-", color=colors[0], linewidth=1.8, label="Analytical")
    ax.plot(y_line, phi1_fdm_y, "--", color=colors[1], linewidth=1.5, label="FDM")
    ax.plot(y_line, phi1_spec_y, ":", color=colors[2], linewidth=1.5, label="Spectral")
    ax.set_xlabel("$y$", fontsize=11)
    ax.set_ylabel(r"$\phi_1(0, y)$", fontsize=11)
    ax.set_title(r"$\phi_1$ along $x=0$", fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(True, linewidth=0.3, alpha=0.5)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = FIGS / f"flux_profiles.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out} ({out.stat().st_size} bytes)")
    plt.close(fig)


if __name__ == "__main__":
    main()
