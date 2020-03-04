import os, sys
import ROOT

from HistInfo import HistInfo
from SampleChain import SampleChain
from FillHistos import FillHistos
from PlotHelper import *

plot_variable = ["MET_pt"]

histos = {}

sample  = 'Stop_500_480_fast'


histos['MET'] = HistInfo(hname = 'MET', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()


ch = SampleChain(sample, 0, 1).getchain()
print ch.GetEntries()

FillHistos(histos, ch).fill()

outputDir = os.getcwd()
Plot1D(histos['MET'], outputDir, islogy=True)
