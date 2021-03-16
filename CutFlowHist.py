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
from Sample.FileList_2016 import samples as samples_2016

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='MET_Run2016B',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year
nEvents = options.nevents

DataLumi=1.0

isData = True if ('Run' in samples or 'Data' in samples) else False

if year==2016:
    samplelist = samples_2016 
    DataLumi = SampleChain.luminosity_2016
elif year==2017:
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018

histext = ''
cutflow = ['nocut', 'met', 'ht', 'isr', 'lepton', 'tauveto', 'dphi', 'xtrajetveto']

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'CFHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        for c in cutflow:
            histos['MET_'+c] = HistInfo(hname = 'MET_'+c, sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['LepPt_'+c] = HistInfo(hname = 'LepPt_'+c, sample = histext, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
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
                MCcorr = MCWeight(tr, year, sample).getTotalWeight()
            Fill1D(histos['MET_nocut'], ch.MET_pt, lumiscale * MCcorr)
            if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_nocut'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut():
                Fill1D(histos['MET_met'], ch.MET_pt, lumiscale * MCcorr)
                if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_met'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut():
                Fill1D(histos['MET_ht'], ch.MET_pt, lumiscale * MCcorr)
                if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_ht'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut() and getsel.ISRcut():
                Fill1D(histos['MET_isr'], ch.MET_pt, lumiscale * MCcorr)
            if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_isr'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto():
                Fill1D(histos['MET_lepton'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['LepPt_lepton'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto():
                Fill1D(histos['MET_tauveto'], ch.MET_pt, lumiscale * MCcorr)
                Fill1D(histos['LepPt_tauveto'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto() and getsel.dphicut():
                Fill1D(histos['MET_dphi'], ch.MET_pt, lumiscale * MCcorr)
                Fill1D(histos['LepPt_dphi'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
            if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto() and getsel.dphicut() and getsel.XtraJetVeto():
                Fill1D(histos['MET_xtrajetveto'], ch.MET_pt, lumiscale * MCcorr)
                Fill1D(histos['LepPt_xtrajetveto'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
                
            hfile.Write()
else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'CFHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    for c in cutflow:
            histos['MET_'+c] = HistInfo(hname = 'MET_'+c, sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
            histos['LepPt_'+c] = HistInfo(hname = 'LepPt_'+c, sample = histext, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
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
            MCcorr = MCWeight(tr, year, sample).getTotalWeight()

        Fill1D(histos['MET_nocut'], ch.MET_pt, lumiscale * MCcorr)
        if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_nocut'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut():
            Fill1D(histos['MET_met'], ch.MET_pt, lumiscale * MCcorr)
            if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_met'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut():
            Fill1D(histos['MET_ht'], ch.MET_pt, lumiscale * MCcorr)
            if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_ht'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut() and getsel.ISRcut():
            Fill1D(histos['MET_isr'], ch.MET_pt, lumiscale * MCcorr)
            if len(getsel.getSortedLepVar()): Fill1D(histos['LepPt_isr'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto():
            Fill1D(histos['MET_lepton'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['LepPt_lepton'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto():
            Fill1D(histos['MET_tauveto'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['LepPt_tauveto'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto() and getsel.dphicut():
            Fill1D(histos['MET_dphi'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['LepPt_dphi'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
        if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.tauVeto() and getsel.dphicut() and getsel.XtraJetVeto():
            Fill1D(histos['MET_xtrajetveto'], ch.MET_pt, lumiscale * MCcorr)
            Fill1D(histos['LepPt_xtrajetveto'], getsel.getSortedLepVar()[0]['pt'], lumiscale * MCcorr)
    hfile.Write()


