"""
结果收集脚本
收集 baseline 和 famou 实验结果，汇总到 comparison_table.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def load_json(path: str) -> Dict[str, Any]:
    """加载 JSON 文件"""
    with open(path, 'r') as f:
        return json.load(f)


def collect_baseline_results(base_dir: str) -> List[Dict[str, Any]]:
    """
    收集所有 baseline 方法的结果

    Args:
        base_dir: baselines 目录路径

    Returns:
        按 combined_score 排序的 baseline 结果列表
    """
    baseline_methods = ['chebyshev', 'pinn', 'fdm', 'fem', 'analytical']
    results = []

    for method in baseline_methods:
        result_path = os.path.join(base_dir, method, 'results.json')
        if os.path.exists(result_path):
            try:
                data = load_json(result_path)
                results.append({
                    'method': data.get('method', method),
                    'directory': method,
                    'combined_score': data.get('combined_score', 0),
                    'validity': data.get('validity', 0),
                    'cost_time': data.get('cost_time', 0),
                    'parameters': data.get('parameters', {}),
                    'description': data.get('description', '')
                })
            except Exception as e:
                print(f"Warning: Failed to load {result_path}: {e}")

    # 按 combined_score 降序排序
    results.sort(key=lambda x: x['combined_score'], reverse=True)
    return results


def collect_famou_results(famou_dir: str) -> Dict[str, Any]:
    """
    收集 Famou 实验结果

    Args:
        famou_dir: famou/task-helmholtz 目录路径

    Returns:
        Famou 实验结果，如果没有则返回空 dict
    """
    results_path = os.path.join(famou_dir, 'results.json')

    if not os.path.exists(results_path):
        return {
            'status': 'not_started',
            'message': 'Famou experiment not yet completed'
        }

    try:
        data = load_json(results_path)
        return {
            'status': 'completed',
            'method': 'Famou (LLM-guided Evolution)',
            'combined_score': data.get('combined_score', 0),
            'validity': data.get('validity', 0),
            'cost_time': data.get('cost_time', 0),
            'rounds': data.get('rounds', 0),
            'best_program': data.get('best_program', '')
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def collect_evolution_log(famou_dir: str) -> List[Dict[str, Any]]:
    """
    收集 Famou 演化日志（各轮次最佳分数）

    Args:
        famou_dir: famou/task-helmholtz 目录路径

    Returns:
        各轮次演化记录列表
    """
    # 查找所有 round-*-evolution_log.json 文件
    evolution_logs = []

    if not os.path.exists(famou_dir):
        return evolution_logs

    for filename in os.listdir(famou_dir):
        if filename.startswith('round-') and filename.endswith('-evolution_log.json'):
            try:
                log_path = os.path.join(famou_dir, filename)
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
                    evolution_logs.append({
                        'filename': filename,
                        'data': log_data
                    })
            except Exception as e:
                print(f"Warning: Failed to load evolution log {filename}: {e}")

    # 按轮次排序
    evolution_logs.sort(key=lambda x: x['filename'])
    return evolution_logs


def generate_comparison_table(baselines: List[Dict], famou: Dict) -> Dict[str, Any]:
    """
    生成对比表格数据

    Args:
        baselines: baseline 结果列表
        famou: famou 结果

    Returns:
        完整的对比表格数据
    """
    # 找出最佳 baseline
    best_baseline = baselines[0] if baselines else None

    # 构建对比表
    comparison = {
        'experiment_date': '2026-03-14',
        'task': 'Two-Group Neutron Diffusion Equation',
        'physical_constants': {
            'D1': 1.0,
            'D2': 0.5,
            'Sigma_R': 0.02,
            'Sigma_A2': 0.1,
            'nu': 2.5,
            'Sigma_F1': 0.005,
            'Sigma_F2': 0.1,
            'Sigma_12': 0.015
        },
        'baselines': baselines,
        'famou': famou,
        'best_baseline': best_baseline,
        'ranking': [b['method'] for b in baselines],
        'summary': {
            'total_baselines': len(baselines),
            'best_baseline_score': best_baseline['combined_score'] if best_baseline else 0,
            'famou_score': famou.get('combined_score', 0) if famou.get('status') == 'completed' else None,
            'improvement': None
        }
    }

    # 计算提升（如果 famou 已完成）
    if famou.get('status') == 'completed' and best_baseline:
        famou_score = famou['combined_score']
        baseline_score = best_baseline['combined_score']
        improvement = ((famou_score - baseline_score) / baseline_score) * 100
        comparison['summary']['improvement'] = improvement
        comparison['summary']['famou_score'] = famou_score

    return comparison


def main():
    """主函数"""
    # 项目根目录
    project_root = Path(__file__).parent.parent.parent

    # 路径配置
    baselines_dir = project_root / 'baselines'
    famou_dir = project_root / 'famou' / 'task-helmholtz'
    output_path = project_root / 'baselines' / 'results' / 'comparison_table.json'

    print("=" * 60)
    print("Collecting Experiment Results")
    print("=" * 60)

    # 收集 baseline 结果
    print("\n[1/3] Collecting baseline results...")
    baselines = collect_baseline_results(str(baselines_dir))
    print(f"      Found {len(baselines)} baseline methods")
    for i, b in enumerate(baselines, 1):
        print(f"      {i}. {b['method']}: {b['combined_score']:.4f}")

    # 收集 famou 结果
    print("\n[2/3] Collecting Famou results...")
    famou = collect_famou_results(str(famou_dir))
    if famou.get('status') == 'completed':
        print(f"      Famou completed: {famou['combined_score']:.4f}")
    else:
        print(f"      Status: {famou.get('status', 'unknown')}")
        print(f"      Message: {famou.get('message', 'N/A')}")

    # 收集演化日志
    print("\n[3/3] Collecting evolution logs...")
    evolution_logs = collect_evolution_log(str(famou_dir))
    print(f"      Found {len(evolution_logs)} evolution log files")

    # 生成对比表
    print("\n[4/4] Generating comparison table...")
    comparison = generate_comparison_table(baselines, famou)

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存结果
    with open(output_path, 'w') as f:
        json.dump(comparison, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Best Baseline: {comparison['summary']['best_baseline_score']:.4f}")
    if comparison['summary']['famou_score']:
        print(f"Famou Score:   {comparison['summary']['famou_score']:.4f}")
        print(f"Improvement:   {comparison['summary']['improvement']:+.2f}%")
    else:
        print("Famou Score:   (pending)")

    return comparison


if __name__ == '__main__':
    main()
