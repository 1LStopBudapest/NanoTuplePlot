import matplotlib
matplotlib.use('Agg')  # Use Agg backend for headless environments

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from stops_13TeV import xsecNNLL 
import json

#############################################
#Define funcions

#Get stop cross-section depending on the stop mass
def get_xsec(mst = 200.):
  # xsec returned in fb
  masses = np.array(sorted(xsecNNLL.keys()))
  # Extract cross sections (first value of each tuple)
  xsecs_pb = np.array([xsecNNLL[m][0] for m in masses])
  # Convert to femtobarns (1 pb = 1000 fb)
  xsecs_fb = xsecs_pb * 1000.0
  if mst < masses[0]: return -1.
  if mst > masses[-1]: return -1.
  xsec = np.interp(mst, masses, xsecs_fb)   
  return xsec

#Get filter efficiency
def getEff(csvFile,mStop, mNeu):
    df = pd.read_csv(csvFile, usecols= ["m","dm","filterEff"])
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

def expected_nevents(lumi,
                     sigma,
                     BR,
                     meteff_44_03,
                     meteff_42_03,
                     meteff_22_03,
                     MCcorr44_03,
                     MCcorr42_03,
                     MCcorr22_03,
                     meteff_44_10,
                     meteff_42_10,
                     meteff_22_10,
                     MCcorr44_10,
                     MCcorr42_10,
                     MCcorr22_10):
   
   br_factor_03 = (BR*BR)*meteff_44_03*MCcorr44_03 + \
            (2*BR*(1-BR))*meteff_42_03*MCcorr42_03 + \
            ((1-BR)*(1-BR))*meteff_22_03*MCcorr22_03
   
   expected_03 = lumi*(sigma/1000)*br_factor_03

   br_factor_10 = (BR*BR)*meteff_44_10*MCcorr44_10 + \
            (2*BR*(1-BR))*meteff_42_10*MCcorr42_10 + \
            ((1-BR)*(1-BR))*meteff_22_10*MCcorr22_10
   
   expected_10 = lumi*(sigma/1000)*br_factor_10

   expected = BR*expected_10 + (1-BR)*expected_03
   
   return expected

#####################################################

luminosity_2018_pb  = 58905.0
#luminosity_2018_pb  = 19520.0#ACTUALLY 2016 PreVPF

# Read the CSV file (no headers)
df = pd.read_csv('info_test_new_comb_tight7_noSel_extra_combined.csv', header=None)

file_data = "/mnt/newDisk/stop_samples_long_lived/2018/summed_2018_reworked.json"
with open(file_data, "r") as f:
    data_nevents = json.load(f)


# ACTUAL CSV STRUCTURE
# Column 0 = x (mStop)
# Column 1 = y (mX0) 
# Column 2 = BR
# Column 3 = histogram entries
# Column 4 = n_rejected_10+n_rejected_03
# Column 5 = n_4bd4bd_03
# Column 6 = n_4bd2bd_03
# Column 7 = n_2bd2bd_03
# Column 8 = n_4bd4bd_10
# Column 9 = n_4bd2bd_10
# Column 10 = n_2bd2bd_10
# Column 11 = run_mcWeight_4bd4bd_03
# Column 12 = run_mcWeight_4bd2bd_03
# Column 13 = run_mcWeight_2bd2bd_03
# Column 14 = run_mcWeight_4bd4bd_10
# Column 15 = run_mcWeight_4bd2bd_10
# Column 16 = run_mcWeight_2bd2bd_10
# Column 17 = histogram integral

# Example: If column 2 is the parameter to filter, and column 3 is z
BR_column = 2  # Change this to the correct column index
z_column = df.columns[-1]  # Last column is z
processed_events_column = df.columns[3]

# Filter for specific parameter value (e.g., 1.0 or whatever value you want)
BR_target = 1.0  # CHANGE THIS to your desired filter value
filtered_df = df[df[BR_column] == BR_target]

x_values = filtered_df[0].values  # mStop
y_values = filtered_df[1].values  # mX0

z_values = filtered_df[z_column].values  # z values

processed_events_values = filtered_df[17].values

n_4bd4bd_03 = filtered_df[5].values
n_4bd2bd_03 = filtered_df[6].values
n_2bd2bd_03 = filtered_df[7].values
n_4bd4bd_10 = filtered_df[8].values
n_4bd2bd_10 = filtered_df[9].values
n_2bd2bd_10 = filtered_df[10].values

