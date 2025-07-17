import ROOT

# Open the ROOT file
file = ROOT.TFile("/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_9.root", "READ")

# Get the tree
tree = file.Get("Events")  # replace with your tree name

# Create a set to store unique values
unique_values = set()

# Branch name you're interested in
branch_name = "SV_x"

nevents = 100

# Loop through all entries
# for entry in tree:
#     value = getattr(entry, branch_name)
#     unique_values.add(value)

# Loop over the first 100 entries (or less if tree has fewer entries)
for i in range(min(nevents, tree.GetEntries())):
    tree.GetEntry(i)
    value = getattr(tree, branch_name)
    print(value)


file.Close()