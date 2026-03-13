"""
Physics-Informed Neural Network (PINN) solver for 2D two-group neutron diffusion.

Architecture: 2-input (x,y) -> 64 -> 64 -> 64 -> 2-output (phi1, phi2)
Activation: tanh
Training: 2000 interior collocation points + 400 BC points, 5000 Adam iterations.

System:
  -D1 * lap(phi1) + A11*phi1 + A12*phi2 = 0
  -D2 * lap(phi2) + A21*phi1 + A22*phi2 = 0

BCs:
  Left  (x=-0.5): -D_g * dphi_g/dx = y
  Right, Top, Bottom: zero Neumann
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Physical constants
D1_val = 1.0
D2_val = 0.5
A11_val = 0.0075
A12_val = -0.25
A21_val = -0.015
A22_val = 0.1

device = torch.device("cpu")


class PINN(nn.Module):
    """Physics-Informed Neural Network for 2-group diffusion."""

    def __init__(self, hidden_dim: int = 64, n_layers: int = 3) -> None:
        super().__init__()
        layers = [nn.Linear(2, hidden_dim), nn.Tanh()]
        for _ in range(n_layers - 1):
            layers.extend([nn.Linear(hidden_dim, hidden_dim), nn.Tanh()])
        layers.append(nn.Linear(hidden_dim, 2))
        self.net = nn.Sequential(*layers)

    def forward(self, xy: torch.Tensor) -> torch.Tensor:
        return self.net(xy)


def compute_pde_loss(model: PINN, xy: torch.Tensor) -> torch.Tensor:
    """Compute PDE residual loss at collocation points."""
    xy.requires_grad_(True)
    out = model(xy)
    phi1 = out[:, 0:1]
    phi2 = out[:, 1:2]

    # First derivatives
    grad_phi1 = torch.autograd.grad(
        phi1, xy, grad_outputs=torch.ones_like(phi1),
        create_graph=True, retain_graph=True
    )[0]
    grad_phi2 = torch.autograd.grad(
        phi2, xy, grad_outputs=torch.ones_like(phi2),
        create_graph=True, retain_graph=True
    )[0]

    dphi1_dx = grad_phi1[:, 0:1]
    dphi1_dy = grad_phi1[:, 1:2]
    dphi2_dx = grad_phi2[:, 0:1]
    dphi2_dy = grad_phi2[:, 1:2]

    # Second derivatives
    d2phi1_dx2 = torch.autograd.grad(
        dphi1_dx, xy, grad_outputs=torch.ones_like(dphi1_dx),
        create_graph=True, retain_graph=True
    )[0][:, 0:1]
    d2phi1_dy2 = torch.autograd.grad(
        dphi1_dy, xy, grad_outputs=torch.ones_like(dphi1_dy),
        create_graph=True, retain_graph=True
    )[0][:, 1:2]
    d2phi2_dx2 = torch.autograd.grad(
        dphi2_dx, xy, grad_outputs=torch.ones_like(dphi2_dx),
        create_graph=True, retain_graph=True
    )[0][:, 0:1]
    d2phi2_dy2 = torch.autograd.grad(
        dphi2_dy, xy, grad_outputs=torch.ones_like(dphi2_dy),
        create_graph=True, retain_graph=True
    )[0][:, 1:2]

    lap1 = d2phi1_dx2 + d2phi1_dy2
    lap2 = d2phi2_dx2 + d2phi2_dy2

    R1 = -D1_val * lap1 + A11_val * phi1 + A12_val * phi2
    R2 = -D2_val * lap2 + A21_val * phi1 + A22_val * phi2

    return torch.mean(R1**2 + R2**2)


def compute_bc_loss(model: PINN, bc_points: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Compute boundary condition loss."""
    loss = torch.tensor(0.0, device=device)

    # Left BC: -D_g * dphi_g/dx = y at x=-0.5
    xy_left = bc_points["left"]
    xy_left.requires_grad_(True)
    out = model(xy_left)
    phi1 = out[:, 0:1]
    phi2 = out[:, 1:2]

    grad1 = torch.autograd.grad(
        phi1, xy_left, grad_outputs=torch.ones_like(phi1),
        create_graph=True, retain_graph=True
    )[0]
    grad2 = torch.autograd.grad(
        phi2, xy_left, grad_outputs=torch.ones_like(phi2),
        create_graph=True, retain_graph=True
    )[0]

    dphi1_dx = grad1[:, 0:1]
    dphi2_dx = grad2[:, 0:1]
    y_vals = xy_left[:, 1:2]

    loss += torch.mean((-D1_val * dphi1_dx - y_vals)**2)
    loss += torch.mean((-D2_val * dphi2_dx - y_vals)**2)

    # Right BC: dphi_g/dx = 0 at x=+0.5
    xy_right = bc_points["right"]
    xy_right.requires_grad_(True)
    out = model(xy_right)
    grad1 = torch.autograd.grad(
        out[:, 0:1], xy_right, grad_outputs=torch.ones_like(out[:, 0:1]),
        create_graph=True, retain_graph=True
    )[0]
    grad2 = torch.autograd.grad(
        out[:, 1:2], xy_right, grad_outputs=torch.ones_like(out[:, 1:2]),
        create_graph=True, retain_graph=True
    )[0]
    loss += torch.mean(grad1[:, 0:1]**2 + grad2[:, 0:1]**2)

    # Top BC: dphi_g/dy = 0 at y=+0.5
    xy_top = bc_points["top"]
    xy_top.requires_grad_(True)
    out = model(xy_top)
    grad1 = torch.autograd.grad(
        out[:, 0:1], xy_top, grad_outputs=torch.ones_like(out[:, 0:1]),
        create_graph=True, retain_graph=True
    )[0]
    grad2 = torch.autograd.grad(
        out[:, 1:2], xy_top, grad_outputs=torch.ones_like(out[:, 1:2]),
        create_graph=True, retain_graph=True
    )[0]
    loss += torch.mean(grad1[:, 1:2]**2 + grad2[:, 1:2]**2)

    # Bottom BC: dphi_g/dy = 0 at y=-0.5
    xy_bot = bc_points["bottom"]
    xy_bot.requires_grad_(True)
    out = model(xy_bot)
    grad1 = torch.autograd.grad(
        out[:, 0:1], xy_bot, grad_outputs=torch.ones_like(out[:, 0:1]),
        create_graph=True, retain_graph=True
    )[0]
    grad2 = torch.autograd.grad(
        out[:, 1:2], xy_bot, grad_outputs=torch.ones_like(out[:, 1:2]),
        create_graph=True, retain_graph=True
    )[0]
    loss += torch.mean(grad1[:, 1:2]**2 + grad2[:, 1:2]**2)

    return loss


