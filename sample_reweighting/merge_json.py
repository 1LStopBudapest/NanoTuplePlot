import os
import json
import matplotlib
matplotlib.use('Agg')  # Disable auto-show (no GUI required)
import matplotlib.pyplot as plt

# === User settings ===
folder_path = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/sample_reweighting/json_2016" # Path to folder containing JSON files
key_to_sum = "large ctau"         # Key you want to sum across all files
key_ratio_num = "large ctau"      # Numerator key for ratio
key_ratio_den = "nentry"      # Denominator key for ratio

# === Initialization ===
total_sum = 0
total_sum_nevents = 0

ratio_list = []
delta_m_list = []
ratio_list_03 = []
delta_m_list_03 = []
ratio_list_10 = []
delta_m_list_10 = []
stop_mass_list_03 = []
stop_mass_list_10 = []
x0_mass_list_03 = []
x0_mass_list_10 = []

# === Loop through files ===
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        filepath = os.path.join(folder_path, filename)
        filename_info = filename.replace("merged_stopLL_","")
        filename_info = filename_info.replace("_processed.json","")
        filename_info = filename_info.replace("BR_","")
        mstop_, mX0_, BR_ = filename_info.split("_")
        # print(mstop)
        # print(mX0)
        # print(BR_)
        mstop = float(mstop_)
        mX0 = float(mX0_)
        BR_float = float(BR_)
        delta_m = mstop-mX0
        


        # Read JSON file
        with open(filepath, "r") as f:
            data = json.load(f)

        # --- Sum values for the given key --- Only long lived in sample with BR=0.3 were actually removed from final data
        if BR_ == "0.3":
            total_sum += data[key_to_sum]
        total_sum_nevents+= data["nentry"]

        # --- Compute and print ratio ---
        denom = data[key_ratio_den]
        ratio = float(data[key_ratio_num]) / denom
        if ratio>0.01:
            print("....................")
        if mstop_!= "1052" or mX0_!= "1024":
            ratio_list.append(ratio*100)
            delta_m_list.append(delta_m)
        print("File: {} -> {}/{} = {:.4f}".format(
            filename, key_ratio_num, key_ratio_den, ratio))
        
        if BR_ == "0.3":
            if mstop_!= "1052" or mX0_!= "1024":
                ratio_list_03.append(ratio*100)
                delta_m_list_03.append(delta_m)
                stop_mass_list_03.append(mstop)
                x0_mass_list_03.append(mstop)
            else:
                print("EXCLUDED")
        elif BR_ == "1.0":
            if mstop_!= "1052" or mX0_!= "1024":
                ratio_list_10.append(ratio*100)
                delta_m_list_10.append(delta_m)
                stop_mass_list_10.append(mstop)
                x0_mass_list_10.append(mstop)
            else:
                print("EXCLUDED")

#
# === Print total sum ===
print("\nTotal sum of key '{}': {}".format(key_to_sum, total_sum))
print("\nTotal sum of key 'nevents': {}".format(total_sum_nevents))

# Histogram settings
hist_title = "Signal eff for removal of ultra long stop events"
x_label = "Ultra long stop events respect to total (%)"
y_label = "Frequency"
bins = 50
color = "skyblue"
edge_color = "black"
output_file = "ratio_histogram.png"

# === Plot histogram (saved, not shown) ===
if ratio_list:
    plt.figure(figsize=(8, 6))
    plt.hist(ratio_list, bins=bins, color=color, edgecolor=edge_color)
    plt.yscale("log")
    plt.title(hist_title, fontsize=16)
    plt.xlabel(x_label, fontsize=15)
    plt.ylabel(y_label, fontsize=15)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print("Histogram saved to '{}'.".format(output_file))
else:
    print("No valid ratios to plot.")

# === Scatter plot settings ===
scatter_title = "Ultra Long stop events vs Delta m"
x_label_scatter = "Delta m (GeV)"
y_label_scatter = "Ultra long stop events respect to total (%)"
marker_size = 10
alpha_value = 0.7
output_scatter_file = "deltaM_vs_removed.png"

# === Scatter plot (saved, not shown) ===
# Make sure you have two lists: x_list and y_list with the same length
plt.figure(figsize=(8, 6))
plt.scatter(delta_m_list_03, ratio_list_03, s=marker_size, color="red", alpha=alpha_value, label="BR=0.3")
plt.scatter(delta_m_list_10, ratio_list_10, s=marker_size, color="blue", alpha=alpha_value, label="BR=1.0")
plt.title(scatter_title, fontsize=16)
plt.xlabel(x_label_scatter, fontsize=15)
plt.ylabel(y_label_scatter, fontsize=15)
plt.legend(loc="best")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(output_scatter_file)
plt.close()
print("Scatter plot saved to '{}'.".format(output_scatter_file))

# === Scatter plot 2 settings ===
scatter_title = "Ultra Long stop events vs stop mass"
x_label_scatter = "stop mass (GeV)"
y_label_scatter = "Ultra long stop events respect to total (%)"
marker_size = 10
alpha_value = 0.7
output_scatter_file = "stopmass_vs_removed.png"

# === Scatter plot 2 (saved, not shown) ===
# Make sure you have two lists: x_list and y_list with the same length
plt.figure(figsize=(8, 6))
plt.scatter(stop_mass_list_03, ratio_list_03, s=marker_size, color="red", alpha=alpha_value, label="BR=0.3")
plt.scatter(stop_mass_list_10, ratio_list_10, s=marker_size, color="blue", alpha=alpha_value, label="BR=1.0")
plt.title(scatter_title, fontsize=16)
plt.xlabel(x_label_scatter, fontsize=15)
plt.ylabel(y_label_scatter, fontsize=15)
plt.legend(loc="best")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(output_scatter_file)
plt.close()
print("Scatter plot saved to '{}'.".format(output_scatter_file))

# === Scatter plot 3 settings ===
scatter_title = "Ultra Long stop events vs X0 mass"
x_label_scatter = "X0 mass (GeV)"
y_label_scatter = "Ultra long stop events respect to total (%)"
marker_size = 10
alpha_value = 0.7
output_scatter_file = "x0mass_vs_removed.png"

# === Scatter plot 3 (saved, not shown) ===
# Make sure you have two lists: x_list and y_list with the same length
plt.figure(figsize=(8, 6))
plt.scatter(x0_mass_list_03, ratio_list_03, s=marker_size, color="red", alpha=alpha_value, label="BR=0.3")
plt.scatter(x0_mass_list_10, ratio_list_10, s=marker_size, color="blue", alpha=alpha_value, label="BR=1.0")
plt.title(scatter_title, fontsize=16)
plt.xlabel(x_label_scatter, fontsize=15)
plt.ylabel(y_label_scatter, fontsize=15)
plt.legend(loc="best")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(output_scatter_file)
plt.close()
print("Scatter plot saved to '{}'.".format(output_scatter_file))
