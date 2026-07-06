import matplotlib
matplotlib.use('Agg')  # Use Agg backend for headless environments

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from stops_13TeV import xsecNNLL

#############################################
# Define functions

# Get stop cross-section depending on the stop mass
def get_xsec(mst=200.):
    # xsec returned in fb
    masses = np.array(sorted(xsecNNLL.keys()))
    # Extract cross sections (first value of each tuple)
    xsecs_pb = np.array([xsecNNLL[m][0] for m in masses])
    # Convert to femtobarns (1 pb = 1000 fb)
    xsecs_fb = xsecs_pb * 1000.0
    if mst < masses[0]:
        return -1.
    if mst > masses[-1]:
        return -1.
    xsec = np.interp(mst, masses, xsecs_fb)
    return xsec

# Get filter efficiency
def getEff(csvFile, mStop, mNeu):
    df = pd.read_csv(csvFile, usecols=["m", "dm", "filterEff"])
    dM = mStop - mNeu
    # Get unique m values
    unique_m = df['m'].unique()
    # Find the closest m to mStop
    closest_m = unique_m[np.argmin(np.abs(unique_m - mStop))]
    # Filter to rows with that m
    sub_df = df[df['m'] == closest_m].copy()  # copy to avoid SettingWithCopyWarning if needed
    # Compute dm differences
    sub_df['dm_diff'] = np.abs(sub_df['dm'] - dM)
    # Get filterEff from the row with minimal dm_diff
    filterEff = sub_df.loc[sub_df['dm_diff'].idxmin(), 'filterEff']
    return filterEff

def expected_nevents(lumi, sigma, BR, met_eff):
    expected = lumi * (sigma / 1000) * met_eff * (2 * BR - BR * BR)
    return expected

# Build a {(mStop, deltaM): value} map from a CSV, filtered on the BR column.
# Column 0 = mStop, column 1 = mX0, BR_col = branching ratio, last column = value.
def build_point_map(df, br_col, br_target):
    z_col = df.columns[-1]
    fdf = df[df[br_col] == br_target]
    xs = fdf[0].values          # mStop
    ys = fdf[1].values          # mX0
    zs = fdf[z_col].values      # value (event count)
    dms = xs - ys               # delta M
    return {(x, dm): z for x, dm, z in zip(xs, dms, zs)}

#####################################################

luminosity_2018_pb = 58905.0

# ------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------
# Numerator: number of events AFTER selection
selFile = 'info_test_new_comb_tight7_combined.csv'
# Denominator: actual number of events WITHOUT selection (this is the new bit)
noSelFile = 'info_test_new_comb_tight7_noSel_combined.csv'

# Read the selected-events CSV (no headers)
df = pd.read_csv(selFile, header=None)

# Assuming:
# Column 0 = x (mStop)
# Column 1 = y (mX0)
# Column 2 = some parameter you want to filter on (BR)
# Column 3 = z value (or whatever last column is)
# ADJUST THIS BASED ON YOUR ACTUAL CSV STRUCTURE

# Example: If column 2 is the parameter to filter, and column 3 is z
BR_column = 2  # Change this to the correct column index
z_column = df.columns[-1]  # Last column is z

# Filter for specific parameter value (e.g., 1.0 or whatever value you want)
BR_target = 0.2  # CHANGE THIS to your desired filter value
filtered_df = df[df[BR_column] == BR_target]

x_values = filtered_df[0].values  # mStop
y_values = filtered_df[1].values  # mX0

z_values = filtered_df[z_column].values  # z values (selected event counts)

# Calculate the new variable: x - y (which is delta mass)
delta_m_values = x_values - y_values

print("Number of points after filtering (selected): {}".format(len(x_values)))
print("Unique X (mStop) values in data: {}".format(np.sort(np.unique(x_values))))
print("Unique delta M (x-y) values in data: {}".format(np.sort(np.unique(delta_m_values))))

# ------------------------------------------------------------------
# Read the no-selection CSV (denominator for the efficiency).
# This run may still be in progress, so handle a missing / partial file
# gracefully: any (mStop, deltaM) point that is not present here will simply
# stay greyed out, exactly like before.
# ------------------------------------------------------------------
if os.path.exists(noSelFile):
    df_noSel = pd.read_csv(noSelFile, header=None)
    point_to_noSel = build_point_map(df_noSel, BR_column, BR_target)
    print("\nLoaded no-selection file '{}': {} grid points after BR filter".format(
        noSelFile, len(point_to_noSel)))
