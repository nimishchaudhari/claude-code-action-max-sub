#!/usr/bin/env python3
"""
Generate a logarithmic graph of the first 100 decimals of Pi using matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

# First 100 decimals of Pi
pi_decimals = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

# Convert to list of integers
digits = [int(d) for d in pi_decimals]

# Calculate log10(digit + 1) to avoid log(0)
log_values = [np.log10(d + 1) for d in digits]

# Create figure with better size for readability
plt.figure(figsize=(16, 10))

# Create color map for digits 0-9
colors = plt.cm.viridis(np.linspace(0, 1, 10))
bar_colors = [colors[d] for d in digits]

# Create bar chart
positions = np.arange(len(digits))
bars = plt.bar(positions, log_values, color=bar_colors, edgecolor='black', linewidth=0.5)

# Customize the plot
plt.title('Logarithmic Graph of First 100 Decimals of Pi', fontsize=20, fontweight='bold', pad=20)
plt.xlabel('Position in Pi Decimal Sequence', fontsize=14)
plt.ylabel('log₁₀(digit + 1)', fontsize=14)
plt.grid(True, alpha=0.3, linestyle='--')

# Add value labels on top of bars (every 10th bar to avoid clutter)
for i in range(0, len(digits), 10):
    plt.text(i, log_values[i] + 0.02, str(digits[i]), 
             ha='center', va='bottom', fontsize=8)

# Create legend for digit colors
from matplotlib.patches import Rectangle
legend_elements = [Rectangle((0,0),1,1, facecolor=colors[i], 
                           edgecolor='black', label=f'Digit {i}')
                  for i in range(10)]
plt.legend(handles=legend_elements, loc='upper right', ncol=2, 
          title='Digit Colors', fontsize=10)

# Add statistics box
stats_text = f"Pi decimals: {pi_decimals}\n\n"
stats_text += "Digit Distribution:\n"
for i in range(10):
    count = digits.count(i)
    percentage = (count / len(digits)) * 100
    stats_text += f"  {i}: {count} ({percentage:.1f}%)\n"

# Place statistics box
plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
         fontsize=9, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Set x-axis limits and ticks
plt.xlim(-1, len(digits))
plt.xticks(range(0, len(digits), 10))

# Set y-axis limits
plt.ylim(0, 1.1)

# Add horizontal line at y=0.5 for reference
plt.axhline(y=0.5, color='red', linestyle=':', alpha=0.5, label='log₁₀(√10) ≈ 0.5')

# Tight layout to prevent label cutoff
plt.tight_layout()

# Save as PNG files
plt.savefig('pi_log_graph.png', dpi=150, bbox_inches='tight')
plt.savefig('pi_log_graph_hires.png', dpi=300, bbox_inches='tight')

# Also save to BytesIO for base64 encoding
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
buffer.seek(0)
image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

print("Graphs saved successfully!")
print(f"Standard resolution: pi_log_graph.png")
print(f"High resolution: pi_log_graph_hires.png")
print(f"\nBase64 encoded image (first 100 chars): {image_base64[:100]}...")

# Show the plot (won't display in GitHub Actions, but useful for local testing)
plt.show()