def train_pinn(
    n_interior: int = 2000,
    n_bc: int = 100,
    n_epochs: int = 5000,
    lr: float = 1e-3,
) -> Tuple[PINN, Dict]:
    """Train the PINN model.

    Args:
        n_interior: number of interior collocation points
        n_bc: number of BC points per boundary edge
        n_epochs: number of Adam iterations
        lr: learning rate

    Returns:
        Trained model and training info dict.
    """
    torch.manual_seed(42)
    np.random.seed(42)

    model = PINN(hidden_dim=64, n_layers=3).to(device)

    # Generate training points
    # Interior: random in (-0.5, 0.5)^2
    xy_interior = torch.rand(n_interior, 2, device=device) - 0.5

    # BC points (100 per edge = 400 total)
    y_bc = torch.linspace(-0.5, 0.5, n_bc, device=device).unsqueeze(1)
    x_bc = torch.linspace(-0.5, 0.5, n_bc, device=device).unsqueeze(1)

    bc_points = {
        "left": torch.cat([torch.full((n_bc, 1), -0.5, device=device), y_bc], dim=1),
        "right": torch.cat([torch.full((n_bc, 1), 0.5, device=device), y_bc], dim=1),
        "top": torch.cat([x_bc, torch.full((n_bc, 1), 0.5, device=device)], dim=1),
        "bottom": torch.cat([x_bc, torch.full((n_bc, 1), -0.5, device=device)], dim=1),
    }

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2000, gamma=0.5)

    history = {"pde_loss": [], "bc_loss": [], "total_loss": []}

    t0 = time.time()
    for epoch in range(n_epochs):
        optimizer.zero_grad()

        pde_loss = compute_pde_loss(model, xy_interior)
        bc_loss = compute_bc_loss(model, bc_points)

        # Weight BC loss higher to enforce boundary conditions
        total_loss = pde_loss + 10.0 * bc_loss

        total_loss.backward()
        optimizer.step()
        scheduler.step()

        if epoch % 500 == 0 or epoch == n_epochs - 1:
            logger.info(
                f"  Epoch {epoch:5d}: PDE={pde_loss.item():.6e}, "
                f"BC={bc_loss.item():.6e}, Total={total_loss.item():.6e}"
            )
            history["pde_loss"].append(float(pde_loss.item()))
            history["bc_loss"].append(float(bc_loss.item()))
            history["total_loss"].append(float(total_loss.item()))

    train_time = time.time() - t0
    logger.info(f"Training completed in {train_time:.2f}s")

    return model, {"train_time": train_time, "history": history}


