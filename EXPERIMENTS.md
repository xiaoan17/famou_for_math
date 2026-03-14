# EXPERIMENTS.md - 实验索引表

**项目**: 二维有限均匀介质边界源双群中子扩散方程解析解
**任务 ID**: Analytical Solution Helmholtz
**最后更新**: 2026-03-14

---

## 实验总览

| 类别 | 数量 | 状态 |
|------|------|------|
| Baseline 实验 | 0 | 待启动 |
| Famou 演化实验 | 0 | 待启动 |
| 消融实验 | 0 | 待启动 |

---

## 1. Baseline 实验索引

| 方法名称 | 来源 | 实验ID | 核心指标 | 状态 | Commit |
|----------|------|--------|----------|------|--------|
| 待补充 | - | - | - | 待启动 | - |

### Baseline 结果汇总

```json
{
  "baselines": {},
  "summary": {
    "best_method": null,
    "best_score": null
  }
}
```

---

## 2. Famou 演化实验索引

### Task: helmholtz

| 轮次 | Experiment ID | 最佳分数 | 程序路径 | 状态 | Commit |
|------|--------------|----------|----------|------|--------|
| Round 1 | - | - | - | 待启动 | - |
| Round 2 | - | - | - | 待启动 | - |
| Round 3 | - | - | - | 待启动 | - |
| Round 4 | - | - | - | 待启动 | - |
| Round 5 | - | - | - | 待启动 | - |

### Famou 最终结果

| 文件 | 路径 | 说明 |
|------|------|------|
| 最优程序 | `famou/task-helmholtz/best_program.py` | 最终交付代码 |
| 结果汇总 | `famou/task-helmholtz/results.json` | 所有指标 |
| 演化日志 | `famou/task-helmholtz/evolution_log.json` | 完整演化记录 |

---

## 3. 消融实验索引

| 实验名称 | 变体描述 | 实验ID | 核心指标 | 状态 | Commit |
|----------|----------|--------|----------|------|--------|
| 待补充 | - | - | - | 待启动 | - |

---

## 4. 实验依赖关系

```
Phase 1: 论文复现
├── Baseline 实验
│   ├── Method 1
│   ├── Method 2
│   └── Method 3
├── Famou 演化
│   ├── Round 1 → Round 2 → Round 3 → Round 4 → Round 5
│   └── Final Selection
└── 消融实验
    ├── Ablation 1
    └── Ablation 2
```

---

## 5. 快速链接

- **工作目录**: `/Users/anbc/baidu_工作文件/agent_for_science/phase_2/working/paper_work_20260313/`
- **Famou 目录**: `famou/task-helmholtz/`
- **Baseline 目录**: `baselines/`
- **消融目录**: `ablations/`
- **分析脚本**: `scripts/analysis/`

---

## 6. 更新记录

| 日期 | 更新内容 | 更新人 |
|------|----------|--------|
| 2026-03-14 | 初始化实验索引表 | Git & Doc Manager |
