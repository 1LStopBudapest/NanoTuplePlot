import ROOT

# Open the ROOT file
file = ROOT.TFile("/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_9.root", "READ")

# Get the tree
tree = file.Get("Events")  # replace with your tree name

# Create a set to store unique values
unique_values = set()

# Branch name you're interested in
branch_name = "GenModel_T2tt_4bd_400_380_0.300"

# Loop through all entries
for entry in tree:
    value = getattr(entry, branch_name)
    unique_values.add(value)

# Print the unique values
print "Unique values in branch '%s':" % branch_name
for val in sorted(unique_values):
    print val

file.Close()