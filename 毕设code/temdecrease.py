import numpy as np
def battery_degradation(temperature):
    """
    计算给定温度下的电池衰减率

    参数:
        temperature (float): 环境温度 (°C), 范围0-50°C

    返回:
        float: 电池衰减率
    """
    if temperature < 0 or temperature > 50:
        raise ValueError("Temperature must be between 0°C and 50°C")

    a, b, c = 0.000126, 0.1288, -0.000126
    degradation = a * np.exp(b * temperature) + c

    # 确保在低温下返回0
    return max(degradation, 0.0)