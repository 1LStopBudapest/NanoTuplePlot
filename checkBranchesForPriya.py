import ROOT
import os

# Specify the input folder path here
input_folder = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples"

# Create a TChain - specify the tree name (change "tree" to your actual tree name)
chain = ROOT.TChain("Events")  # Replace "tree" with your tree name if different

# Get list of all .root files in the folder
root_files = [f for f in os.listdir(input_folder) if f.endswith('.root')]

# Add each file to the chain
for root_file in root_files:
    full_path = os.path.join(input_folder, root_file)
    chain.Add(full_path)
    print("Added file: {}".format(full_path))

# Print summary
print("\nTotal number of files in chain: {}".format(len(root_files)))
print("Total number of entries in chain: {}".format(chain.GetEntries()))


tree_name = "Events"
tree = chain


delta_m_stop = 25
delta_m_x0 = [10,15,20,25,30]
list_of_valid_masspoints = []

nmasspoints = 0

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        nmasspoints = nmasspoints+1

        """
        real_name = "GenModel_T2tt_4bd_{0}_{1}_0.300".format(mStop, mX0)
        alias_name = "T2tt_{0}_{1}".format(mStop, mX0)
        tree.SetAlias(alias_name, real_name)
        # First check if BR branch exists
        branch_name = real_name
        if not tree.GetBranch(alias_name):
            print("Branch '{}' does not exist".format(branch_name))
        """
        

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
        else:
            print(".....................................")
            print("...ONE OF THE BRANCHES DOES NOT EXIST IN THE FILES..")
            print(".....................................")
        


print(list_of_valid_masspoints)
print(len(list_of_valid_masspoints))
print(nmasspoints)
