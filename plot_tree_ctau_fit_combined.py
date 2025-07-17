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

def get_filterEff_Grid(mst, dm, br):
    if dm==10.0: 
        x=0
    elif dm==15.0: 
        x=1
    elif dm==20.0: 
        x=2
    elif dm==25.0: 
        x=3
    elif dm==30.0: 
        x=4
    else:
        x=-1
    if br==0.1: 
        y=0
    elif br==0.2: 
        y=1
    elif br==0.3: 
        y=2
    elif br==0.4: 
        y=3
    elif br==0.5:
        y=4
    elif br==0.6: 
        y=5
    elif br==0.7:
        y=6
    elif br==0.8:
        y=7
    elif br==0.9:
        y=8
    elif br==1.0:
        y=9
    else:
        y=-1
        
    eff200 = [[1.232e-01,1.211e-01, 1.205e-01, 1.215e-01, 1.209e-01,1.209e-01,1.198e-01,1.203e-01,1.197e-01, 1.195e-01], [1.254e-01,1.217e-01,1.221e-01,1.227e-01,1.230e-01,1.235e-01,1.216e-01,1.222e-01,1.228e-01,1.184e-01], [1.323e-01,1.316e-01,1.309e-01,1.292e-01,1.265e-01,1.271e-01,1.245e-01,1.246e-01,1.247e-01,1.239e-01], [1.396e-01,1.386e-01,1.361e-01,1.351e-01,1.331e-01,1.307e-01,1.313e-01,1.290e-01,1.248e-01,1.250e-01], [1.433e-01,1.434e-01,1.419e-01,1.388e-01,1.353e-01,1.356e-01,1.331e-01,1.322e-01,1.319e-01,1.239e-01]]
    eff300 = [[0.1837, 0.1861, 0.1832, 0.1837, 0.1821, 0.1835, 0.182, 0.1826, 0.1809, 0.1821], [0.1881, 0.1889, 0.1838, 0.1851, 0.1837, 0.1871, 0.1832, 0.1824, 0.1832, 0.1857], [0.1948, 0.1919, 0.193, 0.1913, 0.1879, 0.1886, 0.1875, 0.1847, 0.1855, 0.1839], [0.2041, 0.2011, 0.2005, 0.1944, 0.1964, 0.1932, 0.1893, 0.1896, 0.1878, 0.1883], [0.2109, 0.2068, 0.2086, 0.2042, 0.2037, 0.2003, 0.1962, 0.1953, 0.1927, 0.1873]]
    eff400 = [[0.231, 0.2332, 0.2307, 0.2365, 0.2297, 0.231, 0.2301, 0.2295, 0.229, 0.2307], [0.2336, 0.237, 0.2382, 0.2333, 0.231, 0.2344, 0.2353, 0.2332, 0.2332, 0.2323], [0.245, 0.2425, 0.24, 0.241, 0.2349, 0.2373, 0.2361, 0.2351, 0.232, 0.2322], [0.2507, 0.2499, 0.2446, 0.2475, 0.2451, 0.2449, 0.2432, 0.2394, 0.2343, 0.2359], [0.2611, 0.2586, 0.2572, 0.2558, 0.2498, 0.249, 0.2498, 0.2457, 0.2402, 0.2373]]
    eff500 = [[0.2707, 0.2647, 0.2675, 0.2656, 0.2713, 0.2682, 0.267, 0.2636, 0.2661, 0.2675], [0.2695, 0.2743, 0.2742, 0.2694, 0.2679, 0.2707, 0.2701, 0.2716, 0.2641, 0.2681], [0.2796, 0.2775, 0.2762, 0.279, 0.2697, 0.2703, 0.2716, 0.2703, 0.2725, 0.2685], [0.2891, 0.286, 0.2863, 0.2826, 0.2808, 0.2784, 0.2791, 0.2725, 0.2744, 0.2725], [0.3017, 0.2964, 0.2928, 0.2937, 0.2915, 0.2874, 0.2801, 0.2789, 0.2756, 0.2777]]
    eff600 = [[2.938e-01,2.931e-01, 2.958e-01, 2.936e-01, 2.963e-01, 2.932e-01, 2.929e-01, 2.925e-01, 2.927e-01, 2.908e-01], [2.993e-01,2.997e-01, 2.998e-01, 2.962e-01, 2.946e-01, 2.942e-01, 2.960e-01, 2.958e-01, 2.948e-01, 2.971e-01], [3.077e-01,3.100e-01, 3.030e-01, 3.025e-01, 3.011e-01, 3.044e-01, 3.014e-01, 2.963e-01, 2.953e-01, 2.938e-01], [3.174e-01, 3.158e-01, 3.083e-01, 3.080e-01, 3.099e-01, 3.052e-01, 3.036e-01, 2.995e-01, 2.970e-01, 2.972e-01], [3.287e-01, 3.262e-01, 3.185e-01, 3.164e-01, 3.183e-01, 3.136e-01, 3.112e-01, 3.064e-01, 3.035e-01, 2.995e-01]]
    eff700 = [[0.3132, 0.3174, 0.3146, 0.3133, 0.3171, 0.3181, 0.3135, 0.3134, 0.3163, 0.3153], [0.3157, 0.3188, 0.3149, 0.3174, 0.3172, 0.3151, 0.3147, 0.3155, 0.3128, 0.3195], [0.3217, 0.3254, 0.3243, 0.3198, 0.3234, 0.3207, 0.3217, 0.3179, 0.313, 0.3176], [0.3385, 0.3339, 0.3311, 0.3252, 0.3273, 0.3231, 0.326, 0.3193, 0.3223, 0.3185], [0.3467, 0.3423, 0.3396, 0.3377, 0.3255, 0.3352, 0.3317, 0.3244, 0.3233, 0.3174]]
    eff800 = [[0.3273, 0.3271, 0.3301, 0.3322, 0.3296, 0.3267, 0.3276, 0.3285, 0.3252, 0.3295], [0.3341, 0.3322, 0.3302, 0.3304, 0.3266, 0.3301, 0.3264, 0.3343, 0.3337, 0.3263], [0.3399, 0.3391, 0.3423, 0.3333, 0.3346, 0.335, 0.3336, 0.3315, 0.3325, 0.3323], [0.3472, 0.3479, 0.349, 0.342, 0.3409, 0.3389, 0.3345, 0.3404, 0.336, 0.3321], [0.359, 0.3559, 0.3573, 0.3508, 0.3471, 0.3432, 0.3415, 0.344, 0.3375, 0.3369]]
    eff900 = [[0.3341, 0.3386, 0.3371, 0.3373, 0.3371, 0.3343, 0.3368, 0.334, 0.3331, 0.3354], [0.3393, 0.3356, 0.3396, 0.3397, 0.3397, 0.3337, 0.3401, 0.3348, 0.334, 0.3377], [0.3495, 0.3438, 0.3455, 0.3432, 0.3424, 0.3395, 0.3387, 0.3378, 0.3398, 0.3359], [0.3614, 0.3526, 0.351, 0.3508, 0.3512, 0.3467, 0.3478, 0.3436, 0.3432, 0.3411], [0.3638, 0.366, 0.3649, 0.3605, 0.3535, 0.353, 0.3533, 0.347, 0.3493, 0.3476]]
    eff1000 = [[0.3438, 0.3496, 0.3469, 0.3494, 0.3442, 0.3441, 0.3495, 0.3456, 0.3495, 0.3466], [0.3509, 0.3499, 0.3524, 0.3502, 0.3542, 0.3493, 0.3502, 0.3509, 0.348, 0.347], [0.3586, 0.3591, 0.3572, 0.3548, 0.3559, 0.3553, 0.3516, 0.3493, 0.3527, 0.3457], [0.3694, 0.3631, 0.3641, 0.3639, 0.3617, 0.363, 0.3557, 0.3576, 0.3523, 0.3556], [0.3804, 0.3756, 0.3725, 0.3745, 0.3694, 0.3648, 0.367, 0.3604, 0.3567, 0.357]]

    if mst==200:
        return eff200[x][y]
    elif mst==300:
        return eff300[x][y]
    elif mst==400:
        return eff400[x][y]
    elif mst==500:
        return eff500[x][y]
    elif mst==600:
        return eff600[x][y]
    elif mst==700:
        return eff600[x][y]
    elif mst==800:
        return eff800[x][y]
    elif mst==900:
        return eff900[x][y]
    else:
        return eff1000[x][y]

