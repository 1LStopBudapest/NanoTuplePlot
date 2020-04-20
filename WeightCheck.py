import os, sys
import types
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.FileList_2016 import samples


sample1 = 'TTSingleLep_pow'
startfile1 = 0
nfiles1 = -1
nEvents1 = 10

tr = SampleChain(sample1, startfile1, nfiles1).getchain()

n_entries = tr.GetEntries()

for ientry in range(n_entries):
    if not nEvents1 == -1 and ientry > nEvents1 - 1: break
    tr.GetEntry(ientry)
    print 'genWeight', tr.genWeight
    print 'lumi weight: ', tr.weight

    

samplelist = samples

print 'sample: ', sample1, ' Xsec: ', samplelist[sample1][1],' Nevents: ', samplelist[sample1][2], ' scale: ', 1000*(samplelist[sample1][1]/samplelist[sample1][2]) 
