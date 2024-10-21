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
    argParser.add_argument('--reg',            action='store',                    type=str,            default='SR+CR',          help="Which selection?" )
    argParser.add_argument('--cut',            action='store',                    type=str,            default='Val2',          help="Which selection?" )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
cut = options.cut
reg = options.reg

fname = 'PromptBKVal1_' if cut == 'Val1' else 'PromptBKVal2_'

files = []
doplots = True

for sl in samplelists:
    if os.path.exists(fname+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(fname+reg+'_'+sl+'.root'))
    elif os.path.exists(plotDir+'PromptValFiles/'+fname+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'PromptValFiles/'+fname+reg+'_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for', sl, 'sample does not exist. Please run python ',fname,'.py --sample', sl

if doplots:
    StackHists(files, samplelists, 'h_reg', plotDir, cut)
