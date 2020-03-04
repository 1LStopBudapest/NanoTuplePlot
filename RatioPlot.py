import os, sys
import ROOT

from HistInfo import HistInfo
from SampleChain import SampleChain
from FillHistos import FillHistos
from PlotHelper import *

plot_variable = ["MET_pt"]

histos1 = {}
sample1  = 'Stop_500_480_fast'
histos1['MET'] = HistInfo(hname = 'MET', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['HT'] = HistInfo(hname = 'HT', sample = sample1, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos1['Njet20'] = HistInfo(hname = 'Njet20', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Njet30'] = HistInfo(hname = 'Njet30', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Nbjet30'] = HistInfo(hname = 'Nbjet30', sample = sample1, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos1['Muonpt'] = HistInfo(hname = 'Muonpt', sample = sample1, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos1['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample1, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos1['Muondz'] = HistInfo(hname = 'Muondz', sample = sample1, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos1['Elept'] = HistInfo(hname = 'Elept', sample = sample1, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos1['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample1, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos1['Eledz'] = HistInfo(hname = 'Eledz', sample = sample1, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()



histos2 = {}
sample2  = 'Stop_500_480_full'
histos2['MET'] = HistInfo(hname = 'MET', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['HT'] = HistInfo(hname = 'HT', sample = sample2, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos2['Njet20'] = HistInfo(hname = 'Njet20', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Njet30'] = HistInfo(hname = 'Njet30', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Nbjet30'] = HistInfo(hname = 'Nbjet30', sample = sample2, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos2['Muonpt'] = HistInfo(hname = 'Muonpt', sample = sample2, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos2['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample2, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos2['Muondz'] = HistInfo(hname = 'Muondz', sample = sample2, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos2['Elept'] = HistInfo(hname = 'Elept', sample = sample2, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos2['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample2, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()
histos2['Eledz'] = HistInfo(hname = 'Eledz', sample = sample2, binning=[20,0,2], histclass = ROOT.TH1F).make_hist()

ch1 = SampleChain(sample1, 0, -1).getchain()
print ch1.GetEntries()
ch2 = SampleChain(sample2, 0, -1).getchain()
print ch2.GetEntries()

FillHistos(histos1, ch1).fill()
FillHistos(histos2, ch2).fill()



outputDir = os.getcwd()
if not len(histos1)==len(histos2):
    raise ValueError("Two hist container have differnt number of histograms")
else:
    for key in histos1:
        CompareHist(histos1[key], histos2[key], 'fastfull', outputDir, islogy=True)
