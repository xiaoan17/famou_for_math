"""Plot comparison bar chart — unified evaluator scores."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

methods = [
    'FDM\n(2nd-order)',
    'High-order\nFDM (4th)',
    'PINN\n(numpy)',
    'Truncated\nAnalytical\n(K=5)',
    'Fourier\nAnalytical\n(N=30, Ours)',
]
scores = [0.9186, 0.9186, 0.9587, 0.9936, 0.9989]

# Colors: gray for baselines, blue highlight for ours
colors = ['#b0b0b0', '#b0b0b0', '#b0b0b0', '#b0b0b0', '#2563eb']
edge_colors = ['#888888', '#888888', '#888888', '#888888', '#1d4ed8']

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)

bars = ax.bar(range(len(methods)), scores, color=colors, edgecolor=edge_colors,
              linewidth=1.2, width=0.6, zorder=3)

# Score labels on top of bars
for i, (bar, score) in enumerate(zip(bars, scores)):
    weight = 'bold' if i == len(methods) - 1 else 'normal'
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
            f'{score:.4f}', ha='center', va='bottom',
            fontsize=10, fontfamily='serif', fontweight=weight)

ax.set_xticks(range(len(methods)))
ax.set_xticklabels(methods, fontsize=8.5, fontfamily='serif')
ax.set_ylabel('Unified Combined Score', fontsize=11, fontfamily='serif')
ax.set_ylim(0.90, 1.008)
ax.set_xlim(-0.5, len(methods) - 0.5)

# Grid
ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Perfect score reference line
ax.axhline(y=1.0, color='#999999', linestyle=':', linewidth=0.8, zorder=1)
ax.text(len(methods) - 0.6, 1.001, 'Perfect = 1.0',
        fontsize=7.5, fontfamily='serif', color='#999999', ha='right')

# Annotation for FDM interpolation issue
ax.annotate('Interpolation\nartifacts', xy=(0.5, 0.9186),
            xytext=(1.2, 0.935), fontsize=7.5, fontfamily='serif', color='#666666',
            arrowprops=dict(arrowstyle='->', color='#999999', lw=0.8),
            ha='center')

plt.tight_layout()
plt.savefig('/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/paper/figs/fig_comparison.png',
            bbox_inches='tight', facecolor='white')
plt.close('all')
print("fig_comparison.png saved.")