# Define 10 fixed color IDs in a safe range
base_color_id = 300
kP10_colors_list = []
kP10_colors_list_id = []

kP10_rgb = [
    ("kP10Blue",       (63, 144, 218)),
    ("kP10Orange",     (255, 169, 14)),
    ("kP10Red",        (189, 31, 1)),
    ("kP10Gray",       (148, 164, 162)),
    ("kP10Purple",     (131, 45, 182)),
    ("kP10Brown",      (169, 107, 89)),
    ("kP10DarkOrange", (231, 99, 0)),
    ("kP10Tan",        (185, 172, 112)),
    ("kP10DarkGray",   (113, 117, 129)),
    ("kP10LightBlue",  (146, 218, 221)),
]

# Create custom colors once at the beginning
for i, (name, (r, g, b)) in enumerate(kP10_rgb):
    color_id = ROOT.TColor.GetFreeColorIndex()
    new_color = ROOT.TColor(color_id, r / 255.0, g / 255.0, b / 255.0)
    kP10_colors_list.append(new_color)
    kP10_colors_list_id.append(color_id)

mstop = 250
mX0 = 230
Delta_m = abs(mstop-mX0)
dataLumi = 137 #inverse femtobarns
cross_section_stop = get_xsec(mstop)
print("cross_section_stop = "+str(cross_section_stop))
#eff_filter = 0.13 #for mstop=200
#eff_filter_10 = get_filterEff_Grid(mstop, Delta_m, 1.0)
#eff_filter_03 = get_filterEff_Grid(mstop, Delta_m, 0.3)
eff_filter_10 = get_filterEff_Grid(mstop, Delta_m, 0.8)
eff_filter_03 = get_filterEff_Grid(mstop, Delta_m, 0.8)


