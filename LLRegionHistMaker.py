import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel_LL import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning_LL import *
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
    argParser.add_argument('--region',            action='store',                    type=str,            default='DxyDz',                                             help="Which region?" )

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

if region == 'DxyDz':
    bins = 9
    binLabel = DxyDzBinLabelList
elif region == 'SR+CR':
    bins = 56 + 16
    binLabel = SRBinLabelList+CRBinLabelList
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
    hfile = ROOT.TFile( 'LLRegionHistMaker_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_prompt'] = HistInfo(hname = 'h_reg_prompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_nonprompt'] = HistInfo(hname = 'h_reg_nonprompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_nonprompt_fromb'] = HistInfo(hname = 'h_reg_nonprompt_fromb', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_nonprompt_fromc'] = HistInfo(hname = 'h_reg_nonprompt_fromc', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_nonprompt_froml_or_ukn'] = HistInfo(hname = 'h_reg_nonprompt_froml_or_ukn', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_reg_nonprompt_unmatched'] = HistInfo(hname = 'h_reg_nonprompt_unmatched', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    for b in range(bins):
        histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_prompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_nonprompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_nonprompt_fromb'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_nonprompt_fromc'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_nonprompt_froml_or_ukn'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_reg_nonprompt_unmatched'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
        ltp = getsel.getSortedLepVar()[0]['type']
        lidx = getsel.getSortedLepVar()[0]['idx']
        if ltp == 'mu':
            flag=ord(ch.Muon_genPartFlav[lidx])
        elif ltp == 'Electron':
            flag=ord(ch.Electron_genPartFlav[lidx])
        else:
            flag=ord(ch.LowPtElectron_genPartFlav[lidx])
        promptFlag = flag in [ 1 , 15 ]
        NonpromptbFlag = flag==5
        NonpromptcFlag = flag==4
        NonpromptlFlag = flag==3
        NonpromptnmFlag = flag==0
        if region == 'DxyDz':
            idx = findDxyDzBinIndex(getsel.getSortedLepVar()[0]['dxy'], getsel.getSortedLepVar()[0]['dz'])
            if not idx == -1:
                histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                else:
                    histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                    if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                    if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                    if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                    if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
        if region == 'SR+CR':
            if getsel.SearchRegion():
                if getsel.SR1():
                    idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1:
                        histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                        else:
                            histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                if getsel.SR2():
                    idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                    if not idx <= 27:
                        histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                        else:
                            histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
            if getsel.ControlRegion():
                if getsel.CR1():
                    idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 # after 56 SR bins or after bin index 55
                    if not idx <= 55:
                        histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                        else:
                            histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                if getsel.CR2():
                    idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                    if not idx <= 63:
                        histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                        else:
                            histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
    histos['h_reg'].Scale(1/gfltreff)
    histos['h_reg_prompt'].Scale(1/gfltreff)
    histos['h_reg_nonprompt'].Scale(1/gfltreff)
    histos['h_reg_nonprompt_fromb'].Scale(1/gfltreff)
    histos['h_reg_nonprompt_fromc'].Scale(1/gfltreff)
    histos['h_reg_nonprompt_froml_or_ukn'].Scale(1/gfltreff)
    histos['h_reg_nonprompt_unmatched'].Scale(1/gfltreff)
    hfile.Write()
else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'LLRegionHistMaker_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
	    histos = {}
            histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_prompt'] = HistInfo(hname = 'h_reg_prompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_nonprompt'] = HistInfo(hname = 'h_reg_nonprompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_nonprompt_fromb'] = HistInfo(hname = 'h_reg_nonprompt_fromb', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_nonprompt_fromc'] = HistInfo(hname = 'h_reg_nonprompt_fromc', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_nonprompt_froml_or_ukn'] = HistInfo(hname = 'h_reg_nonprompt_froml_or_ukn', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_reg_nonprompt_unmatched'] = HistInfo(hname = 'h_reg_nonprompt_unmatched', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            for b in range(bins):
                histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_prompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_nonprompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_nonprompt_fromb'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_nonprompt_fromc'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_nonprompt_froml_or_ukn'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_reg_nonprompt_unmatched'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
                promptFlag = True if isData else False
                NonpromptbFlag = True if isData else False
                NonpromptcFlag = True if isData else False
                NonpromptlFlag = True if isData else False
                NonpromptnmFlag = True if isData else False
                if not isData:
                    ltp = getsel.getSortedLepVar()[0]['type']
                    lidx = getsel.getSortedLepVar()[0]['idx']
                    if ltp == 'mu':
                        flag=ord(ch.Muon_genPartFlav[lidx])
                    elif ltp == 'Electron':
                        flag=ord(ch.Electron_genPartFlav[lidx])
                    else:
                        flag=ord(ch.LowPtElectron_genPartFlav[lidx])
                    promptFlag = flag in [ 1 , 15 ]
                    NonpromptbFlag = flag==5
                    NonpromptcFlag = flag==4
                    NonpromptlFlag = flag==3
                    NonpromptnmFlag = flag==0
                if region == 'DxyDz':
                    idx = findDxyDzBinIndex(getsel.getSortedLepVar()[0]['dxy'], getsel.getSortedLepVar()[0]['dz'])
                    if not idx == -1:
                        histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                        if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                        else:
                            histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                            if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                if region == 'SR+CR':
                    if getsel.SearchRegion():
                        if getsel.SR1():
                            idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                                else:
                                    histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                        if getsel.SR2():
                            idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                            if not idx <= 27:
                                histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                                else:
                                    histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                    if getsel.ControlRegion():
                        if getsel.CR1():
                            idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 #after 56 SR bins or after bin index 55
                            if not idx <= 55:
                                histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                                else:
                                    histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                        if getsel.CR2():
                            idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                            if not idx <= 63:
                                histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                                else:
                                    histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                    if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
            hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'LLRegionHistMaker_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['h_reg'] = HistInfo(hname = 'h_reg', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_prompt'] = HistInfo(hname = 'h_reg_prompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_nonprompt'] = HistInfo(hname = 'h_reg_nonprompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_nonprompt_fromb'] = HistInfo(hname = 'h_reg_nonprompt_fromb', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_nonprompt_fromc'] = HistInfo(hname = 'h_reg_nonprompt_fromc', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_nonprompt_froml_or_ukn'] = HistInfo(hname = 'h_reg_nonprompt_froml_or_ukn', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_reg_nonprompt_unmatched'] = HistInfo(hname = 'h_reg_nonprompt_unmatched', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        for b in range(bins):
            histos['h_reg'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_prompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_nonprompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_nonprompt_fromb'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_nonprompt_fromc'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_nonprompt_froml_or_ukn'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_reg_nonprompt_unmatched'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
            promptFlag = True if isData else False
            NonpromptbFlag = True if isData else False
            NonpromptcFlag = True if isData else False
            NonpromptlFlag = True if isData else False
            NonpromptnmFlag = True if isData else False
            if not isData:
                ltp = getsel.getSortedLepVar()[0]['type']
                lidx = getsel.getSortedLepVar()[0]['idx']
                if ltp == 'mu':
                    flag=ord(ch.Muon_genPartFlav[lidx])
                elif ltp == 'Electron':
                    flag=ord(ch.Electron_genPartFlav[lidx])
                else:
                    flag=ord(ch.LowPtElectron_genPartFlav[lidx])
                promptFlag = flag in [ 1 , 15 ]
                NonpromptbFlag = flag==5
                NonpromptcFlag = flag==4
                NonpromptlFlag = flag==3
                NonpromptnmFlag = flag==0
            if region == 'DxyDz':
                idx = findDxyDzBinIndex(getsel.getSortedLepVar()[0]['dxy'], getsel.getSortedLepVar()[0]['dz'])
                if not idx == -1:
                    histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                    if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                    else:
                        histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                        if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                        if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                        if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                        if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
            if region == 'SR+CR':
                if getsel.SearchRegion():
                    if getsel.SR1():
                        idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1:
                            histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                    if getsel.SR2():
                        idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                        if not idx <= 27:
                            histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                if getsel.ControlRegion():
                    if getsel.CR1():
                        idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 #after 56 SR bins or after bin index 55
                        if not idx <= 55:
                            histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
                    if getsel.CR2():
                        idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                        if not idx <= 63:
                            histos['h_reg'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_reg_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                histos['h_reg_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptbFlag: histos['h_reg_nonprompt_fromb'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptcFlag: histos['h_reg_nonprompt_fromc'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptlFlag: histos['h_reg_nonprompt_froml_or_ukn'].Fill(idx, lumiscale * MCcorr)
                                if NonpromptnmFlag: histos['h_reg_nonprompt_unmatched'].Fill(idx, lumiscale * MCcorr)
        hfile.Write()
