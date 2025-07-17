import ROOT

def list_branches(root_file_path, tree_name):
    """List all branches in a ROOT tree"""
    # Open the ROOT file
    root_file = ROOT.TFile(root_file_path, "READ")
    if not root_file or root_file.IsZombie():
        print("Error: Could not open file %s" % root_file_path)
        return

    # Get the tree
    tree = root_file.Get(tree_name)
    if not tree:
        print("Error: Could not find tree %s in file" % tree_name)
        root_file.Close()
        return

    # Get list of branches
    branches = tree.GetListOfBranches()

    print("\nBranches in tree '%s':" % tree_name)
    print("=" * (12 + len(tree_name)))
    
    # Print each branch name
    for i in range(branches.GetEntries()):
        branch = branches.At(i)
        print("%3d: %s" % (i+1, branch.GetName()))
    
    print("\nTotal branches: %d" % branches.GetEntries())
    root_file.Close()

# Example usage
if __name__ == "__main__":
    file_path = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_LL_9.root"  # Change to your file path
    tree_name = "Events"  # Change to your tree name
    list_branches(file_path, tree_name)