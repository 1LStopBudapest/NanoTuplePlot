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
    argParser.add_argument('--sample1',           action='store',                     type=str,            default='Stop_500_480_fast',                             help="Which sample?" )
    argParser.add_argument('--sample2',           action='store',                     type=str,            default='Stop_500_480_full',                             help="Which sample?" )
    argParser.add_argument('--year',              action='store',                     type=int,            default=2016,                                            help="Which year?" )
    argParser.add_argument('--startfile',         action='store',                     type=int,            default=0,                                               help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',            action='store',                     type=int,            default=-1,                                              help="No of files to run. -1 means all files" )


    return argParser

options = get_parser().parse_args()




histos1 = {}
sample1  = options.sample1
histos1['MET'] = HistInfo(hname = 'MET', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['HT'] = HistInfo(hname = 'HT', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['Njet20'] = HistInfo(hname = 'Njet20', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Njet30'] = HistInfo(hname = 'Njet30', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Nbjet30'] = HistInfo(hname = 'Nbjet30', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Muonpt'] = HistInfo(hname = 'Muonpt', sample = sample1, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos1['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos1['Muondz'] = HistInfo(hname = 'Muondz', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos1['Elept'] = HistInfo(hname = 'Elept', sample = sample1, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos1['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos1['Eledz'] = HistInfo(hname = 'Eledz', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()



histos2 = {}
sample2  = options.sample2
histos2['MET'] = HistInfo(hname = 'MET', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['HT'] = HistInfo(hname = 'HT', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['Njet20'] = HistInfo(hname = 'Njet20', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Njet30'] = HistInfo(hname = 'Njet30', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Nbjet30'] = HistInfo(hname = 'Nbjet30', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Muonpt'] = HistInfo(hname = 'Muonpt', sample = sample2, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos2['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos2['Muondz'] = HistInfo(hname = 'Muondz', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos2['Elept'] = HistInfo(hname = 'Elept', sample = sample2, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos2['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos2['Eledz'] = HistInfo(hname = 'Eledz', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()

ch1 = SampleChain(sample1, options.startfile, options.nfiles).getchain()
print ch1.GetEntries()
ch2 = SampleChain(sample2, options.startfile, options.nfiles).getchain()
print ch2.GetEntries()

FillHistos(histos1, ch1, options.year).fill()
FillHistos(histos2, ch2, options.year).fill()



#outputDir = os.getcwd()
outputDir = plotDir
if not len(histos1)==len(histos2):
    raise ValueError("Two hist container have differnt number of histograms")
else:
    for key in histos1:
        CompareHist(histos1[key], histos2[key], 'fastfull', outputDir, islogy=True)
