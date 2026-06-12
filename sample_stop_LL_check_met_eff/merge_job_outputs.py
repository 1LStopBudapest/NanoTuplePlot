import os
from pathlib import Path

def merge_files_simple(folder_path):
    """Simple version that merges files without user interaction."""
    folder = Path(folder_path)
    print(folder)
    
    for ext in ['log', 'error', 'out']:
        files = list(folder.glob(f"*.{ext}"))
        print(files)
        if files:
            with open(f"combined_{ext}.txt", 'w') as outfile:
                for file in sorted(files):
                    outfile.write(f"\n\n=== {file.name} ===\n\n")
                    with open(file, 'r') as infile:
                        outfile.write(infile.read())
            print(f"Merged {len(files)} .{ext} files")


merge_files_simple("/media/moises/Data/workspacePcElte/sample_stop_LL_test_condor/jobs_2016")  # Uses current directory