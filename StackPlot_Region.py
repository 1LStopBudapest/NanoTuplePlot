import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper_Region import *

def get_parser():
    ''' Argument parser.                                                                                                                                                 
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-l', '--samplelist',                   # either of this switches
    nargs='+',                              # one or more parameters to this switch
    type=str,                               # /parameters/ are ints
    dest='alist',                           # store in 'list'.
    default=['WJetsToLNu', 'MET_Data'],     # last sample should be data as to be consistent with StackHists funtion.
    )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist


files = []
doplots = True

for sl in samplelists:
    if os.path.exists('RegionPlot_SR_'+sl+'.root'):
        files.append(ROOT.TFile.Open('RegionPlot_SR_'+sl+'.root'))
    elif os.path.exists(plotDir+'RegionFiles/RegionPlot_SR_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'RegionFiles/RegionPlot_SR_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for', sl, 'sample soes not exist. Please run python StackHistMaker.py --sample', sl

if doplots:
    StackHists(files, samplelists, 'h_reg', plotDir, 'final')
