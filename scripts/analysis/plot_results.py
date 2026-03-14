"""
可视化脚本
生成论文所需的实验结果图表
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle


# 设置科学论文风格
def setup_scientific_style():
    """配置 matplotlib 为科学论文风格"""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.02,
    })


# 色盲友好的配色方案 (Okabe-Ito)
OKABE_ITO_COLORS = [
    '#E69F00',  # 橙色
    '#56B4E9',  # 天蓝色
    '#009E73',  # 绿色
    '#F0E442',  # 黄色
    '#0072B2',  # 蓝色
    '#D55E00',  # 红橙色
    '#CC79A7',  # 粉色
    '#999999',  # 灰色
]


def load_comparison_data(project_root: Path) -> Dict[str, Any]:
    """加载对比数据"""
    comparison_path = project_root / 'baselines' / 'results' / 'comparison_table.json'
    if comparison_path.exists():
        with open(comparison_path, 'r') as f:
            return json.load(f)
    return None


def plot_main_results_bar(comparison: Dict, output_path: Path):
    """
    绘制主结果对比柱状图 (baseline vs famou)

    Args:
        comparison: 对比数据
        output_path: 输出文件路径
    """
    setup_scientific_style()

    baselines = comparison.get('baselines', [])
    famou = comparison.get('famou', {})

    # 准备数据
    methods = [b['method'] for b in baselines]
    scores = [b['combined_score'] for b in baselines]

    # 如果 famou 已完成，添加到数据中
    famou_completed = famou.get('status') == 'completed'
    if famou_completed:
        methods.append('Famou (Ours)')
        scores.append(famou['combined_score'])

    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 5))

    # 设置颜色
    colors = OKABE_ITO_COLORS[:len(baselines)]
    if famou_completed:
        colors.append('#009E73')  # 绿色突出 Famou

    # 绘制柱状图
    bars = ax.barh(methods, scores, color=colors, edgecolor='black', linewidth=0.5)

    # 高亮最佳 baseline
    best_idx = np.argmax([b['combined_score'] for b in baselines])
    bars[best_idx].set_edgecolor('#D55E00')
    bars[best_idx].set_linewidth(2)

    # 如果 famou 完成且得分最高，高亮它
    if famou_completed:
        famou_idx = len(baselines)
        if scores[famou_idx] >= max(scores[:-1]):
            bars[famou_idx].set_edgecolor('#009E73')
            bars[famou_idx].set_linewidth(2.5)

    # 添加数值标签
    for i, (bar, score) in enumerate(zip(bars, scores)):
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{score:.4f}',
                ha='left', va='center', fontsize=9,
                fontweight='bold' if i == len(baselines) else 'normal')

    # 设置标签
    ax.set_xlabel('Combined Score (higher is better)', fontsize=11)
    ax.set_title('Performance Comparison: Baseline Methods vs Famou', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 1.1)

    # 添加网格线
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # 添加图例说明
    legend_text = f"Best Baseline: {baselines[0]['method']} ({baselines[0]['combined_score']:.4f})"
    if famou_completed:
        improvement = comparison['summary'].get('improvement', 0)
        legend_text += f"\nFamou Improvement: {improvement:+.2f}%"

    ax.text(0.98, 0.02, legend_text,
            transform=ax.transAxes,
            ha='right', va='bottom',
            fontsize=8,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, format='png')
    plt.savefig(output_path.with_suffix('.pdf'), format='pdf')
    plt.close()

    print(f"  ✓ Saved: {output_path}")


def plot_evolution_curve(project_root: Path, output_path: Path):
    """
    绘制演化曲线图 (Famou各轮最佳分数)

    Args:
        project_root: 项目根目录
        output_path: 输出文件路径
    """
    setup_scientific_style()

    famou_dir = project_root / 'famou' / 'task-helmholtz'

    # 收集所有轮次的最佳分数
    rounds_data = []

    if famou_dir.exists():
        for filename in sorted(os.listdir(famou_dir)):
            if filename.startswith('round-') and filename.endswith('-evolution_log.json'):
                try:
                    round_num = int(filename.split('-')[1])
                    with open(famou_dir / filename, 'r') as f:
                        log_data = json.load(f)

                    # 提取每代最佳分数
                    if 'generations' in log_data:
                        gen_scores = [g['best_score'] for g in log_data['generations']]
                        rounds_data.append({
                            'round': round_num,
                            'scores': gen_scores,
                            'final_score': gen_scores[-1] if gen_scores else 0
                        })
                except Exception as e:
                    print(f"    Warning: Failed to parse {filename}: {e}")

    if not rounds_data:
        print("  ⚠ No evolution data found, skipping evolution curve plot")
        return

    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制每轮的演化曲线
    for i, round_data in enumerate(rounds_data):
        generations = list(range(1, len(round_data['scores']) + 1))
        scores = round_data['scores']

        ax.plot(generations, scores,
                marker='o',
                markersize=4,
                linewidth=1.5,
                label=f'Round {round_data["round"]}',
                color=OKABE_ITO_COLORS[i % len(OKABE_ITO_COLORS)])

    # 设置标签
    ax.set_xlabel('Generation', fontsize=11)
    ax.set_ylabel('Best Score', fontsize=11)
    ax.set_title('Famou Evolution: Best Score per Generation', fontsize=12, fontweight='bold')

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # 图例
    ax.legend(loc='lower right', framealpha=0.9)

    # 添加最终分数标注
    final_scores_text = "Final Scores:\n"
    for rd in rounds_data:
        final_scores_text += f"Round {rd['round']}: {rd['final_score']:.4f}\n"

    ax.text(0.02, 0.98, final_scores_text,
            transform=ax.transAxes,
            ha='left', va='top',
            fontsize=8,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    plt.tight_layout()
    plt.savefig(output_path, format='png')
    plt.savefig(output_path.with_suffix('.pdf'), format='pdf')
    plt.close()

    print(f"  ✓ Saved: {output_path}")


def plot_residual_heatmap(evaluator_path: Path, solution_path: Path, output_path: Path):
    """
    绘制PDE残差热力图

    Args:
        evaluator_path: 评估器路径
        solution_path: 解文件路径 (init.py)
        output_path: 输出文件路径
    """
    setup_scientific_style()

    if not solution_path.exists():
        print(f"  ⚠ Solution file not found: {solution_path}, skipping heatmap")
        return

    try:
        # 导入解函数
        import sys
        sys.path.insert(0, str(solution_path.parent))

        spec = __import__('importlib.util').util.spec_from_file_location(
            "solution", solution_path)
        module = __import__('importlib.util').util.module_from_spec(spec)
        spec.loader.exec_module(module)

        phi1, phi2 = module.solution()

        # 物理常数
        D1, D2 = 1.0, 0.5
        SIGMA_R, SIGMA_A2 = 0.02, 0.1
        NU = 2.5
        SIGMA_F1, SIGMA_F2 = 0.005, 0.1
        SIGMA_12 = 0.015

        # 创建网格
        x = np.linspace(-0.5, 0.5, 50)
        y = np.linspace(-0.5, 0.5, 50)
        X, Y = np.meshgrid(x, y)

        # 计算解和残差
        val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
        val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)

        res1 = -D1*(d2_1_dx2 + d2_1_dy2) + SIGMA_R*val1 - (NU*SIGMA_F1*val1 + NU*SIGMA_F2*val2)
        res2 = -D2*(d2_2_dx2 + d2_2_dy2) + SIGMA_A2*val2 - SIGMA_12*val1

        # 创建子图
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # 快群残差热力图
        im1 = axes[0].contourf(X, Y, np.abs(res1), levels=20, cmap='YlOrRd')
        axes[0].set_title('Fast Group PDE Residual |Res₁|', fontsize=11, fontweight='bold')
        axes[0].set_xlabel('x')
        axes[0].set_ylabel('y')
        plt.colorbar(im1, ax=axes[0], label='|Residual|')

        # 热群残差热力图
        im2 = axes[1].contourf(X, Y, np.abs(res2), levels=20, cmap='YlOrRd')
        axes[1].set_title('Thermal Group PDE Residual |Res₂|', fontsize=11, fontweight='bold')
        axes[1].set_xlabel('x')
        axes[1].set_ylabel('y')
        plt.colorbar(im2, ax=axes[1], label='|Residual|')

        plt.suptitle('PDE Residual Distribution', fontsize=13, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(output_path, format='png')
        plt.savefig(output_path.with_suffix('.pdf'), format='pdf')
        plt.close()

        print(f"  ✓ Saved: {output_path}")

    except Exception as e:
        print(f"  ⚠ Failed to generate heatmap: {e}")


def plot_boundary_residual_distribution(evaluator_path: Path, solution_path: Path, output_path: Path):
    """
    绘制边界条件残差分布图

    Args:
        evaluator_path: 评估器路径
        solution_path: 解文件路径
        output_path: 输出文件路径
    """
    setup_scientific_style()

    if not solution_path.exists():
        print(f"  ⚠ Solution file not found: {solution_path}, skipping boundary plot")
        return

    try:
        # 导入解函数
        import sys
        sys.path.insert(0, str(solution_path.parent))

        spec = __import__('importlib.util').util.spec_from_file_location(
            "solution", solution_path)
        module = __import__('importlib.util').util.module_from_spec(spec)
        spec.loader.exec_module(module)

        phi1, phi2 = module.solution()

        # 物理常数
        D1, D2 = 1.0, 0.5

        # 边界网格
        y_grid = np.linspace(-0.5, 0.5, 21)
        x_grid = np.linspace(-0.5, 0.5, 21)

        # 计算各边界残差
        # 左边界
        x_left = np.full_like(y_grid, -0.5)
        _, d1_dx_left, _, _, _ = phi1(x_left, y_grid)
        _, d2_dx_left, _, _, _ = phi2(x_left, y_grid)
        bc1_left = -D1 * d1_dx_left - y_grid
        bc2_left = -D2 * d2_dx_left - y_grid

        # 右边界
        x_right = np.full_like(y_grid, 0.5)
        _, d1_dx_right, _, _, _ = phi1(x_right, y_grid)
        _, d2_dx_right, _, _, _ = phi2(x_right, y_grid)
        bc1_right = -D1 * d1_dx_right
        bc2_right = -D2 * d2_dx_right

        # 上边界
        y_top = np.full_like(x_grid, 0.5)
        _, _, d1_dy_top, _, _ = phi1(x_grid, y_top)
        _, _, d2_dy_top, _, _ = phi2(x_grid, y_top)
        bc1_top = -D1 * d1_dy_top
        bc2_top = -D2 * d2_dy_top

        # 下边界
        y_bottom = np.full_like(x_grid, -0.5)
        _, _, d1_dy_bottom, _, _ = phi1(x_grid, y_bottom)
        _, _, d2_dy_bottom, _, _ = phi2(x_grid, y_bottom)
        bc1_bottom = -D1 * d1_dy_bottom
        bc2_bottom = -D2 * d2_dy_bottom

        # 创建图形
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 左边界
        axes[0, 0].plot(y_grid, np.abs(bc1_left), 'o-', label='Fast Group', color=OKABE_ITO_COLORS[0])
        axes[0, 0].plot(y_grid, np.abs(bc2_left), 's-', label='Thermal Group', color=OKABE_ITO_COLORS[1])
        axes[0, 0].set_title('Left Boundary (x=-0.5): |-D∂φ/∂x - y|', fontsize=10)
        axes[0, 0].set_xlabel('y')
        axes[0, 0].set_ylabel('|BC Residual|')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 右边界
        axes[0, 1].plot(y_grid, np.abs(bc1_right), 'o-', label='Fast Group', color=OKABE_ITO_COLORS[0])
        axes[0, 1].plot(y_grid, np.abs(bc2_right), 's-', label='Thermal Group', color=OKABE_ITO_COLORS[1])
        axes[0, 1].set_title('Right Boundary (x=0.5): |-D∂φ/∂x|', fontsize=10)
        axes[0, 1].set_xlabel('y')
        axes[0, 1].set_ylabel('|BC Residual|')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # 上边界
        axes[1, 0].plot(x_grid, np.abs(bc1_top), 'o-', label='Fast Group', color=OKABE_ITO_COLORS[0])
        axes[1, 0].plot(x_grid, np.abs(bc2_top), 's-', label='Thermal Group', color=OKABE_ITO_COLORS[1])
        axes[1, 0].set_title('Top Boundary (y=0.5): |-D∂φ/∂y|', fontsize=10)
        axes[1, 0].set_xlabel('x')
        axes[1, 0].set_ylabel('|BC Residual|')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # 下边界
        axes[1, 1].plot(x_grid, np.abs(bc1_bottom), 'o-', label='Fast Group', color=OKABE_ITO_COLORS[0])
        axes[1, 1].plot(x_grid, np.abs(bc2_bottom), 's-', label='Thermal Group', color=OKABE_ITO_COLORS[1])
        axes[1, 1].set_title('Bottom Boundary (y=-0.5): |-D∂φ/∂y|', fontsize=10)
        axes[1, 1].set_xlabel('x')
        axes[1, 1].set_ylabel('|BC Residual|')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.suptitle('Boundary Condition Residual Distribution', fontsize=13, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(output_path, format='png')
        plt.savefig(output_path.with_suffix('.pdf'), format='pdf')
        plt.close()

        print(f"  ✓ Saved: {output_path}")

    except Exception as e:
        print(f"  ⚠ Failed to generate boundary plot: {e}")


def plot_convergence_analysis(project_root: Path, output_path: Path):
    """
    绘制收敛分析图 (iteration vs score)

    Args:
        project_root: 项目根目录
        output_path: 输出文件路径
    """
    setup_scientific_style()

    famou_dir = project_root / 'famou' / 'task-helmholtz'

    # 收集收敛数据
    convergence_data = []

    if famou_dir.exists():
        for filename in sorted(os.listdir(famou_dir)):
            if filename.startswith('round-') and filename.endswith('-evolution_log.json'):
                try:
                    round_num = int(filename.split('-')[1])
                    with open(famou_dir / filename, 'r') as f:
                        log_data = json.load(f)

                    if 'generations' in log_data:
                        for gen in log_data['generations']:
                            convergence_data.append({
                                'round': round_num,
                                'generation': gen.get('generation', 0),
                                'best_score': gen.get('best_score', 0),
                                'mean_score': gen.get('mean_score', 0),
                                'diversity': gen.get('diversity', 0)
                            })
                except Exception as e:
                    pass

    if not convergence_data:
        print("  ⚠ No convergence data found, skipping convergence plot")
        return

    # 按轮次分组
    rounds = sorted(set(d['round'] for d in convergence_data))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：最佳分数收敛
    for round_num in rounds:
        round_data = [d for d in convergence_data if d['round'] == round_num]
        generations = [d['generation'] for d in round_data]
        scores = [d['best_score'] for d in round_data]

        axes[0].plot(generations, scores,
                     marker='o', markersize=3,
                     label=f'Round {round_num}',
                     color=OKABE_ITO_COLORS[(round_num - 1) % len(OKABE_ITO_COLORS)])

    axes[0].set_xlabel('Generation')
    axes[0].set_ylabel('Best Score')
    axes[0].set_title('Convergence: Best Score over Generations')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 右图：种群多样性
    for round_num in rounds:
        round_data = [d for d in convergence_data if d['round'] == round_num]
        generations = [d['generation'] for d in round_data]
        diversity = [d['diversity'] for d in round_data]

        if any(d > 0 for d in diversity):
            axes[1].plot(generations, diversity,
                         marker='s', markersize=3,
                         label=f'Round {round_num}',
                         color=OKABE_ITO_COLORS[(round_num - 1) % len(OKABE_ITO_COLORS)])

    axes[1].set_xlabel('Generation')
    axes[1].set_ylabel('Population Diversity')
    axes[1].set_title('Population Diversity over Generations')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle('Famou Convergence Analysis', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, format='png')
    plt.savefig(output_path.with_suffix('.pdf'), format='pdf')
    plt.close()

    print(f"  ✓ Saved: {output_path}")


def main():
    """主函数"""
    # 项目根目录
    project_root = Path(__file__).parent.parent.parent

    # 输出路径
    figs_dir = project_root / 'paper' / 'figs'
    figs_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Generating Visualization Figures")
    print("=" * 60)

    # 加载对比数据
    print("\n[1/5] Loading comparison data...")
    comparison = load_comparison_data(project_root)
    if not comparison:
        print("  ⚠ No comparison data found. Run collect_results.py first.")
        return

    # 1. 主结果对比柱状图
    print("\n[2/5] Plotting main results comparison...")
    plot_main_results_bar(comparison, figs_dir / 'fig_main_results.png')

    # 2. 演化曲线图
    print("\n[3/5] Plotting evolution curve...")
    plot_evolution_curve(project_root, figs_dir / 'fig_evolution_curve.png')

    # 3. PDE残差热力图 (使用最佳baseline)
    print("\n[4/5] Plotting PDE residual heatmap...")
    evaluator_path = project_root / 'famou' / 'task-helmholtz' / 'evaluator.py'
    best_baseline = comparison['baselines'][0]['directory']
    solution_path = project_root / 'baselines' / best_baseline / 'init.py'
    plot_residual_heatmap(evaluator_path, solution_path, figs_dir / 'fig_residual_heatmap.png')

    # 4. 边界条件残差分布图
    print("\n[5/5] Plotting boundary residual distribution...")
    plot_boundary_residual_distribution(
        evaluator_path, solution_path, figs_dir / 'fig_boundary_residual.png')

    # 5. 收敛分析图
    print("\n[6/6] Plotting convergence analysis...")
    plot_convergence_analysis(project_root, figs_dir / 'fig_convergence.png')

    print("\n" + "=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)
    print(f"Output directory: {figs_dir}")


if __name__ == '__main__':
    main()
