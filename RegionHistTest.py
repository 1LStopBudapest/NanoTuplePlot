import os, sys
import ROOT
import types
from collections import OrderedDict

sys.path.append('../')
from Helper.TreeVarSel import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning import *
from Helper.GenFilterEff import GenFilterEff
from Helper.XsecUnc import *
from Helper.TrigEff import *
from Helper.FullFastSF import FullFastSF
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
    argParser.add_argument('--sample',           action='store',                     type=str,            default='QCD_HT1000to1500',                                help="Which sample?" )
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

trigger = 'HLT_PFMET120_PFMHT120_IDTight' #for inclusive MET triggers (logical OR), use 'HLT_MET_Inclusive'

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
    bins = 108 #prev. ver had 72
    binLabel = SRBinLabelList
elif region == 'CR':
    bins = 24 #prev. ver had 16
    binLabel = CRBinLabelList
elif region == 'SR+CR':
    bins = 108 + 24
    binLabel = SRBinLabelList+CRBinLabelList
else:
    bins = 1
    binLabel = ['REG']
histext = ''

cutflow = ['nocut', 'METcut', 'lepcut', 'muchannel', 'elchannel', 'HTcut', 'ISRcut', 'dphicut', 'XtralepVeto', 'XtraJetVeto', 'tauVeto', 'HardBtagjetVeto', 'presel', 'filtr', 'trgr', 'NonPrompt', 'SRCR', 'SR', 'SR1', 'SR2', 'SR3', 'CR', 'CR1', 'CR2', 'CR3']
ncuts = len(cutflow)

