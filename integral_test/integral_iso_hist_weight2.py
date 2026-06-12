import pandas as pd
import numpy as np
import json


import matplotlib
matplotlib.use('Agg')  # prevents "no display" error on headless systems
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from stops_13TeV import xsecNNLL 


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

def expected_nevents(lumi,sigma,BR,met_eff):
   expected = lumi*(sigma/1000)*met_eff*(2*BR-BR*BR)
   return expected

#####################################################

luminosity_2018_pb  = 58905.0

# Read the CSV file
df_03 = pd.read_csv('/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test_new_comb_tight7_03.csv')
df_10 = pd.read_csv('/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/info_test_new_comb_tight7_10.csv')
summary_file = ""

file_data = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/json_sample_info/summed_2018_reworked.json"
with open(file_data, "r") as f:
    data_nevents = json.load(f)


stop_mass_03 = df_03["Stop mass"].to_numpy()
x0_mass_03 = df_03["X0 mass"].to_numpy()
processed_events_03 = df_03["Processed events"].to_numpy()
rejected_03 = df_03["rejected"].to_numpy()
integral_03 = df_03["integral"].to_numpy()
BR_03 = df_03["BR"].to_numpy()
max_weight_03 = df_03["max_weight"].to_numpy()

stop_mass_10 = df_10["Stop mass"].to_numpy()
x0_mass_10 = df_10["X0 mass"].to_numpy()
processed_events_10 = df_10["Processed events"].to_numpy()
rejected_10 = df_10["rejected"].to_numpy()
integral_10 = df_10["integral"].to_numpy()
BR_10 = df_10["BR"].to_numpy()
max_weight_10 = df_10["max_weight"].to_numpy()


expected_events_03 = []
ratio_03 = []
expected_events_10 = []
ratio_10 = []
integral_list  = []
BR_list  = []

weight_list_03  = []
weight_list_10  = []

#masspoints_isolated = [u'375_360', u'300_285', u'300_280', u'475_450', u'475_455', u'350_340', u'325_305', u'325_300', u'250_240', u'900_870', u'250_230', u'700_670', u'350_335', u'450_425', u'450_420', u'275_265', u'275_260', u'750_720', u'500_480', u'500_485', u'300_270', u'300_275', u'500_490', u'300_290', u'425_405', u'425_400', u'475_445', u'375_365', u'325_310', u'325_315', u'250_225', u'250_220', u'275_250', u'275_255', u'425_410', u'350_320', u'350_325', u'425_415', u'800_770', u'475_460', u'375_350', u'375_355', u'400_385', u'400_380', u'1000_970', u'950_920', u'850_820', u'250_235', u'500_475', u'500_470', u'475_465', u'600_570', u'275_245', u'400_375', u'325_295', u'550_520', u'400_370', u'425_395', u'450_430', u'450_435', u'350_330', u'450_440', u'375_345', u'400_390', u'650_620']
    

#Combine with above once all finish running
for i in range(len(BR_03)):

    mstop_i = stop_mass_03[i]
    mx0_i = x0_mass_03[i]
    processed_events_i = processed_events_03[i]
    BR_i = BR_03[i]
    integral_i = integral_03[i]

    key = str(mstop_i)+"_"+str(mx0_i)

    cross_section_fb = get_xsec(mstop_i)
    
    METeff =  processed_events_i / (data_nevents[key][0])

    expected_events_i = expected_nevents(luminosity_2018_pb,cross_section_fb,BR_i,METeff)
    ratio = integral_i/expected_events_i

    expected_events_03.append(expected_events_i)
    ratio_03.append(ratio)
    weight_list_03.append(max_weight_03[i])

#Combine with above once all finish running
for i in range(len(BR_10)):

    mstop_i = stop_mass_10[i]
    mx0_i = x0_mass_10[i]
    processed_events_i = processed_events_10[i]
    BR_i = BR_10[i]
    integral_i = integral_10[i]

    key = str(mstop_i)+"_"+str(mx0_i)

    cross_section_fb = get_xsec(mstop_i)
    
    METeff =  processed_events_i / (data_nevents[key][1])

    expected_events_i = expected_nevents(luminosity_2018_pb,cross_section_fb,BR_i,METeff)
    ratio = integral_i/expected_events_i

    expected_events_10.append(expected_events_i)
    ratio_10.append(ratio)
    weight_list_10.append(max_weight_10[i])

    BR_list.append(BR_i)




BR_list = np.array(BR_list)
weight_list_03 = np.array(weight_list_03)
weight_list_10 = np.array(weight_list_10)

# Build mask for BR = 0.5 (example)
target_BR = 1.0
mask_BR = np.isclose(BR_list, target_BR)  # safer than == for floats

# Filter the arrays
max_weight_03_filtered = weight_list_03
max_weight_10_filtered = weight_list_10[mask_BR]

max_index = np.argmax(max_weight_03_filtered)
max_value = np.max(max_weight_03_filtered)

print("max_index = "+str(max_index))
print("max_value = "+str(max_value))

# Histogram settings
edge_color = "black"
color1 = "skyblue"
color2 = "red"
color3 = "green"
color4 = "pink"
color5 = "orange"
color6 = "brown"
hist_title = "Maximum weights"
x_label = "Maximum weights"
y_label = "Frequency"
bins = 20
output_file = "max_weight_histogram.png"
# === Plot histogram (saved, not shown) ===
plt.figure(figsize=(8, 6))

plt.hist(max_weight_03_filtered, bins=bins, color=color1, edgecolor=edge_color, alpha=0.3, label="masspoints sample 0.3")
#plt.hist(max_weight_10_filtered, bins=bins, color=color2, edgecolor=edge_color, alpha=0.3, label="masspoint isolated sample 1.0 BR="+str(target_BR))

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



