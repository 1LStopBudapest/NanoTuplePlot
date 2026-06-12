import matplotlib
matplotlib.use('Agg')  # Use Agg backend for headless environments

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Read the CSV file (no headers)
df = pd.read_csv('info_test_new_comb_tight7_combined.csv', header=None)

# Assuming: 
# Column 0 = x (mStop)
# Column 1 = y (mX0) 
# Column 2 = some parameter you want to filter on
# Column 3 = z value (or whatever last column is)
# ADJUST THIS BASED ON YOUR ACTUAL CSV STRUCTURE

# Example: If column 2 is the parameter to filter, and column 3 is z
BR_column = 2  # Change this to the correct column index
z_column = df.columns[-1]  # Last column is z

# Filter for specific parameter value (e.g., 1.0 or whatever value you want)
BR_target = 1.0  # CHANGE THIS to your desired filter value
filtered_df = df[df[BR_column] == BR_target]

x_values = filtered_df[0].values  # mStop
y_values = filtered_df[1].values  # mX0

z_values = filtered_df[z_column].values  # z values

# Calculate the new variable: x - y (which is delta mass)
delta_m_values = x_values - y_values

print("Number of points after filtering: {}".format(len(x_values)))
print("Unique X (mStop) values in data: {}".format(np.sort(np.unique(x_values))))
print("Unique delta M (x-y) values in data: {}".format(np.sort(np.unique(delta_m_values))))


###########################
# Check for non-positive values in z
non_positive_mask = z_values <= 0
if np.any(non_positive_mask):
    print("\nWARNING: Found {} non-positive Z values!".format(np.sum(non_positive_mask)))
    print("Indices with non-positive Z values:")
    for idx in np.where(non_positive_mask)[0][:20]:  # Show first 20
        print("  Row index {}: mStop={}, mX0={}, Z={}, deltaM={}".format(
            idx, x_values[idx], y_values[idx], z_values[idx], delta_m_values[idx]))
    
    # Also print the corresponding rows from the original filtered dataframe
    print("\nCorresponding rows in filtered data:")
    bad_rows = filtered_df.iloc[np.where(non_positive_mask)[0][:20]]
    print(bad_rows.to_string())
    
    # Print unique values to see patterns
    print("\nUnique non-positive Z values: {}".format(np.unique(z_values[non_positive_mask])))

# Also check original dataframe before filtering
original_non_positive = df[df[z_column] <= 0]
if len(original_non_positive) > 0:
    print("\nIn original CSV (before filtering):")
    print("Found {} rows with Z <= 0".format(len(original_non_positive)))
    print(original_non_positive.head(20).to_string())
############################

# Define the FULL theoretical grid parameters
delta_m_stop = 25
delta_m_x0_list = [10, 15, 20, 25, 30]

# Get ALL possible X values (the complete theoretical grid)
all_x_values = np.arange(250, 1100 + delta_m_stop, delta_m_stop)

# Get ALL possible delta M values (the complete theoretical grid)
all_delta_m_values = np.array(sorted(delta_m_x0_list))

print("\nFull theoretical grid:")
print("All X values: {}".format(all_x_values))
print("All Delta M values: {}".format(all_delta_m_values))

# Create cell boundaries for X using LOWER BOUND convention
# The cell starts at the grid point and extends to the next grid point
x_edges = []
for i in range(len(all_x_values)):
    x_edges.append(all_x_values[i])
# Add the upper bound for the last cell
x_edges.append(all_x_values[-1] + delta_m_stop)
x_edges = np.array(x_edges)

# Create cell boundaries for Delta M using LOWER BOUND convention
# Calculate spacing between delta M values (they are not evenly spaced!)
# Sort them first
all_delta_m_sorted = np.sort(all_delta_m_values)
delta_m_edges = []
for i in range(len(all_delta_m_sorted)):
    delta_m_edges.append(all_delta_m_sorted[i])
# Add the upper bound for the last cell (extend by the spacing to previous)
if len(all_delta_m_sorted) > 1:
    last_spacing = all_delta_m_sorted[-1] - all_delta_m_sorted[-2]
    delta_m_edges.append(all_delta_m_sorted[-1] + last_spacing)
