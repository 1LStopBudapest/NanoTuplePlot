import ROOT
import sys
import os
from math import sqrt, atan2, sin, cos

sys.path.append('../')
from Sample.SampleChain import SampleChain

from Sample.NewFile import NewClass

from Sample.SampleChainSplitting import SampleChainSplitting


startfile = 0
nfiles = 5
samples  = "Sig_NoSplitted_mStop_250to1100_full"

ch = SampleChainSplitting(samples, startfile, nfiles, "1984").getchain()
print 'Total events of selected files of the', samples, 'sample: ', ch.GetEntries()


#Define input and output files
#input_file_dir = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_27.root"
input_file_dir = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/disp/SMS_T2tt_mStop_250to1100_dM_10to30_LL_27.root"

output_file_dir = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/output_10.root"

#Define mass splitting ranges, first value is stop, second is neutralino
mass_ranges = [[0,100],[100,200],[200,300],[300,10000]]
#For testing
mA = 550
mB = 540

#Open input file

# Open the input .root file
# input_file = ROOT.TFile.Open(input_file_dir, "READ")
# tree = input_file.Get("Events")  # Replace "Events" with the actual tree name if different

#Create mask for selecting the mass
#cut = f"Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=={mA} && Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=={mB}"
#cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(s[0])+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(s[1])
#cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mA)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mB)
cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mA)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mB)
cut2 = "Max$(@GenModel_T2tt_4bd_"+str(mA)+"_"+str(mB)+"_1.000)=="+str(1)
cut3 = cut+"&&"+cut2

#Apply mask to select the mass
output_file = ROOT.TFile(output_file_dir, "RECREATE")
filtered_tree = ch.CopyTree(cut3)

# Write the filtered tree to the new file
filtered_tree.Write()

# Close the files
output_file.Close()
# input_file.Close()

print("Filtered events have been written to "+output_file_dir)