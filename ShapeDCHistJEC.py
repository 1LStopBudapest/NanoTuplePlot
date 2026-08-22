import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel_JEC import TreeVarSel
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
from Sample.SampleList import *

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
trigger = 'HLT_PFMET120_PFMHT120_IDTight' #for inclusive MET triggers (logical OR), use 'HLT_MET_Inclusive'
shapebins = ShapeDCbins
Jtp = ['Nom', 'JECUp', 'JECDown', 'JERUp', 'JERDown']

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
    ShapebinlPtbinMap = ShapebinlPtbinMapSC
elif region == 'SR':
    ShapebinlPtbinMap = ShapebinlPtbinMapS
else:
    ShapebinlPtbinMap = ShapebinlPtbinMapSC
    print('Using default SR+CR bin setting, check the --region')
   
histext = ''

if 'T2tt' in samples:
    histext = 'signal'
    sample = samples
    print 'running over: ', sample
    ms = int(sample.split('_')[1])
    ml = int(sample.split('_')[2])
    gfiltr = GenFilterEff(year)
    gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    trigeff = getTrigEff(year)
    ffsf = FullFastSF(year)
    softbSF = ffsf.getsoftbSF()
    hfile = ROOT.TFile( 'ShapeDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    for b in range(shapebins):
        for tp in Jtp:
            histos['Bin'+str(b)+'_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
     
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
        for tp in Jtp:
            if not getsel.PreSelection(tp): continue
            lep1 = getsel.getSortedLepVar()[0]
            lepSF = ffsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])
            fMCcorr = MCcorr * softbSF * lepSF
            if region == 'SR':
                if not getsel.SearchRegion(tp): continue
                if getsel.SR1(tp):
                    shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                    lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx != -1 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
                if getsel.SR2(tp):
                    shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                    lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx > 7 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
                if getsel.SR3(tp):
                    shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                    lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx > 15 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
            if region == 'SR+CR':
                if not getsel.SCRegion(tp): continue
                if getsel.SCR1(tp):
                    shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                    lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx != -1 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
                if getsel.SCR2(tp):
                    shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                    lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx > 7 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
                if getsel.SCR3(tp):
                    shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                    lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                    if shapeIdx > 15 and lptIdx!=-1:
                        histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * fMCcorr)
    for b in range(shapebins):                
        for tp in Jtp:
            histos['Bin'+str(b)+'_'+tp].Scale(gfltreff)
    hfile.Write()

else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = 'data_obs' if isData else samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'ShapeDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
            histos = {}
            for b in range(shapebins):
                for tp in Jtp:
                    histos['Bin'+str(b)+'_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
                    histos['Bin'+str(b)+'_prompt_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_prompt_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
                    histos['Bin'+str(b)+'_nonprompt_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_nonprompt_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
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
                for tp in Jtp:
                    if not getsel.PreSelection(tp): continue
                    if not getsel.passFilters(): continue
                    if not getsel.passMETTrig(trigger): continue
                    idx = getsel.getSortedLepVar()[0]['idx']
                    typ = getsel.getSortedLepVar()[0]['type']
                    promptFlag = True if isData else False
                    if not isData:
                        if typ == 'mu':
                            flag=ord(ch.Muon_genPartFlav[idx])
                        elif typ == 'Electron':
                            flag=ord(ch.Electron_genPartFlav[idx])
                        else:
                            flag=ord(ch.LowPtElectron_genPartFlav[idx])
                        promptFlag = flag in [ 1 , 15 ]
                                                                                                                        
                    if region == 'SR':
                        if not getsel.SearchRegion(tp): continue
                        if getsel.SR1(tp):
                            shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                            lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                            if shapeIdx != -1 and lptIdx!=-1:
                                histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if getsel.SR2(tp):
                                shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                                lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                                if shapeIdx > 7 and lptIdx!=-1:
                                    histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                    if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                    else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if getsel.SR3(tp):
                                shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                                lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                                if shapeIdx > 15 and lptIdx!=-1:
                                    histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                    if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                    else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                    if region == 'SR+CR':
                        if not getsel.SCRegion(tp): continue
                        if getsel.SCR1(tp):
                            shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                            lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                            if shapeIdx != -1 and lptIdx!=-1:
                                histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                        if getsel.SCR2(tp):
                            shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                            lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                            if shapeIdx > 7 and lptIdx!=-1:
                                histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                        if getsel.SCR3(tp):
                            shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                            lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                            if shapeIdx > 15 and lptIdx != -1:
                                histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                                else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
            hfile.Write()           
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'ShapeDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        for b in range(shapebins):
            for tp in Jtp:
                histos['Bin'+str(b)+'_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
                histos['Bin'+str(b)+'_prompt_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_prompt_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
                histos['Bin'+str(b)+'_nonprompt_'+tp] = HistInfo(hname = 'Bin'+str(b)+'_nonprompt_'+tp, sample = histext, binning = [ShapebinlPtbinMap[b], 0, ShapebinlPtbinMap[b]], histclass = ROOT.TH1F).make_hist()
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
            for tp in Jtp:
                if not getsel.PreSelection(tp): continue
                if not getsel.passFilters(): continue
                if not getsel.passMETTrig(trigger): continue
                idx = getsel.getSortedLepVar()[0]['idx']
                typ = getsel.getSortedLepVar()[0]['type']
                promptFlag = True if isData else False
                if not isData:
                    if typ == 'mu':
                        flag=ord(ch.Muon_genPartFlav[idx])
                    elif typ == 'Electron':
                        flag=ord(ch.Electron_genPartFlav[idx])
                    else:
                        flag=ord(ch.LowPtElectron_genPartFlav[idx])
                    promptFlag = flag in [ 1 , 15 ]
                                                                        
                if region == 'SR':
                    if not getsel.SearchRegion(tp): continue
                    if getsel.SR1(tp):
                        shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                        lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx != -1 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                    if getsel.SR2(tp):
                        shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                        lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx > 7 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                    if getsel.SR3(tp):
                        shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                        lptIdx = findLepPtBin(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx > 15 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                if region == 'SR+CR':
                    if not getsel.SCRegion(tp): continue
                    if getsel.SCR1(tp):
                        shapeIdx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                        lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx != -1 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                    if getsel.SCR2(tp):
                        shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                        lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx > 7 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                    if getsel.SCR3(tp):
                        shapeIdx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                        lptIdx = findLepPtBinSC(getsel.getSortedLepVar()[0]['pt'], getsel.getLepMT())
                        if shapeIdx > 15 and lptIdx!=-1:
                            histos['Bin'+str(shapeIdx)+'_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            if promptFlag: histos['Bin'+str(shapeIdx)+'_prompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                            else: histos['Bin'+str(shapeIdx)+'_nonprompt_'+tp].Fill(lptIdx-1, lumiscale * MCcorr)
                        
        hfile.Write()