run_mcWeight_4bd4bd_03 = filtered_df[11].values
run_mcWeight_4bd2bd_03 = filtered_df[12].values
run_mcWeight_2bd2bd_03 = filtered_df[13].values
run_mcWeight_4bd4bd_10 = filtered_df[14].values
run_mcWeight_4bd2bd_10 = filtered_df[15].values
run_mcWeight_2bd2bd_10 = filtered_df[16].values

# Calculate the new variable: x - y (which is delta mass)
delta_m_values = x_values - y_values

print("Number of points after filtering: {}".format(len(x_values)))
print("Unique X (mStop) values in data: {}".format(np.sort(np.unique(x_values))))
print("Unique delta M (x-y) values in data: {}".format(np.sort(np.unique(delta_m_values))))


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
processed_events_z = {}
for x_val, dm_val, z_val, procc in zip(x_values, delta_m_values, z_values, processed_events_values):
    point_to_z[(x_val, dm_val)] = z_val
    processed_events_z[(x_val, dm_val)] = procc

n_4bd4bd_10_ = {}
n_4bd2bd_10_ = {}
n_2bd2bd_10_ = {}
run_mcWeight_4bd4bd_10_ = {}
run_mcWeight_4bd2bd_10_ = {}
run_mcWeight_2bd2bd_10_ = {}

for x_val, dm_val, n_44, n_42, n_22, w_44, w_42, w_22   in zip(x_values, 
                                     delta_m_values, 
                                     n_4bd4bd_10, 
                                     n_4bd2bd_10, 
                                     n_2bd2bd_10, 
                                     run_mcWeight_4bd4bd_10, 
                                     run_mcWeight_4bd2bd_10, 
                                     run_mcWeight_2bd2bd_10):
    n_4bd4bd_10_[(x_val, dm_val)] = n_44
    n_4bd2bd_10_[(x_val, dm_val)] = n_42
    n_2bd2bd_10_[(x_val, dm_val)] = n_22
    run_mcWeight_4bd4bd_10_[(x_val, dm_val)] = w_44
    run_mcWeight_4bd2bd_10_[(x_val, dm_val)] = w_42
    run_mcWeight_2bd2bd_10_[(x_val, dm_val)] = w_22

n_4bd4bd_03_ = {}
n_4bd2bd_03_ = {}
n_2bd2bd_03_ = {}
run_mcWeight_4bd4bd_03_ = {}
run_mcWeight_4bd2bd_03_ = {}
run_mcWeight_2bd2bd_03_ = {}

