import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel_JEC import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning import *
from Helper.GenFilterEff import GenFilterEff
from Helper.TrigEff import *
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
    hfile = ROOT.TFile( 'CountDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_JECUp'] = HistInfo(hname = 'h_JECUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_JECDown'] = HistInfo(hname = 'h_JECDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_JERUp'] = HistInfo(hname = 'h_JERUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_JERDown'] = HistInfo(hname = 'h_JERDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    for b in range(bins):
        histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_JECUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_JECDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_JERUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_JERDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])

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
        for tp in ['Nom', 'JECUp', 'JECDown', 'JERUp', 'JERDown']:
            if tp == 'JECUp': h = histos['h_JECUp']
            elif tp == 'JECDown': h = histos['h_JECDown']
            elif tp == 'JERUp': h = histos['h_JERUp']
            elif tp == 'JERDown': h = histos['h_JERDown']
            else: h = histos['h_rate']
            
            if not getsel.PreSelection(tp): continue
            if region == 'SR':
                if not getsel.SearchRegion(tp): continue
                if getsel.SR1(tp):
                    idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1:
                        h.Fill(idx, lumiscale * MCcorr)
                if getsel.SR2(tp):
                    idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                    if not idx <= 35:
                        h.Fill(idx, lumiscale * MCcorr)
                if getsel.SR3(tp):
                    idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                    if not idx <= 71:
                        h.Fill(idx, lumiscale * MCcorr)
            if region == 'CR':
                if not getsel.ControlRegion(tp): continue
                if getsel.CR1(tp):
                    idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1:
                        h.Fill(idx, lumiscale * MCcorr)
                if getsel.CR2(tp):
                    idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                    if not idx <= 7:
                        h.Fill(idx, lumiscale * MCcorr)
                if getsel.CR3(tp):
                    idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                    if not idx <= 15:
                        h.Fill(idx, lumiscale * MCcorr)
            if region == 'SR+CR':
                if getsel.SearchRegion(tp):
                    if getsel.SR1(tp):
                        idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1:
                            h.Fill(idx, lumiscale * MCcorr)
                    if getsel.SR2(tp):
                        idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                        if not idx <= 35:
                            h.Fill(idx, lumiscale * MCcorr)
                    if getsel.SR3(tp):
                        idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                        if not idx <= 71:
                            h.Fill(idx, lumiscale * MCcorr)
                if getsel.ControlRegion(tp):
                    if getsel.CR1(tp):
                        idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 #after 108 SRbins or after bin index 107 
                        if not idx <= 107:
                            h.Fill(idx, lumiscale * MCcorr)
                    if getsel.CR2(tp):
                        idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) +  108 + 8
                        if not idx <= 115:
                            h.Fill(idx, lumiscale * MCcorr)
                    if getsel.CR3(tp):
                        idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 116 + 8
                        if not idx <= 123:
                            h.Fill(idx, lumiscale * MCcorr)
                        
    histos['h_rate'].Scale(gfltreff)
    histos['h_JECUp'].Scale(gfltreff)
    histos['h_JECDown'].Scale(gfltreff)
    histos['h_JERUp'].Scale(gfltreff)
    histos['h_JERDown'].Scale(gfltreff)

    hfile.Write()
