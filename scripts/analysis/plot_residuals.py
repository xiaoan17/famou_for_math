"""
Figure 2: Grouped bar chart — max PDE residual and max BC residual across methods.
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT = Path(__file__).resolve().parents[2]
FIGS = PROJECT / "paper" / "figs"


def main():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })

    with open(PROJECT / "baselines" / "results" / "summary.json") as f:
        data = json.load(f)

    methods_raw = data["methods"]
    short_names = ["Analytical", "FDM", "FEM", "Spectral", "PINN"]
    pde_res = [m["max_pde_residual"] for m in methods_raw]
    bc_res = [m["max_bc_residual"] for m in methods_raw]

    x = np.arange(len(short_names))
    width = 0.35
    colors = plt.cm.Set1.colors

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars1 = ax.bar(
        x - width / 2, pde_res, width,
        label="Max PDE Residual", color=colors[0], edgecolor="black", linewidth=0.5
    )
    bars2 = ax.bar(
        x + width / 2, bc_res, width,
        label="Max BC Residual", color=colors[1], edgecolor="black", linewidth=0.5
    )

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(short_names, fontsize=10)
    ax.set_ylabel("Residual Magnitude", fontsize=11)
    ax.set_title("PDE and Boundary Condition Residuals by Method", fontsize=12)
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_ylim(bottom=1e-17)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = FIGS / f"residual_comparison.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out} ({out.stat().st_size} bytes)")
    plt.close(fig)


if __name__ == "__main__":
    main()
