import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# 从表格中提取的数据
payloads = [0, 2.3, 4.5, 6.8, 9.1, 11.3, 13.6, 15.9]
battery_coeffs = [0.000, 0.166, 0.334, 0.468, 0.560, 0.640, 0.750, 0.785]


# 定义拟合函数 - 逻辑增长模型
def battery_decay(x, a, b, c):
    return a * (1 - np.exp(-b * x)) + c * x


# 使用曲线拟合确定最佳参数
p0 = [0.8, 0.1, 0.01]  # 初始参数估计
params, _ = curve_fit(battery_decay, payloads, battery_coeffs, p0=p0)
a_fit, b_fit, c_fit = params

# 创建专业的数据可视化
plt.figure(figsize=(10, 6))
plt.grid(True, linestyle='--', alpha=0.7)

# 绘制原始数据点
plt.scatter(payloads, battery_coeffs, color='red', s=80, zorder=5,
            label='Measured Data')

# 生成拟合曲线
x_fit = np.linspace(0, 16, 100)
y_fit = battery_decay(x_fit, a_fit, b_fit, c_fit)

# 绘制拟合曲线
plt.plot(x_fit, y_fit, 'b-', linewidth=2.5,
         label=f'Fit: {a_fit:.3f}(1 - exp(-{b_fit:.3f}x)) + {c_fit:.3f}x')

# 标记关键数据点


plt.annotate('Max loaded point at 15.9kg', xy=(15.9, 0.785), xytext=(10, 0.65),
             arrowprops=dict(facecolor='black', shrink=0.05),
             fontsize=10, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"))

# 美化图表
plt.title('Battery Attenuation Coefficient vs Payload', fontsize=14, pad=15)
plt.xlabel('Payload (kg)', fontsize=12, labelpad=10)
plt.ylabel('Battery Attenuation Coefficient', fontsize=12, labelpad=10)
plt.legend(loc='lower right', fontsize=11)

plt.xlim(-0.5, 16.5)
plt.ylim(-0.05, 0.85)
plt.tight_layout()
plt.show()


# 定义用于计算电池衰减系数的Python函数
def calculate_battery_attenuation(payload):
    """
    计算给定有效载荷下的电池衰减系数

    参数:
        payload (float): 有效载荷重量 (kg), 范围0-15.9kg

    返回:
        float: 电池衰减系数
    """
    # 验证输入是否在有效范围内
    if payload < 0 or payload > 15.9:
        raise ValueError("Payload must be between 0 and 15.9 kg")

    # 使用拟合公式计算衰减系数
    a, b, c = 0.810, 0.163, 0.006
    return a * (1 - np.exp(-b * payload)) + c * payload


# 测试函数
test_payloads = [0, 5, 10, 15.9]
for p in test_payloads:
    coeff = calculate_battery_attenuation(p)
    print(f"Payload: {p} kg → Attenuation Coefficient: {coeff:.3f}")