def evaluate_model(model: PINN, x: float, y: float) -> Tuple[float, float]:
    """Evaluate model at a single point."""
    model.eval()
    with torch.no_grad():
        xy = torch.tensor([[x, y]], dtype=torch.float32, device=device)
        out = model(xy)
    return float(out[0, 0].item()), float(out[0, 1].item())


def compute_pde_residual_at(
    model: PINN, x_eval: float, y_eval: float
) -> Tuple[float, float]:
    """Compute PDE residual at a single point using autograd."""
    model.eval()
    xy = torch.tensor([[x_eval, y_eval]], dtype=torch.float32, device=device)
    xy.requires_grad_(True)
    out = model(xy)
    phi1 = out[:, 0:1]
    phi2 = out[:, 1:2]

    grad1 = torch.autograd.grad(phi1, xy, create_graph=True, retain_graph=True)[0]
    grad2 = torch.autograd.grad(phi2, xy, create_graph=True, retain_graph=True)[0]

    d2phi1_dx2 = torch.autograd.grad(
        grad1[:, 0:1], xy, create_graph=True, retain_graph=True
    )[0][:, 0:1]
    d2phi1_dy2 = torch.autograd.grad(
        grad1[:, 1:2], xy, create_graph=True, retain_graph=True
    )[0][:, 1:2]
    d2phi2_dx2 = torch.autograd.grad(
        grad2[:, 0:1], xy, create_graph=True, retain_graph=True
    )[0][:, 0:1]
    d2phi2_dy2 = torch.autograd.grad(
        grad2[:, 1:2], xy, create_graph=True, retain_graph=True
    )[0][:, 1:2]

    lap1 = d2phi1_dx2 + d2phi1_dy2
    lap2 = d2phi2_dx2 + d2phi2_dy2

    R1 = -D1_val * lap1 + A11_val * phi1 + A12_val * phi2
    R2 = -D2_val * lap2 + A21_val * phi1 + A22_val * phi2

    return float(R1.item()), float(R2.item())


def compute_bc_residual_at(
    model: PINN, x_eval: float, y_eval: float, bc_type: str
) -> Tuple[float, float]:
    """Compute BC residual at a boundary point."""
    model.eval()
    xy = torch.tensor([[x_eval, y_eval]], dtype=torch.float32, device=device)
    xy.requires_grad_(True)
    out = model(xy)

    grad1 = torch.autograd.grad(
        out[:, 0:1], xy, create_graph=False, retain_graph=True
    )[0]
    grad2 = torch.autograd.grad(
        out[:, 1:2], xy, create_graph=False, retain_graph=False
    )[0]

    if bc_type == "left":
        R1 = -D1_val * float(grad1[0, 0].item()) - y_eval
        R2 = -D2_val * float(grad2[0, 0].item()) - y_eval
    elif bc_type == "right":
        R1 = -D1_val * float(grad1[0, 0].item())
        R2 = -D2_val * float(grad2[0, 0].item())
    elif bc_type in ("top", "bottom"):
        R1 = -D1_val * float(grad1[0, 1].item())
        R2 = -D2_val * float(grad2[0, 1].item())
    else:
        raise ValueError(f"Unknown bc_type: {bc_type}")

    return R1, R2