else:
    delta_m_edges.append(all_delta_m_sorted[-1] + 5)
delta_m_edges = np.array(delta_m_edges)

# Create a mapping from (x, delta_m) to z using ONLY the filtered data
point_to_z = {}
for x_val, dm_val, z_val in zip(x_values, delta_m_values, z_values):
    point_to_z[(x_val, dm_val)] = z_val

# Create the z_matrix with dimensions (len(delta_m_edges)-1, len(x_edges)-1)
# Initialize with NaN for missing points
z_matrix = np.full((len(delta_m_edges)-1, len(x_edges)-1), np.nan)


####################################
# Check for NaN and inf values
print("\nDebug - Z value statistics:")
print("  Total Z values: {}".format(len(z_values)))
print("  NaN count: {}".format(np.sum(np.isnan(z_values))))
print("  Inf count: {}".format(np.sum(np.isinf(z_values))))
print("  Zero count: {}".format(np.sum(z_values == 0)))
print("  Negative count: {}".format(np.sum(z_values < 0)))
print("  Min value (excluding NaN): {}".format(np.nanmin(z_values)))
print("  Max value: {}".format(np.nanmax(z_values)))

# Check the z_matrix for NaN before LogNorm
print("\nDebug - z_matrix statistics:")
print("  Total cells: {}".format(np.size(z_matrix)))
print("  NaN count in z_matrix: {}".format(np.sum(np.isnan(z_matrix))))
print("  Finite values in z_matrix: {}".format(np.sum(np.isfinite(z_matrix)))) 

# Debug: Check what values you actually have vs theoretical grid
print("\nDebug - Value comparison:")
print("Theoretical X values: {}".format(all_x_values))
print("Actual X values in data: {}".format(np.sort(np.unique(x_values))))
print("\nTheoretical Delta M values: {}".format(all_delta_m_sorted))
print("Actual Delta M values in data: {}".format(np.sort(np.unique(delta_m_values))))

# Check if values are close but not exact (floating point issues)
print("\nDebug - Checking for near matches:")
for x_val in np.unique(x_values):
    if x_val not in all_x_values:
        closest = all_x_values[np.argmin(np.abs(all_x_values - x_val))]
        print("  X={} not in theoretical grid, closest is {}".format(x_val, closest))
        
for dm_val in np.unique(delta_m_values):
    if dm_val not in all_delta_m_sorted:
        closest = all_delta_m_sorted[np.argmin(np.abs(all_delta_m_sorted - dm_val))]
        print("  Delta M={} not in theoretical grid, closest is {}".format(dm_val, closest))

# Debug: Check what keys are in point_to_z vs what you're looking for
print("\nDebug - Point mapping check:")
print("Sample of point_to_z keys (first 5):")
for i, (key, val) in enumerate(point_to_z.items()):
    if i < 5:
        print("  {} -> {}".format(key, val))

print("\nDebug - Checking first few grid positions:")
for i, x_val in enumerate(all_x_values[:5]):
    for j, dm_val in enumerate(all_delta_m_sorted[:3]):
        print("  Checking grid ({}, {}): in point_to_z? {}".format(
            x_val, dm_val, (x_val, dm_val) in point_to_z))

# Also check the types and values
print("\nDebug - Type check:")
if len(point_to_z) > 0:
    sample_key = list(point_to_z.keys())[0]
    print("  Sample key type: {}".format(type(sample_key)))
    print("  Sample key values: x={}, dm={}".format(sample_key[0], sample_key[1]))
    print("  Sample x type: {}, dm type: {}".format(type(sample_key[0]), type(sample_key[1])))


# Debug before filling loop
print("\nDebug - Before filling loop:")
print("Shape of z_matrix: {}".format(z_matrix.shape))
print("Length of all_delta_m_sorted: {}".format(len(all_delta_m_sorted)))
print("Length of all_x_values: {}".format(len(all_x_values)))
print("all_delta_m_sorted: {}".format(all_delta_m_sorted))
print("all_x_values[:5]: {}".format(all_x_values[:5]))
################################

