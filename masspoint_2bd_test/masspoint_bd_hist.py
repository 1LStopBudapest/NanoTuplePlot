import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')  # prevents "no display" error on headless systems
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Read the CSV file
df = pd.read_csv('/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test.csv')

stop_mass = df["Stop mass"].to_numpy()
x0_mass = df["X0 mass"].to_numpy()
processed_events = df["Processed events"].to_numpy()
selected_events = df["selected events"].to_numpy()
rejected = df["rejected"].to_numpy()
integral = df["integral"].to_numpy()

print(stop_mass)
print(integral)

std = []
expected_events = []
sigmas = []
prob_at_least_1_4bd = 0.96
for i in range(len(processed_events)):
    nevents = processed_events[i]
    std_i = np.sqrt(nevents*prob_at_least_1_4bd*(1-prob_at_least_1_4bd))
    std.append(std_i)
    expected_i = nevents*prob_at_least_1_4bd
    expected_events.append(expected_i)
    diff_expected_i = abs( expected_i - selected_events[i] )
    sigma_i = diff_expected_i/std_i
    sigmas.append(sigma_i)

sigmas = np.array(sigmas)
print(sigmas)

# Create mask where both A and B are multiples of 5 at the same position
mask_standard_masspoint = (stop_mass % 5 == 0) & (x0_mass % 5 == 0)
print(mask_standard_masspoint)

sigmas_standard = sigmas[mask_standard_masspoint]
sigmas_non_standard = sigmas[~mask_standard_masspoint]
print(sigmas_standard)
print(sigmas_non_standard)


# Histogram settings
hist_title = "Deviation from expected number of at least 1stop"
x_label = "Sigmas"
y_label = "Frequency"
bins = 25
color1 = "skyblue"
color2 = "red"
edge_color = "black"
output_file = "sigmas_histogram.png"

# === Plot histogram (saved, not shown) ===
plt.figure(figsize=(8, 6))
plt.hist(sigmas_standard, bins=bins, color=color1, edgecolor=edge_color, alpha=0.5, label="masspoint multiples of 5")
plt.hist(sigmas_non_standard, bins=bins, color=color2, edgecolor=edge_color, alpha=0.5, label="masspoint not multiples of 5")
#plt.yscale("log")
plt.title(hist_title, fontsize=16)
plt.xlabel(x_label, fontsize=15)
plt.ylabel(y_label, fontsize=15)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(loc="best")
plt.tight_layout()
plt.savefig(output_file)
plt.close()
print("Histogram saved to '{}'.".format(output_file))






