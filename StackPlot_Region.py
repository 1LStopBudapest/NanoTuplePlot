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
    default=['VV', 'DYJetsToLL', 'ST', 'QCD', 'WJetsToLNu', 'TTbar', 'TTV', 'ZJetsToNuNu', 'T2tt_500_470', 'T2tt_700_620'], # last sample should be data as to be consistent with StackHists funtion.
    )
    argParser.add_argument('--cut',            action='store',                    type=str,            default='jet30',          help="Which selection?" )
    
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
cut = options.cut

files = []
doplots = True

for sl in samplelists:
    if os.path.exists('RegionPlot_SR_'+sl+'.root'):
        files.append(ROOT.TFile.Open('RegionPlot_SR_'+sl+'.root'))
    elif os.path.exists(plotDir+'RegionFiles/extension/RegionPlot_SR_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'RegionFiles/extension/RegionPlot_SR_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for', sl, 'sample does not exist. Please run python RegionPlot.py --sample', sl

if doplots:
    StackHists(files, samplelists, 'h_reg', plotDir, 'extension')
