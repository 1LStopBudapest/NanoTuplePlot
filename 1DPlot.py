import os, sys
import ROOT


from FillHistos import FillHistos

sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.HistInfo import HistInfo
from Helper.PlotHelper import *


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='TTSingleLep_pow',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    

    return argParser

options = get_parser().parse_args()

histos = {}

sample  = options.sample
Rootfilesdirpath = os.path.join(plotDir, "1DFiles")
if not os.path.exists(Rootfilesdirpath): os.makedirs(Rootfilesdirpath)

hfile = ROOT.TFile('1DHist_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')

histos['MET'] = HistInfo(hname = 'MET', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['Njet20'] = HistInfo(hname = 'Njet20', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['Nbjet20'] = HistInfo(hname = 'Nbjet20', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['ISRJetPt'] = HistInfo(hname = 'ISRJetPt', sample = sample, binning=[40,0,1000], histclass = ROOT.TH1F).make_hist()
histos['Nmu'] = HistInfo(hname = 'Nmu', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['Ne'] = HistInfo(hname = 'Ne', sample = sample, binning=[10,0,10], histclass = ROOT.TH1F).make_hist()
histos['LepMT'] = HistInfo(hname = 'LepMT', sample = sample, binning=[50,0,500], histclass = ROOT.TH1F).make_hist()
histos['CT1'] = HistInfo(hname = 'CT1', sample = sample, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()
histos['CT2'] = HistInfo(hname = 'CT2', sample = sample, binning=[100,0,1000], histclass = ROOT.TH1F).make_hist()

histos['GenMuonpt'] = HistInfo(hname = 'GenMuonpt', sample = sample, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
histos['GenElept'] = HistInfo(hname = 'GenElept', sample = sample, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()
histos['GenBpt'] = HistInfo(hname = 'GenBpt', sample = sample, binning=[50,0,100], histclass = ROOT.TH1F).make_hist()


ch = SampleChain(sample, options.startfile, options.nfiles, options.year).getchain()
print ch.GetEntries()


FillHistos(histos, ch, options.year, options.nevents, sample).fill()
hfile.Write()

#outputDir = os.getcwd()

bashline = []    
bashline.append('hadd 1DHist_%s.root 1DHist_%s_*.root\n'%(sample, sample))
bashline.append('mv 1DHist_%s.root %s\n'%(sample, Rootfilesdirpath))

fsh = open("parallelHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelHist.sh')
os.system('./parallelHist.sh')
os.system('rm *.root parallelHist.sh')

outputDir = plotDir
for key in histos:
    Plot1D(histos[key], outputDir, islogy=True)