print("....1......")
# Open the filtered .root file
input_file_10 = ROOT.TFile.Open("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/file_with_new_weight_BR_1.0_mstop_"+str(mstop)+"_mX0_"+str(mX0)+".root", "READ")
input_file_03 = ROOT.TFile.Open("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/file_with_new_weight_BR_0.3_mstop_"+str(mstop)+"_mX0_"+str(mX0)+".root", "READ")

tree_10 = input_file_10.Get("Events")  # Replace "Events" with the actual tree name if different
tree_03 = input_file_03.Get("Events")
print("....2......")

hist_name = "stopCtau"
# BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# BR_targets_i = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#true_ctau = [303.58, 607.15, 910.73, 1214.31, 1517.88, 1821.46, 2125.04, 2428.61, 2732.19, 3035.77]
#true_ctau = [0.17, 0.34, 0.51, 0.67, 0.84, 1.01, 1.18, 1.35, 1.52, 1.68]
BR_targets = [0.1, 0.4, 0.8, 1.0]
BR_targets_i = [0, 3, 7, 9]
#true_ctau = [303.58, 1214.31, 2428.61, 3035.77]
true_ctau = [0.17, 0.67, 1.35, 1.68]

nbins = 20
hist_list_10 = [ROOT.TH1F("h_1.0_"+hist_name+"{}".format(i), "Hist 1.0 "+hist_name+" {}".format(i), nbins, 0, 15) for i in BR_targets]
hist_list_03 = [ROOT.TH1F("h_0.3_"+hist_name+"{}".format(i), "Hist 0.3 "+hist_name+" {}".format(i), nbins, 0, 15) for i in BR_targets]
hist_list_combined = [ROOT.TH1F("h"+hist_name+"{}".format(i), "Hist combined "+hist_name+" {}".format(i), nbins, 0, 15) for i in BR_targets]

print("....2.5......")

#In order to get the right statistical errors
for l in range(len(BR_targets)):
    hist_list_10[l].Sumw2()
    hist_list_03[l].Sumw2()
    hist_list_combined[l].Sumw2()

print("....3......")

# Loop over the events in the tree
for event_10 in tree_10:
    # Access the GenPart_mass and GenPart_pdgId arrays
    stop1_ctau_10 = event_10.stopCtau
    weight_BRctau_10 = event_10.ReweightBRctau
    stop_decay_10 = event_10.stopDecay
    if(stop_decay_10>3):
        for j in range(len(BR_targets)):
            weight_j_10 = weight_BRctau_10[BR_targets_i[j]]
            hist_list_10[j].Fill(stop1_ctau_10,weight_j_10)
print("....4......")

# Loop over the events in the tree
for event_03 in tree_03:
    # Access the GenPart_mass and GenPart_pdgId arrays
    stop1_ctau_03 = event_03.stopCtau
    weight_BRctau_03 = event_03.ReweightBRctau
    stop_decay_03 = event_03.stopDecay
    if(stop_decay_03>3):
        for j in range(len(BR_targets)):
            weight_j_03 = weight_BRctau_03[BR_targets_i[j]]
            hist_list_03[j].Fill(stop1_ctau_03,weight_j_03)
print("....5......")


