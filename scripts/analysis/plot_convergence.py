"""
Figure 3: FDM convergence — log-log of max PDE residual vs grid size N, with O(h^2) reference.
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

    with open(PROJECT / "baselines" / "fdm" / "convergence_results.json") as f:
        conv = json.load(f)

    Ns = np.array([c["N"] for c in conv])
    pde_res = np.array([c["max_pde_residual"] for c in conv])
    hs = np.array([c["h"] for c in conv])

    # O(h^2) reference line anchored to first data point
    h_ref = np.linspace(hs[-1] * 0.7, hs[0] * 1.3, 50)
    ref_line = pde_res[0] * (h_ref / hs[0]) ** 2

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.loglog(Ns, pde_res, "o-", color="tab:blue", markersize=7, linewidth=1.5,
              label="FDM Max PDE Residual")

    # Plot reference on secondary mapping: N ~ 1/h, so use N_ref = 1/h_ref
    N_ref = 1.0 / h_ref
    ax.loglog(N_ref, ref_line, "--", color="gray", linewidth=1.2, label=r"$O(h^2)$ reference")

    ax.set_xlabel("Grid size $N$", fontsize=11)
    ax.set_ylabel("Max PDE Residual", fontsize=11)
    ax.set_title("FDM Convergence Study", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)

    # Compute and annotate convergence rates
    for i in range(1, len(Ns)):
        rate = np.log(pde_res[i - 1] / pde_res[i]) / np.log(hs[i - 1] / hs[i])
        ax.annotate(
            f"rate={rate:.2f}",
            xy=(Ns[i], pde_res[i]),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=8,
            color="tab:red",
        )

    fig.tight_layout()
    for ext in ("png", "pdf"):
        out = FIGS / f"convergence_fdm.{ext}"
        fig.savefig(out, dpi=300, bbox_inches="tight")
        print(f"Saved {out} ({out.stat().st_size} bytes)")
    plt.close(fig)


if __name__ == "__main__":
    main()
