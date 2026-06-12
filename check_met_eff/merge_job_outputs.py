import os

def merge_files_simple(folder_path):
    """Simple version that merges files without user interaction."""
    print(folder_path)
    
    for ext in ['log', 'error', 'out']:
        # Collect all files with the given extension
        files = [f for f in os.listdir(folder_path) if f.endswith('.' + ext)]
        print(files)
        
        if files:
            output_filename = "./combined_" + ext + ".txt"
            with open(output_filename, 'w') as outfile:
                for fname in sorted(files):
                    outfile.write("\n\n=== " + fname + " ===\n\n")
                    infile_path = os.path.join(folder_path, fname)
                    with open(infile_path, 'r') as infile:
                        outfile.write(infile.read())
            print("Merged " + str(len(files)) + " ." + ext + " files")

merge_files_simple("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/check_met_eff/jobs_2018")  # Uses given directory
