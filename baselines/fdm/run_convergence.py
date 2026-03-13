"""FDM convergence study: run at multiple resolutions."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fdm_solver import solve_fdm, compute_pde_residual, compute_bc_residual, interpolate_at

RESOLUTIONS = [21, 51, 101, 201]
TEST_POINTS = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]


def main() -> None:
    out_dir = Path(__file__).parent
    convergence = []

    for N in RESOLUTIONS:
        print(f"\n=== FDM {N}x{N} ===")
        t0 = time.time()
        result = solve_fdm(Nx=N, Ny=N)
        elapsed = time.time() - t0

        # PDE residuals
        pde_res = {}
        all_pde = []
        for xp, yp in TEST_POINTS:
            R1, R2 = compute_pde_residual(result, xp, yp)
            pde_res[f"({xp},{yp})"] = {"R1": R1, "R2": R2}
            all_pde.extend([abs(R1), abs(R2)])

        # BC residuals
        bc_raw = compute_bc_residual(result)
        all_bc = []
        for (R1, R2) in bc_raw.values():
            all_bc.extend([abs(R1), abs(R2)])

        max_pde = max(all_pde)
        max_bc = max(all_bc)

        # Solution values
        sol_vals = {}
        for xp, yp in TEST_POINTS:
            p1, p2 = interpolate_at(result, xp, yp)
            sol_vals[f"({xp},{yp})"] = {"phi1": p1, "phi2": p2}

        entry = {
            "N": N,
            "grid": f"{N}x{N}",
            "dof": 2 * N * N,
            "max_pde_residual": max_pde,
            "max_bc_residual": max_bc,
            "total_time_s": elapsed,
            "h": 1.0 / (N - 1),
            "solution_values": sol_vals,
        }
        convergence.append(entry)
        print(f"  Max PDE: {max_pde:.6e}, Max BC: {max_bc:.6e}, Time: {elapsed:.3f}s")

    with open(out_dir / "convergence_results.json", "w") as f:
        json.dump(convergence, f, indent=2)

    print(f"\nConvergence results saved to {out_dir / 'convergence_results.json'}")


if __name__ == "__main__":
    main()