else:
    df_noSel = None
    point_to_noSel = {}
    print("\nWARNING: no-selection file '{}' not found.".format(noSelFile))
    print("         All cells will be greyed out until the no-selection results are ready.")

# ------------------------------------------------------------------
# Define the FULL theoretical grid parameters
# ------------------------------------------------------------------
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

# Create a mapping from (x, delta_m) to z (selected events) using ONLY the filtered data
point_to_z = {}
for x_val, dm_val, z_val in zip(x_values, delta_m_values, z_values):
    point_to_z[(x_val, dm_val)] = z_val

# Create the z_matrix with dimensions (len(delta_m_edges)-1, len(x_edges)-1)
# Initialize with NaN for missing points
z_matrix = np.full((len(delta_m_edges) - 1, len(x_edges) - 1), np.nan)


####################################
# Check for NaN and inf values (selected-event counts = numerator)
print("\nDebug - Selected-event (numerator) statistics:")
print("  Total Z values: {}".format(len(z_values)))
print("  NaN count: {}".format(np.sum(np.isnan(z_values))))
print("  Inf count: {}".format(np.sum(np.isinf(z_values))))
print("  Zero count: {}".format(np.sum(z_values == 0)))
print("  Negative count: {}".format(np.sum(z_values < 0)))
print("  Min value (excluding NaN): {}".format(np.nanmin(z_values)))
print("  Max value: {}".format(np.nanmax(z_values)))

# Check the z_matrix for NaN before LogNorm
print("\nDebug - z_matrix statistics (before filling):")
print("  Total cells: {}".format(np.size(z_matrix)))
print("  NaN count in z_matrix: {}".format(np.sum(np.isnan(z_matrix))))
print("  Finite values in z_matrix: {}".format(np.sum(np.isfinite(z_matrix))))

# Debug before filling loop
print("\nDebug - Before filling loop:")
print("Shape of z_matrix: {}".format(z_matrix.shape))
print("Length of all_delta_m_sorted: {}".format(len(all_delta_m_sorted)))
print("Length of all_x_values: {}".format(len(all_x_values)))
print("all_delta_m_sorted: {}".format(all_delta_m_sorted))
print("all_x_values[:5]: {}".format(all_x_values[:5]))
################################

# ------------------------------------------------------------------
# Fill the matrix - each grid point corresponds to a cell starting at that
# coordinate.
#
# Efficiency is now:
#     100 * (events after selection) / (events without selection)
# where BOTH come from the produced results. A cell is filled ONLY when both
# the selected and the no-selection numbers are available for that point;
# otherwise it stays NaN and is greyed out (just as before).
# ------------------------------------------------------------------
filled_count = 0
missing_numerator = 0
missing_denominator = 0
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        sel_events = point_to_z.get((x_val, dm_val), None)        # numerator
        noSel_events = point_to_noSel.get((x_val, dm_val), None)  # denominator

        if sel_events is None:
            missing_numerator += 1
        if noSel_events is None:
            missing_denominator += 1

        # Only compute the efficiency when both numbers exist and the
        # denominator is positive; otherwise leave the cell as NaN (grey).
        if sel_events is not None and noSel_events is not None and noSel_events > 0:

            efficiency = 100.0 * sel_events / noSel_events

            # --- Alternative (previous) method: theory-expected denominator ---
            # Kept here as a commented capability, adapted to the new layout.
            # Uncomment to divide by the THEORY-expected number of events
            # instead of the actual no-selection results.
            # cross_section_fb = get_xsec(x_val)
            # METeff = 0.97
            # expected_events_i = expected_nevents(luminosity_2018_pb, cross_section_fb, BR_target, METeff)
            # efficiency = 100.0 * sel_events / expected_events_i
            # # print(expected_events_i)

            # Raw selected-event count instead of an efficiency (commented capability):
            # z_matrix[j, i] = sel_events

            z_matrix[j, i] = efficiency
            filled_count += 1
            if filled_count <= 5:  # Print first 5 fills
                print("  Filled cell ({}, {}) with efficiency {:.4f} %  (sel={}, noSel={})".format(
                    x_val, dm_val, efficiency, sel_events, noSel_events))

print("Total cells filled: {}".format(filled_count))
print("Cells missing the numerator   (selected):    {}".format(missing_numerator))
print("Cells missing the denominator (no-selection): {}".format(missing_denominator))

# Create meshgrid for plotting
X_grid, Y_grid = np.meshgrid(x_edges, delta_m_edges)

