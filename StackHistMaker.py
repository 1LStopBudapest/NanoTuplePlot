import os, sys
import ROOT


from FillHistos import FillHistos

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()



sample  = options.sample

hfile = ROOT.TFile( 'StackHist_'+sample+'.root', 'RECREATE')
histos = {}
histos['MET'] = HistInfo(hname = 'MET', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()

ch = SampleChain(sample, options.startfile, options.nfiles).getchain()
print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()


FillHistos(histos, ch, options.year, options.nevents, sample, SampleChain.luminosity_2016).fill()


hfile.Write()

