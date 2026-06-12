import ROOT
import sys


sys.path.append('../')
from Sample.SampleChainSplitting import SampleChainSplitting


startfile = 0
nfiles = 1000000
samples  = "Sig_NoSplitted_mStop_250to1100_full"

ch = SampleChainSplitting(samples, startfile, nfiles, "1984").getchain()


tree = ch

print("chain obtained")
"""
event_list = []
nentry = 0
# Loop over the events in the tree
for event in tree:
    # Access the GenPart_mass and GenPart_pdgId arrays
    event_value = event.event

    if nentry % 10000==0 : 
        print 'processing ', nentry,'th event'

    if event_value in event_list:
        print("repeated value")
    else:
        event_list.append(event_value)

    nentry = nentry+1
"""

# Assuming tree is already loaded (e.g., from a ROOT file)
event_set = set()
nentry = 0

# Loop over the events in the tree
for event in tree:
    event_value = event.event

    if nentry % 10000 == 0:
        #print(f"Processing {nentry}th event")
        print 'processing ', nentry,'th event'

    if event_value in event_set:
        print("repeated value")
    else:
        event_set.add(event_value)

    nentry += 1

print("Finished checking for duplicates.")

    