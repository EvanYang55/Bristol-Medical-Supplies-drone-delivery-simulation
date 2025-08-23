import matplotlib.pyplot as plt
import numpy as np

# 从图片中提取的数据
temperatures = [0, 10, 20, 30, 40, 50]  # 温度 (°C)
payload_weights = [15.1, 15.1, 14.3, 13.2, 12.1, 11.1]  # 最大有效载荷重量 (kg)
altitude = 1000  # 压力高度 (英尺)

# 创建图表
plt.figure(figsize=(10, 6))

# 绘制折线图
plt.plot(temperatures, payload_weights,
         marker='o',
         markersize=8,
         linewidth=2.5,
         color='#1f77b4',  # 与图片相似的蓝色
         markerfacecolor='#ffcc00')  # 黄色标记点

# 添加数据标签
for i, weight in enumerate(payload_weights):
    plt.text(temperatures[i], weight + 0.2, f'{weight} kg',
             ha='center', va='bottom',
             fontsize=10, fontweight='bold')

# 设置图表标题和标签
plt.title('Maximum Payload Weight vs Temperature at 1,000 ft Pressure Altitude',
          fontsize=14, pad=15)
plt.xlabel('Temperature (°C)', fontsize=12)
plt.ylabel('Maximum Payload Weight (kg)', fontsize=12)

# 设置坐标轴范围
plt.xlim(-5, 55)
plt.ylim(10, 16)

# 设置网格线
plt.grid(True, linestyle='--', alpha=0.7)

# 添加背景色渐变（模仿原图风格）
ax = plt.gca()
ax.set_facecolor('#e6f7ff')  # 浅蓝色背景

# 添加高度信息标注
plt.annotate(f'Pressure Altitude: {altitude:,} ft',
             xy=(0.05, 0.95),
             xycoords='axes fraction',
             fontsize=11,
             bbox=dict(boxstyle="round,pad=0.3", fc="#d4f0fc", ec="#1f77b4", lw=1.5))

# 调整布局并显示
plt.tight_layout()
plt.savefig('payload_vs_temperature.png', dpi=300)
plt.show()