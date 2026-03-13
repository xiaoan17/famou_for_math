"""Run analytical solver and save results to JSON."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import analytical_solver as solver
import numpy as np

N_TERMS = 200
TEST_POINTS = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]

def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent.parent / "baselines" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    residuals = solver.compute_residuals(N_terms=N_TERMS)
    elapsed = time.time() - t0

    # Solution values at test points
    xp = np.array([p[0] for p in TEST_POINTS])
    yp = np.array([p[1] for p in TEST_POINTS])
    phi1_vals, phi2_vals = solver.evaluate_flux(xp, yp, N_terms=N_TERMS)
    solution_values = {}
    for i, (x, y) in enumerate(TEST_POINTS):
        solution_values[f"({x},{y})"] = {
            "phi1": float(phi1_vals[i]),
            "phi2": float(phi2_vals[i]),
        }

    # Extract max residuals
    all_pde = []
    for v in residuals["pde"].values():
        all_pde.extend([abs(v["R1"]), abs(v["R2"])])
    all_bc = []
    for v in residuals["bc"].values():
        all_bc.extend([abs(v["R1"]), abs(v["R2"])])

    output = {
        "method": "Analytical (Fourier-cosine + eigendecomposition)",
        "n_terms": N_TERMS,
        "max_pde_residual": max(all_pde),
        "max_bc_residual": max(all_bc),
        "pde_residuals": residuals["pde"],
        "bc_residuals": residuals["bc"],
        "solution_values": solution_values,
        "computation_time_s": elapsed,
    }

    out_path = out_dir / "analytical_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Analytical solver results (N_terms={N_TERMS}):")
    print(f"  Max PDE residual: {output['max_pde_residual']:.6e}")
    print(f"  Max BC  residual: {output['max_bc_residual']:.6e}")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Saved to: {out_path}")

    # Print solution values
    for pt, vals in solution_values.items():
        print(f"  phi1{pt} = {vals['phi1']:.8e}, phi2{pt} = {vals['phi2']:.8e}")


if __name__ == "__main__":
    main()
