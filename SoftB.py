import os, sys
import ROOT
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Helper.TreeVarSel import TreeVarSel
from Helper.VarCalc import *
from Helper.GenFilterEff import GenFilterEff
from Helper.MCWeight import MCWeight
from Sample.FileList_UL2016PostVFP import samples as samples_2016PostVFP


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

def genB(tr):
    L = []
    for i in range(tr.nGenPart):
        if abs(tr.GenPart_pdgId[i]) ==5 and tr.GenPart_genPartIdxMother[i] >=0 and tr.GenPart_genPartIdxMother[i]<tr.nGenPart:
            if abs(tr.GenPart_pdgId[tr.GenPart_genPartIdxMother[i]])==1000006 and tr.GenPart_statusFlags[tr.GenPart_genPartIdxMother[i]]==10497:
                L.append({'pt':tr.GenPart_pt[i], 'eta':tr.GenPart_eta[i], 'phi':tr.GenPart_phi[i]})
        
    return L

options = get_parser().parse_args()

samples  = options.sample
year = options.year
nEvents = options.nevents

DataLumi=1.0

isData = True if ('Run' in samples or 'Data' in samples) else False

if year=='2016PreVFP':
    samplelist = samples_2016PreVFP
    DataLumi = SampleChain.luminosity_2016PreVFP
elif year=='2016PostVFP':
    samplelist = samples_2016PostVFP
    DataLumi = SampleChain.luminosity_2016PostVFP
