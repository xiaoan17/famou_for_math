## 目标
<!-- READONLY：为 FaMou 进化任务准备 init.py、evaluator.py 和 prompt.md -->

## 1. 任务定义

- **核心问题描述**：为二维有限均匀介质双群中子扩散方程（含非零诺伊曼边界条件）设计高精度数值求解算法。域为 [-0.5,0.5]^2，求解两个耦合通量场 phi1(x,y)（快群）和 phi2(x,y)（热群）。
- **输入**：无命令行参数；算法直接在脚本内定义并在 solution() 函数中返回结果
- **输出**：标准输出 JSON，包含 phi1/phi2 在 4 个测试点的值；脚本必须实现 `solution()` 函数，返回两个可调用对象 (phi1_func, phi2_func)，支持任意 (x,y) 查询
- **主要优化目标**：最小化解在4个测试点上与解析解的误差，同时满足 PDE 残差 < 1e-4 和 BC 残差 < 1e-4
- **关键指标**：`combined_score = 1 / (1 + mean_relative_error)`，越高越好（完美解 = 1.0）

## 2. 数据描述

- **数据来源**：无外部数据文件；物理常数直接在代码中定义
- **物理常数**：
  - D1=1.0, D2=0.5, Sigma_r=0.02, Sigma_a2=0.1
  - nu=2.5, Sigma_f1=0.005, Sigma_f2=0.1, Sigma_12=0.015
  - A11 = Sigma_r - nu*Sigma_f1 = 0.0075
  - A12 = -nu*Sigma_f2 = -0.25
  - A21 = -Sigma_12 = -0.015
  - A22 = Sigma_a2 = 0.1
- **PDE**：
  - -D1*lap(phi1) + A11*phi1 + A12*phi2 = 0
  - -D2*lap(phi2) + A21*phi1 + A22*phi2 = 0
- **边界条件（诺伊曼）**：
  - 左边界 x=-0.5: -D_g * dphi_g/dx = y (非零)
  - 右边界 x=+0.5: -D_g * dphi_g/dx = 0
  - 上边界 y=+0.5: -D_g * dphi_g/dy = 0
  - 下边界 y=-0.5: -D_g * dphi_g/dy = 0
- **测试点**：(0,0), (0.2,0.2), (-0.2,-0.3), (0.4,-0.4)
- **解析解参考值**（由 analytical_solver.py 计算，N_terms=500）：
  路径：../scripts/numerical_solver/analytical_solver.py

## 3. 评估器

### 接口（READONLY）
```python
def evaluate(path_user_py: str, task_name: str = "default", timeout: int = 3600) -> dict:
    return {
        "validity": float,        # 0 或 1；1 表示满足所有硬约束
        "combined_score": float,  # 为可行解打分，0表示无效解，低分表示低质量解，高分表示高质量解
        "cost_time": float,       # 评估花费时间
        "error_info": str,        # 成功时为 ""
    }
```

### 评估流程
1. 导入候选解脚本，调用 `solution()` 获取 (phi1_func, phi2_func)
2. 在4个测试点计算 phi1/phi2 值
3. 与解析解参考值对比，计算相对误差
4. 计算 PDE 残差（在测试点用解析偏导或数值差分）
5. 计算 BC 残差（在边界采样点）
6. 综合打分

### 硬约束
- `solution()` 函数必须存在且可调用
- 返回值必须是两个可调用对象 (phi1_func, phi2_func)，接受 (x, y) 两个浮点数
- 脚本执行不得崩溃（超时或异常 → validity=0）
- phi1/phi2 在测试点必须为有限浮点数（非 NaN/Inf）

### 软约束
- 与解析解的平均相对误差越小越好
- PDE 残差 < 1e-4 → 高分；PDE 残差 < 1e-2 → 中分；> 1e-2 → 低分
- BC 残差 < 1e-4 → 高分
- 计算速度（次要）

### 系统级约束（READONLY）
- 无论 init.py 是否与 evaluator.py 同目录，评估器必须能正确执行
- 如果使用 subprocess 调用子进程，必须将 cwd 设置为 evaluator.py 所在目录
- 不得依赖临时目录作为工作目录

## 4. 初始解

`init.py` 使用有限差分法（FDM）作为初始基线：101×101 网格，scipy 稀疏求解，实现 `solution()` 函数返回双线性插值的 (phi1_func, phi2_func)。

## 5. 进化提示（prompt.md，<=100 行）

见 prompt.md 文件

## 6. 补充信息

- 解析解实现位于：`../scripts/numerical_solver/analytical_solver.py`
- 解析解方法：Fourier-cosine 展开 + 矩阵 D^{-1}A 特征分解 + cosh x 方向解 + 左边界系数匹配
- 演化目标：在保证物理正确性的前提下，探索比解析解更通用（可扩展到非均匀介质）的数值算法
