---
illustration_id: 01
type: framework
style: scientific
aspect: 16:9
---

A clean scientific academic diagram showing the four-step analytical solution framework for 2D two-group neutron diffusion equations. White background, black and dark gray lines only, serif font labels. No color fills except light gray shading for emphasis.

Layout: Horizontal left-to-right pipeline with 4 connected boxes and arrows between them.

ZONES:
- Zone 1 (leftmost box, ~20% width): Title "Physical Problem" with a small square domain sketch labeled "[-0.5,0.5]²", boundary arrows on left side labeled "-D∂φ/∂x = y", other three sides labeled "∂φ/∂n = 0". Two flux symbols φ₁ (fast) and φ₂ (thermal) inside domain.
- Arrow 1: labeled "Step 1: Fourier Expansion"
- Zone 2 (second box, ~20% width): Title "Cosine Basis in y" with mathematical formula: φ_g(x,y) = Σ X_{g,n}(x)·cos(nπ(y+½)). Small vertical waveform sketch showing cosine modes. Label: "satisfies BC at y=±½"
- Arrow 2: labeled "Step 2: Eigendecomposition"
- Zone 3 (third box, ~20% width): Title "Decouple Groups" with matrix equation M = D⁻¹A, eigenvalues λ₁≈0.026, λ₂≈0.181. Two separate arrows splitting from one, representing group decoupling.
- Arrow 3: labeled "Step 3: Solve x-ODE"
- Zone 4 (rightmost box, ~20% width): Title "Analytical Solution" with formula φ_g = Σ c_{p,n}·P[g,p]·cosh(α(x-½))·cos(nπ(y+½)). Label: "Machine precision: |R| ≤ 3×10⁻¹⁶"

LABELS: Use actual mathematical notation with subscripts. All text in black serif font. Box borders in dark gray, 1.5pt weight.

COLORS: White (#FFFFFF) background, Black (#000000) text and main borders, Dark Gray (#444444) secondary elements, Light Gray (#EEEEEE) box fills.

STYLE: Scientific journal illustration, clean line art, no gradients, no decorative elements, academic paper style compatible with IEEE/NeurIPS publications. Thin clean lines, professional typography.

ASPECT: 16:9
