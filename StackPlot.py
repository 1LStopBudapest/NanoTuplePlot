import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser.                                                                                                                                                 
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-l', '--samplelist',  # either of this switches
    nargs='+',       # one or more parameters to this switch
    type=str,        # /parameters/ are ints
    dest='alist',     # store in 'list'.
    default=['WJetsToLNu', 'MET_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist


files = []
doplots = True

for sl in samplelists:
    if os.path.exists('StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open('StackHist_'+sl+'.root'))
    elif os.path.exists(plotDir+'StackFiles/StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'StackFiles/StackHist_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for',sl,'sample soes not exist. Please run python StackHistMaker.py --sample',sl

if doplots :
    StackHists(files, samplelists, 'MET', plotDir, 'final')
    StackHists(files, samplelists, 'Leppt', plotDir, 'final')
    StackHists(files, samplelists, 'LepMT', plotDir, 'final')
    StackHists(files, samplelists, 'HT', plotDir, 'final')
    StackHists(files, samplelists, 'CT1', plotDir, 'final')
    StackHists(files, samplelists, 'CT2', plotDir, 'final')
    StackHists(files, samplelists, 'ISRJetPt', plotDir, 'final')
    StackHists(files, samplelists, 'ISRJetEta', plotDir, 'final')
    StackHists(files, samplelists, 'SSRJetPt', plotDir, 'final')
    StackHists(files, samplelists, 'Njet', plotDir, 'final')
    StackHists(files, samplelists, 'BjetPt', plotDir, 'final')
    StackHists(files, samplelists, 'Nbjet30', plotDir, 'final')
