import ROOT
import sys

def get_branches(file_name):
    try:
        file = ROOT.TFile.Open(file_name)
        if not file or file.IsZombie():
            print("Error: Could not open " + file_name)
            return None
        
        tree = file.Get("Events")
        if not tree:
            print("Error: 'Events' tree not found in " + file_name)
            return None
        
        branches = set([branch.GetName() for branch in tree.GetListOfBranches()])
        file.Close()
        return branches
    except Exception as e:
        print("Error while processing " + file_name + ": " + str(e))
        return None

def compare_root_files(file1, file2):
    branches1 = get_branches(file1)
    branches2 = get_branches(file2)
    
    if branches1 is None or branches2 is None:
        print("Comparison could not be performed due to errors.")
        return
    
    if branches1 == branches2:
        print("Both files have the same branch structure.")
    else:
        print("Branch structures are different:")
        only_in_file1 = branches1 - branches2
        only_in_file2 = branches2 - branches1
        
        if only_in_file1:
            print("Branches only in " + file1 + ": ")
            for branch in only_in_file1:
                if "GenModel" not in branch:
                    print(branch)
        if only_in_file2:
            print("Branches only in " + file2 + ": " )
            for branch in only_in_file2:
                if "GenModel" not in branch:
                    print(branch)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_root_trees.py file1.root file2.root")
    else:
        compare_root_files(sys.argv[1], sys.argv[2])
