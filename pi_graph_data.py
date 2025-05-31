#!/usr/bin/env python3
"""
Generate ASCII representation of logarithmic graph of first 100 decimals of Pi
"""

import math

# First 100 decimals of Pi
pi_decimals = "1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

# Convert to list of integers
digits = [int(d) for d in pi_decimals]

# Calculate log10(digit + 1) to avoid log(0)
log_values = [math.log10(d + 1) for d in digits]

# Create ASCII bar chart
print("Logarithmic Graph of First 100 Decimals of Pi")
print("=" * 60)
print()
print("Position | Digit | log₁₀(d+1) | Bar Graph")
print("-" * 60)

# Show first 50 for readability
for i in range(50):
    digit = digits[i]
    log_val = log_values[i]
    # Scale to 40 characters width
    bar_length = int(log_val * 40)
    bar = "█" * bar_length
    print(f"{i+1:8} | {digit:5} | {log_val:10.3f} | {bar}")

print("\n... (showing first 50 of 100 decimals)")
print()

# Calculate statistics
print("Digit Distribution in First 100 Decimals:")
print("-" * 40)
for i in range(10):
    count = digits.count(i)
    percentage = (count / len(digits)) * 100
    print(f"Digit {i}: {count:2} occurrences ({percentage:5.1f}%)")

print()
print("Summary Statistics:")
print("-" * 40)
print(f"Total digits: {len(digits)}")
print(f"Min log value: {min(log_values):.3f} (digit 0)")
print(f"Max log value: {max(log_values):.3f} (digit 9)")
print(f"Average log value: {sum(log_values)/len(log_values):.3f}")