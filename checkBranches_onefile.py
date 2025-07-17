import ROOT
import sys


# sys.path.append('../')
# from Sample.SampleChainSplitting import SampleChainSplitting


# startfile = 0
# nfiles = 1000000
# samples  = "Sig_NoSplitted_mStop_250to1100_full"

# ch = SampleChainSplitting(samples, startfile, nfiles, "1984").getchain()
# print 'Total events of selected files of the', samples, 'sample: ', ch.GetEntries()

# File and branch info
#filename = "/big_data/LepStop/CentralFullNano/00EE1FC4-D27B-ED47-A567-F7B2E4C766B4.root"
filename = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_0.root"
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

tree_name = "Events"
# tree = ch


delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]
list_of_valid_masspoints = []

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        

        #Check BR 0.300
        branch_name = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_0.300"
        # Check if the branch exists
        branch1 = tree.GetBranch(branch_name)
        """ if branch1:
            print("Branch '" + str(branch_name) + "' exists in the tree '" + str(tree_name) + "'.")
        else:
            print("Branch '" + str(branch_name) + "' does NOT exist in the tree '" + str(tree_name) + "'.")
        """
        #Check BR 1.000
        branch_name2 = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_1.000"
        # Check if the branch exists
        branch2 = tree.GetBranch(branch_name2)
        """ if branch2:
            print("Branch '" + str(branch_name2) + "' exists in the tree '" + str(tree_name) + "'.")
        else:
            print("Branch '" + str(branch_name2) + "' does NOT exist in the tree '" + str(tree_name) + "'.") """

        if branch1 and branch2:
            list_of_valid_masspoints.append([mStop,mX0])
            print(".....................................")
            print("mStop = "+str(mStop))
            print("mx0 = "+str(mX0))
            print("Branch '" + str(branch_name) + "' exists in the tree '" + str(tree_name) + "'.")
            print("Branch '" + str(branch_name2) + "' exists in the tree '" + str(tree_name) + "'.")


print(list_of_valid_masspoints)
print(len(list_of_valid_masspoints))


# Clean up
#file.Close()
