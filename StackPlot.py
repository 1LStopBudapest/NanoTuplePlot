import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *

samplelists = ['WJetsToLNu', 'TTSingleLep_pow', 'MET_Data']
files = []
for sl in samplelists:
    files.append(ROOT.TFile.Open('StackHist_'+sl+'.root'))


StackHists(files, samplelists, 'MET', plotDir, 'cut')

