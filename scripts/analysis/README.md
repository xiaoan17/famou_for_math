# Analysis Scripts

本目录包含用于实验结果分析和可视化的脚本。

## 脚本说明

### 1. collect_results.py

**功能**: 收集 baseline 和 Famou 实验结果，汇总到 `comparison_table.json`

**输入**:
- `baselines/*/results.json` - 各 baseline 方法的结果
- `famou/task-helmholtz/results.json` - Famou 实验结果（如果存在）
- `famou/task-helmholtz/round-*-evolution_log.json` - 演化日志

**输出**:
- `baselines/results/comparison_table.json` - 汇总后的对比数据

**用法**:
```bash
python scripts/analysis/collect_results.py
```

### 2. plot_results.py

**功能**: 生成论文所需的实验结果图表

**输入**:
- `baselines/results/comparison_table.json` - 对比数据
- `famou/task-helmholtz/round-*-evolution_log.json` - 演化日志
- `baselines/*/init.py` - 用于生成残差热力图

**输出**:
- `paper/figs/fig_main_results.png/pdf` - 主结果对比柱状图
- `paper/figs/fig_evolution_curve.png/pdf` - 演化曲线图
- `paper/figs/fig_residual_heatmap.png/pdf` - PDE残差热力图
- `paper/figs/fig_boundary_residual.png/pdf` - 边界条件残差分布图
- `paper/figs/fig_convergence.png/pdf` - 收敛分析图

**用法**:
```bash
python scripts/analysis/plot_results.py
```

### 3. generate_tables.py

**功能**: 生成 LaTeX 表格

**输入**:
- `baselines/results/comparison_table.json` - 对比数据
- `famou/task-helmholtz/round-*-evolution_log.json` - 演化日志
- `ablations/*/results.json` - 消融实验结果

**输出**:
- `paper/tables/table_main_results.tex` - 主结果对比表
- `paper/tables/table_baseline_details.tex` - Baseline 详细参数表
- `paper/tables/table_evolution.tex` - 演化结果表
- `paper/tables/table_ablation.tex` - 消融实验表
- `paper/tables/table_comparison_matrix.tex` - 方法对比矩阵
- `paper/tables/table_physical_constants.tex` - 物理常数表

**用法**:
```bash
python scripts/analysis/generate_tables.py
```

## 完整分析流程

等待 Famou 实验完成后，运行以下命令生成所有结果：

```bash
# 1. 收集结果
cd /Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313
python scripts/analysis/collect_results.py

# 2. 生成图表
python scripts/analysis/plot_results.py

# 3. 生成表格
python scripts/analysis/generate_tables.py
```

## 输出文件结构

```
paper/
├── figs/
│   ├── fig_main_results.png        # 主结果对比柱状图
│   ├── fig_evolution_curve.png     # 演化曲线图
│   ├── fig_residual_heatmap.png    # PDE残差热力图
│   ├── fig_boundary_residual.png   # 边界条件残差分布图
│   └── fig_convergence.png         # 收敛分析图
└── tables/
    ├── table_main_results.tex      # 主结果对比表
    ├── table_baseline_details.tex  # Baseline 详细参数表
    ├── table_evolution.tex         # 演化结果表
    ├── table_ablation.tex          # 消融实验表
    ├── table_comparison_matrix.tex # 方法对比矩阵
    └── table_physical_constants.tex # 物理常数表
```

## 依赖

- Python 3.8+
- numpy
- matplotlib
- seaborn (可选)

安装依赖:
```bash
pip install numpy matplotlib
```

## 注意事项

1. 所有图表使用色盲友好的 Okabe-Ito 配色方案
2. 图表输出为 PNG (用于预览) 和 PDF (用于论文)
3. 表格使用 `booktabs` 宏包格式
4. 在 Famou 实验完成前，演化相关图表会显示为空或跳过
