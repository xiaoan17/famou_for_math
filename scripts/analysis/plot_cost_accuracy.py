"""
Figure 4: Cost-accuracy tradeoff — scatter of solve time vs max PDE residual.
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

    methods = data["methods"]
    short_names = ["Analytical", "FDM", "FEM", "Spectral", "PINN"]
    times = [m["total_time_s"] for m in methods]
    pde_res = [m["max_pde_residual"] for m in methods]

    markers = ["D", "s", "^", "o", "P"]
    colors = plt.cm.tab10.colors

    fig, ax = plt.subplots(figsize=(6, 4.5))
    for i in range(len(short_names)):
        ax.scatter(
            times[i], pde_res[i],
            s=120, marker=markers[i], color=colors[i],
            edgecolors="black", linewidths=0.6, zorder=5,
            label=short_names[i],
        )
        # Place label to avoid overlap
        offset_x = 8
        offset_y = -12 if i != 0 else 8
        ha = "left"
        if short_names[i] == "Spectral":
            offset_y = 10
        ax.annotate(
            short_names[i],
            (times[i], pde_res[i]),
            textcoords="offset points",
            xytext=(offset_x, offset_y),
            fontsize=9,
            ha=ha,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Solve Time (s)", fontsize=11)
    ax.set_ylabel("Max PDE Residual", fontsize=11)
    ax.set_title("Accuracy vs. Computational Cost", fontsize=12)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = FIGS / f"cost_accuracy.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out} ({out.stat().st_size} bytes)")
    plt.close(fig)


if __name__ == "__main__":
    main()
