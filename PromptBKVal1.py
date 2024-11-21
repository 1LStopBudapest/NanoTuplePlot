import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel_BKVal import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning_BKVal import *
from Helper.GenFilterEff import GenFilterEff
from Sample.SampleChain import SampleChain
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

def get_parser():
    ''' Argument parser.                                                                                                                                                                                                                     
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2018',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--region',            action='store',                    type=str,            default='SR+CR',                                             help="Which region?" )

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

if region == 'SR+CR':
    bins = 54 + 12
    binLabel = SRBinLabelListVal1+CRBinLabelListVal1
else:
    bins = 1
    binLabel = ['REG']
histext = ''

if 'T2tt' in samples:
    histext = samples
    sample = samples
    print 'running over: ', sample
    ms = int(sample.split('_')[1])
    ml = int(sample.split('_')[2])
    gfiltr = GenFilterEff(year)
    gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    print 'Gen filter eff: ',gfltreff
    hfile = ROOT.TFile( 'PromptBKVal1_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    for b in range(bins): histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])
    
    ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        lumiscale = (DataLumi/1000.0) * ch.weight
        MCcorr = MCWeight(ch, year, sample).getTotalWeight()
        getsel = TreeVarSel(ch, isData, year)
        if not getsel.PreSelection(): continue
        if region == 'SR+CR':
            if getsel.Val1SearchRegion():
                if getsel.Val1SR1():
                    idx = findSR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if getsel.Val1SR2():
                    idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 18
                    if not idx <= 17: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if getsel.Val1SR3():
                    idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                    if not idx <= 35: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
            if getsel.Val1ControlRegion():
                if getsel.Val1CR1():
                    idx = findCR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 54 # after 54 SR bins or after bin index 53 
                    if not idx <= 53: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if getsel.Val1CR2():
                    idx = findCR2BinIndexVal1(getsel.getLepMT()) +  54 + 4
                    if not idx <= 57: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if getsel.Val1CR3():
                    idx = findCR2BinIndexVal1(getsel.getLepMT()) + 58 + 4
                    if not idx <= 61: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
    histos['h_reg'].Scale(gfltreff)
    hfile.Write()
else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'PromptBKVal1_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
	    histos = {}
            histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
	    for b in range(bins): histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])

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
                if region == 'SR+CR':
                    if getsel.Val1SearchRegion():
                        if getsel.Val1SR1():
                            idx = findSR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if getsel.Val1SR2():
                            idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 18
                            if not idx <= 17: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if getsel.Val1SR3():
                            idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                            if not idx <= 35: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if getsel.Val1ControlRegion():
                        if getsel.Val1CR1():
                            idx = findCR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 54 # after 54 SR bins or after bin index 53 
                            if not idx <= 53: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if getsel.Val1CR2():
                            idx = findCR2BinIndexVal1(getsel.getLepMT()) +  54 + 4
                            if not idx <= 57: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if getsel.Val1CR3():
                            idx = findCR2BinIndexVal1(getsel.getLepMT()) + 58 + 4
                            if not idx <= 61: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
            hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'PromptBKVal1_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        for b in range(bins): histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])
    
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
            if region == 'SR+CR':
                if getsel.Val1SearchRegion():
                    if getsel.Val1SR1():
                        idx = findSR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if getsel.Val1SR2():
                        idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 18
                        if not idx <= 17: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if getsel.Val1SR3():
                        idx = findSR2BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                        if not idx <= 35: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if getsel.Val1ControlRegion():
                    if getsel.Val1CR1():
                        idx = findCR1BinIndexVal1(getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 54 # after 54 SR bins or after bin index 53
                        if not idx <= 53: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if getsel.Val1CR2():
                        idx = findCR2BinIndexVal1(getsel.getLepMT()) +  54 + 4
                        if not idx <= 57: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if getsel.Val1CR3():
                        idx = findCR2BinIndexVal1(getsel.getLepMT()) + 58 + 4
                        if not idx <= 61: histos['h_reg'].Fill(idx, lumiscale * MCcorr)
 
        hfile.Write()