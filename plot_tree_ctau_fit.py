import ROOT

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

# Open the filtered .root file
input_file = ROOT.TFile.Open("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/file_with_new_weight_BR_0.3_mstop_250_mX0_230.root", "READ")
tree = input_file.Get("Events")  # Replace "Events" with the actual tree name if different

# Create a histogram for the mass of the particle
hist_mass = ROOT.TH1F("hist_mass", "Mass of particles with PDG ID ", 100, 0, 0.02)

#hist_list = [ROOT.TH1F(f"h{i}", f"Hist {i}", 50, 0, 200) for i in range(5)]
hist_name = "stopCtau"
# BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# BR_targets_i = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#true_ctau = [303.58, 607.15, 910.73, 1214.31, 1517.88, 1821.46, 2125.04, 2428.61, 2732.19, 3035.77]
#true_ctau = [0.17, 0.34, 0.51, 0.67, 0.84, 1.01, 1.18, 1.35, 1.52, 1.68]
BR_targets = [0.1, 0.4, 0.8, 1.0]
BR_targets_i = [0, 3, 7, 9]
#true_ctau = [303.58, 1214.31, 2428.61, 3035.77]
true_ctau = [0.17, 0.67, 1.35, 1.68]

hist_list = [ROOT.TH1F("h"+hist_name+"{}".format(i), "Hist "+hist_name+" {}".format(i), 20, 0, 5) for i in BR_targets]
#In order to get the right statistical errors
for l in range(len(BR_targets)):
    hist_list[l].Sumw2()

# Loop over the events in the tree
for event in tree:
    # Access the GenPart_mass and GenPart_pdgId arrays
    stop1_ctau = event.stopCtau
    weight_BRctau = event.ReweightBRctau
    stop_decay = event.stopDecay
    # print(stop1_Lxy)

    if(stop_decay>3):
        for j in range(len(BR_targets)):
            weight_j = weight_BRctau[BR_targets_i[j]]
            hist_list[j].Fill(stop1_ctau,weight_j)

    #print(weight_BRctau[9])


# Create a canvas and draw the histogram
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)
canvas.SetLogy()


hist_list[0].SetTitle(hist_name+" reweighted from BR=0.3,mstop250 mX0230")
hist_list[0].GetXaxis().SetTitle(hist_name)
hist_list[0].GetYaxis().SetTitle("Events")
hist_list[0].SetStats(0)

