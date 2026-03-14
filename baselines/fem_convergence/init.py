"""
FEM Mesh Convergence Analysis for two-group neutron diffusion equation.

Tests FEM solver with different mesh densities to verify convergence.
Reviewer A questioned the low FEM score (0.0652) - this analysis
validates whether it's a mesh resolution issue.
"""

import numpy as np
from typing import Tuple
import sys
import os

# Add parent directory to path to import FEM solver
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fem'))
from init import FEMSolver

# Physical constants
D1 = 1.0
D2 = 0.5
SIGMA_R = 0.02
SIGMA_A2 = 0.1
NU = 2.5
SIGMA_F1 = 0.005
SIGMA_F2 = 0.1
SIGMA_12 = 0.015


class FEMConvergenceSolver:
    """FEM solver with configurable mesh size for convergence study."""

    def __init__(self, nx: int = 65, ny: int = 65):
        """Initialize FEM solver with specified mesh size.

        Args:
            nx: Number of grid points in x direction
            ny: Number of grid points in y direction
        """
        self.nx = nx
        self.ny = ny
        self.solver = FEMSolver(nx=nx, ny=ny)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> Tuple:
        """Evaluate solution at query points.

        Returns:
            Tuple of (phi1, dphi1_dx, dphi1_dy, d2phi1_dx2, d2phi1_dy2,
                     phi2, dphi2_dx, dphi2_dy, d2phi2_dx2, d2phi2_dy2)
        """
        r = self.solver.evaluate_at(x, y)
        return (r[0], r[1], r[2], r[3], r[4],
                r[5], r[6], r[7], r[8], r[9])


# Global solver instance (default 65x65 mesh)
_solver = None


def solution():
    """Return solution functions phi1 and phi2.

    Returns:
        tuple: (phi1_func, phi2_func)
               Each function takes (x, y) arrays and returns:
               (value, d_dx, d_dy, d2_dx2, d2_dy2)
    """
    global _solver

    if _solver is None:
        _solver = FEMConvergenceSolver(nx=65, ny=65)

    def phi1(x, y):
        """Fast group flux."""
        r = _solver.evaluate(x, y)
        return r[0], r[1], r[2], r[3], r[4]

    def phi2(x, y):
        """Thermal group flux."""
        r = _solver.evaluate(x, y)
        return r[5], r[6], r[7], r[8], r[9]

    return phi1, phi2


def run_convergence_study(evaluator_path: str = None):
    """Run FEM convergence study with different mesh sizes.

    Args:
        evaluator_path: Path to evaluator.py for scoring

    Returns:
        dict: Convergence results for each mesh size
    """
    mesh_sizes = [33, 65, 129]
    results = {}

    for nx in mesh_sizes:
        print(f"\nTesting mesh size: {nx}x{nx}")

        # Create temporary init.py for this mesh size
        temp_init = f"""
import numpy as np
from typing import Tuple
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fem'))
from init import FEMSolver

class FEMConvergenceSolver:
    def __init__(self, nx={nx}, ny={nx}):
        self.solver = FEMSolver(nx=nx, ny=ny)

    def evaluate(self, x, y):
        r = self.solver.evaluate_at(x, y)
        return (r[0], r[1], r[2], r[3], r[4],
                r[5], r[6], r[7], r[8], r[9])

_solver = None

def solution():
    global _solver
    if _solver is None:
        _solver = FEMConvergenceSolver()

    def phi1(x, y):
        r = _solver.evaluate(x, y)
        return r[0], r[1], r[2], r[3], r[4]

    def phi2(x, y):
        r = _solver.evaluate(x, y)
        return r[5], r[6], r[7], r[8], r[9]

    return phi1, phi2
"""
        # Write temporary file
        temp_path = f"/tmp/fem_convergence_{nx}.py"
        with open(temp_path, 'w') as f:
            f.write(temp_init)

        # Evaluate
        if evaluator_path:
            import subprocess
            result = subprocess.run(
                ['python', evaluator_path, temp_path],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)

        results[f"{nx}x{nx}"] = {
            "mesh_size": nx,
            "description": f"FEM with {nx}x{nx} mesh"
        }

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--convergence', action='store_true', help='Run full convergence study')
    parser.add_argument('--evaluator', type=str, help='Path to evaluator.py')
    args = parser.parse_args()

    if args.convergence:
        results = run_convergence_study(args.evaluator)
        print("\n=== Convergence Study Results ===")
        for mesh, data in results.items():
            print(f"{mesh}: {data}")
    else:
        # Standard test
        phi1, phi2 = solution()
        X, Y = np.meshgrid(np.linspace(-0.4, 0.4, 5), np.linspace(-0.4, 0.4, 5))
        val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
        val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)
        print(f"FEM Convergence Baseline Test (65x65 mesh):")
        print(f"phi1 at center: {val1[2,2]:.6f}")
        print(f"phi2 at center: {val2[2,2]:.6f}")
