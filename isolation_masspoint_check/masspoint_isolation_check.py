import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # prevents "no display" error on headless systems
import matplotlib.pyplot as plt

file_data = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/legacy_archive/check_met_eff/summed_2018.json"
with open(file_data, "r") as f:
    data = json.load(f)

key_list = []
key_list_stop_mass = []
key_list_x0_mass = []
key_list_deltam = []
met_eff_03 = []
met_eff_10 = []
ntotal_03 = []
ntotal_10 = []
nPassing_03 = []
nPassing_10 = []

key_list_standard = []
key_list_non_standard = []


# Add values into result
for key, value in data.items():
    if isinstance(value, list):
        if "_min_MET_pt" not in key and "_failing_MET" not in key and "_passing_MET" not in key:
            #Only draw masspoints with actual entries
            if value[0] > 0.1 or value[0] > 0.1:
                key_list.append(key)

for key in key_list:
    mstop, mx0 = key.split('_')
    mstop = int(mstop)
    mx0 = int(mx0)
    
    if (mstop % 5 == 0) and (mx0 % 5 == 0):
        key_list_standard.append(key)
    else:
        key_list_non_standard.append(key)

threshold_distance = 4
isolated_masspoints = []
for key in key_list_standard:
    mstop_i, mx0_i = key.split('_')
    mstop_i = int(mstop_i)
    mx0_i = int(mx0_i)
    distances = []

    for key2 in key_list:
        mstop_j, mx0_j = key2.split('_')
        mstop_j = int(mstop_j)
        mx0_j = int(mx0_j)

        if key != key2:
            distance_i = np.sqrt( (mstop_i-mstop_j)**2 + (mx0_i - mx0_j)**2  )
            distances.append(distance_i)

    min_distance = min(distances)
    print("min_distance in key"+key+" is = "+str(min_distance))
    if min_distance>threshold_distance:
        isolated_masspoints.append(key)

print("The isolated standard masspoints are: "+str(isolated_masspoints))
print(isolated_masspoints)

"""

########################################################################        
#Now plot
# Create figure with custom size (width, height in inches)
plt.figure(figsize=(6, 6))
# Create scatter plot
plt.scatter(key_list_stop_mass, met_eff_03, color='red', s=1,label="met eff BR=0.3")  # s=marker size
plt.scatter(key_list_stop_mass, met_eff_10, color='blue', s=1,label="met eff BR=1.0") 
# Set titles and labels
plt.title('Stop mass vs met eff', fontsize=14, fontweight='bold')
plt.xlabel('Stop masses', fontsize=12)
plt.ylabel('Met eff', fontsize=12)
# Add grid for better readability
plt.grid(True, alpha=0.3)
# Save the plot as PNG file
plt.savefig('scatter_met_stop.png', dpi=300, bbox_inches='tight')
# Optional: Close the plot to free memory (not strictly necessary)
plt.close()

########################################################################        
#Now plot
# Create figure with custom size (width, height in inches)
plt.figure(figsize=(6, 6))
# Create scatter plot
plt.scatter(key_list_x0_mass, met_eff_03, color='red', s=1,label="met eff BR=0.3")  # s=marker size
plt.scatter(key_list_x0_mass, met_eff_10, color='blue', s=1,label="met eff BR=1.0") 
# Set titles and labels
plt.title('X0 mass vs met eff', fontsize=14, fontweight='bold')
plt.xlabel('X0 masses', fontsize=12)
plt.ylabel('Met eff', fontsize=12)
# Add grid for better readability
plt.grid(True, alpha=0.3)
# Save the plot as PNG file
plt.savefig('scatter_met_x0.png', dpi=300, bbox_inches='tight')
# Optional: Close the plot to free memory (not strictly necessary)
plt.close()

########################################################################        
#Now plot
# Create figure with custom size (width, height in inches)
plt.figure(figsize=(6, 6))
# Create scatter plot
plt.scatter(key_list_deltam, met_eff_03, color='red', s=1,label="met eff BR=0.3")  # s=marker size
plt.scatter(key_list_deltam, met_eff_10, color='blue', s=1,label="met eff BR=1.0") 
# Set titles and labels
plt.title('Delta m vs met eff', fontsize=14, fontweight='bold')
plt.xlabel('Delta m', fontsize=12)
plt.ylabel('Met eff', fontsize=12)
# Add grid for better readability
plt.grid(True, alpha=0.3)
# Save the plot as PNG file
plt.savefig('scatter_met_deltam.png', dpi=300, bbox_inches='tight')
# Optional: Close the plot to free memory (not strictly necessary)
plt.close()



# Histogram settings
hist_title = "Met eff (N passing/N total)"
x_label = "Sigmas"
y_label = "Frequency"
bins = 25
color1 = "skyblue"
color2 = "red"
edge_color = "black"
output_file = "MET_eff_histogram.png"
# === Plot histogram (saved, not shown) ===
plt.figure(figsize=(8, 6))
plt.hist(met_eff_03, bins=bins, color=color1, edgecolor=edge_color, alpha=0.5, label="met eff BR=0.3")
plt.hist(met_eff_10, bins=bins, color=color2, edgecolor=edge_color, alpha=0.5, label="met eff BR=1.0")
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
"""