for x_val, dm_val, n_44, n_42, n_22, w_44, w_42, w_22   in zip(x_values, 
                                     delta_m_values, 
                                     n_4bd4bd_03, 
                                     n_4bd2bd_03, 
                                     n_2bd2bd_03, 
                                     run_mcWeight_4bd4bd_03, 
                                     run_mcWeight_4bd2bd_03, 
                                     run_mcWeight_2bd2bd_03):
    n_4bd4bd_03_[(x_val, dm_val)] = n_44
    n_4bd2bd_03_[(x_val, dm_val)] = n_42
    n_2bd2bd_03_[(x_val, dm_val)] = n_22
    run_mcWeight_4bd4bd_03_[(x_val, dm_val)] = w_44
    run_mcWeight_4bd2bd_03_[(x_val, dm_val)] = w_42
    run_mcWeight_2bd2bd_03_[(x_val, dm_val)] = w_22

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

            cross_section_fb = get_xsec(x_val)

            try:
                key = str(x_val)+"_"+str(x_val-dm_val)
                #METeff =  processed_events_z[(x_val, dm_val)] / (data_nevents[key][0]+data_nevents[key][1])
                #METeff =  0.97
                #print(key)
                #print(point_to_z[(x_val, dm_val)])
                #print(METeff)
                # meteff_44 =  n_4bd4bd_10_[(x_val, dm_val)] / ((data_nevents[key][0]+data_nevents[key][1])*0.64)
                # meteff_42 =  n_4bd2bd_10_[(x_val, dm_val)] / ((data_nevents[key][0]+data_nevents[key][1])*0.32)
                # meteff_22 =  n_2bd2bd_10_[(x_val, dm_val)] / ((data_nevents[key][0]+data_nevents[key][1])*0.04)

                meteff_44_10 =  n_4bd4bd_10_[(x_val, dm_val)] / ((data_nevents[key][1])*0.64)
                meteff_42_10 =  n_4bd2bd_10_[(x_val, dm_val)] / ((data_nevents[key][1])*0.32)
                meteff_22_10 =  n_2bd2bd_10_[(x_val, dm_val)] / ((data_nevents[key][1])*0.04)
                MCcorr44_10 =  run_mcWeight_4bd4bd_10_[(x_val, dm_val)]
                MCcorr42_10 =  run_mcWeight_4bd2bd_10_[(x_val, dm_val)]
                MCcorr22_10 =  run_mcWeight_2bd2bd_10_[(x_val, dm_val)]

                meteff_44_03 =  n_4bd4bd_03_[(x_val, dm_val)] / ((data_nevents[key][0])*0.64)
                meteff_42_03 =  n_4bd2bd_03_[(x_val, dm_val)] / ((data_nevents[key][0])*0.32)
                meteff_22_03 =  n_2bd2bd_03_[(x_val, dm_val)] / ((data_nevents[key][0])*0.04)
                MCcorr44_03 =  run_mcWeight_4bd4bd_03_[(x_val, dm_val)]
                MCcorr42_03 =  run_mcWeight_4bd2bd_03_[(x_val, dm_val)]
                MCcorr22_03 =  run_mcWeight_2bd2bd_03_[(x_val, dm_val)]
                # print("----------------")
                # print(meteff_44)
                # print(meteff_42)
                # print(meteff_22)
                # print(MCcorr44)
                # print(MCcorr42)
                # print(MCcorr22)
                # print("----------------")

            except:
                print("divide by zero")

            expected_events_i = expected_nevents(luminosity_2018_pb,
                                                 cross_section_fb,
                                                 BR_target,
                                                 meteff_44_03,
                                                 meteff_42_03,
                                                 meteff_22_03,
                                                 MCcorr44_03,
                                                 MCcorr42_03,
                                                 MCcorr22_03,
                                                 meteff_44_10,
                                                 meteff_42_10,
                                                 meteff_22_10,
                                                 MCcorr44_10,
                                                 MCcorr42_10,
                                                 MCcorr22_10)
            
            #print("expected_events_i = "+str(expected_events_i))

            if key == "1100_1070":
                print(".....................")
                print("integral_i = "+str(point_to_z[(x_val, dm_val)]))
                #print("meteff_44 = "+str(meteff_44))
                print("cross_section_fb = "+str(cross_section_fb))
                print("expected_events_i = "+str(expected_events_i))
                print("processed_events_i = "+str(processed_events_z[(x_val, dm_val)]))
                print("luminosity_2018_pb = "+str(luminosity_2018_pb))
                print("data_nevents[key][0] = "+str(data_nevents[key][0]))
                print("data_nevents[key][1] = "+str(data_nevents[key][1]))
                print("data_nevents[key][0]+data_nevents[key][1] = "+str(data_nevents[key][0]+data_nevents[key][1]))
                print(".....................")

            #z_matrix[j, i] = point_to_z[(x_val, dm_val)]

            z_matrix[j, i] = point_to_z[(x_val, dm_val)]
            #print(expected_events_i)
            filled_count += 1
            if filled_count <= 5:  # Print first 5 fills
                print("  Filled cell ({}, {}) with value {}".format(x_val, dm_val, expected_events_i))

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
cbar.set_label('nEvents no selection', fontsize=20)

# Labels and title
ax.set_xlabel('mStop (GeV)', fontsize=20)
ax.set_ylabel('DeltaM (GeV)', fontsize=20)
ax.set_title('mStop vs Delta M, BR = {}'.format(BR_target), fontsize=14)

# Add text labels for each cell that HAS data
for i, x_val in enumerate(all_x_values):
    for j, dm_val in enumerate(all_delta_m_sorted):
        z_val = z_matrix[j, i]
        if not np.isnan(z_val):
            # The cell center is at lower bound + half the cell width
            x_center = (x_edges[i] + x_edges[i+1]) / 2
            y_center = (delta_m_edges[j] + delta_m_edges[j+1]) / 2
            z_val_formatted = "{:.2f}".format(z_val)
            
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
output_filename = 'grid_nevents_noSel.png'
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