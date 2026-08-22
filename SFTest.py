import os, sys
import ROOT
import types

sys.path.append('../')
from Helper.TreeVarSel import TreeVarSel
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from Helper.Binning import *
from Helper.GenFilterEff import GenFilterEff
from Helper.XsecUnc import *
from Helper.TrigEff import *
from Sample.SampleChain import SampleChain
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

from Helper.LeptonSF import LeptonSF
from Helper.FullFastSF import FullFastSF

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
    argParser.add_argument('--region',            action='store',                    type=str,            default='REG',                                             help="Which region?" )

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

PDFVar = 103
ScaleVar = 9

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
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
            #if not getsel.PreSelection(): continue
            #if not getsel.passFilters(): continue
            #if not getsel.passMETTrig(trigger): continue
            if not getsel.SearchRegion(): continue
        

else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    if 'Sig' in sample:
        ms = int(sample.split('_')[2])
        ml = int(sample.split('_')[3])
        gfiltr = GenFilterEff(year)
        gfltreff = gfiltr.getEff(ms,ml) if gfiltr.getEff(ms,ml) else 0.48
    else:
        gfltreff = 1.0
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
        MCwgt = MCWeight(ch, year, sample)
        getsel = TreeVarSel(ch, isData, year)
        lepsf = LeptonSF(year)
        ffsf = FullFastSF(year)

        print ffsf.getLepSF(104, -0.6, 'ele')
        
        if not getsel.PreSelection(): continue

        lepvar = getsel.getSortedLepVar()
        lep1 = lepvar[0]
        lepsfwgt = lepsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])[0]
        lepsfwgtunc = lepsf.getLepSF(lep1['pt'], lep1['eta'], lep1['type'])[1]
        
        #print MCwgt.getHEMWeight()

        eles = getsel.getEleVar()
        HEMElectrons = filter(lambda e:e['eta']<-1.392 and e['eta']>-3.00 and e['phi']<-0.87 and e['phi']>-1.57, eles )
        nHEMElectrons = len(filter(lambda e:e['eta']<-1.392 and e['eta']>-3.00 and e['phi']<-0.87 and e['phi']>-1.57, eles ))
        #print 'eles: ', eles, HEMElectrons, nHEMElectrons
        jets = []
        for idx in getsel.selectjetIdx(20):
            jets.append({'pt':ch.Jet_pt[idx], 'eta':ch.Jet_eta[idx], 'phi':ch.Jet_phi[idx]})
        HEMJets = filter( lambda j:j['pt']>20 and j['eta']>-3.2 and j['eta']<-1.2 and j['phi']>-1.77 and j['phi']<-0.67, jets )
        nHEMJets = len(filter( lambda j:j['pt']>20 and j['eta']>-3.2 and j['eta']<-1.2 and j['phi']>-1.77 and j['phi']<-0.67, jets ))
        #print 'jets: ', jets, HEMJets, nHEMJets
        
        #if not getsel.passFilters(): continue
        #if not getsel.passMETTrig(trigger): continue
        if not getsel.SearchRegion(): continue
        
    
