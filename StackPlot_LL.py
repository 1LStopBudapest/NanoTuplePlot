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
    default=['WJetsToLNu', 'TTbar', 'ST', 'DYJetsToLL', 'ZJetsToNuNu', 'QCD', 'TTV', 'VV', 'Sig_Displaced_300_290_full', 'Sig_Displaced_350_335_full', 'Sig_Displaced_400_380_full', 'MET_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist


files = []
doplots = True

for sl in samplelists:
    if os.path.exists('StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open('StackHist_'+sl+'.root'))
    elif os.path.exists(plotDir+'StackFiles/Displaced/Dxy3/Dz2/StackHist_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'StackFiles/Displaced/Dxy3/Dz2/StackHist_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for',sl,'sample soes not exist. Please run python StackHistMaker.py --sample',sl


vList = ['MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'LeppT', 'Lepdxy', 'LepdxySig', 'Lepdz', 'LepdzSig', 'Njet', 'Nbjet', 'MupT', 'Mudxy', 'MudxySig', 'Mudz', 'MudzSig', 'epT', 'edxy', 'edxySig', 'edz', 'edzSig', 'AllLeppT', 'AllLepdxy', 'AllLepdxySig', 'AllLepdz', 'Nlep', '2ndLeppT', '2ndLepeta', '2ndLepdxy', '2ndLepdz', 'METSig', 'NPV', 'NGdPV', 'PVscore', 'PVchi'] #same list as in StackHistMaker_LL.py

ROOT.gROOT.SetBatch(True)        
if doplots :
    for v in vList:
        StackHistsExt(files, samplelists, v, plotDir, 'Displaced/Dxy3/Dz2')
