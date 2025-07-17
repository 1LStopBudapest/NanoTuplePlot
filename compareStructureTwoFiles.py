import ROOT

def print_keys(root_file, file_name):
    """Print the keys in a ROOT file."""
    print("Keys in file '{}':".format(file_name))
    keys = root_file.GetListOfKeys()
    for i in range(keys.GetSize()):
        key = keys.At(i)
        print("  - {} (Type: {})".format(key.GetName(), key.GetClassName()))

def compare_root_files(file1, file2):
    # Open the two ROOT files
    root_file1 = ROOT.TFile.Open(file1)
    root_file2 = ROOT.TFile.Open(file2)

    if not root_file1 or not root_file2:
        print("Error: One or both files could not be opened.")
        return False

    # Get the list of keys in each file
    keys1 = root_file1.GetListOfKeys()
    keys2 = root_file2.GetListOfKeys()

    # Compare the number of keys
    if keys1.GetSize() != keys2.GetSize():
        print("The files have different numbers of keys.")
        print_keys(root_file1, file1)
        print_keys(root_file2, file2)
        return False

    # Compare the names and types of the keys
    for i in range(keys1.GetSize()):
        key1 = keys1.At(i)
        key2 = keys2.At(i)

        # Remove suffixes like ":1" or ";2" for comparison
        name1 = key1.GetName().split(";")[0]
        name2 = key2.GetName().split(";")[0]

        if name1 != name2:
            print("Key names differ: {} vs {}".format(name1, name2))
            return False

        if key1.GetClassName() != key2.GetClassName():
            print("Key types differ: {} vs {}".format(key1.GetClassName(), key2.GetClassName()))
            return False

        # If the key is a TTree, compare the tree structures and data
        if key1.GetClassName() == "TTree":
            tree1 = root_file1.Get(key1.GetName())
            tree2 = root_file2.Get(key2.GetName())

            if not compare_trees(tree1, tree2):
                return False

    print("The files have the same structure and data.")
    return True

def compare_trees(tree1, tree2):
    # Compare the number of branches
    if tree1.GetNbranches() != tree2.GetNbranches():
        print("Trees {} and {} have different numbers of branches.".format(tree1.GetName(), tree2.GetName()))
        return False

    # Compare the branch names and types
    branches1 = tree1.GetListOfBranches()
    branches2 = tree2.GetListOfBranches()

    for i in range(branches1.GetEntries()):
        branch1 = branches1.At(i)
        branch2 = branches2.At(i)

        if branch1.GetName() != branch2.GetName():
            print("Branch names differ: {} vs {}".format(branch1.GetName(), branch2.GetName()))
            return False

        if branch1.GetClassName() != branch2.GetClassName():
            print("Branch types differ: {} vs {}".format(branch1.GetClassName(), branch2.GetClassName()))
            return False

    # Compare the number of entries
    if tree1.GetEntries() != tree2.GetEntries():
        print("Trees {} and {} have different numbers of entries.".format(tree1.GetName(), tree2.GetName()))
        return False

    # Compare the data in each entry
    for i in range(tree1.GetEntries()):
        tree1.GetEntry(i)
        tree2.GetEntry(i)

        for branch in branches1:
            branch_name = branch.GetName()
            value1 = getattr(tree1, branch_name)
            value2 = getattr(tree2, branch_name)

            if value1 != value2:
                print("Data mismatch in tree {} at entry {} for branch {}: {} vs {}".format(
                    tree1.GetName(), i, branch_name, value1, value2))
                return False

    return True



# Example usage
#file1 = "/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/output_test.root"
file1 = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/disp/SMS_T2tt_mStop_250to1100_dM_10to30_LL_27.root"
file2 = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/SMS_T2tt_mStop_250to1100_dM_10to30_27.root"
compare_root_files(file1, file2)