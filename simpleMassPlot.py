import ROOT

# Open the filtered .root file
#input_file = ROOT.TFile.Open("output_test.root", "READ")
input_file = ROOT.TFile.Open("/big_data/LepStop/PostProcessedNtuple/2016/UL/SignalGrid/Prompt/T2tt/T2tt_400_380.root", "READ")
tree = input_file.Get("Events")  # Replace "Events" with the actual tree name if different

# Define the PDG ID of the particle you want to plot
pdgId_to_plot = 1000006  # top squark (stop)
#pdgId_to_plot = 1000022  # lightest neutralino 

# Create a histogram for the mass of the particle
hist_mass = ROOT.TH1F("hist_mass", "Mass of particles with PDG ID " + str(pdgId_to_plot), 100, 0, 0.02)

# Loop over the events in the tree
for event in tree:
    # Access the GenPart_mass and GenPart_pdgId arrays
    genPart_mass = event.GenPart_mass
    genPart_pdgId = event.GenPart_pdgId
    weight = event.weight

    # # Loop over the particles in the event
    # for i in range(len(genPart_pdgId)):
    #     if abs(genPart_pdgId[i]) == pdgId_to_plot:
    #         hist_mass.Fill(genPart_mass[i])

    # Loop over the particles in the event
    # for i in range(len(genPart_pdgId)):
    #     if abs(genPart_pdgId[i]) == pdgId_to_plot and weight<0.009:
    #         hist_mass.Fill(genPart_mass[i])

    hist_mass.Fill(weight)

# Create a canvas and draw the histogram
canvas = ROOT.TCanvas("canvas", "Canvas", 800, 600)

hist_mass.SetMinimum(0.1)
hist_mass.Draw("HIST")

canvas.SetLogy()

# Save the histogram as an image
canvas.SaveAs("mass_histogram.png")

# Write the histogram to a new .root file (optional)
# output_file = ROOT.TFile("mass_histogram.root", "RECREATE")
# hist_mass.Write()
# output_file.Close()

# Close the input file
input_file.Close()

