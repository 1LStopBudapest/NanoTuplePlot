import ROOT
import numpy as np

def get_xsec(mst = 200.):
   # xsec returned in fb
   stoparray = [200., 250., 300., 350., 400., 450., 500., 550., 600., 650., 700., 750., 800., 850., 900., 950., 1000.]
   xsecarray = [0.755E+05, 0.248E+05, 0.100E+05, 0.443E+04, 0.215E+04, 0.111E+04, 0.609E+03, 0.347E+03, 0.205E+03, 0.125E+03, 0.783E+02, 0.5E+02, 0.326E+02, 0.216E+02, 0.145E+02, 0.991E+01, 0.683E+01]#https://github.com/HephyAnalysisSW/StopsCompressed/blob/master/Tools/python/xSecSusyData/stops_13TeV.py
   if mst < stoparray[0]: return -1.
   if mst > stoparray[-1]: return -1.
   xsec = np.interp(mst, stoparray, xsecarray)   
   return xsec

mstop = 250
mX0 = 240
BR_true = 0.3
dataLumi = 137 #inverse femtobarns
cross_section_stop = get_xsec(mstop)
print("cross_section_stop = "+str(cross_section_stop))

if BR_true == 1.0:
    BR_true_str = "1.0"
elif BR_true == 0.3:
    BR_true_str = "0.3"

eff_filter = 0.13 #for mstop=200
BR_W_to_lep = 0.246
BR_stop_to_bW = BR_true
BR_factor = 2*BR_stop_to_bW*BR_W_to_lep-(BR_stop_to_bW**2)*(BR_W_to_lep**2)
print("BR_factor = "+str(BR_factor))
normalization_factor = dataLumi*cross_section_stop*BR_factor*eff_filter
print("normalization_factor = "+str(normalization_factor))



# Open the filtered .root file
input_file = ROOT.TFile.Open("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/file_with_new_weight_BR_"+BR_true_str+"_mstop_"+str(mstop)+"_mX0_"+str(mX0)+".root", "READ")
tree = input_file.Get("Events")  # Replace "Events" with the actual tree name if different

# Create a histogram for the mass of the particle
hist_mass = ROOT.TH1F("hist_mass", "Mass of particles with PDG ID ", 100, 0, 0.02)

#hist_list = [ROOT.TH1F(f"h{i}", f"Hist {i}", 50, 0, 200) for i in range(5)]
BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
BR_targets_i = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#BR_targets = [0.1, 0.4, 0.8, 1.0]
#BR_targets_i = [0, 3, 7, 9]

# Get the number of events (entries in the tree)
n_events = tree.GetEntries()
print "Total number of events: {}".format(n_events)

#create and initialize weighted sum array
weighted_sum = []
unweighted_sum = []
for k in range(0,len(BR_targets)):
    weighted_sum.append(0.0)
    unweighted_sum.append(0.0)

# Loop over the events in the tree
for event in tree:
    # Access the GenPart_mass and GenPart_pdgId arrays
    stop1_Lxy = event.stop1_Lxy
    weight_BRctau = event.ReweightBRctau
    stop1_ctau = event.stopCtau
    print(stop1_ctau)

    for j in range(len(BR_targets)):
        weight_j = weight_BRctau[BR_targets_i[j]]
        weighted_sum[j] = weighted_sum[j]+weight_j
        unweighted_sum[j] = unweighted_sum[j]+1
        print("..weight_j = "+str(weight_j))

    #print(weight_BRctau[9])

print("weighted_sum = "+str(weighted_sum))
print("unweighted_sum = "+str(unweighted_sum))





# Close the input file
input_file.Close()
