import os, sys
import types
import ROOT


from VarHandler import VarHandler

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Helper.HistInfo import HistInfo
from Helper.VarCalc import *
from Helper.PlotHelper import *


sample1 = 'Stop_500_480_fast'
startfile1 = 0
nfiles1 = 1
nEvents1 = -1

tr1 = SampleChain(sample1, startfile1, nfiles1).getchain()
histos1 = {}
histos1['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos1['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample1, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()

keylist1 = ['Muondxy','Eledxy']
var1 = {key: None for key in keylist1}

n_entries1 = tr1.GetEntries()
print 'fastsim tree entries: ', n_entries1
for ientry in range(n_entries1):
    if not nEvents1 == -1 and ientry > nEvents1 - 1: break
    tr1.GetEntry(ientry)
    getvar = VarHandler(tr1, 2016)
    var1['Muondxy'] = [x for x in getvar.getMuonvar()['dxy']]
    var1['Eledxy'] = [x for x in getvar.getElevar()['dxy']]

    for key in histos1:
        if key in var1.keys():
            if var1[key] is not None:
                if isinstance(var1[key], types.ListType):
                    for x in var1[key]: Fill1D(histos1[key], x)
                else:
                    Fill1D(histos1[key], var[key])
        else:
            print "You are trying to fill the histos for the keys", key, " which are missing in var dictionary"




sample2 = 'Stop_500_480_full'
startfile2 = 0
nfiles2 = 1
nEvents2 = -1

tr2 = SampleChain(sample2, startfile2, nfiles2).getchain()
histos2 = {}
histos2['Eledxy'] = HistInfo(hname = 'Eledxy', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()
histos2['Muondxy'] = HistInfo(hname = 'Muondxy', sample = sample2, binning=[20,0,5], histclass = ROOT.TH1F).make_hist()

keylist2 = ['Muondxy','Eledxy']
var2 = {key: None for key in keylist2}

n_entries2 = tr2.GetEntries()
print 'fullsim tree entries: ', n_entries2
for ientry in range(n_entries2):
    if not nEvents2 == -1 and ientry > nEvents2 - 1: break
    tr2.GetEntry(ientry)
    getvar = VarHandler(tr2, 2016)
    var2['Muondxy'] = [x for x in getvar.getMuonvar()['dxy']]
    var2['Eledxy'] = [x for x in getvar.getElevar()['dxy']]

    for key in histos2:
        if key in var2.keys():
            if var2[key] is not None:
                if isinstance(var2[key], types.ListType):
                    for x in var2[key]: Fill1D(histos2[key], x)
                else:
                    Fill1D(histos2[key], var[key])
        else:
            print "You are trying to fill the histos for the keys", key, " which are missing in var dictionary"

#outputDir = os.getcwd()
#if not len(histos1)==len(histos2):
#    raise ValueError("Two hist container have differnt number of histograms")
#else:
#    for key in histos1:
#        CompareHist(histos1[key], histos2[key], 'fastfull', outputDir, islogy=True)

print 'fast: total: ', histos1['Eledxy'].Integral()
print 'full: total: ', histos2['Eledxy'].Integral()

if histos1['Eledxy'].Integral(): histos1['Eledxy'].Scale(1/histos1['Eledxy'].Integral())
if histos2['Eledxy'].Integral(): histos2['Eledxy'].Scale(1/histos2['Eledxy'].Integral())

#hRatio = histos1['Eledxy'].Clone("Ratio")
#hRatio.Divide(histos2['Eledxy'])

hRatio = getHistratio(histos1['Eledxy'], histos2['Eledxy'], 'fastfull', histos1['Eledxy'].GetTitle())

import math
def calcEr(x,y,dx,dy):
    return (x/y) * math.sqrt((dx/x)**2 + (dy/y)**2)

print 'fast:  bin ', 1, 'bincontent: ', histos1['Eledxy'].GetBinContent(1), 'bin error: ', histos1['Eledxy'].GetBinError(1)
print 'full:  bin ', 1, 'bincontent: ', histos2['Eledxy'].GetBinContent(1), 'bin error: ', histos2['Eledxy'].GetBinError(1)
print 'fast/full: bin ', 1, 'bincontent: ', hRatio.GetBinContent(1), 'bin error: ', hRatio.GetBinError(1)
print 'errorCalc: ', calcEr(histos1['Eledxy'].GetBinContent(1), histos2['Eledxy'].GetBinContent(1), histos1['Eledxy'].GetBinError(1), histos2['Eledxy'].GetBinError(1))

print 'fastsim Eledxy total: ', histos1['Eledxy'].Integral(), '  after 3 cm: ', histos1['Eledxy'].Integral(17, 20)
print 'fastsim Muondxy total: ', histos1['Muondxy'].Integral(), '  after 3 cm: ', histos1['Muondxy'].Integral(17, 20)
print 'fullsim total: ', histos2['Eledxy'].Integral(), '  after 3 cm: ', histos2['Eledxy'].Integral(17, 20)
print 'fullsim Muondxy total: ', histos2['Muondxy'].Integral(), '  after 3 cm: ', histos2['Muondxy'].Integral(17, 20)