# Create the plot
fig, ax = plt.subplots(figsize=(8, 6))

# Mask NaN values (missing / unfinished data points)
z_masked = np.ma.masked_invalid(z_matrix)

# Log-norm based on the EFFICIENCY values that are actually present
# (adapted from the old version, which used the raw z_values).
finite_eff = z_matrix[np.isfinite(z_matrix)]
if finite_eff.size > 0:
    eff_min = max(np.min(finite_eff), 1e-6)  # guard against <= 0 for LogNorm
    eff_max = np.max(finite_eff)
else:
    eff_min, eff_max = 1e-3, 1.0
norm = LogNorm(vmin=eff_min, vmax=eff_max)

# Plot with pcolormesh
cmap = plt.cm.viridis
cmap.set_bad('lightgray', alpha=0.5)  # Color for missing / unfinished points

# Log plot (commented capability, adapted to the efficiency norm):
# mesh = ax.pcolormesh(X_grid, Y_grid, z_masked, shading='flat',
#                      cmap=cmap, norm=norm, edgecolors='black', linewidth=0.5)

# No log
mesh = ax.pcolormesh(X_grid, Y_grid, z_masked, shading='flat',
                     cmap=cmap, edgecolors='black', linewidth=0.5)

# Add colorbar
cbar = plt.colorbar(mesh, ax=ax)
cbar.set_label('pre-selection efficiency (%)', fontsize=20)

# Labels and title
ax.set_xlabel('mStop (GeV)', fontsize=20)
ax.set_ylabel('DeltaM (GeV)', fontsize=20)
ax.set_title('mStop vs Delta M, BR = {}'.format(BR_target), fontsize=14)

# Add text labels for each cell that HAS data (commented capability)
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        z_val = z_matrix[j, i]
        if not np.isnan(z_val):
            # The cell center is at lower bound + half the cell width
            x_center = (x_edges[i] + x_edges[i+1]) / 2
            y_center = (delta_m_edges[j] + delta_m_edges[j+1]) / 2
            z_val_formatted = "{:.2f}".format(z_val)  # efficiency in %

            ax.text(x_center, y_center, z_val_formatted,
                   ha='center', va='center', fontsize=8, color='white',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.2),rotation='vertical')

# Set axis limits
ax.set_xlim(x_edges[0], x_edges[-1])
ax.set_ylim(delta_m_edges[0], delta_m_edges[-1])

# Add grid lines for better readability
ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)

plt.tight_layout()

# Save the figure
output_filename = 'grid_selection_efficiency_noTheory.png'
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print("Plot saved as: {}".format(output_filename))

# plt.savefig('grid_selection_efficiency.pdf', bbox_inches='tight')
# print("Plot also saved as: grid_selection_efficiency.pdf")

plt.close()

# Print debug info
print("\n" + "=" * 50)
print("Grid information (Full Theoretical Grid, Lower Bound Convention):")
print("X edges: {} (from {} to {})".format(x_edges, x_edges[0], x_edges[-1]))
print("Number of X cells: {}".format(len(x_edges) - 1))
print("Delta M edges: {}".format(delta_m_edges))
print("Number of Delta M cells: {}".format(len(delta_m_edges) - 1))
print("Total possible cells: {}".format(len(all_x_values) * len(all_delta_m_sorted)))
print("Cells with data: {}".format(np.sum(~np.isnan(z_matrix))))
print("Data coverage: {:.1f}%".format(
    100 * np.sum(~np.isnan(z_matrix)) / (len(all_x_values) * len(all_delta_m_sorted))))

# Show which points are missing (greyed out)
print("\n" + "=" * 50)
print("Missing data points (theoretical grid positions without a full efficiency):")
missing_count = 0
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        if np.isnan(z_matrix[j, i]):
            missing_count += 1
            # Report WHY the cell is greyed out: missing numerator, denominator, or both.
            has_num = (x_val, dm_val) in point_to_z
            has_den = (x_val, dm_val) in point_to_noSel
            if not has_num and not has_den:
                reason = "no selected AND no no-selection results"
            elif not has_num:
                reason = "no selected results"
            elif not has_den:
                reason = "no no-selection results (denominator)"
            else:
                reason = "denominator <= 0"
            if missing_count <= 10:  # Show first 10 missing points
                print("  mStop={}, Delta M={}  -> {}".format(x_val, dm_val, reason))
if missing_count > 10:
    print("  ... and {} more missing points".format(missing_count - 10))