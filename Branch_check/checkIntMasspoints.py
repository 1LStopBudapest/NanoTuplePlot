import ROOT
import os

# Specify the input folder path here
input_folder = "/eos/cms/store/group/phys_susy/hephy/StopsCompressed/nanoTuples/compstops_UL18v9_nano_v10_GenModel/Met/SMS_T2tt_mStop_250to1100_dM_10to30_LL"

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
stop_pdgid = 1000006
x0_pdgid = 1000022
nentry = 0

# Loop over entries
for entry in chain:

    if nentry % 100000 == 0:
        #print(f"Processing {nentry}th event")
        print ("processing "+str(nentry)+"th event")

    for i, pdgId in enumerate(entry.GenPart_pdgId):
        if pdgId == stop_pdgid:
            stop_mass = entry.GenPart_mass[i]
            #print("stop found with mass = "+str(stop_mass))
            if not float( abs(stop_mass) ).is_integer():
                print("Non-integer value found: stop mass = "+str(stop_mass))
        if pdgId == x0_pdgid:
            x0_mass = entry.GenPart_mass[i]
            #print("x0 found with mass = "+str(x0_mass))
            if not float( abs(x0_mass) ).is_integer():
                print("Non-integer value found: x0 mass = "+str(x0_mass))

    nentry += 1

print("end of events")