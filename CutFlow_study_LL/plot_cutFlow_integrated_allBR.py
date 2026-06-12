import ROOT
import os, sys, math

sys.path.append('../../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir




year = "2018"
masspoint = "1075_1065"
variable = "cutFlow"
sdir = '1DFiles_LL/'+year
filename = "1DHist_Sig_Splitted_"+masspoint+"_1_10.root"
out_plot_path = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/CutFlow_study_LL"
#out_plot_path = os.path.join(plotDir, sdir,target_BR_folder,"Sig_Splitted_"+masspoint)

BR_list = ["BR_0.1","BR_0.2","BR_0.3","BR_0.4","BR_0.5","BR_0.6","BR_0.7","BR_0.8","BR_0.9","BR_1.0"]

Rootfilesdirpath_list = []
for BR_ in BR_list:
    root_dir_i = os.path.join(plotDir, sdir,BR_,filename)
    Rootfilesdirpath_list.append(root_dir_i)


print("plot dir is: "+str(out_plot_path))
print("root input file dir list is: "+str(Rootfilesdirpath_list))

# ==================== CMS 10-color categorical scheme ====================
# Source: https://cms-analysis.docs.cern.ch/guidelines/plotting/colors/#categorical-data-eg-1d-stackplots
cms_colors_hex = [
    "#3f90da", "#ffa90e", "#bd1f01", "#94a4a2",
    "#832db6", "#a96b59", "#e76300", "#b9ac70",
    "#717581", "#92dadd"
]

# Convert hex ROOT color indices (creates the colors on-the-fly)
cms_color_indices = []
for hex_col in cms_colors_hex:
    idx = ROOT.TColor.GetColor(hex_col)   # works directly in ROOT 6.14
    cms_color_indices.append(idx)

print("CMS colors registered:", cms_color_indices)   # optional debug

hist_cumul_list = []
for i, input_file_path in enumerate(Rootfilesdirpath_list):
    # Open the ROOT files
    file1 = ROOT.TFile.Open(input_file_path)
    
    file1.ls()
    
    hist_name_1 = variable+"_Sig_Splitted_"+masspoint
    print(hist_name_1)

    # Get the original histogram
    hist1 = file1.Get(hist_name_1)

    # Create a new histogram with the same binning
    n_bins = hist1.GetNbinsX()
    xmin = hist1.GetXaxis().GetXmin()
    xmax = hist1.GetXaxis().GetXmax()
    hist_cumul_i = ROOT.TH1F(hist_name_1 + "_"+BR_list[i], hist_name_1 + "_"+BR_list[i], n_bins, xmin, xmax)
    hist_cumul_i.SetDirectory(0)

    # Compute reverse cumulative sums (from last bin to first)
    cumulative_sum = 0.0
    cumulative_err = 0.0
    for bin in range(n_bins, 0, -1):   # bins are 1-indexed
        cumulative_sum += hist1.GetBinContent(bin)
        cumulative_err += hist1.GetBinError(bin)**2
        hist_cumul_i.SetBinContent(bin, cumulative_sum)
        # Optional: set bin error (sum in quadrature)
        hist_cumul_i.SetBinError(bin, math.sqrt(cumulative_err))

    # Define custom labels for bins 1 to 11 (bin index starts at 1)
    custom_labels = ['nocut', 'passFilters', 'met200', 'ht300', 'isr', 'tauveto', 'lepton', 'xtralepton', 'xtrajetveto', 'dphi', 'SR']
    # You could also use more descriptive strings, e.g. "Category A", etc.

    # Apply the labels
    for i, label in enumerate(custom_labels, start=1):
        hist_cumul_i.GetXaxis().SetBinLabel(i, label)

    hist_cumul_list.append(hist_cumul_i)
    file1.Close()

print(hist_cumul_list)



canvas = ROOT.TCanvas("canvas", "Histograms", 800, 600)
# canvas.SetLogy(1)

for j, hist_ in enumerate(hist_cumul_list):
    hist_.SetLineColor(cms_color_indices[j])   #your beautiful CMS colors
    hist_.SetLineWidth(3)
    hist_.SetStats(0)
    
    hist_.GetYaxis().SetTitle("Number of events")
    hist_.GetYaxis().SetTitleSize(0.035)
    hist_.GetYaxis().SetTitleOffset(1.2)
    hist_.GetYaxis().SetLabelSize(0.03)
    
    hist_.GetXaxis().SetTitle(variable)
    hist_.GetXaxis().SetTitleSize(0.04)
    hist_.GetXaxis().SetTitleOffset(0.8)
    hist_.GetXaxis().SetLabelSize(0.04)
    
    if j == 0:
        hist_.Draw("HIST")
    else:
        hist_.Draw("HIST same")

# Legend (already perfect with BR names)
legend = ROOT.TLegend(0.55, 0.65, 0.9, 0.9)
for j, hist_ in enumerate(hist_cumul_list):
    legend.AddEntry(hist_, BR_list[j], "l")
legend.Draw()

canvas.Update()
canvas.SaveAs(out_plot_path + "/" + variable + "_cumulative.png")
