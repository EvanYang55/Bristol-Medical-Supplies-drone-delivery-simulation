import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# Data preparation from the image
temperatures = [0, 10, 20, 30, 40, 50]  # Temperature (°C)
altitudes = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000,
             9000, 10000, 11000, 12000, 13000, 14000, 15000]  # Altitude (ft)

# Maximum Gross Weight data (kg) from the image
weight_data = np.array([
    [15.1, 15.1, 15.1, 14.4, 13.3, 12.3],
    [15.1, 15.1, 14.3, 13.2, 12.1, 11.1],
    [15.1, 14.2, 13.1, 12.0, 11.0, 10.0],
    [14.2, 13.0, 11.9, 10.8, 9.9, 8.9],
    [13.0, 11.8, 10.7, 9.7, 8.8, 7.9],
    [11.8, 10.6, 9.6, 8.6, 7.7, 6.9],
    [10.6, 9.5, 8.5, 7.6, 6.7, 5.9],
    [9.5, 8.4, 7.5, 6.6, 5.7, 4.9],
    [8.4, 7.4, 6.5, 5.6, 4.8, 4.0],
    [7.3, 6.4, 5.5, 4.6, 3.9, 3.1],
    [6.3, 5.4, 4.5, 3.7, 3.0, 2.2],
    [5.3, 4.4, 3.6, 2.8, 2.1, 1.4],
    [4.3, 3.5, 2.7, 1.9, 1.2, 0.6],
    [3.4, 2.6, 1.8, 1.1, 0.4, -0.2],
    [2.5, 1.7, 1.0, 0.3, -0.4, -1.0],
    [1.6, 0.9, 0.1, -0.5, -1.1, -1.7]
])

# Create meshgrid boundaries
T_bound = np.arange(0, 61, 10)  # Temperature boundaries 0-60°C
A_bound = np.arange(0, 16001, 1000)  # Altitude boundaries 0-16000 ft
T_mesh, A_mesh = np.meshgrid(T_bound, A_bound)

# Create custom colormap: blue-yellow for positives, red for negatives
colors = ["#1f77b4", "#a8e61d", "#ffcc00"]  # blue -> green -> yellow
pos_cmap = LinearSegmentedColormap.from_list("positive", colors)
neg_cmap = LinearSegmentedColormap.from_list("negative", ["#d62728", "#d62728"])  # solid red

# Normalize data separately for positive and negative regions
positive_mask = weight_data >= 0
negative_mask = weight_data < 0

# Create a new array with masked negative values
masked_data = np.where(negative_mask, np.nan, weight_data)

# Create figure
plt.figure(figsize=(14, 9))

# Plot positive values with color gradient
pos_plot = plt.pcolormesh(T_mesh, A_mesh, masked_data,
                          cmap=pos_cmap,
                          vmin=0, vmax=16,
                          shading='flat',
                          edgecolor='black',
                          linewidth=0.5)

# Plot negative values in red
plt.pcolormesh(T_mesh, A_mesh, np.where(negative_mask, -1, np.nan),  # set all negatives to same value
               cmap=neg_cmap,
               vmin=-2, vmax=0,
               shading='flat',
               edgecolor='black',
               linewidth=0.5)

# Add colorbar for positive values
cbar = plt.colorbar(pos_plot, shrink=0.75, extend='max')
cbar.set_label('Maximum Payload Weight (kg)', fontsize=12)
cbar.ax.tick_params(labelsize=10)

# Add text annotations only for positive values
for i in range(len(altitudes)):
    for j in range(len(temperatures)):
        val = weight_data[i, j]
        # Only add text if value is non-negative
        if val >= 0:
            # Position at cell centers
            x_pos = temperatures[j] + 5
            y_pos = altitudes[i] + 500

            # Choose text color for contrast
            text_color = 'white' if val < 3 else 'black'

            plt.text(x_pos, y_pos, f'{val:.1f}',
                     ha='center', va='center',
                     fontsize=9, color=text_color)

# Add negative zone indicator
plt.annotate('NEGATIVE ZONE (No payload capacity)',
             xy=(40, 14000),
             xytext=(28, 12000),
             arrowprops=dict(arrowstyle="->", color='red', linewidth=1.5),
             fontsize=12, color='red', weight='bold')

# Format graph
plt.title('Maximum Payload Weight vs Temperature and Altitude', fontsize=16, pad=20)
plt.xlabel('Temperature (°C)', fontsize=14)
plt.ylabel('Pressure Altitude (ft)', fontsize=14)

# Set ticks at correct positions
plt.xticks(T_bound, labels=[f'{t}°C' for t in T_bound])
plt.yticks(A_bound[::2], labels=[f'{a:,}' for a in A_bound[::2]])

# Add grid for better readability
plt.grid(True, color='gray', linestyle='--', alpha=0.3)

# Invert y-axis for altitude representation
plt.gca().invert_yaxis()

# Add legend for negative zone
red_patch = mpl.patches.Patch(color='#d62728', label='Negative Weight (No payload capacity)')
plt.legend(handles=[red_patch], loc='upper right', fontsize=11)

plt.tight_layout()
plt.savefig('gross_weight_heatmap_with_negatives.png', dpi=300, bbox_inches='tight')
plt.show()