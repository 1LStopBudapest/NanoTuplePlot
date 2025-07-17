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
input_file = ROOT.TFile.Open("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/file_with_new_weight_BR_0.3_mstop_250_mX0_240.root", "READ")
tree = input_file.Get("Events")  # Replace "Events" with the actual tree name if different

# Create a histogram for the mass of the particle
hist_mass = ROOT.TH1F("hist_mass", "Mass of particles with PDG ID ", 100, 0, 0.02)

#hist_list = [ROOT.TH1F(f"h{i}", f"Hist {i}", 50, 0, 200) for i in range(5)]
hist_name = "stop1_Lxy"
BR_targets = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
BR_targets_i = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#BR_targets = [0.1, 0.4, 0.8, 1.0]
#BR_targets_i = [0, 3, 7, 9]

hist_list = [ROOT.TH1F("h"+hist_name+"{}".format(i), "Hist "+hist_name+" {}".format(i), 10, 0, 4000) for i in BR_targets]


# Loop over the events in the tree
for event in tree:
    # Access the GenPart_mass and GenPart_pdgId arrays
    stop1_Lxy = event.stop1_Lxy
    weight_BRctau = event.ReweightBRctau
    # print(stop1_Lxy)

    for j in range(len(BR_targets)):
        weight_j = weight_BRctau[BR_targets_i[j]]
        hist_list[j].Fill(stop1_Lxy,weight_j)

    #print(weight_BRctau[9])


# Create a canvas and draw the histogram
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)

hist_list[0].SetMinimum(0.1)
hist_list[0].SetTitle(hist_name+" reweighted from BR=1.0,mstop250 mX0240")
hist_list[0].GetXaxis().SetTitle(hist_name)
hist_list[0].GetYaxis().SetTitle("Events")

for k in range(0,len(BR_targets)):
    
    hist_list[k].SetLineColor(kP10_colors_list_id[k])
    hist_list[k].SetLineWidth(2)
    if k==0:
        hist_list[k].Draw("HIST")
    else:
        hist_list[k].Draw("histsame")
    

canvas.SetLogy()

# Add a legend
legend = ROOT.TLegend(0.3, 0.65, 0.55, 0.9)
for k in range(0,len(BR_targets)):
    #legend.AddEntry(hist_list[k], "BR = "+str(BR_targets[k])+" mean = "+str(hist_list[k].GetMean()), "l")
    legend.AddEntry(
        hist_list[k],
        "BR = %.3f  mean = %.2f" % (BR_targets[k], hist_list[k].GetMean()),
        "l"
    )
legend.Draw()


# Save the histogram as an image
canvas.SaveAs("met_histogram.png")

# Write the histogram to a new .root file (optional)
# output_file = ROOT.TFile("mass_histogram.root", "RECREATE")
# hist_mass.Write()
# output_file.Close() """

# Close the input file
input_file.Close()
