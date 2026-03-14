# PROGRESS.md - 项目进度跟踪

**项目**: 二维有限均匀介质边界源双群中子扩散方程解析解
**任务 ID**: Analytical Solution Helmholtz
**目标**: 顶会论文 (16页 PDF)
**最后更新**: 2026-03-14

---

## 总体进度

```
Phase 1: 论文复现 [████████░░░░░░░░░░░░] 10%
Phase 2: 创新改进 [░░░░░░░░░░░░░░░░░░░░] 0%
Phase 3: 论文撰写 [░░░░░░░░░░░░░░░░░░░░] 0%
```

---

## 当前阶段: Phase 1 - 论文复现

### 阶段目标
复现基准方法，建立 Famou 演化框架，获得可对比的实验结果。

### 任务清单

#### 1. 项目初始化
- [x] 初始化 Git 仓库
- [x] 配置 .gitignore
- [x] 创建项目文档结构 (EXPERIMENTS.md, PROGRESS.md, README.md)
- [x] 创建防错位机制 (paper_results_registry.json)
- [ ] Background Researcher: 文献调研
- [ ] Background Researcher: 撰写 methodology-background.md

#### 2. 数据准备
- [ ] Data Engineer: 数据集分析与划分
- [ ] Data Engineer: 数据预处理脚本
- [ ] Data Engineer: 验证数据正确性

#### 3. 初始算法设计
- [ ] Model Developer: 设计 init.py 初稿
- [ ] Model Developer: 编写 evaluator.py
- [ ] Model Developer: 本地验证初始算法

#### 4. Baseline 实验
- [ ] 确定对比方法列表
- [ ] 实现 Baseline 1
- [ ] 实现 Baseline 2
- [ ] 实现 Baseline 3
- [ ] 汇总 Baseline 结果

#### 5. Famou 演化实验
- [ ] Famou Agent: 准备 problem.md
- [ ] Famou Agent: 准备 prompt.md
- [ ] Famou Agent: Round 1 演化
- [ ] Famou Agent: Round 2 演化
- [ ] Famou Agent: Round 3 演化
- [ ] Famou Agent: Round 4 演化
- [ ] Famou Agent: Round 5 演化
- [ ] Famou Agent: 选择最优程序

#### 6. 结果分析
- [ ] Evaluator: 对比 Famou vs Baseline
- [ ] Evaluator: 生成可视化图表
- [ ] Evaluator: 撰写结果分析

---

## Agent 状态看板

| Agent | 当前任务 | 状态 | 进度 |
|-------|----------|------|------|
| Team Lead | 项目启动 | 活跃 | - |
| Git & Doc Manager | 初始化仓库 | 进行中 | 90% |
| Background Researcher | 待分配 | 待启动 | - |
| Data Engineer | 待分配 | 待启动 | - |
| Famou Agent | 待分配 | 待启动 | - |
| Model Developer | 待分配 | 待启动 | - |
| Experiment Runner | 待分配 | 待启动 | - |
| Evaluator | 待分配 | 待启动 | - |
| Paper Writer | 待分配 | 待启动 | - |
| Strict Reviewer | 待分配 | 待启动 | - |
| Debugger | 备用 | 待命 | - |

---

## 关键里程碑

| 里程碑 | 计划日期 | 实际日期 | 状态 |
|--------|----------|----------|------|
| 项目启动 | 2026-03-14 | 2026-03-14 | 完成 |
| Git 仓库初始化 | 2026-03-14 | - | 进行中 |
| 文献调研完成 | 2026-03-15 | - | 待启动 |
| init.py 完成 | 2026-03-16 | - | 待启动 |
| Baseline 完成 | 2026-03-18 | - | 待启动 |
| Famou Round 5 完成 | 2026-03-22 | - | 待启动 |
| Phase 1 完成 | 2026-03-24 | - | 待启动 |

---

## 阻塞事项

| 问题 | 影响 | 解决方案 | 状态 |
|------|------|----------|------|
| 无 | - | - | - |

---

## 决策记录

| 日期 | 决策 | 负责人 | 理由 |
|------|------|--------|------|
| 2026-03-14 | 项目启动，组建10人Agent团队 | Team Lead | 覆盖完整研究生命周期 |
| 2026-03-14 | 使用 Famou 演化框架 | Team Lead | 自动化代码演化，提升效率 |

---

## 下一步行动

1. **Git & Doc Manager**: 完成初始 commit
2. **Team Lead**: 分配任务给 Background Researcher
3. **Background Researcher**: 开始文献调研

---

## 附录

### 文档索引

- [CONTEXT.md](./CONTEXT.md) - 项目上下文
- [EXPERIMENTS.md](./EXPERIMENTS.md) - 实验索引表
- [README.md](./README.md) - 项目说明

### 关键路径

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
├── CONTEXT.md               # 项目上下文
├── EXPERIMENTS.md           # 实验索引表
├── PROGRESS.md              # 本文件
└── README.md                # 项目说明
```