#Normalize histograms
print("Begining normalization")
#First clone in order to keep the originals
hist_list_10_norm = []
hist_list_03_norm = []
for v in range(len(BR_targets)):
    hist_list_10_norm.append( hist_list_10[v].Clone("Hist "+hist_name+"") )
    hist_list_03_norm.append( hist_list_03[v].Clone("Hist "+hist_name+"") )
    #hist_list_10_norm[v].Sumw2()
    #hist_list_03_norm[v].Sumw2()

    #Get normalization scale
    BR_W_to_lep = 0.246
    BR_stop_to_bW = BR_targets[v]
    eff_filter = get_filterEff_Grid(mstop, Delta_m, BR_targets[v])

    BR_factor = 2*BR_stop_to_bW*BR_W_to_lep-(BR_stop_to_bW**2)*(BR_W_to_lep**2)
    print("BR_factor = "+str(BR_factor))
    predicted_nevents = dataLumi*cross_section_stop*BR_factor*eff_filter
    print("predicted_nevents = "+str(predicted_nevents))

    #Normalize histograms
    scale_10 = predicted_nevents / hist_list_10[v].Integral(0, -1)
    scale_03 = predicted_nevents / hist_list_03[v].Integral(0, -1)
    hist_list_10_norm[v].Scale(scale_10)
    hist_list_03_norm[v].Scale(scale_03)
    #Combine histograms
    #hist_list_combined[v].Add(hist_list_10_norm[v], hist_list_03_norm[v], BR_targets[v]*scale_10, (1-BR_targets[v])*scale_03)

    hist_list_combined[v] = BR_targets[v]*hist_list_10_norm[v] + (1-BR_targets[v])*hist_list_03_norm[v]

for l in range(len(BR_targets)):
    print("....integral.....")
    print(hist_list_10_norm[l].Integral(0, -1))
    print(hist_list_03_norm[l].Integral(0, -1))
    print(hist_list_combined[l].Integral(0, -1))
print("End normalization")
    

# Create a canvas and draw the histogram
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
canvas.SetLogy()


hist_list_combined[0].SetTitle(hist_name+" reweighted from BR=1.0 and BR=0.3,mstop250 mX0230")
hist_list_combined[0].GetXaxis().SetTitle(hist_name)
hist_list_combined[0].GetYaxis().SetTitle("Events")
hist_list_combined[0].SetStats(0)

