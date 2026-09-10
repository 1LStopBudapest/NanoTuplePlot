import os, sys
import ROOT
import types

from FillHistos_test_lepton_truth_TM_comparison import FillHistosBothBR


sys.path.append('../../')
#sys.path.append('../')
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
vList = ['cutFlow','nLeptonMeasured','truthMatchedLepton','nLeptonGen','lepOrigin','lepOriginWhenFlag','bestDeltaRWhenFlag','TMcomparison','genPartFlavValue','2Dpt']
cutflow = ['nocut', 'lepton']



histext = ''

sdir = '1DFiles_LL_lepCount/'+year
Rootfilesdirpath = os.path.join(plotDir, sdir,'BR_'+str(branching_ratio))
if not os.path.exists(Rootfilesdirpath): 
    os.makedirs(Rootfilesdirpath)

print("plot dir is: "+str(Rootfilesdirpath))

if 'T2tt' or 'Sig_Splitted' in samples:
    sample = samples
    histext = samples
    print 'running over: ', sample
    #the TMcomp prefix keeps these files apart from the ones of the main study
    hfile = ROOT.TFile(str(Rootfilesdirpath)+"/"+'1DHist_TMcomp_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}

    histos['cutFlow'] = HistInfo(hname = 'cutFlow', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    histos['nLeptonGen'] = HistInfo(hname = 'nLeptonGen', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    histos['nLeptonMeasured'] = HistInfo(hname = 'nLeptonMeasured', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    histos['truthMatchedLepton'] = HistInfo(hname = 'truthMatchedLepton', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    histos['lepOrigin'] = HistInfo(hname = 'lepOrigin', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    #same codes as lepOrigin, plus 9 (gen lepton too far) and 10 (no gen lepton at all)
    histos['lepOriginWhenFlag'] = HistInfo(hname = 'lepOriginWhenFlag', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    #best_deltaR of the bin 9 events only, to see if the 0.01 cut is too tight
    histos['bestDeltaRWhenFlag'] = HistInfo(hname = 'bestDeltaRWhenFlag', sample = histext, binning=[100,0,0.4], histclass = ROOT.TH1F).make_hist()
    histos['TMcomparison'] = HistInfo(hname = 'TMcomparison', sample = histext, binning=[11,0,11], histclass = ROOT.TH1F).make_hist()
    #raw genPartFlav value, here bin 0 is meaningful: it means no gen match at all
    histos['genPartFlavValue'] = HistInfo(hname = 'genPartFlavValue', sample = histext, binning=[25,0,25], histclass = ROOT.TH1F).make_hist()

    histos['2Dpt'] = HistInfo(hname = '2Dpt', sample = histext, binning=[[50,0,100],[50,0,100]], histclass = ROOT.TH2F).make_hist()

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
    if key == "2Dpt":
        continue
    Plot1D(histos[key], outputDir, islogy=False, canvasX=800, canvasY=600, drawOption="histe")

Plot2D(histos["2Dpt"], 
       outputDir, 
       islogz=False, 
       canvasX=1000, canvasY=600, 
       drawOption="COLZ",
       Xtitle="gen Lepton Pt", Ytitle="reco Lepton Pt", Ztitle="Events")
