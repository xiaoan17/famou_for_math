"""
Generate LaTeX tables for the paper:
  - main_results_table.tex
  - convergence_table.tex
"""
import json
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parents[2]
TABLES = PROJECT / "paper" / "tables"


def sci(val: float) -> str:
    """Format as LaTeX scientific notation using siunitx \\num{}."""
    if val == 0:
        return "0"
    exp = int(np.floor(np.log10(abs(val))))
    mantissa = val / 10**exp
    return f"\\num{{{mantissa:.2f}e{exp}}}"


def main_results_table():
    with open(PROJECT / "baselines" / "results" / "summary.json") as f:
        data = json.load(f)

    methods = data["methods"]
    short = ["Analytical", "FDM", "FEM (Q1)", "Spectral", "PINN"]
    params = [
        "200 modes",
        "20,402 DOF",
        "20,402 DOF",
        "1,800 DOF",
        "8,706 params",
    ]

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Comparison of numerical methods for the 2D two-group neutron diffusion benchmark. "
        r"Residuals are evaluated at interior and boundary test points using the governing PDE and boundary conditions.}",
        r"\label{tab:main_results}",
        r"\begin{tabular}{lllll}",
        r"\toprule",
        r"Method & Max PDE Res. & Max BC Res. & Solve Time (s) & DOF / Params \\",
        r"\midrule",
    ]

    for i, m in enumerate(methods):
        pde_str = sci(m["max_pde_residual"])
        bc_str = sci(m["max_bc_residual"])
        time_str = f"{m['total_time_s']:.3f}"
        lines.append(
            f"  {short[i]} & {pde_str} & {bc_str} & {time_str} & {params[i]} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    out = TABLES / "main_results_table.tex"
    out.write_text("\n".join(lines) + "\n")
    print(f"Saved {out} ({out.stat().st_size} bytes)")


def convergence_table():
    with open(PROJECT / "baselines" / "fdm" / "convergence_results.json") as f:
        conv = json.load(f)

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{FDM convergence study: max PDE residual as a function of grid refinement. "
        r"The observed convergence rate approaches the expected $O(h^2)$ for second-order finite differences.}",
        r"\label{tab:convergence}",
        r"\begin{tabular}{lllll}",
        r"\toprule",
        r"Grid $N$ & $h$ & Max PDE Res. & Time (s) & Conv. Rate \\",
        r"\midrule",
    ]

    for i, c in enumerate(conv):
        pde_str = sci(c["max_pde_residual"])
        time_str = f"{c['total_time_s']:.3f}"
        if i == 0:
            rate_str = "---"
        else:
            prev = conv[i - 1]
            rate = np.log(prev["max_pde_residual"] / c["max_pde_residual"]) / np.log(
                prev["h"] / c["h"]
            )
            rate_str = f"{rate:.2f}"
        lines.append(
            f"  {c['N']} & {c['h']:.3f} & {pde_str} & {time_str} & {rate_str} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    out = TABLES / "convergence_table.tex"
    out.write_text("\n".join(lines) + "\n")
    print(f"Saved {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main_results_table()
    convergence_table()