fitted_ctau_str_list = []
FOM_str_list = []
for k in range(0,len(BR_targets)):
    
    hist_list_combined[k].SetLineColor(kP10_colors_list_id[k])
    hist_list_combined[k].SetLineWidth(2)
    #normalize to 1
    #hist_list_combined[k].Scale(1.0 / hist_list_combined[k].Integral("width"))

    if k==0:
        #hist_list_combined[k].Draw("HISTE")
        #fit_func_k.SetLineColor(ROOT.kRed)
        #fit_func_k.Draw("SAME")
        hist_list_combined[k].Draw("PE")
    else:
        #hist_list_combined[k].Draw("histsameE")
        #fit_func_k.SetLineColor(ROOT.kRed)
        #fit_func_k.Draw("SAME")
        hist_list_combined[k].Draw("psameE")

    #set fit
    # Get the number of bins
    nbins = hist_list_combined[k].GetNbinsX()
    # Initialize a variable to store the maximum x value
    max_x = None
    # Loop over bins (bin numbers go from 1 to nbins)
    for i in range(nbins, 0, -1):  # Start from highest bin
        if hist_list_combined[k].GetBinContent(i) > 0:
            max_x = hist_list_combined[k].GetBinLowEdge(i) + hist_list_combined[k].GetBinWidth(i)
            break

        

    #fit_func_k = ROOT.TF1("fit_pdf", "(1.0 / [0]) * exp(-x / [0])", 0, max_x)
    #fit_func_k = ROOT.TF1("fit_pdf", "[1] * exp(-x / ([0]))+ [2]", 0, hist_list_combined[k].GetXaxis().GetXmax())
    fit_func_k = ROOT.TF1("fit_pdf", "[1] * exp(-x / [0])", 0.01, hist_list_combined[k].GetXaxis().GetXmax())
    # Set initial parameters
    #initial_ctau = hist_list_combined[k].GetBinCenter(hist_list_combined[k].GetMaximumBin())
    initial_ctau = hist_list_combined[k].GetMean()
    initial_amp = hist_list_combined[k].GetMaximum()
    fit_func_k.SetParameter(0, true_ctau[k])  # ctau
    fit_func_k.SetParameter(1, initial_amp)   # amplitude
    #fit_func_k.SetParameter(2, 0.001 * initial_amp)   # backround
    #fit_func_k.SetParameter(0, hist_list_combined[k].GetBinCenter(hist_list_combined[k].GetMaximumBin()))
    fit_func_k.SetParLimits(0, 1e-2, 1e4)
    fit_func_k.SetParLimits(1, 1e-3, 1e6)
    #fit_func_k.SetParLimits(2, 1e-1, 1e6)

    # Fit the histogram
    fit_result = hist_list_combined[k].Fit(fit_func_k, "RS")  # "R" = fit in specified range
    #fit_result = hist_list_combined[k].Fit(fit_func_k, "S")  # "R" = fit in specified range

    # Extract fitted ctau value and uncertainty
    fitted_ctau = fit_func_k.GetParameter(0)
    fitted_ctau_err = fit_func_k.GetParError(0)
    fitted_amp = fit_func_k.GetParameter(1)
    fitted_amp_err = fit_func_k.GetParError(1)

    chi2 = fit_result.Chi2()
    ndf = fit_result.Ndf()
    chi2_ndf = chi2 / ndf

    #Manual calculation of chi**2 when using LL fits
    ########################
    chi2_manual = 0
    ndf_manual = 0

    for i in range(1, hist_list_combined[k].GetNbinsX() + 1):
        obs = hist_list_combined[k].GetBinContent(i)
        err = hist_list_combined[k].GetBinError(i)
        x = hist_list_combined[k].GetBinCenter(i)
        exp = fit_func_k.Eval(x)
        
        if err > 0:
            chi2_manual += ((obs - exp) ** 2) / (err ** 2)
            ndf_manual += 1

    ndf_manual -= fit_func_k.GetNpar()
    chi2_ndf_manual = chi2_manual / ndf_manual
    ####################3
    
    fitted_ctau_str = " FitCtau = {:.2f} +- {:.2f} mm".format(fitted_ctau, fitted_ctau_err)
    fitted_FOM_str = " #chi^2/dof = {:.2f}".format(chi2_ndf)
    fitted_FOM_str_manual = " #chi^2/dof MANUAL= {:.2f}".format(chi2_ndf_manual)
    #fitted_ctau_str2 = " ctau = {:.2f} +- {:.2f} mm, A = {:.2e} +- {:.2e}".format(
        #fitted_ctau, fitted_ctau_err, fitted_amp, fitted_amp_err)
    print(fitted_ctau_str)
    fitted_ctau_str_list.append(fitted_ctau_str)
    FOM_str_list.append(fitted_FOM_str)

    fitted_ctau_FOM_str = " chi^2/NDF= {:.2f}".format(chi2_ndf)
    fitted_ctau_chi2_str = " chi^2= {:.2f}".format(chi2)
    print(fitted_ctau_chi2_str)
    print(fitted_ctau_FOM_str)
    print(fitted_FOM_str_manual)

    fit_func_k.SetLineColor(kP10_colors_list_id[k])
    fit_func_k.Draw("SAME")



# Add a legend
#Upper left
#legend = ROOT.TLegend(0.1, 0.65, 0.50, 0.9)
#Lower left
legend = ROOT.TLegend(0.1, 0.1, 0.65, 0.35)
for k in range(0,len(BR_targets)):
    #legend.AddEntry(hist_list_combined[k], "BR = "+str(BR_targets[k])+" mean = "+str(hist_list_combined[k].GetMean()), "l")
    #BR_sttring = "BR = %.1f  mean = %.2f" % (BR_targets[k], hist_list_combined[k].GetMean())
    BR_sttring = "BR = %.1f" % (BR_targets[k])
    true_ctau_str = " TrueCtau = %.3f" % (true_ctau[k])
    legend.AddEntry(
        hist_list_combined[k],
        BR_sttring+fitted_ctau_str_list[k]+true_ctau_str+FOM_str_list[k],
        "l"
    )
legend.SetTextSize(0.02)
legend.SetMargin(0.05)
legend.Draw()

# After all histograms are drawn and before saving:
max_y = 0
for hist in hist_list_combined:
    if hist.GetMaximum() > max_y:
        max_y = hist.GetMaximum()
#hist_list_combined[0].SetMaximum(max_y * 1e10)  # Set after Draw and SetLogy
canvas.Modified()
canvas.Update()


# Save the histogram as an image
canvas.SaveAs("stop_ctau_combined_histogram.png")

# Write the histogram to a new .root file (optional)
# output_file = ROOT.TFile("mass_histogram.root", "RECREATE")
# hist_mass.Write()
# output_file.Close() """

# Close the input file
input_file_10.Close()
input_file_03.Close()

