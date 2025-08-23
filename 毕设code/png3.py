import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# 从图片中提取的数据
temperatures = ['0°C', '10°C', '20°C', '30°C', '40°C', '50°C']
degradation_rates = [0, 0, 0.052980132, 0.125827815, 0.198675497, 0.264900662]
pressure_altitude = 1000  # 压力高度（英尺）

# 创建渐变色（浅蓝到深蓝）
colors = ['#ADD8E6', '#87CEEB', '#1E90FF', '#0000CD', '#00008B', '#000080']
cmap = mcolors.LinearSegmentedColormap.from_list("blue_gradient", colors)
norm = mcolors.Normalize(vmin=0, vmax=len(temperatures)-1)

# 创建图表
plt.figure(figsize=(12, 8))

# 创建柱状图
bars = plt.bar(temperatures, degradation_rates,
               color=[cmap(norm(i)) for i in range(len(temperatures))],
               edgecolor='black',
               linewidth=1.5,
               width=0.7)

# 添加数据标签
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.005,
             f'{degradation_rates[i]:.5f}',
             ha='center', va='bottom',
             fontsize=10,
             fontweight='bold')

# 设置图表标题和标签
plt.title('Battery Degradation Rate VS Temperature',
          fontsize=16, pad=20, fontweight='bold')
plt.xlabel('Temperature', fontsize=14, labelpad=15)
plt.ylabel('Degradation Rate', fontsize=14, labelpad=15)

# 设置Y轴范围
plt.ylim(0, 0.3)

# 添加压力高度信息
plt.text(0.5, -0.15, f'Pressure Altitude: {pressure_altitude:,} ft',
         ha='center', va='center',
         transform=plt.gca().transAxes,
         fontsize=12,
         bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="blue", lw=1.5))

# 添加网格线
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 添加图例说明
plt.legend(['Degradation Rate increases with temperature'],
           loc='upper left', frameon=True, framealpha=0.9)

# 添加关键观察点
plt.annotate('Higher temperatures accelerate battery degradation.',
             xy=(3.5, 0.27),
             xytext=(1.5, 0.28),
             fontsize=12, color='red', weight='bold')


# 调整布局
plt.tight_layout()
plt.subplots_adjust(bottom=0.15)  # 为底部文本留出空间

# 保存并显示
plt.savefig('battery_degradation_vs_temperature.png', dpi=300, bbox_inches='tight')
plt.show()