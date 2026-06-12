import os, sys
import ROOT
import types

from FillHistos_LL import FillHistos
from FillHistos_LL_BR import FillHistosBR


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.SampleChainSplitted import SampleChainSplitted
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *
from Sample.FileList_UL2016PostVFP import samples as samples_2016Post
from Sample.FileList_UL2016PreVFP import samples as samples_2016Pre
from Sample.FileList_UL2017 import samples as samples_2017
from Sample.FileList_UL2018 import samples as samples_2018

from Sample.FileList_LLStops_splitted import samples as samples_LL


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
vList = ['stopCtau', 'MET', 'ISRJetPt', 'HT', 'LepMT', 'CT1', 'CT2', 'LeppT', 'Lepdxy', 'LepdxySig', 'Lepdz', 'Njet', 'Nbjet', 'MupT', 'Mudxy', 'Mudz', 'epT', 'edxy', 'edz', 'AllLeppT', 'AllLepdxy', 'AllLepdxySig', 'AllLepdz', 'Nlep', '2ndLeppT', '2ndLepeta', '2ndLepdxy', '2ndLepdz']



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

    histos['stopCtau'] = HistInfo(hname = 'stopCtau', sample = histext, binning=[40,0,10], histclass = ROOT.TH1F).make_hist()

    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning=[40,0,500], histclass = ROOT.TH1F).make_hist()
    histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['HT'] = HistInfo(hname = 'HT', sample = histext, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['LepMT'] = HistInfo(hname = 'LepMT', sample = histext, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
    histos['CT1'] = HistInfo(hname = 'CT1', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['CT2'] = HistInfo(hname = 'CT2', sample = histext, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
    histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Lepdxy'] = HistInfo(hname = 'Lepdxy', sample = histext, binning=[0,0.2,1,10], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['LepdxySig'] = HistInfo(hname = 'LepdxySig', sample = histext, binning=[20,0,1], histclass = ROOT.TH1F).make_hist()
    histos['Lepdz'] = HistInfo(hname = 'Lepdz', sample = histext, binning=[0,0.5,1,10], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Njet'] = HistInfo(hname = 'Njet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    histos['Nbjet'] = HistInfo(hname = 'Nbjet', sample = histext, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
    

    #Moises DEBUG
    histos['LeppT'] = HistInfo(hname = 'LeppT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['MupT'] = HistInfo(hname = 'MupT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['epT'] = HistInfo(hname = 'epT', sample = histext, binning=[0,3,5,12,20,30,50,100], histclass = ROOT.TH1F, binopt = 'var').make_hist()
    #######
   
    ch = SampleChainSplitted(sample, options.startfile, options.nfiles, options.year).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    FillHistosBR(histos, ch, options.year, options.nevents, sample, vList, branching_ratio, DataLumi, False).fill()
    hfile.Write()
else:
    print("this code doesnt work for BKG samples. Only for LL stop signal samples")


print("ejecuta hasta aqui")
outputDir = Rootfilesdirpath
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True, canvasX=800, canvasY=600, drawOption="histe")