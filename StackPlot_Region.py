import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
#from Helper.PlotHelper_Region import *
from Helper.PlotHelper import *

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
    default=['VV', 'TTV', 'ZJetsToNuNu', 'QCD', 'DYJetsToLL', 'ST', 'TTbar', 'WJetsToLNu', 'MET_Data'],     # last sample should be data as to be consistent with StackHists funtion.
    )
    argParser.add_argument('--reg',            action='store',                    type=str,            default='CR',          help="Which selection?" )
    argParser.add_argument('--cut',            action='store',                    type=str,            default='CR',          help="Which selection?" )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
cut = options.cut
reg = options.reg

files = []
doplots = True

for sl in samplelists:
    if os.path.exists('RegionPlot_'+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open('RegionPlot_'+reg+'_'+sl+'.root'))
    elif os.path.exists(plotDir+'RegionHistFiles/RegionPlot_'+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'RegionHistFiles/RegionPlot_'+reg+'_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for', sl, 'sample does not exist. Please run python RegionPlot.py --sample', sl

if doplots:
    StackHists(files, samplelists, 'h_reg', plotDir, cut)
