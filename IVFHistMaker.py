import os, sys
import ROOT
import types

from FillHistos_IVF import FillHistos_IVF

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_2016 import samples as samples_2016
from Helper.VarCalc import *


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='UL17V9_Full99mm',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year
nEvents = options.nevents

isData = True if ('Run' in samples or 'Data' in samples) else False
DataLumi=1.0

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

Rootfilesdirpath = os.path.join(plotDir, "1DFiles/IVF")
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

histext = samples
for l in list(samplelist.values()):
    if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
sample = samples
print 'running over: ', sample
hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}
histos['nSV'] = HistInfo(hname = 'nSV', sample = sample, binning=[15,0,15], histclass = ROOT.TH1F).make_hist()
histos['Ntracks'] = HistInfo(hname = 'Ntracks', sample = sample, binning=[20,0,20], histclass = ROOT.TH1F).make_hist()
histos['SVdxy'] = HistInfo(hname = 'SVdxy', sample = sample, binning=[50,0,5], histclass = ROOT.TH1F).make_hist()
histos['SVdxySig'] = HistInfo(hname = 'SVdxySig', sample = sample, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos['SVmass'] = HistInfo(hname = 'SVmass', sample = sample, binning=[20,0,10], histclass = ROOT.TH1F).make_hist()
histos['SVdlenSig'] = HistInfo(hname = 'SVdlenSig', sample = sample, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos['SVpAngle'] = HistInfo(hname = 'SVpAngle', sample = sample, binning=[50,0.5,3.5], histclass = ROOT.TH1F).make_hist()
histos['SVpT'] = HistInfo(hname = 'SVpT', sample = sample, binning=[50,0,50], histclass = ROOT.TH1F).make_hist()
histos['SVdR'] = HistInfo(hname = 'SVdR', sample = sample, binning=[40,0,4], histclass = ROOT.TH1F).make_hist()

histos['MET'] = HistInfo(hname = 'MET', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['Leppt'] = HistInfo(hname = 'Leppt', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['LepMT'] = HistInfo(hname = 'LepMT', sample = sample, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
histos['HT'] = HistInfo(hname = 'HT', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['CT1'] = HistInfo(hname = 'CT1', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['CT2'] = HistInfo(hname = 'CT2', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()

ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
n_entries = ch.GetEntries()
nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
print 'Running over total events: ', nevtcut+1
FillHistos_IVF(histos, ch, options.year, options.nevents, sample, DataLumi, False).fill()
hfile.Write()