if 'T2tt' in samples:
    histext = samples
    sample = samples
    print 'running over: ', sample
    ms = int(sample.split('_')[1])
    ml = int(sample.split('_')[2])
    gfiltr = GenFilterEff(year)
    gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    #print 'Gen filter eff: ',gfltreff
    trigeff = getTrigEff(year)
    ffsf = FullFastSF(year)
    softbSF = ffsf.getsoftbSF()
    hfile = ROOT.TFile( 'RegionHistTest_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
    histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
    for b in range(bins):
        histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
        MCcorr = MCWeight(ch, year, sample).getTotalWeight() * trigeff
        getsel = TreeVarSel(ch, isData, year)

        #cutflowhist
        conjcuts = OrderedDict()
        conjcuts['nocut'] = True
        conjcuts['presel'] = conjcuts['nocut'] * getsel.PreSelection()
        muflag = False
        NonPromptflag = False
        if getsel.PreSelection():
            idx = getsel.getSortedLepVar()[0]['idx']
            tp = getsel.getSortedLepVar()[0]['type']
            if tp == 'mu':
                muflag = True
                flag=ord(ch.Muon_genPartFlav[idx])
            elif tp == 'Electron':
                flag=ord(ch.Electron_genPartFlav[idx])
            else:
                flag=ord(ch.LowPtElectron_genPartFlav[idx])
            NonPromptflag = not flag in [ 1 , 15 ]
                
        conjcuts['muchannel'] = conjcuts['nocut'] * getsel.PreSelection() * muflag
        conjcuts['NonPrompt'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag
        conjcuts['SRCR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion())
        conjcuts['SR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.SearchRegion()
        conjcuts['CR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.ControlRegion()
        conjcuts['SR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR1()
        conjcuts['SR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR2()
        conjcuts['SR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR3()
        conjcuts['CR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR1()
        conjcuts['CR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR2()
        conjcuts['CR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR3()
        for k in conjcuts:
            histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
            histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * fMCcorr)
        #........................................................#   
        if not getsel.PreSelection(): continue
        lep1 = getsel.getSortedLepVar()[0]
        lepSF = ffsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])
        fMCcorr = MCcorr * softbSF * lepSF
        if region == 'SR+CR':
            if getsel.SearchRegion():
                if getsel.SR1():
                    idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                if getsel.SR2():
                    idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                    if not idx <= 35:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                if getsel.SR3():
                    idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                    if not idx <= 71:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                
            if getsel.ControlRegion():
                if getsel.CR1():
                    idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 # after 108 SR bins or after bin index 107 
                    if not idx <= 107:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                
                if getsel.CR2():
                    idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  108 + 8
                    if not idx <= 115:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                
                if getsel.CR3():
                    idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) + 116 + 8
                    if not idx <= 123:
                        histos['h_rate'].Fill(idx, lumiscale * fMCcorr)
                
    histos['h_rate'].Scale(gfltreff)
    hfile.Write()
else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'RegionHistTest_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
	    histos = {}
            histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_rate_prompt'] = HistInfo(hname = 'h_rate_prompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_rate_nonprompt'] = HistInfo(hname = 'h_rate_nonprompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
            histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
            for b in range(bins):
                histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_rate_prompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_rate_nonprompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                                                
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
                #..........cutflowhist.............
                conjcuts = OrderedDict()
                conjcuts['nocut'] = True
                conjcuts['presel'] = conjcuts['nocut'] * getsel.PreSelection()
                muflag = False
                NonPromptflag = False
                if getsel.PreSelection():
                    idx = getsel.getSortedLepVar()[0]['idx']
                    tp = getsel.getSortedLepVar()[0]['type']
                    if tp == 'mu':
                        muflag = True
                        flag=ord(ch.Muon_genPartFlav[idx])
                    elif tp == 'Electron':
                        flag=ord(ch.Electron_genPartFlav[idx])
                    else:
                        flag=ord(ch.LowPtElectron_genPartFlav[idx])
                    NonPromptflag = not flag in [ 1 , 15 ]
                    
                conjcuts['muchannel'] = conjcuts['nocut'] * getsel.PreSelection() * muflag
                conjcuts['NonPrompt'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag
                conjcuts['SRCR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion())
                conjcuts['SR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.SearchRegion()
                conjcuts['CR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.ControlRegion()
                conjcuts['SR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR1()
                conjcuts['SR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR2()
                conjcuts['SR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR3()
                conjcuts['CR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR1()
                conjcuts['CR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR2()
                conjcuts['CR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR3()
                for k in conjcuts:
                    histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
                    histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * MCcorr)
                #........................................................#   
                if not getsel.PreSelection(): continue
                if not getsel.passFilters(): continue
                if not getsel.passMETTrig(trigger): continue
                idx = getsel.getSortedLepVar()[0]['idx']
                tp = getsel.getSortedLepVar()[0]['type']
                promptFlag = True if isData else False
                if not isData:
                    if tp == 'mu':
                        flag=ord(ch.Muon_genPartFlav[idx])
                    elif tp == 'Electron':
                        flag=ord(ch.Electron_genPartFlav[idx])
                    else:
                        flag=ord(ch.LowPtElectron_genPartFlav[idx])
                    promptFlag = flag in [ 1 , 15 ]
                
                if region == 'SR+CR':
                    if getsel.SearchRegion():
                        if getsel.SR1():
                            idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
                        if getsel.SR2():
                            idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                            if not idx <= 35:
                                histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
                        if getsel.SR3():
                            idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                            if not idx <= 71:
                                histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
                    if getsel.ControlRegion():
                        if getsel.CR1():
                            idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 # after 108 SR bins or after bin index 107 
                            if not idx <= 107:
                                #histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                histos['h_rate'].Fill(idx, 1.0)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
                        if getsel.CR2():
                            idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  108 + 8
                            if not idx <= 115:
                                histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
                        if getsel.CR3():
                            idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) + 116 + 8
                            if not idx <= 123:
                                histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                                if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                                else: histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                                
            hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        cntdic = OrderedDict()
        cntdicWgt = OrderedDict()
        cntdic['nocut'] = 0
        cntdic['presel'] = 0
        cntdic['filtr'] = 0
        cntdic['trigr'] = 0
        cntdic['SR'] = 0
        cntdic['SR1'] = 0
        cntdic['SR2'] = 0
        cntdic['SR3'] = 0
        cntdic['SR1NonPrmp'] = 0
        cntdic['SR2NonPrmp'] = 0
        cntdic['SR3NonPrmp'] = 0
        cntdic['SR1NonPrmpMu'] = 0
        cntdic['SR2NonPrmpMu'] = 0
        cntdic['SR3NonPrmpMu'] = 0
        cntdic['CR'] = 0
        cntdic['CR1'] = 0
        cntdic['CR2'] = 0
        cntdic['CR3'] = 0
        cntdic['CR1NonPrmp'] = 0
        cntdic['CR2NonPrmp'] = 0
        cntdic['CR3NonPrmp'] = 0
        cntdic['CR1NonPrmpMu'] = 0
        cntdic['CR2NonPrmpMu'] = 0
        cntdic['CR3NonPrmpMu'] = 0
        cntdicWgt['nocut'] = 0
        cntdicWgt['presel'] = 0
        cntdicWgt['filtr'] = 0
        cntdicWgt['trigr'] = 0
        cntdicWgt['SR'] = 0
        cntdicWgt['SR1'] = 0
        cntdicWgt['SR2'] = 0
        cntdicWgt['SR3'] = 0
        cntdicWgt['SR1NonPrmp'] = 0
        cntdicWgt['SR2NonPrmp'] = 0
        cntdicWgt['SR3NonPrmp'] = 0
        cntdicWgt['SR1NonPrmpMu'] = 0
        cntdicWgt['SR2NonPrmpMu'] = 0
        cntdicWgt['SR3NonPrmpMu'] = 0
        cntdicWgt['CR'] = 0
        cntdicWgt['CR1'] = 0
        cntdicWgt['CR2'] = 0
        cntdicWgt['CR3'] = 0
        cntdicWgt['CR1NonPrmp'] = 0
        cntdicWgt['CR2NonPrmp'] = 0
        cntdicWgt['CR3NonPrmp'] = 0
        cntdicWgt['CR1NonPrmpMu'] = 0
        cntdicWgt['CR2NonPrmpMu'] = 0
        cntdicWgt['CR3NonPrmpMu'] = 0
        
        hfile = ROOT.TFile( 'RegionHistTest_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_rate_prompt'] = HistInfo(hname = 'h_rate_prompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_rate_nonprompt'] = HistInfo(hname = 'h_rate_nonprompt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
        histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
        histos['hcnt'] = HistInfo(hname = 'hcnt', sample = histext, binning=[len(cntdic),0,len(cntdic)], histclass = ROOT.TH1F).make_hist()
        histos['hcntWgt'] = HistInfo(hname = 'hcntWgt', sample = histext, binning=[len(cntdicWgt),0,len(cntdicWgt)], histclass = ROOT.TH1F).make_hist()
        for b in range(bins):
            histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_rate_prompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_rate_nonprompt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        for b, k in enumerate(cntdic):
            histos['hcnt'].GetXaxis().SetBinLabel(b+1, k)
        for b, k in enumerate(cntdicWgt):
            histos['hcntWgt'].GetXaxis().SetBinLabel(b+1, k)
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

            #..........cutflowhist.............
            conjcuts = OrderedDict()
            conjcuts['nocut'] = True
            conjcuts['METcut'] = conjcuts['nocut'] * getsel.METcut()
            conjcuts['lepcut'] = conjcuts['nocut'] * getsel.METcut() * getsel.lepcut()

            muflag = False
            elflag = False
            NonPromptflag = False
            if getsel.lepcut():
                idx = getsel.getSortedLepVar()[0]['idx']
                tp = getsel.getSortedLepVar()[0]['type']
                if tp == 'mu':
                    muflag = True
                    flag=ord(ch.Muon_genPartFlav[idx])
                elif tp == 'Electron':
                    elflag = True
                    flag=ord(ch.Electron_genPartFlav[idx])
                else:
                    elflag = True
                    flag=ord(ch.LowPtElectron_genPartFlav[idx])
                NonPromptflag = not flag in [ 1 , 15 ]
            
            conjcuts['muchannel'] = conjcuts['nocut'] * getsel.METcut() * getsel.lepcut() * muflag
            conjcuts['elchannel'] = conjcuts['nocut'] * getsel.METcut() * getsel.lepcut() * elflag
            conjcuts['HTcut'] = conjcuts['nocut'] * getsel.METcut() * getsel.lepcut() * getsel.HTcut()
            conjcuts['ISRcut'] = conjcuts['nocut'] * getsel.METcut() * getsel.lepcut() * getsel.HTcut() * getsel.ISRcut()
            conjcuts['dphicut'] = conjcuts['nocut'] * getsel.METcut() * getsel.HTcut() * getsel.ISRcut() * getsel.lepcut() * getsel.dphicut()
            conjcuts['XtralepVeto'] = conjcuts['nocut'] * getsel.METcut() * getsel.HTcut() * getsel.ISRcut() * getsel.lepcut() * getsel.dphicut() * getsel.XtralepVeto()
            conjcuts['XtraJetVeto'] = conjcuts['nocut'] * getsel.METcut() * getsel.HTcut() * getsel.ISRcut() * getsel.lepcut() * getsel.dphicut() * getsel.XtralepVeto() * getsel.XtraJetVeto()
            conjcuts['tauVeto'] = conjcuts['nocut'] * getsel.METcut() * getsel.HTcut() * getsel.ISRcut() * getsel.lepcut() * getsel.dphicut() * getsel.XtralepVeto() * getsel.XtraJetVeto() * getsel.tauVeto()
            conjcuts['HardBtagjetVeto'] = conjcuts['tauVeto'] and getsel.cntBtagjet(pt=60)==0
            conjcuts['presel'] = conjcuts['nocut'] * getsel.PreSelection()
            conjcuts['filtr'] = conjcuts['nocut'] * getsel.PreSelection() * getsel.passFilters()
            conjcuts['trigr'] = conjcuts['nocut'] * getsel.PreSelection() * getsel.passFilters() * getsel.passMETTrig(trigger)
            conjcuts['NonPrompt'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag
            conjcuts['SRCR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion())
            conjcuts['SR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.SearchRegion()
            conjcuts['CR'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * getsel.ControlRegion()
            conjcuts['SR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR1()
            conjcuts['SR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR2()
            conjcuts['SR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.SR3()
            conjcuts['CR1'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR1()
            conjcuts['CR2'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR2()
            conjcuts['CR3'] = conjcuts['nocut'] * getsel.PreSelection() * muflag * NonPromptflag * ( getsel.SearchRegion() or getsel.ControlRegion()) * getsel.CR3()
            for k in conjcuts:
                histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
                histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * MCcorr)
            #........................................................#
            cntdic['nocut'] = cntdic['nocut'] + 1
            cntdicWgt['nocut'] = cntdicWgt['nocut'] + (1 * lumiscale * MCcorr)
            if not getsel.PreSelection(): continue
            cntdic['presel'] = cntdic['presel'] + 1
            cntdicWgt['presel'] = cntdicWgt['presel'] + (1 * lumiscale * MCcorr)
            #if not getsel.passFilters(): continue
            cntdic['filtr'] = cntdic['filtr'] + 1
            cntdicWgt['filtr'] = cntdicWgt['filtr'] + (1 * lumiscale * MCcorr)
            #if not getsel.passMETTrig(trigger): continue
            cntdic['trigr'] = cntdic['trigr'] + 1
            cntdicWgt['trigr'] = cntdicWgt['trigr'] + (1 * lumiscale * MCcorr)
            idx = getsel.getSortedLepVar()[0]['idx']
            tp = getsel.getSortedLepVar()[0]['type']
            promptFlag = True if isData else False
            if not isData:
                if tp == 'mu':
                    flag=ord(ch.Muon_genPartFlav[idx])
                elif tp == 'Electron':
                    flag=ord(ch.Electron_genPartFlav[idx])
                else:
                    flag=ord(ch.LowPtElectron_genPartFlav[idx])
                promptFlag = flag in [ 1 , 15 ]
            
            if region == 'SR+CR':
                if getsel.SearchRegion():
                    cntdic['SR'] = cntdic['SR'] + 1
                    cntdicWgt['SR'] = cntdicWgt['SR'] + (1 * lumiscale * MCcorr)
                    if getsel.SR1():
                        cntdic['SR1'] = cntdic['SR1'] + 1
                        cntdicWgt['SR1'] = cntdicWgt['SR1'] + (1 * lumiscale * MCcorr)
                        idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['SR1NonPrmp'] = cntdic['SR1NonPrmp'] + 1
                                cntdicWgt['SR1NonPrmp'] = cntdicWgt['SR1NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['SR1NonPrmpMu'] = cntdic['SR1NonPrmpMu'] + 1
                                    cntdicWgt['SR1NonPrmpMu'] = cntdicWgt['SR1NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                    if getsel.SR2():
                        cntdic['SR2'] = cntdic['SR2'] + 1
                        cntdicWgt['SR2'] = cntdicWgt['SR2'] + (1 * lumiscale * MCcorr)
                        idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                        if not idx <= 35:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['SR2NonPrmp'] = cntdic['SR2NonPrmp'] + 1
                                cntdicWgt['SR2NonPrmp'] = cntdicWgt['SR2NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['SR2NonPrmpMu'] = cntdic['SR2NonPrmpMu'] + 1
                                    cntdicWgt['SR2NonPrmpMu'] = cntdicWgt['SR2NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                    if getsel.SR3():
                        cntdic['SR3'] = cntdic['SR3'] + 1
                        cntdicWgt['SR3'] = cntdicWgt['SR3'] + (1 * lumiscale * MCcorr)
                        idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                        if not idx <= 71:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['SR3NonPrmp'] = cntdic['SR3NonPrmp'] + 1
                                cntdicWgt['SR3NonPrmp'] = cntdicWgt['SR3NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['SR3NonPrmpMu'] = cntdic['SR3NonPrmpMu'] + 1
                                    cntdicWgt['SR3NonPrmpMu'] = cntdicWgt['SR3NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                if getsel.ControlRegion():
                    cntdic['CR'] = cntdic['CR'] + 1
                    cntdicWgt['CR'] = cntdicWgt['CR'] + (1 * lumiscale * MCcorr)
                    if getsel.CR1():
                        cntdic['CR1'] = cntdic['CR1'] + 1
                        cntdicWgt['CR1'] = cntdicWgt['CR1'] + (1 * lumiscale * MCcorr)
                        idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 # after 108 SR bins or after bin index 107
                        #print 'idx: ', idx, ' promptFlag: ',promptFlag,' muflag',muflag
                        if not idx <= 107:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['CR1NonPrmp'] = cntdic['CR1NonPrmp'] + 1
                                cntdicWgt['CR1NonPrmp'] = cntdicWgt['CR1NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['CR1NonPrmpMu'] = cntdic['CR1NonPrmpMu'] + 1
                                    cntdicWgt['CR1NonPrmpMu'] = cntdicWgt['CR1NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                    if getsel.CR2():
                        cntdic['CR2'] = cntdic['CR2'] + 1
                        cntdicWgt['CR2'] = cntdicWgt['CR2'] + (1 * lumiscale * MCcorr)
                        idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  108 + 8
                        if not idx <= 115:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['CR2NonPrmp'] = cntdic['CR2NonPrmp'] + 1
                                cntdicWgt['CR2NonPrmp'] = cntdicWgt['CR2NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['CR2NonPrmpMu'] = cntdic['CR2NonPrmpMu'] + 1
                                    cntdicWgt['CR2NonPrmpMu'] = cntdicWgt['CR2NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
                    if getsel.CR3():
                        cntdic['CR3'] = cntdic['CR3'] + 1
                        cntdicWgt['CR3'] = cntdicWgt['CR3'] + (1 * lumiscale * MCcorr)
                        idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) + 116 + 8
                        if not idx <= 123:
                            histos['h_rate'].Fill(idx, lumiscale * MCcorr)
                            if promptFlag: histos['h_rate_prompt'].Fill(idx, lumiscale * MCcorr)
                            else:
                                cntdic['CR3NonPrmp'] = cntdic['CR3NonPrmp'] + 1
                                cntdicWgt['CR3NonPrmp'] = cntdicWgt['CR3NonPrmp'] + (1 * lumiscale * MCcorr)
                                if muflag:
                                    cntdic['CR3NonPrmpMu'] = cntdic['CR3NonPrmpMu'] + 1
                                    cntdicWgt['CR3NonPrmpMu'] = cntdicWgt['CR3NonPrmpMu'] + (1 * lumiscale * MCcorr)
                                histos['h_rate_nonprompt'].Fill(idx, lumiscale * MCcorr)
        for b, k in enumerate(cntdic):
            histos['hcnt'].SetBinContent(b+1, cntdic[k])
        for b, k in enumerate(cntdicWgt):
            histos['hcntWgt'].SetBinContent(b+1, cntdicWgt[k])
        hfile.Write()
