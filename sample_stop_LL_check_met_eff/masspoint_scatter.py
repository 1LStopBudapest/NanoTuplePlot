import json
import matplotlib.pyplot as plt


file_data = "summed.json"
with open(file_data, "r") as f:
    data = json.load(f)

key_list = []
key_list_stop_mass = []
key_list_x0_mass = []

# Add values into result
for key, value in data.items():
    if isinstance(value, list):
        #Only draw masspoints with actual entries
        if value[0] > 0.1 or value[0] > 0.1:
            key_list.append(key)

for key in key_list:
    mstop, mx0 = key.split('_')
    mstop = int(mstop)
    mx0 = int(mx0)
    key_list_stop_mass.append(mstop)
    key_list_x0_mass.append(mx0)

#Now plot
# Create figure with custom size (width, height in inches)
plt.figure(figsize=(6, 6))

# Create scatter plot
plt.scatter(key_list_stop_mass, key_list_x0_mass, color='blue', s=1)  # s=marker size

# Set titles and labels
plt.title('Integral stop and X0 masses in files', fontsize=14, fontweight='bold')
plt.xlabel('Stop masses', fontsize=12)
plt.ylabel('X0 masses', fontsize=12)

# Add grid for better readability
plt.grid(True, alpha=0.3)

# Save the plot as PNG file
plt.savefig('scatter_masses.png', dpi=300, bbox_inches='tight')

# Optional: Close the plot to free memory (not strictly necessary)
plt.close()