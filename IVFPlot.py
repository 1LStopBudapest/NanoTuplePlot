import os, sys
import ROOT

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser. '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-l', '--samplelist',   # either of this switches
    nargs='+',              # one or more parameters to this switch
    type=str,               # /parameters/ are ints
    dest='alist',           # store in 'list'.
    default=['TTToSemiLeptonic', 'TTTo2L2Nu', 'UL17V9_Full99mm']
    )
    argParser.add_argument('--cut',      type=str,      default='before')
    argParser.add_argument('--date',     type=str,      default='1117')
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
cut = options.cut
date = options.date


files = []
doplots = True
subfolder = 'IVF'
plots = ['MET', 'Leppt', 'LepMT', 'HT', 'CT1', 'CT2', 'ISRJetPt',
         'nSV', 'Ntracks', 'SVdxy', 'SVdxySig', 'SVmass', 'SVdlenSig', 'SVpAngle', 'SVpT', 'SVdR']

for sl in samplelists:
    if os.path.exists(plotDir+'1DFiles/IVF/1DHist_'+sl+'.root'): #if os.path.exists(plotDir+'1DFiles/IVF/1DHist_'+sl+'_'+cut+'_'+date+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'1DFiles/IVF/1DHist_'+sl+'.root')) #files.append(ROOT.TFile.Open(plotDir+'1DFiles/IVF/1DHist_'+sl+'_'+cut+'_'+date+'.root'))
    else:
        doplots = False
        print 'Root files for',sl,'sample does not exist. Please run python IVFHistMaker.py --sample',sl

if doplots :
    for p in plots:
        StackHists(files, samplelists, p, plotDir, subfolder)