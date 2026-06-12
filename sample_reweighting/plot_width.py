import math
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')  # prevents "no display" error on headless systems
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Define exponential function
# def power_law(x, A, b, c):
#     return A * x**b+c

def power_law(x, A, b, c):
    return A * x**b+c


def log_expo(x, logA, b):
    return logA + b * x

decay_width_by_DeltaM_4bd_mstop500 = {10.:3.25e-17, 15.:3.52e-15, 20.:5.86e-14, 25.:4.48e-13, 30.:2.24e-12}

# Get sorted keys for interpolation
delta_m_keys = sorted(decay_width_by_DeltaM_4bd_mstop500.keys())
delta_m_vals = [decay_width_by_DeltaM_4bd_mstop500[k] for k in delta_m_keys]

Delta_m = 12
mStop = 500

# Get the base width at mStop=500 (interpolated if needed)
if Delta_m in delta_m_keys:
    width_500 = decay_width_by_DeltaM_4bd_mstop500[Delta_m]
else:
    width_500 = np.interp(Delta_m, delta_m_keys, delta_m_vals)

# NOW scale properly to actual mStop
decay_width_by_mstop_4bd = width_500 * (500.0 / mStop)


print(delta_m_keys)
print(delta_m_vals)

# Example input data
x = delta_m_keys
y = delta_m_vals
x = np.array(x)
y = np.array(y)

# Create scatter plot (no label yet)
plt.yscale("log")
scatter = plt.scatter(x, y, s=10)

# Create fine x values for interpolation
x_interp = np.linspace(min(x), max(x), 1000)
y_interp = np.interp(x_interp, x, y)
line, = plt.plot(x_interp, y_interp, label='Interpolated', color='red')


# Fit the exponential curve to the data
weights = 1.0 / y
popt, pcov = curve_fit(power_law, x, y, p0=(1e-17, 8, -8), sigma=weights)  # initial guesses (A=1, b=0.5)
A_fit, b_fit, c_fit = popt
y_fit = power_law(x_interp, A_fit, b_fit, c_fit)

# logy = np.log(y)
# weights = 1.0 / y
# popt, pcov = curve_fit(log_expo, x, logy, sigma=weights)
# A_fit = np.exp(popt[0])
# b_fit = popt[1]
# y_fit = log_expo(x_interp, A_fit, b_fit)



# Plot exponential fit
label_fit = 'Exp Fit: A={:.2e}, b={:.2e}, c={:.2e}'.format(A_fit, b_fit, c_fit)
#label_fit = 'Exp Fit: A={:.2e}, b={:.2e}'.format(A_fit, b_fit)

line_fit, = plt.plot(x_interp, y_fit, label=label_fit, color='green')




# Add labels, title
plt.xlabel('DeltaM')
plt.ylabel('decay width')
plt.title('decay width by DeltaM 4bd mstop500')

# Set log scale for y-axis


# Manually set legend labels
#plt.legend([scatter], ['My Data Points'], title='Legend Title', loc='upper left')
#plt.legend([scatter, line, line_fit], ['Data Points', 'Linearly interpolated', 'power law fit'])
# Legend
plt.legend()

# Save and show the plot
plt.savefig('widths.png')