else:
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'CountDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
	    histos = {}
            histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_JECUp'] = HistInfo(hname = 'h_JECUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_JECDown'] = HistInfo(hname = 'h_JECDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_JERUp'] = HistInfo(hname = 'h_JERUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
            histos['h_JERDown'] = HistInfo(hname = 'h_JERDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
	    for b in range(bins):
                histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_JECUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_JECDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_JERUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
                histos['h_JERDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
                for tp in ['Nom', 'JECUp', 'JECDown', 'JERUp', 'JERDown']:
                    if tp == 'JECUp': h = histos['h_JECUp']
                    elif tp == 'JECDown': h = histos['h_JECDown']
                    elif tp == 'JERUp': h = histos['h_JERUp']
                    elif tp == 'JERDown': h = histos['h_JERDown']
                    else: h = histos['h_rate']

                    if not getsel.PreSelection(tp): continue
                    if not getsel.passFilters(): continue
                    if not getsel.passMETTrig(trigger): continue
                    if region == 'SR':
                        if not getsel.SearchRegion(tp): continue
                        if getsel.SR1(tp):
                            idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.SR2(tp):
                            idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                            if not idx <= 35:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.SR3(tp):
                            idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                            if not idx <= 71:
                                h.Fill(idx, lumiscale * MCcorr)
                    if region == 'CR':
                        if not getsel.ControlRegion(tp): continue
                        if getsel.CR1(tp):
                            idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.CR2(tp):
                            idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                            if not idx <= 7:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.CR3(tp):
                            idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                            if not idx <= 15:
                                h.Fill(idx, lumiscale * MCcorr)
                    if region == 'SR+CR':
                        if getsel.SearchRegion(tp):
                            if getsel.SR1(tp):
                                idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                                if not idx == -1:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.SR2(tp):
                                idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                                if not idx <= 35:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.SR3(tp):
                                idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                                if not idx <= 71:
                                    h.Fill(idx, lumiscale * MCcorr)
                        if getsel.ControlRegion(tp):
                            if getsel.CR1(tp):
                                idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 #after 108 SRbins or after bin index 107 
                                if not idx <= 107:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.CR2(tp):
                                idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) +  108 + 8
                                if not idx <= 115:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.CR3(tp):
                                idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 116 + 8
                                if not idx <= 123:
                                    h.Fill(idx, lumiscale * MCcorr)
                
                                    
            hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'CountDCHistJEC_'+region+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_JECUp'] = HistInfo(hname = 'h_JECUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_JECDown'] = HistInfo(hname = 'h_JECDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_JERUp'] = HistInfo(hname = 'h_JERUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['h_JERDown'] = HistInfo(hname = 'h_JERDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        for b in range(bins):
            histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_JECUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_JECDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_JERUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['h_JERDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
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
            for tp in ['Nom', 'JECUp', 'JECDown', 'JERUp', 'JERDown']:
                    if tp == 'JECUp': h = histos['h_JECUp']
                    elif tp == 'JECDown': h = histos['h_JECDown']
                    elif tp == 'JERUp': h = histos['h_JERUp']
                    elif tp == 'JERDown': h = histos['h_JERDown']
                    else: h = histos['h_rate']
                    if not getsel.PreSelection(tp): continue
                    if not getsel.passFilters(): continue
                    if not getsel.passMETTrig(trigger): continue
                    if region == 'SR':
                        if not getsel.SearchRegion(tp): continue
                        if getsel.SR1(tp):
                            idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.SR2(tp):
                            idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                            if not idx <= 35:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.SR3(tp):
                            idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                            if not idx <= 71:
                                h.Fill(idx, lumiscale * MCcorr)
                    if region == 'CR':
                        if not getsel.ControlRegion(tp): continue
                        if getsel.CR1(tp):
                            idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg'])
                            if not idx == -1:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.CR2(tp):
                            idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 8
                            if not idx <= 7:
                                h.Fill(idx, lumiscale * MCcorr)
                        if getsel.CR3(tp):
                            idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 16
                            if not idx <= 15:
                                h.Fill(idx, lumiscale * MCcorr)
                    if region == 'SR+CR':
                        if getsel.SearchRegion(tp):
                            if getsel.SR1(tp):
                                idx = findSR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                                if not idx == -1:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.SR2(tp):
                                idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 36
                                if not idx <= 35:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.SR3(tp):
                                idx = findSR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 72
                                if not idx <= 71:
                                    h.Fill(idx, lumiscale * MCcorr)
                        if getsel.ControlRegion(tp):
                            if getsel.CR1(tp):
                                idx = findCR1BinIndex(getsel.calCT(1, tp), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 108 #after 108 SRbins or after bin index 107 
                                if not idx <= 107:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.CR2(tp):
                                idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) +  108 + 8
                                if not idx <= 115:
                                    h.Fill(idx, lumiscale * MCcorr)
                            if getsel.CR3(tp):
                                idx = findCR2BinIndex(getsel.calCT(2, tp), getsel.getLepMT()) + 116 + 8
                                if not idx <= 123:
                                    h.Fill(idx, lumiscale * MCcorr)

                                
        hfile.Write()
