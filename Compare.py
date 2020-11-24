import os, sys
import ROOT

sys.path.append('../')
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *

f20 = ROOT.TFile(plotDir+"1DFiles/1DHist_TTSingleLep_pow_cleaned20.root")
f30 = ROOT.TFile(plotDir+"1DFiles/1DHist_TTSingleLep_pow_cleaned30.root")

keys20 = [key.GetName() for key in f20.GetListOfKeys()]
keys30 = [key.GetName() for key in f30.GetListOfKeys()]

outputDir = plotDir
if keys20 != keys30:
    raise ValueError("Histograms don't match!")
else:
    for i in range(len(keys20)):
        h20 = f20.Get(keys20[i])
        h30 = f30.Get(keys30[i])
        CompareHist(h20, h30, 'fastfull', outputDir, islogy=True, scaleOption='Lumiscaling')
