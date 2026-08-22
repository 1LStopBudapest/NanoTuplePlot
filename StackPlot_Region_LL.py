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
        default=['VV', 'TTV', 'ZJetsToNuNu', 'QCD', 'DYJetsToLL', 'ST', 'TTbar', 'WJetsToLNu', 'Sig_Displaced_300_290_full', 'Sig_Displaced_350_335_full', 'Sig_Displaced_400_380_full'],     # last sample should be data (when data is included) as to be consistent with StackHists funtion.
    )
    argParser.add_argument('--fname',            action='store',                    type=str,            default='LLRegionHistMaker_',          help="root file name prefix?" )
    argParser.add_argument('--reg',            action='store',                    type=str,            default='DxyDz',          help="Which region?" )
    argParser.add_argument('--cut',            action='store',                    type=str,            default='LLDxyDzRegHist',          help="Which selection?" )
    argParser.add_argument('--filedir',            action='store',                    type=str,            default='LLRegionHistFiles',          help="Which directory input files are located?" )

    return argParser

options = get_parser().parse_args()

samplelists = options.alist
cut = options.cut
reg = options.reg
filedir = options.filedir
fname = options.fname

files = []
doplots = True

for sl in samplelists:
    if os.path.exists(fname+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(fname+reg+'_'+sl+'.root'))
    elif os.path.exists(plotDir+filedir+'/'+fname+reg+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+filedir+'/'+fname+reg+'_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for', sl, 'sample does not exist. Please run python LLRegionHistMaker.py --sample', sl

ROOT.gROOT.SetBatch(True)
if doplots:
    #StackHists(files, samplelists, 'h_reg', plotDir, cut)# use this one when data is included
    StackHistsNoDataExt(files, samplelists, 'h_reg', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_prompt', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_nonprompt', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_nonprompt_fromb', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_nonprompt_fromc', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_nonprompt_froml_or_ukn', plotDir, cut)
    StackHistsNoDataExt(files, samplelists, 'h_reg_nonprompt_unmatched', plotDir, cut)

    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_prompt', 'h_reg', plotDir, cut)
    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_nonprompt', 'h_reg', plotDir, cut)
    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_nonprompt_fromb', 'h_reg_nonprompt', plotDir, cut)
    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_nonprompt_fromc', 'h_reg_nonprompt', plotDir, cut)
    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_nonprompt_froml_or_ukn', 'h_reg_nonprompt', plotDir, cut)
    StackHistsNoDataExt_Alt(files, samplelists, 'h_reg_nonprompt_unmatched', 'h_reg_nonprompt', plotDir, cut)
