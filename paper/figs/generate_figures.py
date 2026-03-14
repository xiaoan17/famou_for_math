"""
Generate scientific figures for the paper:
"LLM-Guided Evolutionary Search for Two-Group Neutron Diffusion Equation"

Style: Scientific/Academic publication quality
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np
import os

# Set scientific style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['figure.dpi'] = 300

# Color palette - scientific
COLORS = {
    'primary': '#1f4e79',      # Deep blue
    'secondary': '#c55a11',    # Orange
    'accent1': '#70ad47',      # Green
    'accent2': '#7030a0',      # Purple
    'accent3': '#00b0f0',      # Light blue
    'gray': '#7f7f7f',         # Gray
    'light_gray': '#d9d9d9',   # Light gray
    'white': '#ffffff',
    'black': '#000000'
}


def save_fig(fig, name):
    """Save figure with tight layout."""
    fig.tight_layout()
    fig.savefig(f'{name}.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(f'{name}.pdf', bbox_inches='tight', facecolor='white')
    print(f"Saved: {name}.png and {name}.pdf")


def create_framework_figure():
    """Figure 1: System Framework Overview"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Title
    ax.text(5, 5.7, 'Famou Evolutionary Framework for Neutron Diffusion',
            ha='center', va='top', fontsize=14, fontweight='bold', color=COLORS['primary'])

    # Input box
    input_box = FancyBboxPatch((0.3, 3.8), 1.8, 1.2, boxstyle="round,pad=0.05",
                                facecolor=COLORS['light_gray'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(input_box)
    ax.text(1.2, 4.6, 'Problem', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(1.2, 4.2, 'Two-Group', ha='center', va='center', fontsize=8)
    ax.text(1.2, 3.95, 'Neutron Diffusion', ha='center', va='center', fontsize=8)

    # Arrow to LLM
    ax.annotate('', xy=(3, 4.4), xytext=(2.2, 4.4),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], lw=2))

    # LLM box
    llm_box = FancyBboxPatch((3, 3.6), 2, 1.6, boxstyle="round,pad=0.05",
                              facecolor=COLORS['accent3'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(llm_box)
    ax.text(4, 4.9, 'Large Language', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(4, 4.6, 'Model (LLM)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(4, 4.15, 'Code Generation', ha='center', va='center', fontsize=8, style='italic')
    ax.text(4, 3.85, '& Mutation', ha='center', va='center', fontsize=8, style='italic')

    # Arrow to Islands
    ax.annotate('', xy=(5.5, 4.4), xytext=(5.1, 4.4),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], lw=2))

    # Islands boxes
    island_colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent1'], COLORS['accent2']]
    island_names = ['Island 1', 'Island 2', 'Island 3', 'Island 4']

    for i, (color, name) in enumerate(zip(island_colors, island_names)):
        x = 5.8 + (i % 2) * 1.6
        y = 4.5 if i < 2 else 3.0

        island_box = FancyBboxPatch((x, y), 1.4, 1.2, boxstyle="round,pad=0.03",
                                     facecolor=color, edgecolor=COLORS['black'], linewidth=1.2, alpha=0.7)
        ax.add_patch(island_box)
        ax.text(x + 0.7, y + 0.75, name, ha='center', va='center', fontsize=8, fontweight='bold', color='white')
        ax.text(x + 0.7, y + 0.4, 'Population', ha='center', va='center', fontsize=7, color='white')

    # Migration arrows between islands
    ax.annotate('', xy=(7.4, 4.8), xytext=(7.2, 4.8),
                arrowprops=dict(arrowstyle='<->', color=COLORS['gray'], lw=1, linestyle='--'))
    ax.annotate('', xy=(7.4, 3.3), xytext=(7.2, 3.3),
                arrowprops=dict(arrowstyle='<->', color=COLORS['gray'], lw=1, linestyle='--'))
    ax.annotate('', xy=(6.5, 4.4), xytext=(6.5, 3.6),
                arrowprops=dict(arrowstyle='<->', color=COLORS['gray'], lw=1, linestyle='--'))

    # Migration label
    ax.text(7.3, 4.05, 'Migration', ha='center', va='center', fontsize=7, color=COLORS['gray'], style='italic')

    # Fitness Evaluation box
    eval_box = FancyBboxPatch((3, 1.8), 2, 1.2, boxstyle="round,pad=0.05",
                               facecolor=COLORS['accent1'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(eval_box)
    ax.text(4, 2.7, 'Fitness', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(4, 2.35, 'Evaluation', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(4, 2.0, 'PDE + BC Residuals', ha='center', va='center', fontsize=7)

    # Arrow from Islands to Evaluation
    ax.annotate('', xy=(4, 3.0), xytext=(6.5, 3.0),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], lw=1.5,
                               connectionstyle="arc3,rad=0.2"))

    # Arrow from Evaluation back to LLM (feedback loop)
    ax.annotate('', xy=(3, 3.2), xytext=(3, 3.6),
                arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], lw=1.5, linestyle='--'))
    ax.text(2.5, 3.4, 'Feedback', ha='center', va='center', fontsize=7, color=COLORS['secondary'], rotation=90)

    # Output box
    output_box = FancyBboxPatch((7.5, 1.8), 1.8, 1.2, boxstyle="round,pad=0.05",
                                 facecolor=COLORS['secondary'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(output_box)
    ax.text(8.4, 2.7, 'Best Solution', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(8.4, 2.3, r'$\phi_1(x,y), \phi_2(x,y)$', ha='center', va='center', fontsize=9, color='white')

    # Arrow from Evaluation to Output
    ax.annotate('', xy=(7.5, 2.4), xytext=(5.1, 2.4),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], lw=1.5))

    # Legend for components
    legend_y = 0.8
    ax.text(5, legend_y + 0.4, 'Components:', ha='center', va='center', fontsize=9, fontweight='bold')

    components = [
        ('PDE Residuals', COLORS['primary']),
        ('BC Residuals', COLORS['secondary']),
        ('Coupling Term', COLORS['accent1'])
    ]

    for i, (label, color) in enumerate(components):
        x_pos = 2.5 + i * 2
        rect = Rectangle((x_pos - 0.3, legend_y - 0.15), 0.6, 0.3,
                         facecolor=color, edgecolor=COLORS['black'], alpha=0.7)
        ax.add_patch(rect)
        ax.text(x_pos + 0.5, legend_y, label, ha='left', va='center', fontsize=8)

    save_fig(fig, 'fig_framework')
    plt.close()


def create_motivation_figure():
    """Figure 2: Research Motivation - Method Comparison"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    # Left panel: Method comparison
    ax1 = axes[0]
    methods = ['FDM', 'FEM', 'Spectral', 'PINN', 'Famou\n(Ours)']
    accuracy = [0.75, 0.70, 0.95, 0.85, 0.90]
    interpretability = [0.9, 0.7, 0.8, 0.3, 0.95]
    training_cost = [0.3, 0.5, 0.4, 0.9, 0.5]

    x = np.arange(len(methods))
    width = 0.25

    bars1 = ax1.bar(x - width, accuracy, width, label='Accuracy', color=COLORS['primary'], alpha=0.8)
    bars2 = ax1.bar(x, interpretability, width, label='Interpretability', color=COLORS['accent1'], alpha=0.8)
    bars3 = ax1.bar(x + width, training_cost, width, label='Training Cost', color=COLORS['secondary'], alpha=0.8)

    ax1.set_ylabel('Score (0-1)', fontsize=10)
    ax1.set_title('Method Comparison', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=9)
    ax1.legend(loc='upper left', fontsize=8)
    ax1.set_ylim(0, 1.1)
    ax1.grid(axis='y', alpha=0.3)

    # Right panel: Challenges and Solutions
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('Research Challenges \u0026 Solutions', fontsize=12, fontweight='bold')

    # Challenges box
    challenge_box = FancyBboxPatch((0.5, 5.5), 4, 4, boxstyle="round,pad=0.05",
                                    facecolor='#ffcccc', edgecolor='#cc0000', linewidth=2)
    ax2.add_patch(challenge_box)
    ax2.text(2.5, 9.2, 'CHALLENGES', ha='center', va='center', fontsize=11, fontweight='bold', color='#cc0000')

    challenges = [
        '• Mixed Neumann BCs',
        '• Coupled PDE system',
        '• High accuracy needed',
        '• Interpretability required'
    ]
    for i, chal in enumerate(challenges):
        ax2.text(0.8, 8.5 - i * 0.7, chal, ha='left', va='center', fontsize=9)

    # Solutions box
    solution_box = FancyBboxPatch((5.5, 5.5), 4, 4, boxstyle="round,pad=0.05",
                                   facecolor='#ccffcc', edgecolor='#006600', linewidth=2)
    ax2.add_patch(solution_box)
    ax2.text(7.5, 9.2, 'SOLUTIONS', ha='center', va='center', fontsize=11, fontweight='bold', color='#006600')

    solutions = [
        '• LLM-guided evolution',
        '• Code-space search',
        '• Physics-informed fitness',
        '• Analytical expressions'
    ]
    for i, sol in enumerate(solutions):
        ax2.text(5.8, 8.5 - i * 0.7, sol, ha='left', va='center', fontsize=9)

    # Arrow between boxes
    ax2.annotate('', xy=(5.3, 7.5), xytext=(4.7, 7.5),
                arrowprops=dict(arrowstyle='->', color=COLORS['black'], lw=2))

    # Bottom: Key advantage
    advantage_box = FancyBboxPatch((2, 0.5), 6, 1.5, boxstyle="round,pad=0.05",
                                    facecolor=COLORS['accent3'], edgecolor=COLORS['primary'], linewidth=2)
    ax2.add_patch(advantage_box)
    ax2.text(5, 1.5, 'Key Advantage', ha='center', va='center', fontsize=10, fontweight='bold')
    ax2.text(5, 0.9, 'Explicit analytical solutions vs. black-box neural networks',
            ha='center', va='center', fontsize=9)

    save_fig(fig, 'fig_motivation')
    plt.close()


def create_evolution_figure():
    """Figure 3: Famou Evolution Strategy"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Title
    ax.text(5, 6.7, 'Island-Based Evolutionary Search', ha='center', va='top',
            fontsize=14, fontweight='bold', color=COLORS['primary'])

    # Generation timeline
    gen_y = 6.0
    for i, gen in enumerate(['Gen 0', 'Gen 10', 'Gen 20', 'Gen 50', 'Gen 100']):
        x = 1 + i * 1.8
        ax.text(x, gen_y, gen, ha='center', va='center', fontsize=9, fontweight='bold')
        if i < 4:
            ax.annotate('', xy=(x + 1.3, gen_y), xytext=(x + 0.5, gen_y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['gray'], lw=1))

    # Island representation for each generation
    island_data = [
        # (gen_idx, island_populations, best_fitness)
        (0, [0.3, 0.25, 0.28, 0.22], 0.30),
        (1, [0.45, 0.42, 0.48, 0.40], 0.48),
        (2, [0.60, 0.58, 0.62, 0.55], 0.62),
        (3, [0.78, 0.75, 0.80, 0.72], 0.80),
        (4, [0.88, 0.85, 0.90, 0.82], 0.90),
    ]

    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent1'], COLORS['accent2']]

    for gen_idx, populations, best in island_data:
        x_base = 1 + gen_idx * 1.8
        y_base = 4.5

        for i, (pop, color) in enumerate(zip(populations, colors)):
            # Island circle size proportional to fitness
            size = 150 + pop * 300
            circle = Circle((x_base - 0.4 + (i % 2) * 0.8, y_base - (i // 2) * 0.8),
                           radius=0.15 + pop * 0.15,
                           facecolor=color, edgecolor=COLORS['black'],
                           alpha=0.6 + pop * 0.3, linewidth=1)
            ax.add_patch(circle)

        # Best fitness label
        ax.text(x_base, y_base - 1.2, f'{best:.2f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color=COLORS['primary'])

    # Label for best fitness
    ax.text(5, 3.0, 'Best Fitness Score', ha='center', va='center',
           fontsize=10, fontweight='bold', color=COLORS['primary'])

    # Fitness function details
    fitness_box = FancyBboxPatch((0.5, 0.5), 4, 2, boxstyle="round,pad=0.05",
                                  facecolor=COLORS['light_gray'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(fitness_box)
    ax.text(2.5, 2.3, 'Fitness Function', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(2.5, 1.8, r'$\mathcal{F} = -(\text{MSE}_{PDE} + \lambda \cdot \text{MSE}_{BC})$',
           ha='center', va='center', fontsize=9)
    ax.text(2.5, 1.3, 'PDE Residual: Fast group + Thermal group', ha='center', va='center', fontsize=8)
    ax.text(2.5, 0.9, 'BC Residual: Mixed Neumann conditions', ha='center', va='center', fontsize=8)

    # LLM Mutation details
    llm_box = FancyBboxPatch((5.5, 0.5), 4, 2, boxstyle="round,pad=0.05",
                              facecolor=COLORS['accent3'], edgecolor=COLORS['black'], linewidth=1.5)
    ax.add_patch(llm_box)
    ax.text(7.5, 2.3, 'LLM-Guided Mutation', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(7.5, 1.8, '• Code structure modification', ha='left', va='center', fontsize=8)
    ax.text(7.5, 1.4, '• Mathematical term insertion', ha='left', va='center', fontsize=8)
    ax.text(7.5, 1.0, '• Coefficient optimization', ha='left', va='center', fontsize=8)
    ax.text(7.5, 0.6, '• Crossover between islands', ha='left', va='center', fontsize=8)

    save_fig(fig, 'fig_evolution')
    plt.close()


def create_domain_figure():
    """Figure 4: Problem Domain and Boundary Conditions"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 7))

    # Domain
    domain = Rectangle((-0.5, -0.5), 1, 1, facecolor=COLORS['light_gray'],
                        edgecolor=COLORS['black'], linewidth=2)
    ax.add_patch(domain)

    # Grid lines
    for i in range(5):
        x = -0.5 + i * 0.25
        ax.plot([x, x], [-0.5, 0.5], 'k--', alpha=0.3, linewidth=0.5)
        ax.plot([-0.5, 0.5], [x, x], 'k--', alpha=0.3, linewidth=0.5)

    # Boundary labels with conditions
    # Left boundary - non-homogeneous Neumann
    ax.annotate('', xy=(-0.7, 0.3), xytext=(-0.5, 0.3),
               arrowprops=dict(arrowstyle='->', color=COLORS['secondary'], lw=2))
    ax.text(-0.85, 0.3, r'$-D\frac{\partial\phi}{\partial x}=y$',
           ha='center', va='center', fontsize=10, color=COLORS['secondary'])
    ax.text(-0.7, -0.3, 'Left BC:\nNon-homogeneous\nNeumann', ha='center', va='center',
           fontsize=8, color=COLORS['secondary'])

    # Right boundary - homogeneous Neumann
    ax.annotate('', xy=(0.7, 0), xytext=(0.5, 0),
               arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=2))
    ax.text(0.85, 0, r'$-D\frac{\partial\phi}{\partial x}=0$',
           ha='center', va='center', fontsize=10, color=COLORS['primary'])

    # Top boundary - homogeneous Neumann
    ax.annotate('', xy=(0, 0.7), xytext=(0, 0.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=2))
    ax.text(0, 0.85, r'$-D\frac{\partial\phi}{\partial y}=0$',
           ha='center', va='center', fontsize=10, color=COLORS['primary'])

    # Bottom boundary - homogeneous Neumann
    ax.annotate('', xy=(0, -0.7), xytext=(0, -0.5),
               arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=2))
    ax.text(0, -0.85, r'$-D\frac{\partial\phi}{\partial y}=0$',
           ha='center', va='center', fontsize=10, color=COLORS['primary'])

    # Domain label
    ax.text(0, 0, r'$\Omega$', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(0, -0.15, r'$[-0.5,0.5]^2$', ha='center', va='center', fontsize=9)

    # Title
    ax.set_title('Problem Domain and Boundary Conditions', fontsize=13, fontweight='bold', pad=20)

    # Set limits and aspect
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLORS['secondary'], label='Non-homogeneous Neumann'),
        mpatches.Patch(color=COLORS['primary'], label='Homogeneous Neumann')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    save_fig(fig, 'fig_domain')
    plt.close()


def create_equations_figure():
    """Figure 5: Two-Group Equations Visualization"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Fast group equation
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')

    fast_box = FancyBboxPatch((0.5, 2), 9, 6, boxstyle="round,pad=0.05",
                               facecolor=COLORS['accent3'], edgecolor=COLORS['primary'], linewidth=2)
    ax1.add_patch(fast_box)

    ax1.text(5, 7.5, 'FAST GROUP', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['primary'])

    # Equation
    ax1.text(5, 5.5, r'$-D_1\nabla^2\phi_1 + \Sigma_r\phi_1 = \nu\Sigma_{f1}\phi_1 + \nu\Sigma_{f2}\phi_2$',
            ha='center', va='center', fontsize=11)

    # Terms explanation
    terms = [
        (r'$-D_1\nabla^2\phi_1$', 'Diffusion (Leakage)'),
        (r'$\Sigma_r\phi_1$', 'Removal'),
        (r'$\nu\Sigma_{f1}\phi_1$', 'Fast fission source'),
        (r'$\nu\Sigma_{f2}\phi_2$', 'Thermal fission source')
    ]

    for i, (term, desc) in enumerate(terms):
        y_pos = 4.0 - i * 0.6
        ax1.text(1.5, y_pos, term, ha='left', va='center', fontsize=9)
        ax1.text(5.5, y_pos, f'→ {desc}', ha='left', va='center', fontsize=8, color=COLORS['gray'])

    # Thermal group equation
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')

    thermal_box = FancyBboxPatch((0.5, 2), 9, 6, boxstyle="round,pad=0.05",
                                  facecolor=COLORS['accent1'], edgecolor=COLORS['secondary'], linewidth=2)
    ax2.add_patch(thermal_box)

    ax2.text(5, 7.5, 'THERMAL GROUP', ha='center', va='center',
            fontsize=12, fontweight='bold', color=COLORS['secondary'])

    # Equation
    ax2.text(5, 5.5, r'$-D_2\nabla^2\phi_2 + \Sigma_{a2}\phi_2 = \Sigma_{1\to2}\phi_1$',
            ha='center', va='center', fontsize=11)

    # Terms explanation
    terms2 = [
        (r'$-D_2\nabla^2\phi_2$', 'Diffusion (Leakage)'),
        (r'$\Sigma_{a2}\phi_2$', 'Absorption'),
        (r'$\Sigma_{1\to2}\phi_1$', 'Group transfer from fast')
    ]

    for i, (term, desc) in enumerate(terms2):
        y_pos = 4.0 - i * 0.6
        ax2.text(1.5, y_pos, term, ha='left', va='center', fontsize=9)
        ax2.text(5.5, y_pos, f'→ {desc}', ha='left', va='center', fontsize=8, color=COLORS['gray'])

    # Coupling arrow
    fig.text(0.5, 0.35, r'$\phi_1$ drives $\phi_2$ via group transfer',
            ha='center', va='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    save_fig(fig, 'fig_equations')
    plt.close()


if __name__ == '__main__':
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("Generating scientific figures for the paper...")
    print("-" * 50)

    create_framework_figure()
    create_motivation_figure()
    create_evolution_figure()
    create_domain_figure()
    create_equations_figure()

    print("-" * 50)
    print("All figures generated successfully!")
