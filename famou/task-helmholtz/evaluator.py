"""
双群中子扩散方程解的评估器
验证PDE残差和边界条件
"""

import numpy as np
import time
import sys
import os


def evaluate(path_user_py: str, task_name: str = "default", timeout: int = 3600) -> dict:
    """
    评估候选解的质量

    Args:
        path_user_py: 候选解文件路径 (init.py)
        task_name: 任务名称
        timeout: 超时时间（秒）

    Returns:
        dict: 包含以下字段
            - validity: 0 或 1，表示是否满足所有硬约束
            - combined_score: 综合得分，0表示无效，越高表示质量越好
            - cost_time: 评估耗时
            - error_info: 错误信息，成功时为 ""
    """
    start_time = time.time()

    try:
        # 加载用户解
        import importlib.util
        spec = importlib.util.spec_from_file_location("user_solution", path_user_py)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        # 检查solution函数是否存在
        if not hasattr(user_module, 'solution'):
            return {
                "validity": 0,
                "combined_score": 0,
                "cost_time": time.time() - start_time,
                "error_info": "Missing 'solution' function"
            }

        # 获取解函数
        phi1, phi2 = user_module.solution()

        # 物理常数
        D1 = 1.0
        D2 = 0.5
        SIGMA_R = 0.02
        SIGMA_A2 = 0.1
        NU = 2.5
        SIGMA_F1 = 0.005
        SIGMA_F2 = 0.1
        SIGMA_12 = 0.015

        # 测试内部点（均匀网格）
        x_test = np.linspace(-0.4, 0.4, 9)
        y_test = np.linspace(-0.4, 0.4, 9)
        X, Y = np.meshgrid(x_test, y_test)

        try:
            val1, d1_dx, d1_dy, d2_1_dx2, d2_1_dy2 = phi1(X, Y)
            val2, d2_dx, d2_dy, d2_2_dx2, d2_2_dy2 = phi2(X, Y)
        except Exception as e:
            return {
                "validity": 0,
                "combined_score": 0,
                "cost_time": time.time() - start_time,
                "error_info": f"Error evaluating functions: {str(e)}"
            }

        # 计算PDE残差
        res1 = -D1*(d2_1_dx2 + d2_1_dy2) + SIGMA_R*val1 - (NU*SIGMA_F1*val1 + NU*SIGMA_F2*val2)
        res2 = -D2*(d2_2_dx2 + d2_2_dy2) + SIGMA_A2*val2 - SIGMA_12*val1

        res1_max = np.max(np.abs(res1))
        res2_max = np.max(np.abs(res2))

        # 测试边界条件
        y_grid = np.linspace(-0.5, 0.5, 21)
        x_grid = np.linspace(-0.5, 0.5, 21)

        # 左边界 x = -0.5: -D * dphi/dx = y
        x_left = np.full_like(y_grid, -0.5)
        _, d1_dx_left, _, _, _ = phi1(x_left, y_grid)
        _, d2_dx_left, _, _, _ = phi2(x_left, y_grid)
        bc1_left = np.max(np.abs(-D1 * d1_dx_left - y_grid))
        bc2_left = np.max(np.abs(-D2 * d2_dx_left - y_grid))

        # 右边界 x = 0.5: -D * dphi/dx = 0
        x_right = np.full_like(y_grid, 0.5)
        _, d1_dx_right, _, _, _ = phi1(x_right, y_grid)
        _, d2_dx_right, _, _, _ = phi2(x_right, y_grid)
        bc1_right = np.max(np.abs(-D1 * d1_dx_right))
        bc2_right = np.max(np.abs(-D2 * d2_dx_right))

        # 上边界 y = 0.5: -D * dphi/dy = 0
        y_top = np.full_like(x_grid, 0.5)
        _, _, d1_dy_top, _, _ = phi1(x_grid, y_top)
        _, _, d2_dy_top, _, _ = phi2(x_grid, y_top)
        bc1_top = np.max(np.abs(-D1 * d1_dy_top))
        bc2_top = np.max(np.abs(-D2 * d2_dy_top))

        # 下边界 y = -0.5: -D * dphi/dy = 0
        y_bottom = np.full_like(x_grid, -0.5)
        _, _, d1_dy_bottom, _, _ = phi1(x_grid, y_bottom)
        _, _, d2_dy_bottom, _, _ = phi2(x_grid, y_bottom)
        bc1_bottom = np.max(np.abs(-D1 * d1_dy_bottom))
        bc2_bottom = np.max(np.abs(-D2 * d2_dy_bottom))

        # 计算综合得分（越小越好，所以取倒数）
        # 使用加权组合
        pde_weight = 1.0
        bc_weight = 1.0

        pde_score = (res1_max + res2_max) / 2.0
        bc_score = (bc1_left + bc2_left + bc1_right + bc2_right +
                    bc1_top + bc2_top + bc1_bottom + bc2_bottom) / 8.0

        total_error = pde_weight * pde_score + bc_weight * bc_score

        # 转换为得分（越大越好）
        # 使用指数衰减: score = exp(-total_error)
        combined_score = np.exp(-total_error)

        # 判断是否有效（所有残差有限且函数可计算）
        validity = 1
        error_info = ""

        # 检查是否有NaN或Inf
        if (np.any(np.isnan(val1)) or np.any(np.isnan(val2)) or
            np.any(np.isinf(val1)) or np.any(np.isinf(val2))):
            validity = 0
            combined_score = 0
            error_info = "NaN or Inf in solution values"

        cost_time = time.time() - start_time

        return {
            "validity": validity,
            "combined_score": float(combined_score),
            "cost_time": cost_time,
            "error_info": error_info
        }

    except Exception as e:
        return {
            "validity": 0,
            "combined_score": 0,
            "cost_time": time.time() - start_time,
            "error_info": f"Evaluation error: {str(e)}"
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <path_to_init.py>")
        sys.exit(1)

    path = sys.argv[1]
    result = evaluate(path)
    print(f"Validity: {result['validity']}")
    print(f"Combined Score: {result['combined_score']:.6f}")
    print(f"Cost Time: {result['cost_time']:.4f}s")
    print(f"Error Info: '{result['error_info']}'")
