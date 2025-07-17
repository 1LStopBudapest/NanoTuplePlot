import ROOT
import os, sys

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir


year = "2018"
sample = "400_380"
#sample = "350_335"
#sample = "300_290"
variable = "epT"

sdir = '1DFiles_LL/'+year
Rootfilesdirpath = os.path.join(plotDir, sdir)
print("plot dir is: "+str(Rootfilesdirpath))

# Open the ROOT files
file1 = ROOT.TFile.Open(Rootfilesdirpath+"/1DHist_Sig_Displaced_"+sample+"_full_1_1000.root")
file2 = ROOT.TFile.Open(Rootfilesdirpath+"_lowPt/1DHist_Sig_Displaced_"+sample+"_full_1_1000_lowPt.root")
file3 = ROOT.TFile.Open(Rootfilesdirpath+"_std/1DHist_Sig_Displaced_"+sample+"_full_1_1000_std.root")

file1.ls()

hist_name_1 = variable+"_Sig_Displaced_"+sample+"_full"
hist_name_2 = variable+"_Sig_Displaced_"+sample+"_full"
hist_name_3 = variable+"_Sig_Displaced_"+sample+"_full"


# Retrieve histograms (replace "hist_name" with the actual histogram name)
hist1 = file1.Get(hist_name_1)
hist2 = file2.Get(hist_name_2)
hist3 = file3.Get(hist_name_3)

# Find the maximum values of each histogram
max1 = hist1.GetMaximum()
max2 = hist2.GetMaximum()
max3 = hist3.GetMaximum()

# Determine the overall maximum and scale it
overall_max = max(max1, max2, max3)
new_max = 1.2 * overall_max

# Set y-axis maximum
hist1.SetMaximum(new_max)  # Apply it to the first histogram (controls the axis)

# Create a canvas
canvas = ROOT.TCanvas("canvas", "Histograms", 800, 600)


hist1.GetYaxis().SetTitle("Number of events")
hist1.GetYaxis().SetTitleSize(0.035)
hist1.GetYaxis().SetTitleOffset(1.2)
hist1.GetYaxis().SetLabelSize(0.03)
hist1.GetXaxis().SetTitle(variable)
hist1.GetXaxis().SetTitleSize(0.04)
hist1.GetXaxis().SetTitleOffset(0.8)
hist1.GetXaxis().SetLabelSize(0.04)

# Set different colors
hist1.SetLineColor(ROOT.kRed)
hist2.SetLineColor(ROOT.kBlue)
hist3.SetLineColor(ROOT.kGreen)

# Set different colors
hist1.SetLineWidth(3)
hist2.SetLineWidth(3)
hist3.SetLineWidth(3)

# Draw histograms
hist1.Draw("HIST")  # First histogram sets the axis
hist2.Draw("HIST SAME")
hist3.Draw("HIST SAME")

#remove box of stats
hist1.SetStats(0)
hist2.SetStats(0)
hist3.SetStats(0)


# Enable log scale for both axes
#canvas.SetLogx(1)  # Log scale for X-axis
canvas.SetLogy(1)  # Log scale for Y-axis

# Add a legend
legend = ROOT.TLegend(0.55, 0.75, 0.9, 0.9)
legend.AddEntry(hist1, variable+" "+sample +"_"+ year + " " + "combined e", "l")
legend.AddEntry(hist2, variable+" "+sample +"_"+ year + " " + "lowPt e", "l")
legend.AddEntry(hist3, variable+" "+sample +"_"+ year + " " + "std e", "l")
legend.Draw()

# Save the plot as a PNG file
canvas.SaveAs(Rootfilesdirpath+"/"+variable+"_different_e.png")

# Show the plot
#canvas.Draw()

canvas.Close()