elif year=='2017':
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018

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
    hfile = ROOT.TFile( 'SoftB_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['Genb_pT'] = HistInfo(hname = 'Genb_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
    histos['NGenjet20'] = HistInfo(hname = 'NGenjet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['GenMET'] = HistInfo(hname = 'GenMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
    histos['NRecojet20'] = HistInfo(hname = 'NRecojet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['RecoMET'] = HistInfo(hname = 'RecoMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
    histos['NSV'] = HistInfo(hname = 'NSV', sample = histext, binning=[5,0,5], histclass = ROOT.TH1F).make_hist()
    histos['SV_pT'] = HistInfo(hname = 'SV_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
    histos['SV_m'] = HistInfo(hname = 'SV_m', sample = histext, binning=[20,0,10], histclass = ROOT.TH1F).make_hist()
    histos['SV_dxy'] = HistInfo(hname = 'SV_dxy', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
    histos['SV_Sigmadxy'] = HistInfo(hname = 'SV_Sigmadxy', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
    histos['SV_Sigdxy'] = HistInfo(hname = 'SV_Sigdxy', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
    histos['SV_dl'] = HistInfo(hname = 'SV_dl', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
    histos['SV_Sigmadl'] = HistInfo(hname = 'SV_Sigmadl', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
    histos['SV_Sigdl'] = HistInfo(hname = 'SV_Sigdl', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
    histos['SV_pAngle'] = HistInfo(hname = 'SV_pAngle', sample = histext, binning=[20,-1,1], histclass = ROOT.TH1F).make_hist()
    histos['SV_nDOF'] = HistInfo(hname = 'SV_nDOF', sample = histext, binning=[20,-1,1], histclass = ROOT.TH1F).make_hist()
    
    ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        getsel = TreeVarSel(ch, isData, year)
        lumiscale = (DataLumi/1000.0) * ch.weight
        MCcorr = MCWeight(ch, year, sample).getTotalWeight()
        Fill1D(histos['RecoMET'], ch.MET_pt, lumiscale  * MCcorr * gfltreff)
        Fill1D(histos['GenMET'], ch.GenMET_pt, lumiscale  * MCcorr * gfltreff)
        
            

    hfile.Write()

else:    
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'SoftB_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
            histos = {}
            histos['Genb_pT'] = HistInfo(hname = 'Genb_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
            histos['NGenjet20'] = HistInfo(hname = 'NGenjet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
            histos['GenMET'] = HistInfo(hname = 'GenMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
            histos['NRecojet20'] = HistInfo(hname = 'NRecojet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
            histos['RecoMET'] = HistInfo(hname = 'RecoMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
            histos['NSV'] = HistInfo(hname = 'NSV', sample = histext, binning=[5,0,5], histclass = ROOT.TH1F).make_hist()
            histos['SV_pT'] = HistInfo(hname = 'SV_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
            histos['SV_m'] = HistInfo(hname = 'SV_m', sample = histext, binning=[20,0,10], histclass = ROOT.TH1F).make_hist()
            histos['SV_dxy'] = HistInfo(hname = 'SV_dxy', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
            histos['SV_Sigmadxy'] = HistInfo(hname = 'SV_Sigmadxy', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
            histos['SV_Sigdxy'] = HistInfo(hname = 'SV_Sigdxy', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
            histos['SV_dl'] = HistInfo(hname = 'SV_dl', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
            histos['SV_Sigmadl'] = HistInfo(hname = 'SV_Sigmadl', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
            histos['SV_Sigdl'] = HistInfo(hname = 'SV_Sigdl', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
            histos['SV_pAngle'] = HistInfo(hname = 'SV_pAngle', sample = histext, binning=[20,-1,1], histclass = ROOT.TH1F).make_hist()
            histos['SV_nDOF'] = HistInfo(hname = 'SV_nDOF', sample = histext, binning=[20,-1,1], histclass = ROOT.TH1F).make_hist()

            ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
            print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
            n_entries = ch.GetEntries()
            nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
            print 'Running over total events: ', nevtcut+1
            for ientry in range(n_entries):
                if ientry > nevtcut: break
                if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
                ch.GetEntry(ientry)
                getsel = TreeVarSel(ch, isData, year)
                if isData:
                    lumiscale = 1.0
                else:
                    lumiscale = (DataLumi/1000.0) * ch.weight
                if isData:
                    MCcorr = 1.0
                else:
                    MCcorr = MCWeight(ch, year, sample).getTotalWeight()
                Fill1D(histos['RecoMET'], ch.MET_pt, lumiscale * MCcorr)
                Fill1D(histos['GenMET'], ch.GenMET_pt, lumiscale  * MCcorr)
            
        hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'SoftB_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['Genb_pT'] = HistInfo(hname = 'Genb_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
        histos['NGenjet20'] = HistInfo(hname = 'NGenjet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        histos['GenMET'] = HistInfo(hname = 'GenMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
        histos['NRecojet20'] = HistInfo(hname = 'NRecojet20', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        histos['RecoMET'] = HistInfo(hname = 'RecoMET', sample = histext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
        histos['NSV'] = HistInfo(hname = 'NSV', sample = histext, binning=[5,0,5], histclass = ROOT.TH1F).make_hist()
        histos['SV_pT'] = HistInfo(hname = 'SV_pT', sample = histext, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
        histos['SV_m'] = HistInfo(hname = 'SV_m', sample = histext, binning=[20,0,10], histclass = ROOT.TH1F).make_hist()
        histos['SV_dxy'] = HistInfo(hname = 'SV_dxy', sample = histext, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
        histos['SV_Sigdxy'] = HistInfo(hname = 'SV_Sigdxy', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
        histos['SV_dl'] = HistInfo(hname = 'SV_dl', sample = histext, binning=[50,0,10], histclass = ROOT.TH1F).make_hist()
        histos['SV_Sigdl'] = HistInfo(hname = 'SV_Sigdl', sample = histext, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
        histos['SV_pAngle'] = HistInfo(hname = 'SV_pAngle', sample = histext, binning=[50,0.5,1], histclass = ROOT.TH1F).make_hist()
        histos['SV_nDOF'] = HistInfo(hname = 'SV_nDOF', sample = histext, binning=[20,-1,1], histclass = ROOT.TH1F).make_hist()
        histos['SV_Chi_nDOF'] = HistInfo(hname = 'SV_Chi_nDOF', sample = histext, binning=[20,-10,10], histclass = ROOT.TH1F).make_hist()

        ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            getsel = TreeVarSel(ch, isData, year)
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0
            else:
                lumiscale = (DataLumi/1000.0) * ch.weight
                MCcorr = MCWeight(ch, year, sample).getTotalWeight()

            Fill1D(histos['RecoMET'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['GenMET'], ch.GenMET_pt, lumiscale  * MCcorr)
            for b in genB(ch):
                Fill1D(histos['Genb_pT'], b['pt'], lumiscale * MCcorr)
            Fill1D(histos['NSV'], getsel.cntSoftB(), lumiscale  * MCcorr)
            for i in getsel.selectSoftBIdx():
                Fill1D(histos['SV_pT'], ch.SV_pt[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_m'], ch.SV_mass[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_dl'], ch.SV_dlen[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_Sigdl'], ch.SV_dlenSig[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_pAngle'], ch.SV_pAngle[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_nDOF'], ch.SV_ndof[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_Chi_nDOF'], ch.SV_chi2[i]/ch.SV_ndof[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_dxy'], ch.SV_dxy[i], lumiscale  * MCcorr)
                Fill1D(histos['SV_Sigdxy'], ch.SV_dxySig[i], lumiscale  * MCcorr)
        hfile.Write()