# Fill the matrix - each grid point corresponds to a cell starting at that coordinate
filled_count = 0
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        if (x_val, dm_val) in point_to_z:
            z_matrix[j, i] = point_to_z[(x_val, dm_val)]
            filled_count += 1
            if filled_count <= 5:  # Print first 5 fills
                print("  Filled cell ({}, {}) with value {}".format(x_val, dm_val, point_to_z[(x_val, dm_val)]))

print("Total cells filled: {}".format(filled_count))

# Create meshgrid for plotting
X_grid, Y_grid = np.meshgrid(x_edges, delta_m_edges)

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))

# Mask NaN values (missing data points)
z_masked = np.ma.masked_invalid(z_matrix)

norm = LogNorm(vmin=np.nanmin(z_values), vmax=np.nanmax(z_values))

# Plot with pcolormesh
cmap = plt.cm.viridis
cmap.set_bad('lightgray', alpha=0.5)  # Color for missing points

mesh = ax.pcolormesh(X_grid, Y_grid, z_masked, shading='flat', 
                     cmap=cmap, norm=norm, edgecolors='black', linewidth=0.5)

# Add colorbar
cbar = plt.colorbar(mesh, ax=ax)
cbar.set_label('nEvents passing pre-selection', fontsize=20)

# Labels and title
ax.set_xlabel('mStop (GeV)', fontsize=20)
ax.set_ylabel('DeltaM (GeV)', fontsize=20)
ax.set_title('mStop vs Delta M, BR = {})'.format(BR_target), fontsize=14)

# Add text labels for each cell that HAS data
# for i, x_val in enumerate(all_x_values):
#     for j, dm_val in enumerate(all_delta_m_sorted):
#         z_val = z_matrix[j, i]
#         if not np.isnan(z_val):
#             # The cell center is at lower bound + half the cell width
#             x_center = (x_edges[i] + x_edges[i+1]) / 2
#             y_center = (delta_m_edges[j] + delta_m_edges[j+1]) / 2
#             z_val_formatted = "{:.2f}".format(z_val)
            
#             ax.text(x_center, y_center, z_val_formatted, 
#                    ha='center', va='center', fontsize=8, color='white',
#                    bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6))

# Set axis limits
ax.set_xlim(x_edges[0], x_edges[-1])
ax.set_ylim(delta_m_edges[0], delta_m_edges[-1])

# Add grid lines for better readability
ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)

plt.tight_layout()

# Save the figure
output_filename = 'grid_nevents_passing.png'
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print("Plot saved as: {}".format(output_filename))

# plt.savefig('grid_efficiency.pdf', bbox_inches='tight')
# print("Plot also saved as: grid_efficiency.pdf")

plt.close()

# Print debug info
print("\n" + "="*50)
print("Grid information (Full Theoretical Grid, Lower Bound Convention):")
print("X edges: {} (from {} to {})".format(x_edges, x_edges[0], x_edges[-1]))
print("Number of X cells: {}".format(len(x_edges)-1))
print("Delta M edges: {}".format(delta_m_edges))
print("Number of Delta M cells: {}".format(len(delta_m_edges)-1))
print("Total possible cells: {}".format(len(all_x_values) * len(all_delta_m_sorted)))
print("Cells with data: {}".format(np.sum(~np.isnan(z_matrix))))
print("Data coverage: {:.1f}%".format(100 * np.sum(~np.isnan(z_matrix)) / (len(all_x_values) * len(all_delta_m_sorted))))

# Show which points are missing
print("\n" + "="*50)
print("Missing data points (theoretical grid positions without data):")
missing_count = 0
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        if np.isnan(z_matrix[j, i]):
            missing_count += 1
            if missing_count <= 10:  # Show first 10 missing points
                print("  mStop={}, Delta M={}".format(x_val, dm_val))
if missing_count > 10:
    print("  ... and {} more missing points".format(missing_count - 10))