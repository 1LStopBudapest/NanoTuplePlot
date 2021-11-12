import os, sys
import ROOT

sys.path.append('../')
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *

before = ROOT.TFile(plotDir+"1DFiles/IVF/1DHist_UL17V9_before_1108.root")
after = ROOT.TFile(plotDir+"1DFiles/IVF/1DHist_UL17V9_after_1108.root")

keys_b = [key.GetName() for key in before.GetListOfKeys()]
keys_a = [key.GetName() for key in after.GetListOfKeys()]

outputDir = plotDir
if keys_b != keys_a:
    raise ValueError("Histograms don't match!")
else:
    for i in range(len(keys_b)):
        hb = before.Get(keys_b[i])
        ha = after.Get(keys_a[i])
        CompareHist(hb, ha, 'IVF', outputDir, islogy=True, scaleOption='Lumiscaling')
