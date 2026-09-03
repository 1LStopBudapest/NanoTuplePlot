import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel_LL import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning_LL import *
from Helper.GenFilterEff import GenFilterEff
from Helper.XsecUnc import *
from Helper.TrigEff import *
from Helper.FullFastSF import FullFastSF
from Helper.VarCalc import Get_ctau_sample as Get_ctau
from Sample.LLStopsSampleChain import SampleChain
from Sample.FileList_LLStops2016PreVFP import samples as samples_2016Pre
from Sample.FileList_LLStops2016PostVFP import samples as samples_2016Post
from Sample.FileList_LLStops2017 import samples as samples_2017
from Sample.FileList_LLStops2018 import samples as samples_2018

def get_parser():
    ''' Argument parser.                                                                                                                                                                                                                     
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='stopLL_1000_985',                                help="Which sample?" )
    argParser.add_argument('--BR',               action='store',                     type=str,            default='05',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2018',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--region',            action='store',                    type=str,            default='SR+CR',                                             help="Which region?" )

    return argParser

options = get_parser().parse_args()

samples  = options.sample
BR = options.BR
year = options.year
region = options.region
nEvents = options.nevents

isData = True if ('Run' in samples or 'Data' in samples) else False
DataLumi=1.0

trigger = 'HLT_PFMET120_PFMHT120_IDTight' #for inclusive MET triggers (logical OR), use 'HLT_MET_Inclusive'

trigeff = getTrigEff(year)

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
    bins = 56 + 16
    binLabel = SRBinLabelList+CRBinLabelList
else:
    bins = 1
    binLabel = ['REG']

histext = ''

if 'stopLL' in samples:
    histext = samples
    sample = samples
    print 'running over: ', sample
    ms = int(sample.split('_')[1])
    ml = int(sample.split('_')[2])
    ctau_sample_03 = Get_ctau(ms, ms-ml, 0.3)
    ctau_sample_10 = Get_ctau(ms, ms-ml, 1.0)
    ctau_ratio_threshold = 7

    gfiltr = GenFilterEff(year)
    gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    #print 'Gen filter eff: ',gfltreff
    ffsf = FullFastSF(year)
    ffsoftbSF = ffsf.getsoftbSF()
    hfile = ROOT.TFile( 'LLSigCountDCHist_'+region+'_'+sample+'_'+BR+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['h_rate'] = HistInfo(hname = 'h_rate', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_PU'] = HistInfo(hname = 'h_PU', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_PUUp'] = HistInfo(hname = 'h_PUUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_PUDown'] = HistInfo(hname = 'h_PUDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_WPt'] = HistInfo(hname = 'h_WPt', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_WPtUp'] = HistInfo(hname = 'h_WPtUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_WPtDown'] = HistInfo(hname = 'h_WPtDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_LeptonSF'] = HistInfo(hname = 'h_LeptonSF', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_LeptonSFUp'] = HistInfo(hname = 'h_LeptonSFUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_LeptonSFDown'] = HistInfo(hname = 'h_LeptonSFDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSF'] = HistInfo(hname = 'h_BTagSF', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbUp'] = HistInfo(hname = 'h_BTagSFbUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbDown'] = HistInfo(hname = 'h_BTagSFbDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlUp'] = HistInfo(hname = 'h_BTagSFlUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlDown'] = HistInfo(hname = 'h_BTagSFlDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbUpCorr'] = HistInfo(hname = 'h_BTagSFbUpCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbDownCorr'] = HistInfo(hname = 'h_BTagSFbDownCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlUpCorr'] = HistInfo(hname = 'h_BTagSFlUpCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlDownCorr'] = HistInfo(hname = 'h_BTagSFlDownCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbUpUnCorr'] = HistInfo(hname = 'h_BTagSFbUpUnCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFbDownUnCorr'] = HistInfo(hname = 'h_BTagSFbDownUnCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlUpUnCorr'] = HistInfo(hname = 'h_BTagSFlUpUnCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_BTagSFlDownUnCorr'] = HistInfo(hname = 'h_BTagSFlDownUnCorr', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_L1Prefire'] = HistInfo(hname = 'h_L1Prefire', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_L1PrefireUp'] = HistInfo(hname = 'h_L1PrefireUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    histos['h_L1PrefireDown'] = HistInfo(hname = 'h_L1PrefireDown', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()    
    histos['h_XsecUp'] = HistInfo(hname = 'h_XsecUp', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
    for b in range(bins):
        histos['h_rate'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_PU'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_PUUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_PUDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_WPt'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_WPtUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_WPtDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_LeptonSF'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_LeptonSFUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_LeptonSFDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSF'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbUpCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbDownCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlUpCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlDownCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbUpUnCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFbDownUnCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlUpUnCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_BTagSFlDownUnCorr'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_L1Prefire'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_L1PrefireUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_L1PrefireDown'].GetXaxis().SetBinLabel(b+1, binLabel[b])
        histos['h_XsecUp'].GetXaxis().SetBinLabel(b+1, binLabel[b])
    ch03, ch10 = SampleChain(sample, options.startfile, options.nfiles, year).getchains()

    #Making histograms copies
    hfTmp = ROOT.TFile( 'LLSigCountDCHist_Tmp'+'.root', 'RECREATE')
    histos03 = {}
    histos10 = {}
    histos10_tail = {}
    for hname, h in histos.items():
        histos03[hname] = h.Clone()
        histos10[hname] = h.Clone()
        histos10_tail[hname] = h.Clone()

    ###Filling from BR03 file###
    print 'Total events of selected BR03 files of the', sample, 'sample: ', ch03.GetEntries()
    n_entries03 = ch03.GetEntries()
    nevtcut = n_entries03 -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
        
    for ientry in range(n_entries03):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch03.GetEntry(ientry)
        lumiscale = (DataLumi/1000.0) * ch03.lumi_weight
        MCcorr = MCWeight(ch03, year, sample).getTotalWeight() * trigeff
        getsel = TreeVarSel(ch03, isData, year)
        if not getsel.PreSelection(): continue
        lep1 = getsel.getSortedLepVar()[0]
        lepSF = ffsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])
        fMCcorr = MCcorr * lepSF
        reweightBTag_SF_b_Up_Corr = ch03.reweightBTag_SF_b_Up_Correlated if hasattr(ch03, 'reweightBTag_SF_b_Up_Correlated') else ch03.reweightBTag_SF
        reweightBTag_SF_b_Down_Corr = ch03.reweightBTag_SF_b_Down_Correlated if hasattr(ch03, 'reweightBTag_SF_b_Down_Correlated') else ch03.reweightBTag_SF
        reweightBTag_SF_l_Up_Corr = ch03.reweightBTag_SF_l_Up_Correlated if hasattr(ch03, 'reweightBTag_SF_l_Up_Correlated') else ch03.reweightBTag_SF
        reweightBTag_SF_l_Down_Corr = ch03.reweightBTag_SF_l_Down_Correlated if hasattr(ch03, 'reweightBTag_SF_l_Down_Correlated') else ch03.reweightBTag_SF
        reweightBTag_SF_b_Up_UnCorr = ch03.reweightBTag_SF_b_Up_Uncorrelated if hasattr(ch03, 'reweightBTag_SF_b_Up_Uncorrelated') else ch03.reweightBTag_SF
        reweightBTag_SF_b_Down_UnCorr = ch03.reweightBTag_SF_b_Down_Uncorrelated if hasattr(ch03, 'reweightBTag_SF_b_Down_Uncorrelated') else ch03.reweightBTag_SF
        reweightBTag_SF_l_Up_UnCorr = ch03.reweightBTag_SF_l_Up_Uncorrelated if hasattr(ch03, 'reweightBTag_SF_l_Up_Uncorrelated') else ch03.reweightBTag_SF
        reweightBTag_SF_l_Down_UnCorr = ch03.reweightBTag_SF_l_Down_Uncorrelated if hasattr(ch03, 'reweightBTag_SF_l_Down_Uncorrelated') else ch03.reweightBTag_SF

        weight_BRctau_list = ch03.ReweightBRctau
        w_BRctau03 = weight_BRctau_list[int(BR)-1]

        #Discrad event on long tail
        if (ch03.stopCtau/ctau_sample_03) > ctau_ratio_threshold or (ch03.stopAntiCtau/ctau_sample_03) > ctau_ratio_threshold: continue

        if region == 'SR+CR':
            if getsel.SearchRegion():
                if getsel.SR1():
                    idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                    if not idx == -1:
                        histos03['h_rate'].Fill(idx, lumiscale * w_BRctau03 * fMCcorr)
                        histos03['h_PU'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPU)
                        histos03['h_PUUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUUp)
                        histos03['h_PUDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUDown)
                        histos03['h_WPt'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPt)
                        histos03['h_WPtUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtUp)
                        histos03['h_WPtDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtDown)
                        histos03['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSF)
                        histos03['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFUp)
                        histos03['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFDown)
                        histos03['h_BTagSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF)
                        histos03['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Up)
                        histos03['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Down)
                        histos03['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Up)
                        histos03['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Down)
                        histos03['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_Corr)
                        histos03['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_Corr)
                        histos03['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_Corr)
                        histos03['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_Corr)
                        histos03['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_UnCorr)
                        histos03['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_UnCorr)
                        histos03['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_UnCorr)
                        histos03['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_UnCorr)
                        histos03['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1Prefire)
                        histos03['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireUp)
                        histos03['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireDown)
                        histos03['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                if getsel.SR2():
                    idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                    if not idx <= 27:
                        histos03['h_rate'].Fill(idx, lumiscale * w_BRctau03 * fMCcorr)
                        histos03['h_PU'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPU)
                        histos03['h_PUUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUUp)
                        histos03['h_PUDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUDown)
                        histos03['h_WPt'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPt)
                        histos03['h_WPtUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtUp)
                        histos03['h_WPtDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtDown)
                        histos03['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSF)
                        histos03['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFUp)
                        histos03['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFDown)
                        histos03['h_BTagSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF)
                        histos03['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Up)
                        histos03['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Down)
                        histos03['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Up)
                        histos03['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Down)
                        histos03['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_Corr)
                        histos03['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_Corr)
                        histos03['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_Corr)
                        histos03['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_Corr)
                        histos03['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_UnCorr)
                        histos03['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_UnCorr)
                        histos03['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_UnCorr)
                        histos03['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_UnCorr)
                        histos03['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1Prefire)
                        histos03['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireUp)
                        histos03['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireDown)
                        histos03['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)

            if getsel.ControlRegion():
                if getsel.CR1():
                    idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 # after 56 SR bins or after bin index 55 
                    if not idx <= 55:
                        histos03['h_rate'].Fill(idx, lumiscale * w_BRctau03 * fMCcorr)
                        histos03['h_PU'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPU)
                        histos03['h_PUUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUUp)
                        histos03['h_PUDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUDown)
                        histos03['h_WPt'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPt)
                        histos03['h_WPtUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtUp)
                        histos03['h_WPtDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtDown)
                        histos03['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSF)
                        histos03['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFUp)
                        histos03['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFDown)
                        histos03['h_BTagSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF)
                        histos03['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Up)
                        histos03['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Down)
                        histos03['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Up)
                        histos03['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Down)
                        histos03['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_Corr)
                        histos03['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_Corr)
                        histos03['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_Corr)
                        histos03['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_Corr)
                        histos03['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_UnCorr)
                        histos03['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_UnCorr)
                        histos03['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_UnCorr)
                        histos03['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_UnCorr)
                        histos03['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1Prefire)
                        histos03['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireUp)
                        histos03['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireDown)
                        histos03['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                if getsel.CR2():
                    idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                    if not idx <= 63:
                        histos03['h_rate'].Fill(idx, lumiscale * w_BRctau03 * fMCcorr)
                        histos03['h_PU'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPU)
                        histos03['h_PUUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUUp)
                        histos03['h_PUDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightPUDown)
                        histos03['h_WPt'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPt)
                        histos03['h_WPtUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtUp)
                        histos03['h_WPtDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightwPtDown)
                        histos03['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSF)
                        histos03['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFUp)
                        histos03['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightLeptonSFDown)
                        histos03['h_BTagSF'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF)
                        histos03['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Up)
                        histos03['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_b_Down)
                        histos03['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Up)
                        histos03['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightBTag_SF_l_Down)
                        histos03['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_Corr)
                        histos03['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_Corr)
                        histos03['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_Corr)
                        histos03['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_Corr)
                        histos03['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Up_UnCorr)
                        histos03['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_b_Down_UnCorr)
                        histos03['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Up_UnCorr)
                        histos03['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau03 * reweightBTag_SF_l_Down_UnCorr)
                        histos03['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1Prefire)
                        histos03['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireUp)
                        histos03['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau03 * ch03.reweightL1PrefireDown)
                        histos03['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)

    ###Filling from BR10 file###
    print 'Total events of selected BR10 files of the', sample, 'sample: ', ch10.GetEntries()
    n_entries10 = ch10.GetEntries()
    nevtcut = n_entries10 -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
        
    for ientry in range(n_entries10):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch10.GetEntry(ientry)
        lumiscale = (DataLumi/1000.0) * ch10.lumi_weight
        MCcorr = MCWeight(ch10, year, sample).getTotalWeight() * trigeff
        getsel = TreeVarSel(ch10, isData, year)
        if not getsel.PreSelection(): continue
        lep1 = getsel.getSortedLepVar()[0]
        lepSF = ffsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])
        fMCcorr = MCcorr * lepSF
        reweightBTag_SF_b_Up_Corr = ch10.reweightBTag_SF_b_Up_Correlated if hasattr(ch10, 'reweightBTag_SF_b_Up_Correlated') else ch10.reweightBTag_SF
        reweightBTag_SF_b_Down_Corr = ch10.reweightBTag_SF_b_Down_Correlated if hasattr(ch10, 'reweightBTag_SF_b_Down_Correlated') else ch10.reweightBTag_SF
        reweightBTag_SF_l_Up_Corr = ch10.reweightBTag_SF_l_Up_Correlated if hasattr(ch10, 'reweightBTag_SF_l_Up_Correlated') else ch10.reweightBTag_SF
        reweightBTag_SF_l_Down_Corr = ch10.reweightBTag_SF_l_Down_Correlated if hasattr(ch10, 'reweightBTag_SF_l_Down_Correlated') else ch10.reweightBTag_SF
        reweightBTag_SF_b_Up_UnCorr = ch10.reweightBTag_SF_b_Up_Uncorrelated if hasattr(ch10, 'reweightBTag_SF_b_Up_Uncorrelated') else ch10.reweightBTag_SF
        reweightBTag_SF_b_Down_UnCorr = ch10.reweightBTag_SF_b_Down_Uncorrelated if hasattr(ch10, 'reweightBTag_SF_b_Down_Uncorrelated') else ch10.reweightBTag_SF
        reweightBTag_SF_l_Up_UnCorr = ch10.reweightBTag_SF_l_Up_Uncorrelated if hasattr(ch10, 'reweightBTag_SF_l_Up_Uncorrelated') else ch10.reweightBTag_SF
        reweightBTag_SF_l_Down_UnCorr = ch10.reweightBTag_SF_l_Down_Uncorrelated if hasattr(ch10, 'reweightBTag_SF_l_Down_Uncorrelated') else ch10.reweightBTag_SF

        weight_BRctau_list = ch10.ReweightBRctau
        w_BRctau10 = weight_BRctau_list[int(BR)-1]

        #Filling tail events
        if (ch10.stopCtau/ctau_sample_03) > ctau_ratio_threshold or (ch10.stopAntiCtau/ctau_sample_03) > ctau_ratio_threshold:
            if region == 'SR+CR':
                if getsel.SearchRegion():
                    if getsel.SR1():
                        idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1:
                            histos10_tail['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10_tail['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10_tail['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10_tail['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10_tail['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10_tail['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10_tail['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10_tail['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10_tail['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10_tail['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10_tail['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10_tail['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10_tail['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10_tail['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10_tail['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10_tail['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10_tail['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10_tail['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10_tail['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10_tail['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10_tail['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10_tail['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10_tail['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10_tail['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10_tail['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10_tail['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10_tail['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                    if getsel.SR2():
                        idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                        if not idx <= 27:
                            histos10_tail['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10_tail['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10_tail['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10_tail['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10_tail['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10_tail['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10_tail['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10_tail['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10_tail['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10_tail['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10_tail['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10_tail['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10_tail['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10_tail['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10_tail['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10_tail['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10_tail['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10_tail['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10_tail['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10_tail['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10_tail['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10_tail['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10_tail['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10_tail['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10_tail['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10_tail['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10_tail['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                        
                if getsel.ControlRegion():
                    if getsel.CR1():
                        idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 # after 56 SR bins or after bin index 55 
                        if not idx <= 55:
                            histos10_tail['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10_tail['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10_tail['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10_tail['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10_tail['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10_tail['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10_tail['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10_tail['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10_tail['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10_tail['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10_tail['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10_tail['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10_tail['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10_tail['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10_tail['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10_tail['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10_tail['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10_tail['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10_tail['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10_tail['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10_tail['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10_tail['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10_tail['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10_tail['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10_tail['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10_tail['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10_tail['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                    if getsel.CR2():
                        idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                        if not idx <= 63:
                            histos10_tail['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10_tail['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10_tail['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10_tail['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10_tail['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10_tail['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10_tail['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10_tail['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10_tail['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10_tail['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10_tail['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10_tail['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10_tail['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10_tail['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10_tail['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10_tail['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10_tail['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10_tail['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10_tail['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10_tail['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10_tail['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10_tail['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10_tail['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10_tail['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10_tail['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10_tail['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10_tail['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
        else: #filling non-tail events
            if region == 'SR+CR':
                if getsel.SearchRegion():
                    if getsel.SR1():
                        idx = findSR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt'], getsel.getSortedLepVar()[0]['charg'])
                        if not idx == -1:
                            histos10['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                    if getsel.SR2():
                        idx = findSR2BinIndex(getsel.calCT(2), getsel.getLepMT(), getsel.getSortedLepVar()[0]['pt']) + 28
                        if not idx <= 27:
                            histos10['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                        
                if getsel.ControlRegion():
                    if getsel.CR1():
                        idx = findCR1BinIndex(getsel.calCT(1), getsel.getLepMT(), getsel.getSortedLepVar()[0]['charg']) + 56 # after 56 SR bins or after bin index 55 
                        if not idx <= 55:
                            histos10['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)
                    if getsel.CR2():
                        idx = findCR2BinIndex(getsel.calCT(2), getsel.getLepMT()) +  56 + 8
                        if not idx <= 63:
                            histos10['h_rate'].Fill(idx, lumiscale * w_BRctau10 * fMCcorr)
                            histos10['h_PU'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPU)
                            histos10['h_PUUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUUp)
                            histos10['h_PUDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightPUDown)
                            histos10['h_WPt'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPt)
                            histos10['h_WPtUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtUp)
                            histos10['h_WPtDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightwPtDown)
                            histos10['h_LeptonSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSF)
                            histos10['h_LeptonSFUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFUp)
                            histos10['h_LeptonSFDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightLeptonSFDown)
                            histos10['h_BTagSF'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF)
                            histos10['h_BTagSFbUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Up)
                            histos10['h_BTagSFbDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_b_Down)
                            histos10['h_BTagSFlUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Up)
                            histos10['h_BTagSFlDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightBTag_SF_l_Down)
                            histos10['h_BTagSFbUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_Corr)
                            histos10['h_BTagSFbDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_Corr)
                            histos10['h_BTagSFlUpCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_Corr)
                            histos10['h_BTagSFlDownCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_Corr)
                            histos10['h_BTagSFbUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Up_UnCorr)
                            histos10['h_BTagSFbDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_b_Down_UnCorr)
                            histos10['h_BTagSFlUpUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Up_UnCorr)
                            histos10['h_BTagSFlDownUnCorr'].Fill(idx, lumiscale * w_BRctau10 * reweightBTag_SF_l_Down_UnCorr)
                            histos10['h_L1Prefire'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1Prefire)
                            histos10['h_L1PrefireUp'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireUp)
                            histos10['h_L1PrefireDown'].Fill(idx, lumiscale * w_BRctau10 * ch10.reweightL1PrefireDown)
                            histos10['h_XsecUp'].Fill(idx, lumiscale*(1+getSigXsecUnc(ms)) * fMCcorr)

    #combining histograms assigning error properly
    branching_ratio = float(BR)/10
    for key in histos:
        term_03 = histos03[key].Clone()
        term_03.Scale(1-branching_ratio)
        
        term_10 = histos10[key].Clone()
        term_10.Scale(branching_ratio)
        
        term_10_tail = histos10_tail[key].Clone()
        
        histos[key].Add(term_03)
        histos[key].Add(term_10)
        histos[key].Add(term_10_tail)

        #Error propagation
        for i in range(1, histos[key].GetNbinsX() + 1):  # Loop through all bins (1 to NbinsX)
            error10 = histos10[key].GetBinError(i)
            error03 = histos03[key].GetBinError(i)
            error10_tail = histos10_tail[key].GetBinError(i)
            
            # Calculate the propagated error: sqrt(error1^2 + error2^2)
            propagated_error_head = math.sqrt((branching_ratio**2)*(error10**2) + ((1-branching_ratio)**2)*(error03**2))
            propagated_error = math.sqrt((propagated_error_head**2) + (error10_tail**2))
            
            # Set the error for this bin in the sum histogram
            histos[key].SetBinError(i, propagated_error)
        
        #Scaling for filterEfficiency
        histos[key].Scale(1/gfltreff)
    
        histos[key].SetDirectory(hfile) 
        histos[key].Write()
        
        
    hfile.Write()

    os.system('rm LLSigCountDCHist_Tmp.root')
