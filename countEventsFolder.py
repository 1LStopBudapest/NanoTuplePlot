import ROOT
import os

def count_events_in_file(file_path, tree_name="Events"):
    """Count the number of events in a single .root file."""
    try:
        # Open the file in READ mode
        input_file = ROOT.TFile.Open(file_path, "READ")
        if not input_file or input_file.IsZombie():
            print("Error: Could not open file %s" % file_path)
            return 0

        # Get the TTree
        tree = input_file.Get(tree_name)
        if not tree:
            print("Error: Could not find tree '%s' in file %s" % (tree_name, file_path))
            input_file.Close()
            return 0

        # Get the number of entries (events)
        n_events = tree.GetEntries()
        input_file.Close()
        return n_events

    except Exception as e:
        print("Error processing file %s: %s" % (file_path, str(e)))
        return 0

def count_events_in_folder(folder_path, tree_name="Events"):
    """Count the number of events in all .root files in a folder."""
    total_events = 0
    file_count = 0  # Counter for the number of .root files

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".root"):
            file_path = os.path.join(folder_path, file_name)
            n_events = count_events_in_file(file_path, tree_name)
            print("File: %s, Events: %d" % (file_name, n_events))
            total_events += n_events
            file_count += 1  # Increment the file counter

    # Print the total number of files and events
    print("\nNumber of .root files: %d" % file_count)
    print("Total events in all files: %d" % total_events)

if __name__ == "__main__":
    # Specify the folder containing the .root files
    folder_path = "/big_data/LepStop/PostProcessedNtuple/displacedNonProcessedSamples/"  # Replace with your folder path

    # Call the function to count events
    count_events_in_folder(folder_path)