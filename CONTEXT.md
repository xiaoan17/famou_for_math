# CONTEXT.md - AI4S 论文项目上下文

**项目**: 二维有限均匀介质边界源双群中子扩散方程解析解
**任务 ID**: Analytical Solution Helmholtz
**工作目录**: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/`
**创建日期**: 2026-03-14
**目标**: 顶会论文 (16页 PDF)

---

## 当前阶段

**Phase 1: 完成** - 论文通过审稿，准备最终提交

---

## 研究背景（Background Researcher 维护）

### 核心任务
构造两个函数 φ₁(x,y) 和 φ₂(x,y)，使得它们同时满足：
1. 双群中子扩散方程（PDE）
2. 四条边界上的诺伊曼边界条件（BC）

### 文献调研总结

**核心研究领域**：
1. **AI4S/PDE求解**: Physics-Informed Neural Networks (PINNs), Neural Operators (DeepONet, FNO, LNO)
2. **演化计算方法**: FunSearch (DeepMind, Nature 2023), Famou, Evolutionary Algorithms for PDEs
3. **传统数值方法**: Finite Difference (FDM), Finite Element (FEM), Spectral Methods (Chebyshev)
4. **中子扩散方程**: CNN-PINN (Seoul NU, 2025), FC-PINNs (JCP 2025), Laplace transform analytical solutions

**关键论文**：
- FunSearch: Romera-Paredes et al., Nature 2023 - LLM-guided evolutionary search for mathematical discovery
- LNO: Wang & Wang, NeurIPS 2024 - Latent Neural Operator with Physics-Cross-Attention
- FC-PINNs: Song et al., JCP 2025 - PINNs for neutron diffusion eigenvalue problems
- CNN-PINN: Seoul National University, 2025 - 0.63% flux error vs 3.80% baseline

**方法对比矩阵**：
| 方法类别 | 代表方法 | 精度 | 计算成本 | 适用性 |
|----------|----------|------|----------|--------|
| 传统数值 | FDM, FEM, Spectral | O(h^p) | 高（细网格） | 成熟可靠 |
| 神经网络 | PINNs, DeepONet, FNO | 10^-3-10^-6 | 训练成本高 | 无网格 |
| 演化搜索 | FunSearch, Famou | 问题依赖 | 中等 | 可解释 |

**研究缺口**：
- LLM-guided evolutionary search 尚未应用于双群中子扩散方程
- 混合诺伊曼边界条件（非齐次+齐次）的演化求解方法
- 快群-热群耦合系统的联合演化策略

**推荐Baseline**（详见 baseline-candidates.md）：
1. FDM - 金标准，易验证
2. PINN - SOTA ML方法
3. Chebyshev Spectral - 高精度基准
4. FEM - 工业标准
5. Analytical Expansion - 理论真值

### 物理方程

**快群方程**:
```
-D₁∇²φ₁ + Σᵣφ₁ = νΣf₁φ₁ + νΣf₂φ₂
```

**热群方程**:
```
-D₂∇²φ₂ + Σₐ₂φ₂ = Σ₁→₂φ₁
```

### 物理常数

| 符号 | 数值 | 含义 |
|------|------|------|
| D₁ | 1.0 | 快群扩散系数 |
| D₂ | 0.5 | 热群扩散系数 |
| Σᵣ | 0.02 | 快群移出截面 |
| Σₐ₂ | 0.1 | 热群吸收截面 |
| ν | 2.5 | 每次裂变平均中子数 |
| Σf₁ | 0.005 | 快群裂变截面 |
| Σf₂ | 0.1 | 热群裂变截面 |
| Σ₁→₂ | 0.015 | 群间转移截面 |

### 边界条件

**几何区域**: 方形区域 [-0.5, 0.5] × [-0.5, 0.5]

- **左边界** (x = -0.5): -D·∂φ/∂x = y (非零诺伊曼)
- **右边界** (x = 0.5): -D·∂φ/∂x = 0 (零诺伊曼)
- **上边界** (y = 0.5): -D·∂φ/∂y = 0 (零诺伊曼)
- **下边界** (y = -0.5): -D·∂φ/∂y = 0 (零诺伊曼)

### 验收标准

**PDE 残差计算** (在内部测试点):
- Res₁ = -D₁(φ₁,xx + φ₁,yy) + Σᵣφ₁ - (νΣf₁φ₁ + νΣf₂φ₂) → 期望 ≈ 0
- Res₂ = -D₂(φ₂,xx + φ₂,yy) + Σₐ₂φ₂ - Σ₁→₂φ₁ → 期望 ≈ 0

**边界条件残差**: 各边界上 -D·∂φ/∂n - 边界值 → 期望 = 0

---

## 团队配置

| Agent | 状态 | 职责 |
|-------|------|------|
| Team Lead | ✅ 完成 | 整体协调、任务分配、质量门禁 |
| Git & Doc Manager | ✅ 完成 | 版本控制、进度文档维护 |
| Background Researcher | ✅ 完成 | 文献调研、Introduction 前置准备 |
| Data Engineer | ✅ 完成 | 数据处理、数据集划分 |
| Famou Agent | ✅ 完成 | famou 演化框架全生命周期守护 |
| Model Developer | ✅ 完成 | 初始算法设计 (init.py) |
| Experiment Runner | ✅ 完成 | 补充实验执行、数据分析 |
| Evaluator | ✅ 完成 | 评估指标、结果对比、代码绘图 |
| Paper Writer | ✅ 完成 | 论文撰写、图表制作 |
| Strict Reviewer | ✅ 完成 | 双审稿人角色、批判性反馈 |
| Debugger | ⏳ 备用 | 异常处理、代码调试 |

---

## 实验进度

### Baseline 实验

| Rank | Method | Combined Score | Validity | Time (s) | Status |
|------|--------|---------------|----------|----------|--------|
| 1 | Chebyshev Spectral | 0.8788 | 1 | 0.14 | Best |
| 2 | PINN | 0.6780 | 1 | 0.04 | Good |
| 3 | FDM | 0.5695 | 1 | 0.35 | Moderate |
| 4 | Analytical/Polynomial | 0.5097 | 1 | 0.05 | Moderate |
| 5 | FEM | 0.0652 | 1 | 0.29 | Lower |

**最佳 Baseline**: Chebyshev Spectral (0.8788)
**Famou 目标**: 超过 0.88 综合得分

### Famou 演化实验

| 轮次 | Experiment ID | 最佳分数 | 状态 | Commit |
|------|--------------|----------|------|--------|
| Round 1 | exp-20260314112524-p3aqyn | 0.8800 | ✅ 完成 | - |
| Round 2 | exp-20260314124458-smndl2 | **0.8805** | ✅ 完成 | - |
| **最终** | - | **0.8805** | ✅ 超baseline | - |

---

## 关键决策记录

| 日期 | 决策 | 负责人 |
|------|------|--------|
| 2026-03-14 | 项目启动，组建10人Agent团队 | Team Lead |
| 2026-03-14 | 完成 init.py 初始算法设计，基于多项式拟合构造双群扩散方程解 | Model Developer |
| 2026-03-14 | 完成文献调研，输出4份文档，确定5个baseline候选方法 | Background Researcher |
| 2026-03-14 | 完成5个baseline实验 (FDM, PINN, Chebyshev, FEM, Analytical)，最佳得分0.8788 | Experiment Runner |

---

## 待办任务

### Phase 1 启动阶段
- [x] Background Researcher: 文献调研 + methodology-background.md
- [ ] Git & Doc Manager: 初始化 Git 仓库 + .gitignore
- [x] Model Developer: 设计 init.py 初稿
- [x] Baseline 实验: 确定对比方法并执行 (5个baseline完成，最佳0.8788)
- [ ] Famou Agent: 多轮演化循环
- [ ] Evaluator: 结果汇总与可视化
- [ ] Paper Writer: 论文撰写
- [ ] Strict Reviewer: 2-3轮审稿循环

---

## 项目路径

```
working/paper_work_20260313/
├── famou/                   # Famou 演化实验
│   └── task-helmholtz/      # 本任务目录
├── baselines/               # 对比实验
├── ablations/               # 消融实验
├── scripts/                 # 过程代码
│   ├── data_processing/
│   ├── analysis/
│   └── utils/
├── paper/                   # 论文
│   └── figs/                # 配图
├── CONTEXT.md               # 本文件
└── EXPERIMENTS.md           # 实验索引表
```

---

## 关键文档链接

- 任务描述: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/task_and_prompt/任务数据+描述（from 凯铭）整理版.md`
- Agent 团队配置: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/task_and_prompt/Agent团队配置方案.md`
- LaTeX 模板: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/Arxiv_PRIME_AI_Style_Template`

---

*最后更新: 2026-03-14 by Experiment Runner*
