import os
from pathlib import Path

def merge_files_simple(folder_path):
    """Simple version that merges files without user interaction."""
    folder = Path(folder_path)
    print(folder)
    
    for ext in ['log', 'error', 'out']:
        files = list(folder.glob("*."+ext))
        print(files)
        if files:
            with open("combined_"+ext+".txt", 'w') as outfile:
                for file in sorted(files):
                    outfile.write("\n\n=== "+file.name+" ===\n\n")
                    print(file)
                    with open(str(file), 'r') as infile:
                        outfile.write(infile.read())
            print("Merged "+str(len(files))+" ."+ext+" files")


merge_files_simple("/home/mleoncoe/stopAnalysis/test/NanoTuplePlot/sample_reweighting/jobs_2016")