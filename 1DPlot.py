import os, sys
import ROOT

from HistInfo import HistInfo
from SampleChain import SampleChain
from FillHistos import FillHistos
from PlotHelper import *
from Dir import plotDir

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    

    return argParser

options = get_parser().parse_args()

histos = {}

sample  = options.sample


histos['MET'] = HistInfo(hname = 'MET', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()


ch = SampleChain(sample, options.startfile, options.nfiles).getchain()
print ch.GetEntries()

FillHistos(histos, ch, options.year).fill()

#outputDir = os.getcwd()
outputDir = plotDir
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