fitted_ctau_str_list = []
FOM_str_list = []
for k in range(0,len(BR_targets)):
    
    hist_list[k].SetLineColor(kP10_colors_list_id[k])
    hist_list[k].SetLineWidth(2)
    #normalize to 1
    #hist_list[k].Scale(1.0 / hist_list[k].Integral("width"))

    if k==0:
        hist_list[k].Draw("HISTE")
        #fit_func_k.SetLineColor(ROOT.kRed)
        #fit_func_k.Draw("SAME")
    else:
        hist_list[k].Draw("histsameE")
        #fit_func_k.SetLineColor(ROOT.kRed)
        #fit_func_k.Draw("SAME")

    #set fit
    # Get the number of bins
    nbins = hist_list[k].GetNbinsX()
    # Initialize a variable to store the maximum x value
    max_x = None
    # Loop over bins (bin numbers go from 1 to nbins)
    for i in range(nbins, 0, -1):  # Start from highest bin
        if hist_list[k].GetBinContent(i) > 0:
            max_x = hist_list[k].GetBinLowEdge(i) + hist_list[k].GetBinWidth(i)
            break

        

    #fit_func_k = ROOT.TF1("fit_pdf", "(1.0 / [0]) * exp(-x / [0])", 0, max_x)
    #fit_func_k = ROOT.TF1("fit_pdf", "[1] * exp(-x / ([0]))+ [2]", 0, hist_list[k].GetXaxis().GetXmax())
    fit_func_k = ROOT.TF1("fit_pdf", "[1] * exp(-x / ([0]))", 0.01, hist_list[k].GetXaxis().GetXmax())
    # Set initial parameters
    #initial_ctau = hist_list[k].GetBinCenter(hist_list[k].GetMaximumBin())
    initial_ctau = hist_list[k].GetMean()
    initial_amp = hist_list[k].GetMaximum()
    fit_func_k.SetParameter(0, initial_ctau)  # ctau
    fit_func_k.SetParameter(1, initial_amp)   # amplitude
    #fit_func_k.SetParameter(2, 0.001 * initial_amp)   # backround
    #fit_func_k.SetParameter(0, hist_list[k].GetBinCenter(hist_list[k].GetMaximumBin()))
    fit_func_k.SetParLimits(0, 1e-2, 1e4)
    fit_func_k.SetParLimits(1, 1e-3, 1e4)
    #fit_func_k.SetParLimits(2, 1e-1, 1e6)

    # Fit the histogram
    fit_result = hist_list[k].Fit(fit_func_k, "LL RS")  # "R" = fit in specified range
    # Extract fitted ctau value and uncertainty
    fitted_ctau = fit_func_k.GetParameter(0)
    fitted_ctau_err = fit_func_k.GetParError(0)
    fitted_amp = fit_func_k.GetParameter(1)
    fitted_amp_err = fit_func_k.GetParError(1)

    chi2 = fit_result.Chi2()
    ndf = fit_result.Ndf()
    chi2_ndf = chi2 / ndf
    
    fitted_ctau_str = " FitCtau = {:.2f} +- {:.2f} mm".format(fitted_ctau, fitted_ctau_err)
    fitted_FOM_str = " #chi^2/dof = {:.2f}".format(chi2_ndf)
    #fitted_ctau_str2 = " ctau = {:.2f} +- {:.2f} mm, A = {:.2e} +- {:.2e}".format(
        #fitted_ctau, fitted_ctau_err, fitted_amp, fitted_amp_err)
    print(fitted_ctau_str)
    fitted_ctau_str_list.append(fitted_ctau_str)
    FOM_str_list.append(fitted_FOM_str)

    fitted_ctau_FOM_str = " chi^2/NDF= {:.2f}".format(chi2_ndf)
    fitted_ctau_chi2_str = " chi^2= {:.2f}".format(chi2)
    print(fitted_ctau_chi2_str)
    print(fitted_ctau_FOM_str)

    fit_func_k.SetLineColor(kP10_colors_list_id[k])
    fit_func_k.Draw("SAME")



# Add a legend
#Upper left
#legend = ROOT.TLegend(0.1, 0.65, 0.50, 0.9)
#Lower left
legend = ROOT.TLegend(0.1, 0.1, 0.65, 0.35)
for k in range(0,len(BR_targets)):
    #legend.AddEntry(hist_list[k], "BR = "+str(BR_targets[k])+" mean = "+str(hist_list[k].GetMean()), "l")
    #BR_sttring = "BR = %.1f  mean = %.2f" % (BR_targets[k], hist_list[k].GetMean())
    BR_sttring = "BR = %.1f" % (BR_targets[k])
    true_ctau_str = " TrueCtau = %.3f" % (true_ctau[k])
    legend.AddEntry(
        hist_list[k],
        BR_sttring+fitted_ctau_str_list[k]+true_ctau_str+FOM_str_list[k],
        "l"
    )
legend.SetTextSize(0.02)
legend.SetMargin(0.05)
legend.Draw()

# After all histograms are drawn and before saving:
max_y = 0
for hist in hist_list:
    if hist.GetMaximum() > max_y:
        max_y = hist.GetMaximum()
#hist_list[0].SetMaximum(max_y * 1e10)  # Set after Draw and SetLogy
canvas.Modified()
canvas.Update()


# Save the histogram as an image
canvas.SaveAs("met_histogram.png")

# Write the histogram to a new .root file (optional)
# output_file = ROOT.TFile("mass_histogram.root", "RECREATE")
# hist_mass.Write()
# output_file.Close() """

# Close the input file
input_file.Close()
