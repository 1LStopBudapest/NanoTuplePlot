import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning import *
from Helper.GenFilterEff import GenFilterEff
from Sample.SampleChain import SampleChain
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post

from Helper.VarCalc import *
from Helper.PlotHelper import *
from Sample.Dir import plotDir


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                    help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--region',            action='store',                    type=str,            default='SR',                                             help="Which region?" )

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year
region = options.region
nEvents = options.nevents

isData = True if ('Run' in samples or 'Data' in samples) else False
DataLumi=1.0

if year=='2016PreVFP':
    samplelist = samples_2016Pre
    DataLumi = SampleChain.luminosity_2016PreVFP
elif year=='2016PostVFP':
    samplelist = samples_2016Post
    DataLumi = SampleChain.luminosity_2016PostVFP
elif year=='2017':
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018

if region == 'SR':
    bins = 50 #value of pT
    binLabel = SRpTList
else:
    bins = 1
    binLabel = ['REG']
histext = ''


if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile('RegionPT_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        for sr in SRpTList:
            histos[sr] = HistInfo(hname = sr, sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()

    ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        if isData:
            lumiscale = 1.0
            MCcorr = 1.0
        else:
            lumiscale = (DataLumi/1000.0) * ch.weight
            MCcorr = MCWeight(ch, year, sample).getTotalWeight()
        getsel = TreeVarSel(ch, isData, year)
        if not getsel.PreSelection(): continue
        if region == 'SR':
            if not getsel.SearchRegion(): continue
            if getsel.SR1():
                idx = findSR1BinIndexPT(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                if not idx == -1:
                    pT = getsel.getSortedLepVar()[0]['pt']
                    Fill1D(histos[SRpTList[idx]], pT, lumiscale * MCcorr)
            if getsel.SR2():
                idx = findSR2BinIndexPT(getsel.calCT(2), getsel.getLepMT()) + 8
                if not idx == -1:
                    pT = getsel.getSortedLepVar()[0]['pt']
                    Fill1D(histos[SRpTList[idx]], pT, lumiscale * MCcorr)
    hfile.Write()

else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile('RegionPT_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    for sr in SRpTList:
        histos[sr] = HistInfo(hname = sr, sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()

    ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        if isData:
            lumiscale = 1.0
            MCcorr = 1.0
        else:
            lumiscale = (DataLumi/1000.0) * ch.weight
            MCcorr = MCWeight(ch, year, sample).getTotalWeight()
        getsel = TreeVarSel(ch, isData, year)
        if not getsel.PreSelection(): continue
        if region == 'SR':
            if not getsel.SearchRegion(): continue
            if getsel.SR1():
                idx = findSR1BinIndexPT(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                if not idx == -1:
                    pT = getsel.getSortedLepVar()
                    for x in pT: Fill1D(histos[SRpTList[idx]], x['pt'], lumiscale * MCcorr) #Fill1D(histos[SRpTList[idx]], pT, lumiscale * MCcorr)
            if getsel.SR2():
                idx = findSR2BinIndexPT(getsel.calCT(2), getsel.getLepMT()) + 8
                if not idx == -1:
                    pT = getsel.getSortedLepVar()
                    for x in pT: Fill1D(histos[SRpTList[idx]], x['pt'], lumiscale * MCcorr) #Fill1D(histos[SRpTList[idx]], pT, lumiscale * MCcorr)
    hfile.Write()

outputDir = plotDir
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
