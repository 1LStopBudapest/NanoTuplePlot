import ROOT
import os

# Specify the input folder path here
#input_folder = "/eos/cms/store/group/phys_susy/hephy/StopsCompressed/nanoTuples/compstops_UL18v9_nano_v10_GenModel/Met/SMS_T2tt_mStop_250to1100_dM_10to30_LL"
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

nmasspoints = 0

for mStop in range(250,1100+delta_m_stop,delta_m_stop):
    
    for Dmx0 in delta_m_x0:
        mX0 = mStop-Dmx0
        nmasspoints = nmasspoints+1

        print(".....................................")
        print("mStop = "+str(mStop))
        print("mx0 = "+str(mX0))


        print("Filtering..................")
        #cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=={0}&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=={1}".format(mStop, mX0)
        cut = "Max$(GenPart_mass*(abs(GenPart_pdgId)==1000006))=="+str(mStop)+"&&Max$(GenPart_mass*(abs(GenPart_pdgId)==1000022))=="+str(mX0)
        filtered_tree = tree.CopyTree(cut)
        print("Filtering finished.........")

        branch_name = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_0.300"
        branch_name2 = "GenModel_T2tt_4bd_"+str(mStop)+"_"+str(mX0)+"_1.000"
        genmodel_branches = []

        for br in filtered_tree.GetListOfBranches():
            name = br.GetName()
            if name == branch_name:
                genmodel_branches.append(name)
            elif name == branch_name2:
                genmodel_branches.append(name)
        
        if len(genmodel_branches)<2:
            print(".....................................")
            print("...ONE OF THE BRANCHES DOES NOT EXIST IN THE FILES..")
            print(".....................................")
        else:
            print("WWWWWWWWWWWWWWWWWWWWWWW")
            print(genmodel_branches)
            print("WWWWWWWWWWWWWWWWWWWWWWW")



print(nmasspoints)