def main() -> None:
    """Train PINN and save results."""
    out_dir = Path(__file__).parent
    test_points = [(0, 0), (0.2, 0.2), (-0.2, -0.3), (0.4, -0.4)]

    logger.info("Training PINN...")
    model, train_info = train_pinn(
        n_interior=2000, n_bc=100, n_epochs=5000, lr=1e-3
    )

    # PDE residuals
    pde_residuals = {}
    all_pde = []
    for xp, yp in test_points:
        R1, R2 = compute_pde_residual_at(model, xp, yp)
        pde_residuals[f"({xp},{yp})"] = {"R1": R1, "R2": R2}
        all_pde.extend([abs(R1), abs(R2)])
        logger.info(f"  PDE residual at ({xp},{yp}): R1={R1:.6e}, R2={R2:.6e}")

    # BC residuals
    bc_residuals = {}
    all_bc = []
    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        R1, R2 = compute_bc_residual_at(model, -0.5, y_val, "left")
        bc_residuals[f"left(x=-0.5,y={y_val})"] = {"R1": R1, "R2": R2}
        all_bc.extend([abs(R1), abs(R2)])

    for y_val in [-0.3, 0.0, 0.2, 0.4]:
        R1, R2 = compute_bc_residual_at(model, 0.5, y_val, "right")
        bc_residuals[f"right(x=0.5,y={y_val})"] = {"R1": R1, "R2": R2}
        all_bc.extend([abs(R1), abs(R2)])

    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        R1, R2 = compute_bc_residual_at(model, x_val, 0.5, "top")
        bc_residuals[f"top(x={x_val},y=0.5)"] = {"R1": R1, "R2": R2}
        all_bc.extend([abs(R1), abs(R2)])

    for x_val in [-0.3, 0.0, 0.2, 0.4]:
        R1, R2 = compute_bc_residual_at(model, x_val, -0.5, "bottom")
        bc_residuals[f"bottom(x={x_val},y=-0.5)"] = {"R1": R1, "R2": R2}
        all_bc.extend([abs(R1), abs(R2)])

    # Solution values
    solution_values = {}
    for xp, yp in test_points:
        p1, p2 = evaluate_model(model, xp, yp)
        solution_values[f"({xp},{yp})"] = {"phi1": p1, "phi2": p2}

    max_pde = max(all_pde) if all_pde else 0.0
    max_bc = max(all_bc) if all_bc else 0.0

    logger.info(f"Max PDE residual: {max_pde:.6e}")
    logger.info(f"Max BC residual:  {max_bc:.6e}")

    # Count parameters
    n_params = sum(p.numel() for p in model.parameters())

    output = {
        "method": "Physics-Informed Neural Network (PINN)",
        "architecture": "2-64-64-64-2 MLP (tanh)",
        "n_parameters": n_params,
        "n_interior_points": 2000,
        "n_bc_points": 400,
        "n_epochs": 5000,
        "pde_residuals": pde_residuals,
        "bc_residuals": bc_residuals,
        "solution_values": solution_values,
        "max_pde_residual": max_pde,
        "max_bc_residual": max_bc,
        "train_time_s": train_info["train_time"],
        "total_time_s": train_info["train_time"],
        "final_pde_loss": train_info["history"]["pde_loss"][-1],
        "final_bc_loss": train_info["history"]["bc_loss"][-1],
    }

    with open(out_dir / "results.json", "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Results saved to {out_dir / 'results.json'}")


if __name__ == "__main__":
    main()
