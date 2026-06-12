import ROOT
import os, sys, math

sys.path.append('../../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir


year = "2018"
masspoint = "450_430"
target_BR_folder = "BR_0.5"

sdir = '1DFiles_LL/'+year
filename = "1DHist_Sig_Splitted_"+masspoint+"_1_10.root"
Rootfilesdirpath = os.path.join(plotDir, sdir,target_BR_folder,filename)
out_plot_path = os.path.join(plotDir, sdir,target_BR_folder,"Sig_Splitted_"+masspoint)
print("plot dir is: "+str(Rootfilesdirpath))
print("root input file dir is: "+str(Rootfilesdirpath))

# Open the ROOT files
file1 = ROOT.TFile.Open(Rootfilesdirpath)
# file2 = ROOT.TFile.Open(Rootfilesdirpath+"/1DHist_Sig_Displaced_350_335_full_1_1000.root")
# file3 = ROOT.TFile.Open(Rootfilesdirpath+"/1DHist_Sig_Displaced_400_380_full_1_1000.root")

file1.ls()

variable = "cutFlow"

hist_name_1 = variable+"_Sig_Splitted_"+masspoint
# hist_name_2 = variable+"_Sig_Displaced_350_335_full"
# hist_name_3 = variable+"_Sig_Displaced_400_380_full"

# ... (previous code to open file and retrieve hist1)

# Get the original histogram
hist1 = file1.Get(hist_name_1)

# Create a new histogram with the same binning
n_bins = hist1.GetNbinsX()
xmin = hist1.GetXaxis().GetXmin()
xmax = hist1.GetXaxis().GetXmax()
hist_cumul = ROOT.TH1F(hist_name_1 + "_"+target_BR_folder, hist_name_1 + "_"+target_BR_folder, n_bins, xmin, xmax)

# Compute reverse cumulative sums (from last bin to first)
cumulative_sum = 0.0
cumulative_err = 0.0
for bin in range(n_bins, 0, -1):   # bins are 1-indexed
    cumulative_sum += hist1.GetBinContent(bin)
    cumulative_err += hist1.GetBinError(bin)**2
    hist_cumul.SetBinContent(bin, cumulative_sum)
    # Optional: set bin error (sum in quadrature)
    hist_cumul.SetBinError(bin, math.sqrt(cumulative_err))

# Define custom labels for bins 1 to 11 (bin index starts at 1)
custom_labels = ['nocut', 'passFilters', 'met200', 'ht300', 'isr', 'tauveto', 'lepton', 'xtralepton', 'xtrajetveto', 'dphi', 'SR']
# You could also use more descriptive strings, e.g. "Category A", etc.

# Apply the labels
for i, label in enumerate(custom_labels, start=1):
    hist_cumul.GetXaxis().SetBinLabel(i, label)

# Optional: propagate errors properly (if you need uncertainties)
# If you want error propagation, uncomment the lines inside the loop and initialize cumulative_err = 0.0
# For simplicity, errors are left as zero (default) in the example above.

canvas = ROOT.TCanvas("canvas", "Histograms", 800, 600)
# Now use hist_cumul for plotting instead of hist1
# You can keep the same styling (color, line width, etc.)
hist_cumul.SetLineColor(ROOT.kRed)
hist_cumul.SetLineWidth(3)
hist_cumul.SetStats(0)   # remove stats box

hist_cumul.GetYaxis().SetTitle("Number of events")
hist_cumul.GetYaxis().SetTitleSize(0.035)
hist_cumul.GetYaxis().SetTitleOffset(1.2)
hist_cumul.GetYaxis().SetLabelSize(0.03)
hist_cumul.GetXaxis().SetTitle(variable)
hist_cumul.GetXaxis().SetTitleSize(0.04)
hist_cumul.GetXaxis().SetTitleOffset(0.8)
hist_cumul.GetXaxis().SetLabelSize(0.04)

# Draw the cumulative histogram
hist_cumul.Draw("HIST")

# Update legend to reflect cumulative
legend = ROOT.TLegend(0.55, 0.75, 0.9, 0.9)
legend.AddEntry(hist_cumul, hist_name_1 + " (cumulative)", "l")
legend.Draw()


# Get y-axis range to place text in the middle
ymin = hist_cumul.GetMinimum()
ymax = hist_cumul.GetMaximum()
y_text = ymin + 0.5 * (ymax - ymin)

# Create text object
latex = ROOT.TLatex()
latex.SetTextAlign(22)  # center horizontally and vertically
latex.SetTextSize(0.03)

# Loop over bins
for i in range(2, hist_cumul.GetNbinsX() + 1):
    x = hist_cumul.GetBinCenter(i)

    prev = hist_cumul.GetBinContent(i-1)
    curr = hist_cumul.GetBinContent(i)
    percent = (curr* 100/prev)-100

    value = percent

    latex.DrawLatex(x, y_text, "{:.1f}%".format(value))

canvas.Update() 

"""
# ... after drawing the histogram (e.g., hist_cumul.Draw("HIST"))
# and after setting up the canvas (but before canvas.SaveAs)

canvas.Update()               # make sure the pad is ready
pad = canvas.GetPad(0)        # get the current pad

# Fixed vertical position in NDC (0=bottom, 1=top). 0.5 = center of canvas.
label_y_ndc = 0.5

n_bins = hist_cumul.GetNbinsX()     # number of bins (11 in your case)

for i in range(2, n_bins + 1):   # start from bin 2, skip the first bin
    prev = hist_cumul.GetBinContent(i-1)
    curr = hist_cumul.GetBinContent(i)

    if prev != 0:
        percent = (prev - curr) / prev * 100
        text = "{:+.1f}%".format(percent)  # e.g., "-50.0%"
    else:
        text = "0%"                 # or "N/A" if you prefer

    # Bin center in user coordinates (the x position)
    bin_center_x = hist_cumul.GetBinCenter(i)
    # Get pad margins
    left = ROOT.gStyle.GetPadLeftMargin()
    right = 1 - ROOT.gStyle.GetPadRightMargin()

    # Get axis range
    xmin = hist_cumul.GetXaxis().GetXmin()
    xmax = hist_cumul.GetXaxis().GetXmax()

    # Calculate NDC x coordinate
    ndc_x = left + (right - left) * (bin_center_x - xmin) / (xmax - xmin)

    # Create and draw the text
    latex = ROOT.TLatex(bin_center_x, label_y_ndc, text)
    #latex.SetNDC(True)                     # interpret coordinates as NDC
    latex.SetTextAlign(22)                 # center horizontally and vertically
    latex.SetTextSize(0.03)                # adjust font size as needed
    latex.Draw()
"""



# Save the canvas as before
canvas.SaveAs(out_plot_path + "/" + variable + "_cumulative.png")