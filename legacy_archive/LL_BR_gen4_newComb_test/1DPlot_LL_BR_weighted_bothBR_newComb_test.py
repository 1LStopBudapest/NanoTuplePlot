import os, sys
import ROOT
import types

from FillHistos_LL_bothBR_newComb_test import FillHistosBothBR


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.SampleChainSplittedBothBR import SampleChainSplittedBothBR
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

from Sample.FileList_LLStops_2018_reworked import samples as samples_LL


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='MET_Data',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=str,            default='2016PostVFP',                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--br',           action='store',                    type=float,            default=0.8,                                               help="BR of the signal long lived sample. Ignore if bkg." )
    

    return argParser

options = get_parser().parse_args()

samples  = options.sample
year = options.year
branching_ratio = options.br

DataLumi=1.0


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
            
#vList = ['MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'LeppT', 'Lepdxy', 'LepdxySig', 'Lepdz', 'Njet', 'Nbjet']
#vList = ['LeppT', 'MupT', 'epT']
#vList = ['MupT', 'epT', 'MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'LeppT', 'Lepdxy', 'LepdxySig', 'Lepdz', 'Njet', 'Nbjet']
#vList = ['stopCtau', 'MET', 'MCWeight', 'gfltreff', 'lumiWeight', 'w_BRctau']
vList = ['stopCtau', 'MET','stopCtauStack']



histext = ''

sdir = '1DFiles_LL/'+year
Rootfilesdirpath = os.path.join(plotDir, sdir,'BR_'+str(branching_ratio))
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

print("plot dir is: "+str(Rootfilesdirpath))

if 'T2tt' or 'Sig_Splitted' in samples:
    sample = samples
    histext = samples
    print 'running over: ', sample
    hfile = ROOT.TFile(str(Rootfilesdirpath)+"/"+'1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}

    histos['stopCtau'] = HistInfo(hname = 'stopCtau', sample = histext, binning=[80,0,10], histclass = ROOT.TH1F).make_hist()
    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()

    histos['stopCtauStack'] = HistInfo(hname = 'stopCtauStack', sample = histext, binning=[80,0,10], histclass = ROOT.THStack).make_hist_stack()

    #control histograms
    # histos['MCWeight'] = HistInfo(hname = 'MCWeight', sample = histext, binning=[40,0,3.0], histclass = ROOT.TH1F).make_hist()
    # histos['gfltreff'] = HistInfo(hname = 'gfltreff', sample = histext, binning=[40,0,2.0], histclass = ROOT.TH1F).make_hist()
    # histos['lumiWeight'] = HistInfo(hname = 'lumiWeight', sample = histext, binning=[40,0,0.00001], histclass = ROOT.TH1F).make_hist()
    # histos['w_BRctau'] = HistInfo(hname = 'w_BRctau', sample = histext, binning=[40,0,2.0], histclass = ROOT.TH1F).make_hist()

    ch03, ch10 = SampleChainSplittedBothBR(sample, options.startfile, options.nfiles, options.year).get2chain_simple()
    print 'Total events of selected files of the', sample, 'sample BR=0.3: ', ch03.GetEntries()
    print 'Total events of selected files of the', sample, 'sample BR=1.0: ', ch10.GetEntries()
    FillHistosBothBR(hfile, histos, ch03, ch10, options.year, options.nevents, sample, vList, branching_ratio, DataLumi, False).fill2()
    hfile.Write()
else:
    print("this code doesnt work for BKG samples. Only for LL stop signal samples")

print("ejecuta hasta aqui")
outputDir = Rootfilesdirpath
for key in histos:
    if key == "stopCtauStack":
        continue
    Plot1D(histos[key], outputDir, islogy=True, canvasX=800, canvasY=600, drawOption="histe")

Plot1DStackSimple(histos["stopCtauStack"], outputDir, islogy=True, canvasX=800, canvasY=600, drawOption="histe")