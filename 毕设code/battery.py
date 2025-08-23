import numpy as np
def calculate_battery_attenuation(payload):
    """
    计算给定有效载荷下的电池衰减系数
    参数:
        payload (float): 有效载荷重量 (kg), 范围0-15.9kg
    返回:
        float: 电池衰减系数
    """
    if payload < 0 or payload > 15.9:
        raise ValueError("Payload must be between 0 and 15.9 kg")
    a, b, c = 0.810, 0.163, 0.006
    return a * (1 - np.exp(-b * payload)) + c * payload