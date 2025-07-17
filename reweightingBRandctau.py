import ROOT
import sys


sys.path.append('../')
from Sample.SampleChainSplitting import SampleChainSplitting
from array import array

startfile = 0
nfiles = 10000000
samples  = "Sig_NoSplitted_mStop_250to1100_full"

#If using chain, uncomment
# ch = SampleChainSplitting(samples, startfile, nfiles, "1984").getchain()
# print 'Total events of selected files of the', samples, 'sample: ', ch.GetEntries()

# File and branch info
filename = "/big_data/LepStop/CentralFullNano/00EE1FC4-D27B-ED47-A567-F7B2E4C766B4.root"
tree_name = "Events"

# Open the ROOT file
file = ROOT.TFile.Open(filename)
if not file or file.IsZombie():
    print("Failed to open file: " + str(filename))
    exit(1)

# Get the TTree
tree = file.Get(tree_name)
if not tree:
    print("TTree '" + str(tree_name) + "' not found in file.")
    file.Close()
    exit(1)

#If using chain, uncomment
# tree_name = "Events"
# tree = ch

delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]

total_events = tree.GetEntries()

#For loop goes over all masspoints
for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    print("mStop = "+str(mStop))
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        print("mx0 = "+str(mX0))

        #Check BR 0.300
        branch_name = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_0.300"
        # Check if the branch exists
        branch = tree.GetBranch(branch_name)

        if branch:
            print("Branch '" + str(branch_name) + "' exists in the tree '" + str(tree_name) + "'.")

            for event in tree:
                # Access the GenPart_mass and GenPart_pdgId arrays
                branching_ratio = getattr(event, branch_name)
                ones_count = ones_count+float(branching_ratio)

        else:
            print("Branch '" + str(branch_name) + "' does NOT exist in the tree '" + str(tree_name) + "'.")

        #Check BR 1.000
        branch_name2 = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_1.000"
        # Check if the branch exists
        branch = tree.GetBranch(branch_name2)
        if branch:
            print("Branch '" + str(branch_name2) + "' exists in the tree '" + str(tree_name) + "'.")
        else:
            print("Branch '" + str(branch_name2) + "' does NOT exist in the tree '" + str(tree_name) + "'.")

        

        


print("..........................................................................")
print("the total number of ones inside all the brances is = "+str(ones_count))
print("the total number of total_events is = "+str(total_events))


# Clean up, if using chain comment
file.Close()
