import matplotlib.pyplot as plt
import numpy as np

# Data from the table
flight_times = [50, 41.7, 33.3, 26.6, 22, 18, 12.5, 10.75]
payloads = [0, 2.3, 4.5, 6.8, 9.1, 11.3, 13.6, 15.9]

# Create professional data visualization
plt.figure(figsize=(10, 6), dpi=100)

# Plot main curve and scatter points
plt.plot(payloads, flight_times, 'o-', color='#1f77b4',
         markersize=8, linewidth=2.5, markerfacecolor='white',
         markeredgewidth=2, label='Measured Data')

# Add data labels
for i, (payload, time) in enumerate(zip(payloads, flight_times)):
    plt.annotate(f'({payload}, {time})',
                 xy=(payload, time),
                 xytext=(payload+0.5, time+1),
                 fontsize=9)

# Add trend line (quadratic polynomial fit)
z = np.polyfit(payloads, flight_times, 2)
p = np.poly1d(z)
plt.plot(payloads, p(payloads), 'r--', linewidth=1.5, alpha=0.7, label='Trend Line')

# Enhance the chart appearance
plt.title('Drone Payload vs Flight Time Relationship', fontsize=14, pad=20)
plt.xlabel('Payload (kg)', fontsize=12, labelpad=10)
plt.ylabel('Flight Time (min)', fontsize=12, labelpad=10)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.tight_layout()

# Set axis limits
plt.xlim(min(payloads)-1, max(payloads)+2)
plt.ylim(min(flight_times)-5, max(flight_times)+5)

plt.show()