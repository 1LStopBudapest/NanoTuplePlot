import os, sys
import ROOT
import types

from FillHistos_LL import FillHistos

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016 import samples as samples_2016
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

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

options = get_parser().parse_args()

samples  = options.sample
year = options.year


DataLumi=1.0

if year=='2016PreVFP':
    samplelist = samples_2016Pre
    DataLumi = SampleChain.luminosity_2016PreVFP
elif year=='2016PostVFP':
    samplelist = samples_2016Post
    DataLumi = SampleChain.luminosity_2016PostVFP
elif year=='2016':
    samplelist = samples_2016 
    DataLumi = SampleChain.luminosity_2016
elif year=='2017':
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018

histext = ''
vList = ['MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'LeppT', 'Lepdxy', 'LepdxySig', 'Lepdz', 'Njet', 'Nbjet', 'MupT', 'Mudxy', 'Mudz', 'epT', 'edxy', 'edz', 'AllLeppT', 'AllLepdxy', 'AllLepdxySig', 'AllLepdz', 'Nlep', '2ndLeppT', '2ndLepeta', '2ndLepdxy', '2ndLepdz']

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'StackHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
        histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
        histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
        histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
        histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
        histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['Lepdxy'] = HistInfo(hname = 'Lepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['LepdxySig'] = HistInfo(hname = 'LepdxySig', sample = histext, binning=[100,0,100], histclass = ROOT.TH1F).make_hist()
        histos['Lepdz'] = HistInfo(hname = 'Lepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
        histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['Mudxy'] = HistInfo(hname = 'Mudxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['Mudz'] = HistInfo(hname = 'Mudz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['edxy'] = HistInfo(hname = 'edxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['edz'] = HistInfo(hname = 'edz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['AllLeppT'] = HistInfo(hname = 'AllLeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['AllLepdxy'] = HistInfo(hname = 'AllLepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['AllLepdxySig'] = HistInfo(hname = 'AllLepdxySig', sample = histext, binning=[100,0,100], histclass = ROOT.TH1F).make_hist()
        histos['AllLepdz'] = HistInfo(hname = 'AllLepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['2ndLeppT'] = HistInfo(hname = '2ndLeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['2ndLepeta'] = HistInfo(hname = '2ndLepeta', sample = histext, binning=[0,1.44,1.56,2.5], histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['2ndLepdxy'] = HistInfo(hname = '2ndLepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['2ndLepdz'] = HistInfo(hname = '2ndLepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
        histos['Nlep'] = HistInfo(hname = 'Nlep', sample = histext, binning=[5,0,5], histclass = ROOT.TH1F).make_hist()
        
        ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        FillHistos(histos, ch, options.year, options.nevents, sample, vList, DataLumi, False).fill()
        hfile.Write()
else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
 
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'StackHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
    histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
    histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[40,0,200], histclass = ROOT.TH1F).make_hist()
    histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
    histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Lepdxy'] = HistInfo(hname = 'Lepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['LepdxySig'] = HistInfo(hname = 'LepdxySig', sample = histext, binning=[100,0,100], histclass = ROOT.TH1F).make_hist()
    histos['Lepdz'] = HistInfo(hname = 'Lepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Mudxy'] = HistInfo(hname = 'Mudxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Mudz'] = HistInfo(hname = 'Mudz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['edxy'] = HistInfo(hname = 'edxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['edz'] = HistInfo(hname = 'edz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['AllLeppT'] = HistInfo(hname = 'AllLeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['AllLepdxy'] = HistInfo(hname = 'AllLepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['AllLepdxySig'] = HistInfo(hname = 'AllLepdxySig', sample = histext, binning=[100,0,100], histclass = ROOT.TH1F).make_hist()
    histos['AllLepdz'] = HistInfo(hname = 'AllLepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['2ndLeppT'] = HistInfo(hname = '2ndLeppT', sample = histext, binning=[3,5,12,20,30,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['2ndLepeta'] = HistInfo(hname = '2ndLepeta', sample = histext, binning=[0,1.44,1.56,2.5], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['2ndLepdxy'] = HistInfo(hname = '2ndLepdxy', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['2ndLepdz'] = HistInfo(hname = '2ndLepdz', sample = histext, binning=[100,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Nlep'] = HistInfo(hname = 'Nlep', sample = histext, binning=[5,0,5], histclass = ROOT.TH1F).make_hist()
    ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    FillHistos(histos, ch, options.year, options.nevents, sample, vList, DataLumi, False).fill()
    hfile.Write()


