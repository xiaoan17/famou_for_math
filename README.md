# 二维有限均匀介质边界源双群中子扩散方程解析解

**任务 ID**: Analytical Solution Helmholtz
**项目类型**: AI4S (AI for Science)
**目标**: 顶会论文 (16页 PDF)

---

## 项目简介

本项目旨在利用 AI 方法求解二维有限均匀介质边界源双群中子扩散方程的解析解。通过 Famou 演化框架自动生成满足偏微分方程 (PDE) 和边界条件 (BC) 的函数。

### 核心任务

构造两个函数 φ₁(x,y) 和 φ₂(x,y)，使得它们同时满足：
1. 双群中子扩散方程（PDE）
2. 四条边界上的诺伊曼边界条件（BC）

### 物理方程

**快群方程**:
```
-D₁∇²φ₁ + Σᵣφ₁ = νΣf₁φ₁ + νΣf₂φ₂
```

**热群方程**:
```
-D₂∇²φ₂ + Σₐ₂φ₂ = Σ₁→₂φ₁
```

---

## 项目结构

```
working/paper_work_20260313/
├── famou/                   # Famou 演化实验
│   └── task-helmholtz/      # 本任务目录
│       ├── programs/        # 演化程序快照
│       ├── best_program.py  # 最终最优程序
│       ├── results.json     # 实验结果
│       └── evolution_log.json  # 演化日志
├── baselines/               # 对比实验
│   ├── <method-1>/
│   ├── <method-2>/
│   └── results/             # 汇总结果
├── ablations/               # 消融实验
│   └── <ablation-name>/
├── scripts/                 # 过程代码
│   ├── data_processing/     # 数据处理脚本
│   ├── analysis/            # 分析绘图脚本
│   └── utils/               # 共享工具
├── paper/                   # 论文
│   ├── figs/                # 实验结果图
│   └── tables/              # LaTeX 表格
├── CONTEXT.md               # 项目上下文
├── EXPERIMENTS.md           # 实验索引表
├── PROGRESS.md              # 进度跟踪
└── README.md                # 本文件
```

---

## 快速开始

### 环境要求

- Python 3.9+
- PyTorch
- NumPy
- Matplotlib

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行实验

```bash
# 查看 Famou 实验状态
famou-ctl status

# 提交新实验
famou-ctl submit --task helmholtz --config config.yaml
```

---

## 实验结果

### Baseline 对比

| 方法 | 分数 | 状态 |
|------|------|------|
| 待补充 | - | 进行中 |

### Famou 演化结果

| 轮次 | Experiment ID | 最佳分数 | 状态 |
|------|--------------|----------|------|
| Round 1 | - | - | 待启动 |

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [CONTEXT.md](./CONTEXT.md) | 项目上下文、团队配置、决策记录 |
| [EXPERIMENTS.md](./EXPERIMENTS.md) | 完整实验索引和结果汇总 |
| [PROGRESS.md](./PROGRESS.md) | 项目进度跟踪和里程碑 |

---

## 团队

本项目由 10 人 Agent 团队协作完成：

| Agent | 职责 |
|-------|------|
| Team Lead | 整体协调、任务分配、质量门禁 |
| Git & Doc Manager | 版本控制、进度文档维护 |
| Background Researcher | 文献调研、Introduction 前置准备 |
| Data Engineer | 数据处理、数据集划分 |
| Famou Agent | Famou 演化框架全生命周期守护 |
| Model Developer | 初始算法设计 (init.py) |
| Experiment Runner | 补充实验执行、数据分析 |
| Evaluator | 评估指标、结果对比、代码绘图 |
| Paper Writer | 论文撰写、图表制作 |
| Strict Reviewer | 双审稿人角色、批判性反馈 |

---

## 引用

```bibtex
@article{helmholtz2026,
  title={Analytical Solution for Two-Group Neutron Diffusion Equation},
  author={Agent Team},
  journal={arXiv preprint},
  year={2026}
}
```

---

## 许可证

本项目为学术研究用途。

---

*最后更新: 2026-03-14*
