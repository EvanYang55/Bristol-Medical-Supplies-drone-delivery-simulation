import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 从图表中提取的数据
temperatures = np.array([0, 10, 20, 30, 40, 50])
degradation_rates = np.array([0.0, 0.0, 0.05298, 0.12583, 0.19868, 0.2649])


# 定义拟合函数 - 指数增长模型
def degradation_model(x, a, b, c):
    """电池降解速率与温度的关系模型"""
    return a * np.exp(b * x) + c


# 执行曲线拟合
initial_guess = [0.001, 0.05, -0.1]  # 初始参数估计
params, covariance = curve_fit(degradation_model,
                               temperatures,
                               degradation_rates,
                               p0=initial_guess,
                               bounds=([0, 0.01, -0.5], [0.1, 0.2, 0.1]))

# 提取拟合参数
a_fit, b_fit, c_fit = params
print(f"拟合参数: a = {a_fit:.6f}, b = {b_fit:.6f}, c = {c_fit:.6f}")

# 创建专业的数据可视化
plt.figure(figsize=(12, 7))
plt.grid(True, linestyle='--', alpha=0.5)

# 绘制原始数据点
plt.scatter(temperatures, degradation_rates,
            color='red', s=120, zorder=5,
            label='Measured Data')

# 生成拟合曲线
temp_range = np.linspace(0, 55, 100)
deg_rate_fit = degradation_model(temp_range, a_fit, b_fit, c_fit)

# 绘制拟合曲线
plt.plot(temp_range, deg_rate_fit, 'b-', linewidth=2.5,
         label=f'Fit: y = {a_fit:.6f} * exp({b_fit:.4f}x) + {c_fit:.6f}')



# 美化图表
plt.title('Battery Degradation Rate vs Temperature', fontsize=16, pad=15)
plt.xlabel('Temperature (°C)', fontsize=13, labelpad=10)
plt.ylabel('Battery Degradation Rate', fontsize=13, labelpad=10)
plt.legend(loc='upper left', fontsize=11)

plt.xlim(-2, 55)
plt.ylim(-0.02, 0.32)
plt.tight_layout()


plt.show()


# 定义电池衰减系数计算函数
def battery_degradation(temperature):
    """
    计算给定温度下的电池降解速率

    参数:
        temperature (float): 环境温度 (°C), 范围0-50°C

    返回:
        float: 电池降解速率
    """
    # 验证输入是否在有效范围内
    if temperature < 0 or temperature > 50:
        raise ValueError("Temperature must be between 0°C and 50°C")

    # 使用拟合参数进行计算
    a, b, c = 0.000126, 0.1288, -0.000126
    degradation = a * np.exp(b * temperature) + c

    # 确保在低温下返回0
    return max(degradation, 0.0)

