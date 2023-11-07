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
from Sample.FileList_UL2016 import samples as samples_2016
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

from collections import OrderedDict

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTbar',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
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

if year=='2016':
    samplelist = samples_2016 
    DataLumi = SampleChain.luminosity_2016
elif year=='2016PreVFP':
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

histext = ''
#cutflow = ['nocut', 'met200', 'ht300', 'isr', 'tauveto', 'lepton', 'xtralepton', 'xtrajetveto', 'dphi', 'met300', 'lepPt50', '0b', 'CT1300', 'lepEta15', 'CT1400', 'lepChrg', 'mt60' ]
cutflow = ['nocut', 'met200', 'ht300', 'isr', 'tauveto', 'lepton', 'xtralepton', 'xtrajetveto', 'dphi', 'SR']
ncuts = len(cutflow)

if 'T2tt' in samples:
    histext = samples
    sample = samples
    print 'running over: ', sample
    ms = int(sample.split('_')[1])
    ml = int(sample.split('_')[2])
    gfiltr = GenFilterEff(year)
    gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    print 'Gen filter eff: ',gfltreff
    hfile = ROOT.TFile( 'CFHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
    histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
    
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

        cuts = OrderedDict()
        conjcuts = OrderedDict()
        cuts['nocut'] = True
        conjcuts['nocut'] = True
        cuts['met200'] = getsel.METcut()
        conjcuts['met200'] = cuts['nocut'] * cuts['met200']
        cuts['ht300'] = getsel.HTcut()
        conjcuts['ht300'] = cuts['nocut'] *cuts['met200'] * cuts['ht300']
        cuts['isr'] = getsel.ISRcut()
        conjcuts['isr'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr']
        cuts['tauveto'] = getsel.tauVeto()
        conjcuts['tauveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto']
        cuts['lepton'] = getsel.lepcut()
        conjcuts['lepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton']
        cuts['xtralepton'] = getsel.XtralepVeto()
        conjcuts['xtralepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] 
        cuts['xtrajetveto'] = getsel.XtraJetVeto()
        conjcuts['xtrajetveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto']
        cuts['dphi'] = getsel.dphicut()
        conjcuts['dphi'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi']
        cuts['SR'] = getsel.SearchRegion()
        conjcuts['SR'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi'] * cuts['SR']
            
        for k in conjcuts:
            histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
            histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * MCcorr * gfltref)

    hfile.Write()

else:    
    if isinstance(samplelist[samples][0], types.ListType):
        histext = samples
        for s in samplelist[samples]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            print 'running over: ', sample
            hfile = ROOT.TFile( 'CFHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
            histos = {}
            histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
            histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
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

                cuts = OrderedDict()
                conjcuts = OrderedDict()
                cuts['nocut'] = True
                conjcuts['nocut'] = True
                cuts['met200'] = getsel.METcut()
                conjcuts['met200'] = cuts['nocut'] * cuts['met200']
                cuts['ht300'] = getsel.HTcut()
                conjcuts['ht300'] = cuts['nocut'] *cuts['met200'] * cuts['ht300']
                cuts['isr'] = getsel.ISRcut()
                conjcuts['isr'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr']
                cuts['tauveto'] = getsel.tauVeto()
                conjcuts['tauveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto']
                cuts['lepton'] = getsel.lepcut()
                conjcuts['lepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton']
                cuts['xtralepton'] = getsel.XtralepVeto()
                conjcuts['xtralepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] 
                cuts['xtrajetveto'] = getsel.XtraJetVeto()
                conjcuts['xtrajetveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto']
                cuts['dphi'] = getsel.dphicut()
                conjcuts['dphi'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi']
                cuts['SR'] = getsel.SearchRegion()
                conjcuts['SR'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi'] * cuts['SR']
            
                for k in conjcuts:
                    histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
                    histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * MCcorr)
                #if getsel.METcut() and getsel.HTcut() and getsel.ISRcut() and getsel.dphicut() and getsel.XtraJetVeto() and  getsel.tauVeto() and getsel.lepcut() and  getsel.XtralepVeto() and getsel.getSortedLepVar()[0]['pt'] > 30 and getsel.cntBtagjet()==0 and getsel.calCT(1) > 300 and abs(getsel.getSortedLepVar()[0]['eta'])<1.5 and getsel.calCT(1) < 400 and getsel.getSortedLepVar()[0]['charg']==-1 and getsel.getLepMT() < 60:
                    #Fill1D(histos['MET_mt60'], ch.MET_pt, lumiscale * MCcorr)
            hfile.Write()
    else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'CFHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['hcutflowRaw'] = HistInfo(hname = 'hcutflowRaw', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()
        histos['hcutflow'] = HistInfo(hname = 'hcutflow', sample = histext, binning=[ncuts,0,ncuts], histclass = ROOT.TH1F).make_hist()

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

            cuts = OrderedDict()
            conjcuts = OrderedDict()
            cuts['nocut'] = True
            conjcuts['nocut'] = True
            cuts['met200'] = getsel.METcut()
            conjcuts['met200'] = cuts['nocut'] * cuts['met200']
            cuts['ht300'] = getsel.HTcut()
            conjcuts['ht300'] = cuts['nocut'] *cuts['met200'] * cuts['ht300']
            cuts['isr'] = getsel.ISRcut()
            conjcuts['isr'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr']
            cuts['tauveto'] = getsel.tauVeto()
            conjcuts['tauveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto']
            cuts['lepton'] = getsel.lepcut()
            conjcuts['lepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton']
            cuts['xtralepton'] = getsel.XtralepVeto()
            conjcuts['xtralepton'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] 
            cuts['xtrajetveto'] = getsel.XtraJetVeto()
            conjcuts['xtrajetveto'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto']
            cuts['dphi'] = getsel.dphicut()
            conjcuts['dphi'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi']
            cuts['SR'] = getsel.SearchRegion()
            conjcuts['SR'] = cuts['nocut'] *cuts['met200'] *cuts['ht300'] * cuts['isr'] * cuts['tauveto'] * cuts['lepton'] * cuts['xtralepton'] * cuts['xtrajetveto'] * cuts['dphi'] * cuts['SR']
            
            for k in conjcuts:
                histos['hcutflowRaw'].Fill(k, conjcuts[k] * 1.0)
                histos['hcutflow'].Fill(k, conjcuts[k] * lumiscale * MCcorr)

        hfile.Write()


