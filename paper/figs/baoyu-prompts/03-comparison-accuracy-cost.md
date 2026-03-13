---
illustration_id: 03
type: comparison
style: scientific
aspect: 16:9
---

A scientific comparison diagram showing accuracy versus computational cost tradeoff for five PDE solver methods for neutron diffusion equations. White background, clean academic style.

Layout: Two-column layout. Left column: vertical ranking list of methods by accuracy. Right column: horizontal bar chart of solve time.

ZONES:
- Left column header: "PDE Residual (log scale)" — vertical axis from 10⁻¹⁶ (top, best) to 10⁻² (bottom, worst)
- Left column entries (top to bottom, with small circular markers):
  1. ● Analytical: 2.81×10⁻¹⁶ (at very top, star marker)
  2. ● FEM: 9.20×10⁻⁷
  3. ● Spectral: 7.23×10⁻⁶
  4. ● FDM: 9.07×10⁻⁵
  5. ● PINN: 9.54×10⁻³ (at bottom)
- Right column header: "Solve Time (seconds)"
- Right column horizontal bars (same method order):
  1. Analytical: 0.017s (very short bar)
  2. FEM: 0.824s
  3. Spectral: 0.079s
  4. FDM: 0.134s
  5. PINN: 98.6s (very long bar)
- Connecting dotted lines between left and right columns for each method
- Bottom annotation: "★ Analytical solution: best accuracy + competitive speed"

LABELS: Method names in bold. Numbers in scientific notation. Clear axis labels. Each method has a distinct marker shape (●, ■, ▲, ◆, ★).

COLORS: White (#FFFFFF) background, Black (#000000) text, Dark Gray (#333333) bars and markers, Light Gray (#CCCCCC) grid lines, Black star (★) for Analytical to highlight it.

STYLE: Clean scientific infographic, academic publication quality, no gradients, minimal design, data-focused layout.

ASPECT: 16:9
